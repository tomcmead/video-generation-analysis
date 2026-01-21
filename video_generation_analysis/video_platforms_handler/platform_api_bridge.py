from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class VideoEngagement:
    views: int = 0
    likes: int = 0
    comments: int = 0

    def add(self, other: "VideoEngagement") -> None:
        self.views += other.views
        self.likes += other.likes
        self.comments += other.comments


class PlatformApiBridge(ABC):
    """Defines the low-level platform operations."""

    @abstractmethod
    def publish_video(
        self, video_path: Path, title: str, desc: str, tags: list[str]
    ) -> Optional[str]:
        """Publishes video to platform, returns video URL if successful"""
        pass

    @abstractmethod
    def get_engagement_metrics(self, video_url: str) -> Optional[VideoEngagement]:
        """Fetches engagement metrics [views, likes, comments] for URL"""
        pass
