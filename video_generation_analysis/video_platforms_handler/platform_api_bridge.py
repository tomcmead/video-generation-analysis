from abc import ABC, abstractmethod
from typing import Optional


class PlatformApiBridge(ABC):
    """Defines the low-level platform operations."""

    @abstractmethod
    def publish_video(self, video_path, title, desc, tags) -> Optional[str]:
        pass
