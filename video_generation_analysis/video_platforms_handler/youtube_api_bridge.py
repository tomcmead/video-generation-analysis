import logging
import os
from typing import Optional

from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from video_generation_analysis.config import (
    YOUTUBE_API_VERSION,
    YOUTUBE_CLIENT_SECRETS_ENV,
    YOUTUBE_SCOPES,
    YOUTUBE_SERVICE_NAME,
)
from video_generation_analysis.video_platforms_handler.platform_api_bridge import (
    PlatformApiBridge,
)


class YouTubeApiBridge(PlatformApiBridge):
    def __init__(self):
        load_dotenv()
        self._client_secrets = os.getenv(YOUTUBE_CLIENT_SECRETS_ENV, "")
        self._logger = logging.getLogger(__name__)

        if not self._client_secrets:
            self._logger.error(
                f"Failed {YOUTUBE_CLIENT_SECRETS_ENV} not found environment variable"
            )
            raise ValueError(
                f"Set API key in {YOUTUBE_CLIENT_SECRETS_ENV} environment variable"
            )

        # authenticate
        flow = InstalledAppFlow.from_client_secrets_file(
            self._client_secrets, YOUTUBE_SCOPES
        )
        credentials = flow.run_local_server(port=0)
        self._youtube_service = build(
            YOUTUBE_API_VERSION, YOUTUBE_SERVICE_NAME, credentials=credentials
        )

    def publish_video(
        self, video_path: str, title: str, desc: str, tags: list[str]
    ) -> Optional[str]:
        """
        Uploads the video file and inserts the video resource into YouTube.
        """
        if not os.path.exists(video_path):
            raise OSError(f"File not found: {video_path}")

        body = {
            "snippet": {
                "title": title,
                "description": desc,
                "categoryId": 24,  # Entertainment category
                "tags": tags,
            },
            "status": {
                "privacyStatus": "public",
                "notifySubscribers": True,
            },
        }

        media = MediaFileUpload(
            filename=video_path,
            chunksize=-1,  # -1 means chunking is managed automatically
            resumable=True,
            mimetype="video/*",
        )

        try:
            # API insert method to upload video
            request = self._youtube_service.videos().insert(
                part="snippet,status", body=body, media_body=media
            )

            # wait for upload to complete
            response = None
            while response is None:
                status, response = request.next_chunk()

            return f"https://www.youtube.com/watch?v={response.get('id')}"

        except HttpError as e:
            self._logger.error(
                f"YouTube API HTTP error occurred: {e.resp.status} - {e.content}"
            )
            return None
        except Exception as e:
            self._logger.error(f"YouTube API unexpected error during upload: {e}")
            return None
