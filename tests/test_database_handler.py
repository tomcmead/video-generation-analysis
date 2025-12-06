import os
import sqlite3
import unittest
from datetime import datetime

from video_generation_analysis.database_handler.database_handler import DatabaseHandler
from video_generation_analysis.database_handler.query_builder import (
    QueryBuilder,
    WhereComparison,
)
from video_generation_analysis.database_handler.schema import VideoEngagementRecord


class TestDatabaseHandler(unittest.TestCase):
    DB_PATH = "test_temp_db.sqlite"
    TABLE_NAME = VideoEngagementRecord.__name__.lower() + "s"
    TEST_DATETIME = datetime(2025, 11, 25, 12, 0, 0)

    TEST_RECORD_A = VideoEngagementRecord(
        datetime_publish=TEST_DATETIME,
        title="Test Video A",
        description="A short description.",
        views=1000,
        likes=50,
        comments=5,
        keywords=["tutorial", "python"],
    )
    TEST_RECORD_B = VideoEngagementRecord(
        datetime_publish=TEST_DATETIME,
        title="Test Video B",
        description="Another short description.",
        views=2000,
        likes=100,
        comments=10,
        keywords=["gaming", "fun"],
    )
    # Record for delete test, matching mock QueryBuilder criteria
    TEST_RECORD_DELETE = VideoEngagementRecord(
        datetime_publish=TEST_DATETIME,
        title="Temporary Delete Video",
        description="To be deleted.",
        views=10,
        likes=1,
        comments=0,
        keywords=["temp"],
    )

    def setUp(self):
        self.tearDown()
        self.handler = DatabaseHandler(self.DB_PATH, VideoEngagementRecord)

    def tearDown(self):
        if os.path.exists(self.DB_PATH):
            os.remove(self.DB_PATH)

    def _get_raw_connection(self):
        return sqlite3.connect(self.DB_PATH)

    def test_context_manager_connects_and_closes(self):
        self.assertIsNone(self.handler._conn)
        self.assertIsNone(self.handler._cursor)

        with self.handler as db:
            self.assertIsInstance(db._conn, sqlite3.Connection)
            self.assertIsInstance(db._cursor, sqlite3.Cursor)

        self.assertIsNone(self.handler._conn)
        self.assertIsNone(self.handler._cursor)

    def test_commit_on_successful_exit(self):
        test_data = self.TEST_RECORD_A

        with self.handler as db:
            db.create(test_data)

        conn = self._get_raw_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT title, views, keywords FROM {self.TABLE_NAME} WHERE title = ?",
            (test_data.title,),
        )
        result = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(result)
        self.assertEqual(result[0], test_data.title)
        self.assertEqual(result[1], str(test_data.views))
        list_kw_result = result[2].strip("[]").replace('"', "").split(", ")
        for kw_result, keyword in zip(list_kw_result, test_data.keywords):
            self.assertEqual(kw_result, keyword)

    def test_rollback_on_exception(self):
        test_data = VideoEngagementRecord(
            datetime_publish=self.TEST_DATETIME,
            title="RollbackTest",
            description="D",
            views=1,
            likes=1,
            comments=1,
            keywords=["rollback"],
        )

        try:
            with self.handler as db:
                db.create(test_data)
                raise ValueError("Simulated Rollback")  # force exception
        except ValueError:
            pass

        conn = self._get_raw_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM {self.TABLE_NAME} WHERE title = ?", ("RollbackTest",)
        )
        result = cursor.fetchone()
        conn.close()
        self.assertIsNone(result)

    def test_execution_outside_context_raises_runtime_error(self):
        with self.assertRaises(RuntimeError):
            self.handler.create(self.TEST_RECORD_A)

    def test_create_and_read(self):
        results = None
        with self.handler as db:
            db.create(self.TEST_RECORD_A)
            db.create(self.TEST_RECORD_B)
            db.create(self.TEST_RECORD_DELETE)

            qb = (
                QueryBuilder()
                .where_compare("views", WhereComparison.GREATER_THAN, 0)
                .limit(2)
            )
            results = db.read(qb)  # views > 0

        if results is None:
            self.fail("Read returned None")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].title, self.TEST_RECORD_A.title)
        self.assertEqual(results[1].title, self.TEST_RECORD_B.title)
        self.assertEqual(
            results[0].datetime_publish, self.TEST_RECORD_B.datetime_publish.isoformat()
            )
        for kw_result, kw_db in zip(results[0].keywords, self.TEST_RECORD_A.keywords):
            self.assertEqual(kw_result, kw_db)

    def test_update(self):
        with self.handler as db:
            db.create(self.TEST_RECORD_A)

            qb = QueryBuilder().select_columns("id")
            result = db.read(qb)
            if result is None:
                self.fail("Read returned None")

            record_id = result[0].id
            db.update(record_id, {"title": "Updated Title", "views": 9999})

            qb = QueryBuilder().select_columns(["id", "title", "views"])
            updated_results = db.read(qb)
            if updated_results is None:
                self.fail("Read returned None")

            self.assertEqual(updated_results[0].title, "Updated Title")
            self.assertEqual(updated_results[0].views, str(9999))

    def test_delete(self):
        """Test the delete method logic."""
        with self.handler as db:
            db.create(self.TEST_RECORD_DELETE)
            db.create(self.TEST_RECORD_B)

            qb = (
                QueryBuilder()
                .select_columns("id")
                .where_compare("title", WhereComparison.EQUAL, "Temporary Delete Video")
            )
            db.delete(qb)  # delete title='Temporary Delete Video'

            qb = QueryBuilder().select_columns(["id", "title"])
            remaining_results = db.read(qb)

            if remaining_results is None:
                self.fail("Read returned None")
            self.assertEqual(len(remaining_results), 1)
            self.assertEqual(remaining_results[0].title, self.TEST_RECORD_B.title)

    def test_create_with_non_dataclass_raises_type_error(self):
        with self.handler as db:
            with self.assertRaises(TypeError):
                db.create({"title": "dict", "views": 1})
