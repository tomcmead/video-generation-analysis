import logging
import os
from pathlib import Path
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
    VideoEngagement,
)


class YouTubeApiBridge(PlatformApiBridge):
    def __init__(self):
        load_dotenv()
        self._client_secrets = os.getenv(YOUTUBE_CLIENT_SECRETS_ENV, "")
        self._logger = logging.getLogger(__name__)
        self._YOUTUBE_URL_PREFIX = "https://www.youtube.com/watch?v="
        self._is_authenticated = False

        if not self._client_secrets:
            self._logger.error(
                f"Failed {YOUTUBE_CLIENT_SECRETS_ENV} not found environment variable"
            )
            raise ValueError(
                f"Set API key in {YOUTUBE_CLIENT_SECRETS_ENV} environment variable"
            )

    def publish_video(
        self, video_path: Path, title: str, desc: str, tags: list[str]
    ) -> Optional[str]:
        """Uploads the video file and inserts the video resource to YouTube"""
        if not video_path.is_file():
            raise OSError(f"File not found: {video_path}")

        if not self._is_authenticated:
            self._authenticate_youtube()

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
            filename=video_path.resolve(),
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

            return f"{self._YOUTUBE_URL_PREFIX}{response.get('id')}"

        except HttpError as e:
            self._logger.error(
                f"YouTube API Publishing HTTP Error: {e.resp.status} - {e.content}"
            )
            return None
        except Exception as e:
            self._logger.error(f"YouTube API unexpected error during upload: {e}")
            return None

    def get_engagement_metrics(self, video_url: str) -> Optional[VideoEngagement]:
        """Fetches engagement metrics [views, likes, comments] for URL"""
        video_id = video_url[
            len(self._YOUTUBE_URL_PREFIX) :
        ]  # extract video ID from URL

        if not self._is_authenticated:
            self._authenticate_youtube()

        try:
            request = self._youtube_service.videos().list(
                part="statistics,snippet", id=video_id
            )
            response = request.execute()

            if not response["items"]:
                self._logger.warning(f"No video found with ID: {video_id}")
                return None

            stats = response["items"][0]["statistics"]

            return VideoEngagement(
                views=int(stats.get("viewCount", 0)),
                likes=int(stats.get("likeCount", 0)),
                comments=int(stats.get("commentCount", 0)),
            )

        except HttpError as e:
            self._logger.error(f"YouTube API Fetching Engagement HTTP Error: {e}")
            return None

    def _authenticate_youtube(self):
        flow = InstalledAppFlow.from_client_secrets_file(
            self._client_secrets, YOUTUBE_SCOPES
        )
        credentials = flow.run_local_server(port=0)
        self._youtube_service = build(
            YOUTUBE_API_VERSION, YOUTUBE_SERVICE_NAME, credentials=credentials
        )
        self._is_authenticated = True
