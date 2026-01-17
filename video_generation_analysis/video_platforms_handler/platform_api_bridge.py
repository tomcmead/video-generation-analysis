from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class PlatformApiBridge(ABC):
    """Defines the low-level platform operations."""

    @abstractmethod
    def publish_video(
        self, video_path: Path, title: str, desc: str, tags: list[str]
    ) -> Optional[str]:
        """Publishes video to platform, returns video URL if successful"""
        pass

    @abstractmethod
    def get_engagement_metrics(self, video_url: str) -> Optional[tuple[int, int, int]]:
        """Fetches engagement metrics [views, likes, comments] for URL"""
        pass
