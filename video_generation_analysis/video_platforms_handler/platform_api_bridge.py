from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class PlatformApiBridge(ABC):
    """Defines the low-level platform operations."""

    @abstractmethod
    def publish_video(
        self, video_path: Path, title: str, desc: str, tags: list[str]
    ) -> Optional[str]:
        pass
