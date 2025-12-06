import os
import unittest
from datetime import datetime

from video_generation_analysis.database_handler.database_handler import DatabaseHandler
from video_generation_analysis.database_handler.schema import VideoEngagementRecord
from video_generation_analysis.video_generator.keyword_generator import KeywordGenerator
from video_generation_analysis.video_generator.keyword_gensim_strategy import (
    KeywordGensimStrategy,
)


class TestKeywordGenerator(unittest.TestCase):
    DB_PATH = "test_temp_db.sqlite"
    TABLE_NAME = VideoEngagementRecord.__name__.lower() + "s"
    TEST_DATETIME = datetime(2025, 11, 25, 12, 0, 0)
    KEYWORD_STRATEGY = KeywordGensimStrategy()

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
        keyword_generator = KeywordGenerator(
            db_handler=self._db_handler, keyword_strategy=self.KEYWORD_STRATEGY
        )

        result_keywords = keyword_generator.get_top_keywords(num_top_videos=2)

        self.assertEqual(result_keywords, expected_keywords)

    def test_generate_keywords(self):
        keyword_generator = KeywordGenerator(
            db_handler=self._db_handler, keyword_strategy=self.KEYWORD_STRATEGY
        )

        result_keywords = keyword_generator.generate_keywords(
            num_new_keywords=5, num_top_videos=2
        )

        assert len(result_keywords) == 5
        assert isinstance(result_keywords, list)
