import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from video_generation_analysis.database_handler.database_handler import DatabaseHandler
from video_generation_analysis.database_handler.query_builder import (
    QueryBuilder,
)
from video_generation_analysis.database_handler.schema import VideoEngagementRecord
from video_generation_analysis.video_analytics.video_analytics import VideoAnalytics
from video_generation_analysis.video_platforms_handler.video_platforms_handler import (
    VideoEngagement,
)


class TestVideoAnalytis(unittest.TestCase):
    DB_PATH = Path("test_db.sqlite")
    TABLE_NAME = VideoEngagementRecord.__name__.lower() + "s"
    TEST_DATETIME = datetime(2025, 11, 25, 12, 0, 0)
    TEST_VIDEO_FILE = Path("test_video.mp4")
    TEST_VIDEO_PROMPT = "Test Prompt for Video Generation"
    TEST_TITLE = "Test Video Title"
    TEST_DESCRIPTION = "This is a test description for the video"
    TEST_KEYWORDS = ["test", "video", "keywords"]
    TEST_VIDEO_URLS = ["https://www.youtube.com/watch?v=12345"]

    TEST_RECORD_A = VideoEngagementRecord(
        datetime_publish=TEST_DATETIME,
        title="Test Video A",
        description="A short description.",
        urls=["url_a1", "url_a2"],
        views=2000,
        likes=100,
        comments=10,
        keywords=["tutorial", "python"],
    )
    TEST_RECORD_B = VideoEngagementRecord(
        datetime_publish=TEST_DATETIME,
        title="Test Video B",
        description="Another short description.",
        urls=["url_b1"],
        views=1000,
        likes=50,
        comments=5,
        keywords=["gaming", "fun"],
    )
    TEST_RECORDS = [TEST_RECORD_A, TEST_RECORD_B]
    UPDATED_VIDEO_ENGAGEMENT = VideoEngagement(views=3000, likes=150, comments=15)

    def setUp(self):
        self.tearDown()
        self._db_handler = DatabaseHandler(Path(self.DB_PATH), VideoEngagementRecord)

    def tearDown(self):
        if self.DB_PATH.exists():
            self.DB_PATH.unlink()
        if self.TEST_VIDEO_FILE.exists():
            self.TEST_VIDEO_FILE.unlink()

    @patch(
        "video_generation_analysis.video_generator.video_generator.VideoGenerator",
    )
    @patch(
        "video_generation_analysis.video_platforms_handler.video_platforms_handler.VideoPlatformsFacade",
    )
    @patch(
        "video_generation_analysis.video_generator.description_generator.DescriptionGenerator",
    )
    def test_generate_video(
        self, mock_description_generator, mock_platforms, mock_video_generator
    ):
        (
            mock_desc_inst,
            mock_platforms_inst,
            mock_video_gen_inst,
        ) = self._setup_mocks_generate_video(
            description=mock_description_generator,
            platforms=mock_platforms,
            video_generator=mock_video_generator,
        )
        video_analytics = VideoAnalytics(
            db_handler=self._db_handler,
            description_generator=mock_desc_inst,
            video_generator=mock_video_gen_inst,
            video_platforms=mock_platforms_inst,
        )
        self.TEST_VIDEO_FILE.touch()

        video_analytics.generate_video(num_top_videos=5, prompt=self.TEST_VIDEO_PROMPT)

        mock_desc_inst.generate_description.assert_called_once()
        mock_platforms_inst.publish_to_all.assert_called_once()
        mock_video_gen_inst.create_video.assert_called_once()

        with self._db_handler as db:
            qb = QueryBuilder().select_columns("*")
            records = db.read(qb)

            for record in records:
                assert record.title == self.TEST_TITLE
                assert record.description == self.TEST_DESCRIPTION
                assert record.keywords == self.TEST_KEYWORDS
                assert record.urls == self.TEST_VIDEO_URLS
                assert int(record.views) == 0
                assert int(record.likes) == 0
                assert int(record.comments) == 0

    def _setup_mocks_generate_video(self, **mocks):
        mock_description = mocks["description"].return_value
        mock_platforms = mocks["platforms"].return_value
        mock_video_generator = mocks["video_generator"].return_value

        mock_description.generate_description.return_value = (
            self.TEST_TITLE,
            self.TEST_DESCRIPTION,
            self.TEST_KEYWORDS,
        )
        mock_platforms.publish_to_all.return_value = self.TEST_VIDEO_URLS
        mock_platforms.get_engagement_metrics_all.return_value = (
            self.UPDATED_VIDEO_ENGAGEMENT
        )
        mock_video_generator.create_video.return_value = self.TEST_VIDEO_FILE

        return mock_description, mock_platforms, mock_video_generator
