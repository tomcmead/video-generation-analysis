from video_generation_analysis.database_handler.database_handler import DatabaseHandler
from video_generation_analysis.database_handler.query_builder import (
    OrderByType,
    QueryBuilder,
)
from video_generation_analysis.video_generator.keyword_context import KeywordContext


class KeywordGenerator:
    """Generates new keywords based on top engagement keywords in database."""

    def __init__(self, db_handler: DatabaseHandler, keyword_strategy: KeywordContext):
        self._db_handler = db_handler
        self._keyword_strategy = keyword_strategy

    def generate_keywords(
        self, num_new_keywords, num_top_videos: int = 10
    ) -> list[str]:
        """Gets top keywords from db, generates new keywords by strategy algorithm."""
        top_keywords = self.get_top_keywords(num_top_videos=num_top_videos)
        return self._keyword_strategy.generate_keywords(top_keywords, num_new_keywords)

    def get_top_keywords(self, num_top_videos: int) -> list[str]:
        """Retrieves top keywords from database based on engagement metrics."""
        views_keywords = self._top_database_records_keywords(
            num_records=num_top_videos, engagement_type="views"
        )
        likes_keywords = self._top_database_records_keywords(
            num_records=num_top_videos, engagement_type="likes"
        )
        comments_keywords = self._top_database_records_keywords(
            num_records=num_top_videos, engagement_type="comments"
        )

        top_keywords = self._combine_dicts(views_keywords, likes_keywords)
        top_keywords = self._combine_dicts(comments_keywords, top_keywords)

        sorted_keywords = sorted(
            top_keywords.items(), key=lambda item: item[1], reverse=True
        )
        return [keyword[0] for keyword in sorted_keywords]  # keyword str only

    def _top_database_records_keywords(
        self, num_records: int, engagement_type: str
    ) -> dict[str, int]:
        query_builder = (
            QueryBuilder()
            .select_columns("keywords")
            .order_by(engagement_type, OrderByType.DESCENDING)
            .limit(num_records)
        )
        top_enagement_record = []
        with self._db_handler as db_handler:
            top_enagement_record = db_handler.read(query_builder)

        top_engagement_keywords = {}
        for record in top_enagement_record:
            for keyword in record.keywords:
                if keyword in top_engagement_keywords:
                    top_engagement_keywords[keyword] += 1
                else:
                    top_engagement_keywords[keyword] = 1

        return top_engagement_keywords

    def _combine_dicts(
        self, dict1: dict[str, int], dict2: dict[str, int]
    ) -> dict[str, int]:
        combined_dict = dict1.copy()
        for key, value in dict2.items():
            combined_dict[key] = combined_dict.get(key, 0) + value
        return combined_dict
