import json
import logging
import sqlite3
from dataclasses import fields, is_dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Type

from video_generation_analysis.database_handler.query_builder import (
    QueryBuilder,
    QueryType,
)
from video_generation_analysis.database_handler.schema import SQLITE_TYPE_MAP


class DatabaseHandler:
    """Context Manager handles all database operations for a specific SQLite file."""

    def __init__(self, db_path: str, db_schema: Type) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._db_path: str = db_path
        self._db_schema: Type = db_schema
        self._table_name: str = ""
        self._conn: Optional[sqlite3.Connection] = None
        self._cursor: Optional[sqlite3.Cursor] = None

    def __enter__(self) -> "DatabaseHandler":
        """Context Manager establish db connection & cursor entering 'with' block."""
        self._conn = sqlite3.connect(self._db_path)
        self._cursor = self._conn.cursor()
        self._create_table(self._db_schema)
        return self

    def __exit__(self, exc_type, exc_val, traceback) -> bool:
        """Context Manager commit/rollback & close connection on 'with' block exit."""
        try:
            if exc_type is None:
                self._conn.commit()  # commit if no exceptions
            else:
                self._conn.rollback()
                self._logger.error(
                    f"DatabaseHandler transaction rollback: exception\
                                   {exc_val}",
                    exc_info=True,
                )
                return False
        finally:
            if self._conn:
                self._conn.close()
            self._conn = None
            self._cursor = None

        return True

    def create(self, record: Any) -> None:
        """Inserts a new record into database."""
        if not is_dataclass(record):
            raise TypeError("Input must be dataclass type")

        field_names = [field.name for field in fields(record) if field.name != "id"]
        placeholders = ", ".join(["?"] * len(field_names))
        columns = ", ".join(field_names)
        values = [getattr(record, name) for name in field_names]

        sql = f"INSERT INTO {self._table_name} ({columns}) VALUES ({placeholders})"
        self._execute(sql, values)

    def read(self, criteria: QueryBuilder) -> Optional[list[Any]]:
        """Reads records matching criteria"""
        sql, params = criteria.build(self._table_name, QueryType.READ)
        return self._execute(sql, params)

    def update(self, record_id: int, updates: Dict[str, Any]) -> None:
        """Update existing record by ID"""
        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values()) + [
            record_id,
        ]

        sql = f"UPDATE {self._table_name} SET {set_clause} WHERE id = ?"
        self._execute(sql, values)

    def delete(self, criteria: QueryBuilder) -> None:
        """Deletes records matching criteria"""
        sql, params = criteria.build(self._table_name, QueryType.DELETE)
        self._execute(sql, params)

    def _execute(self, sql: str, params: list = []) -> Optional[list[Any]]:
        """Executes SQL command."""
        if not self._cursor:
            raise RuntimeError("Database operation attempted outside of 'with' block.")

        for i in range(len(params)):
            if isinstance(params[i], list):
                params[i] = json.dumps(params[i])
            elif isinstance(params[i], datetime):
                params[i] = params[i].isoformat()

        try:
            self._cursor.execute(sql, tuple(params))
            if sql.strip().upper().startswith("SELECT"):
                return self._cursor.fetchall()
            return None
        except sqlite3.Error as e:
            self._logger.error(
                f"DatabaseHandler error {e} executing SQL: {sql} with params {params}"
            )
            raise

    def _create_table(self, data_class: Type) -> None:
        """Creates a table based on a dataclass structure."""
        if not is_dataclass(data_class):
            raise TypeError("Input must be dataclass type")

        self._table_name = data_class.__name__ + "s"
        columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]

        for field in fields(data_class):
            if field.name == "id":
                continue
            sql_type = SQLITE_TYPE_MAP.get(str(field.type), "TEXT")
            column_def = f"{field.name} {sql_type}"
            columns.append(column_def)

        columns_str = ", ".join(columns)
        sql = f"CREATE TABLE IF NOT EXISTS {self._table_name} ({columns_str})"
        self._execute(sql)
