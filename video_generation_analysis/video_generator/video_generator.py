import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Optional
from uuid import uuid4

from dotenv import load_dotenv
from google.genai import Client, errors, types
from google.genai.types import Operation

from video_generation_analysis.config import (
    GEMINI_API_KEY_ENV,
    GEMINI_MODEL_NAME,
    VIDEO_ASPECT_RATIO,
    VIDEO_DURATION_SECONDS,
)


class VideoGenerator:
    """VideoGenerator uses Google Gemini API to create videos from text prompts"""

    def __init__(self):
        load_dotenv()
        self._gemini_api_key = os.getenv(GEMINI_API_KEY_ENV, "")
        self._logger = logging.getLogger(__name__)

        if not self._gemini_api_key:
            self._logger.error(
                f"Failed {GEMINI_API_KEY_ENV} not found in environment variables"
            )
            raise ValueError(
                f"Set API key in {GEMINI_API_KEY_ENV} environment variable"
            )

    @asynccontextmanager
    async def _get_async_client(self):
        """Context manager to ensure the asynchronous client is open/closed"""
        aclient = None
        try:
            aclient = Client(api_key=self._gemini_api_key).aio
            yield aclient
        finally:
            if aclient:
                await aclient.aclose()

    def create_video(self, prompt: str) -> Optional[str]:
        """Generate video, wait for result and download it locally"""
        try:
            video_path = asyncio.run(self._await_create_video(prompt))
            return video_path
        except Exception as e:
            self._logger.error(f"Unhandled error in synchronous wrapper: {e}")
            return None

    async def _poll_for_completion(
        self, aclient: Client.aio, operation: Operation
    ) -> Operation:
        max_poll_attempts = 50
        poll_interval_seconds = 5
        for attempt in range(max_poll_attempts):
            if operation.done:
                return operation

            await asyncio.sleep(poll_interval_seconds)
            operation = await aclient.operations.get(operation)

        raise TimeoutError(
            f"Video generation timed out {max_poll_attempts * poll_interval_seconds}s"
        )

    async def _await_create_video(self, prompt: str) -> Optional[str]:
        async with self._get_async_client() as aclient:
            try:
                request = await aclient.models.generate_videos(
                    model=GEMINI_MODEL_NAME,
                    prompt=prompt,
                    config=types.GenerateVideosConfig(
                        duration_seconds=VIDEO_DURATION_SECONDS,
                        aspect_ratio=VIDEO_ASPECT_RATIO,
                    ),
                )

                operation = await self._poll_for_completion(aclient, request)

                if operation.error:
                    raise errors.APIError(
                        response_json=f"Error: {operation.error.message}",
                        code=operation.error.code,
                    )

                if not operation.response or not operation.response.generated_videos:
                    self._logger.warning(
                        "Operation completed but no video was found in the response."
                    )
                    return None

                generated_video = operation.response.generated_videos[0]
                video_title = f"{uuid4()}.mp4"
                await generated_video.video.download(download_path=video_title)

                return video_title

            except TimeoutError as e:
                self._logger.error(
                    f"Timeout occurred during video generation prompt '{prompt}': {e}"
                )
            except errors.APIError as e:
                self._logger.error(
                    f"API Error {e.code} creating video prompt '{prompt}': {e.message}"
                )
            except Exception as e:
                self._logger.critical(
                    f"An unexpected error occurred: {e}", exc_info=True
                )

            return None
