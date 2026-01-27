import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from video_generation_analysis.database_handler.database_handler import DatabaseHandler
from video_generation_analysis.database_handler.query_builder import (
    OrderByType,
    QueryBuilder,
)
from video_generation_analysis.database_handler.schema import VideoEngagementRecord
from video_generation_analysis.video_analytics.video_analytics import VideoAnalytics
from video_generation_analysis.video_platforms_handler.video_platforms_handler import (
    VideoEngagement,
)


@patch(
    "video_generation_analysis.video_generator.video_generator.VideoGenerator",
)
@patch(
    "video_generation_analysis.video_platforms_handler.video_platforms_handler.VideoPlatformsFacade",
)
@patch(
    "video_generation_analysis.video_generator.description_generator.DescriptionGenerator",
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

    UPDATED_ENGAGEMENT = VideoEngagement(views=3000, likes=150, comments=15)

    def setUp(self):
        self._cleanup_files()
        self.addCleanup(self._cleanup_files)
        self._db_handler = DatabaseHandler(self.DB_PATH, VideoEngagementRecord)

        self.test_records = [
            VideoEngagementRecord(
                datetime_publish=self.TEST_DATETIME,
                title="Test Video A",
                description="A short description.",
                urls=["url_a1", "url_a2"],
                views=2000,
                likes=100,
                comments=10,
                keywords=["tutorial", "python"],
            ),
            VideoEngagementRecord(
                datetime_publish=self.TEST_DATETIME,
                title="Test Video B",
                description="Another short description.",
                urls=["url_b1"],
                views=1000,
                likes=50,
                comments=5,
                keywords=["gaming", "fun"],
            ),
        ]

    def tearDown(self):
        self._cleanup_files()

    def test_generate_video(
        self, mock_description, mock_platforms, mock_video_generator
    ):
        (
            mock_desc_inst,
            mock_platforms_inst,
            mock_video_gen_inst,
        ) = self._setup_mocks(
            mock_desc=mock_description,
            mock_platforms=mock_platforms,
            mock_video_gen=mock_video_generator,
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
            record = records[0]

            assert record.title == self.TEST_TITLE
            assert record.description == self.TEST_DESCRIPTION
            assert record.keywords == self.TEST_KEYWORDS
            assert record.urls == self.TEST_VIDEO_URLS
            assert int(record.views) == 0
            assert int(record.likes) == 0
            assert int(record.comments) == 0

    def test_update_video_metrics(
        self, mock_description, mock_platforms, mock_video_generator
    ):
        (
            mock_desc_inst,
            mock_platforms_inst,
            mock_video_gen_inst,
        ) = self._setup_mocks(
            mock_desc=mock_description,
            mock_platforms=mock_platforms,
            mock_video_gen=mock_video_generator,
        )
        video_analytics = VideoAnalytics(
            db_handler=self._db_handler,
            description_generator=mock_desc_inst,
            video_generator=mock_video_gen_inst,
            video_platforms=mock_platforms_inst,
        )

        with self._db_handler as db:
            for record in self.test_records:
                db.create(record)

        video_analytics.update_video_metrics(top_n_records=2)

        with self._db_handler as db:
            qb = (
                QueryBuilder()
                .select_columns("*")
                .order_by("views", OrderByType.DESCENDING)
            )
            records = db.read(qb)

            assert len(records) == len(self.test_records)
            for record, test_record in zip(records, self.test_records):
                assert record.title == test_record.title
                assert record.description == test_record.description
                assert record.keywords == test_record.keywords
                assert record.urls == test_record.urls
                assert int(record.views) == self.UPDATED_ENGAGEMENT.views
                assert int(record.likes) == self.UPDATED_ENGAGEMENT.likes
                assert int(record.comments) == self.UPDATED_ENGAGEMENT.comments

    def _setup_mocks(self, mock_desc, mock_platforms, mock_video_gen):
        inst_desc = mock_desc.return_value
        inst_platforms = mock_platforms.return_value
        inst_video_gen = mock_video_gen.return_value

        inst_desc.generate_description.return_value = (
            self.TEST_TITLE,
            self.TEST_DESCRIPTION,
            self.TEST_KEYWORDS,
        )
        inst_platforms.publish_to_all.return_value = self.TEST_VIDEO_URLS
        inst_platforms.get_engagement_metrics_all.return_value = self.UPDATED_ENGAGEMENT
        inst_video_gen.create_video.return_value = self.TEST_VIDEO_FILE

        return inst_desc, inst_platforms, inst_video_gen

    def _cleanup_files(self):
        for path in [self.DB_PATH, self.TEST_VIDEO_FILE]:
            if path.exists():
                path.unlink()
