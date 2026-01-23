from datetime import datetime

from video_generation_analysis.config import NUM_KEYWORDS
from video_generation_analysis.database_handler.database_handler import DatabaseHandler
from video_generation_analysis.database_handler.schema import VideoEngagementRecord
from video_generation_analysis.video_generator.description_generator import (
    DescriptionGenerator,
)
from video_generation_analysis.video_generator.video_generator import VideoGenerator
from video_generation_analysis.video_platforms_handler.video_platforms_handler import (
    VideoPlatformsFacade,
)
from video_generation_analysis.video_platforms_handler.youtube_api_bridge import (
    YouTubeApiBridge,
)


class VideoAnalytics:
    def __init__(
        self,
        db_handler: DatabaseHandler,
        description_generator: DescriptionGenerator,
        video_generator: VideoGenerator = None,
        video_platforms: VideoPlatformsFacade = None,
    ):
        self._database_handler = db_handler
        self._description_generator = description_generator
        self._video_generator = video_generator or VideoGenerator()
        self._video_platforms = video_platforms or VideoPlatformsFacade(
            [YouTubeApiBridge()]
        )

    def generate_video(self, num_top_videos: int, prompt: str = "") -> None:
        """Create video from prompt, publish to platforms, put engagement db record"""
        title, description, keywords = self._description_generator.generate_description(
            num_new_keywords=NUM_KEYWORDS,
            num_top_videos=num_top_videos,
            prompt=prompt,
        )

        video_file = self._video_generator.create_video(description)
        if video_file is None:
            raise ValueError("Video generation failed")

        urls = self._video_platforms.publish_to_all(
            file_path=video_file,
            title=title,
            description=description,
            tags=keywords,
        )
        if not urls:
            raise ValueError("Video publishing failed")

        self._video_generator.delete_local_video(video_file)

        video_record = VideoEngagementRecord(
            datetime_publish=datetime.now(),
            title=title,
            description=description,
            keywords=keywords,
            urls=urls,
            views=0,
            likes=0,
            comments=0,
        )

        with self._database_handler as db:
            db.create(video_record)
