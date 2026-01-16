from pathlib import Path

from video_generation_analysis.video_platforms_handler.platform_api_bridge import (
    PlatformApiBridge,
)


class VideoPlatformsFacade:
    """Facade to handle publishing videos to multiple platforms."""

    def __init__(self, publishers: list[PlatformApiBridge]):
        self._publishers = publishers

    def publish_to_all(
        self, file_path: Path, title: str, description: str, tags: list[str]
    ) -> list[str]:
        """
        Provides a simple interface to publish to all configured platforms.
        """
        print(f"Starting VideoPlatformsFacade Publish for: {title}")
        urls = []
        for publisher in self._publishers:
            print(f"--- Publishing via {publisher.__class__.__name__} ---")
            url = publisher.publish_video(file_path, title, description, tags)
            if url:
                urls.append(url)
        print("Publish sequence complete.")
        return urls
