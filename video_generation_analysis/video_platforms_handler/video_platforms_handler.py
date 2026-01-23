import logging
from pathlib import Path

from video_generation_analysis.video_platforms_handler.platform_api_bridge import (
    PlatformApiBridge,
    VideoEngagement,
)


class VideoPlatformsFacade:
    """Facade to handle publishing videos to multiple platforms."""

    def __init__(self, publishers: list[PlatformApiBridge]):
        self._publishers = publishers
        self._logger: logging.Logger = logging.getLogger(__name__)

    def publish_to_all(
        self, file_path: Path, title: str, description: str, tags: list[str]
    ) -> list[str]:
        """Provides a simple interface to publish to all configured platforms"""
        urls = []
        for publisher in self._publishers:
            self._logger.info(
                f"Publishing video '{title}' to {publisher.__class__.__name__}"
            )
            url = publisher.publish_video(file_path, title, description, tags)
            if url:
                urls.append(url)
        return urls

    def get_engagement_metrics_all(self, video_url: list[str]) -> VideoEngagement:
        """Provides a simple interface to get engagement metrics from all platforms"""
        total_engagement = VideoEngagement()
        for idx, publisher in enumerate(self._publishers):
            engagement = publisher.get_engagement_metrics(video_url[idx])
            if engagement:
                total_engagement.add(engagement)
        return total_engagement
