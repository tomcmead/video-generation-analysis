import os
import unittest
from datetime import datetime

from video_generation_analysis.database_handler.database_handler import DatabaseHandler
from video_generation_analysis.database_handler.schema import VideoEngagementRecord
from video_generation_analysis.video_generator.description_generator import (
    DescriptionGenerator,
)
from video_generation_analysis.video_generator.keyword_gensim_strategy import (
    KeywordGensimStrategy,
)
from video_generation_analysis.video_generator.keyword_huggingface_strategy import (
    KeywordHuggingFaceStrategy,
)


class TestDescriptionGenerator(unittest.TestCase):
    DB_PATH = "test_temp_db.sqlite"
    TABLE_NAME = VideoEngagementRecord.__name__.lower() + "s"
    TEST_DATETIME = datetime(2025, 11, 25, 12, 0, 0)
    KEYWORD_STRATEGY = KeywordGensimStrategy()
    DESCRIPTION_STRATEGY = KeywordHuggingFaceStrategy()

    TEST_RECORD_A = VideoEngagementRecord(
        datetime_publish=TEST_DATETIME,
        title="Test Video A",
        description="A short description.",
        views=3000,
        likes=50,
        comments=5,
        keywords=["maximum", "maximum", "python"],
    )
    TEST_RECORD_B = VideoEngagementRecord(
        datetime_publish=TEST_DATETIME,
        title="Test Video B",
        description="Another short description.",
        views=2000,
        likes=100,
        comments=10,
        keywords=["python", "python"],
    )

    def setUp(self):
        self.tearDown()
        self._db_handler = DatabaseHandler(self.DB_PATH, VideoEngagementRecord)
        with self._db_handler as db:
            db.create(self.TEST_RECORD_A)
            db.create(self.TEST_RECORD_B)

    def tearDown(self):
        if os.path.exists(self.DB_PATH):
            os.remove(self.DB_PATH)

    def test_get_top_keywords(self):
        expected_keywords = ["python", "maximum"]
        description_generator = DescriptionGenerator(
            db_handler=self._db_handler,
            keyword_strategy=self.KEYWORD_STRATEGY,
            description_strategy=self.DESCRIPTION_STRATEGY,
        )

        result_keywords = description_generator.get_top_keywords(num_top_videos=2)

        self.assertEqual(result_keywords, expected_keywords)

    def test_generate_description_no_prompt(self):
        description_generator = DescriptionGenerator(
            db_handler=self._db_handler,
            keyword_strategy=self.KEYWORD_STRATEGY,
            description_strategy=self.DESCRIPTION_STRATEGY,
        )

        title, description, keywords = description_generator.generate_description(
            num_new_keywords=5, num_top_videos=2
        )

        assert len(keywords) == 5
        assert isinstance(keywords, list)
        assert isinstance(title, str)
        assert isinstance(description, str)
        assert description > title

    def test_generate_description_with_prompt(self):
        description_generator = DescriptionGenerator(
            db_handler=self._db_handler,
            keyword_strategy=self.KEYWORD_STRATEGY,
            description_strategy=self.DESCRIPTION_STRATEGY,
        )

        title, description, keywords = description_generator.generate_description(
            num_new_keywords=3, num_top_videos=2, prompt="Video Testing Fun Games Ideas"
        )

        assert len(keywords) == 3
        assert isinstance(keywords, list)
        assert isinstance(title, str)
        assert isinstance(description, str)
        assert description > title
