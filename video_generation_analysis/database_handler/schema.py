from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class VideoEngagementRecord:
    datetime_publish: datetime
    title: str
    description: str
    views: int
    likes: int
    comments: int
    keywords: List[str]


SQLITE_TYPE_MAP = {
    "str": "TEXT",
    "int": "INTEGER",
    "float": "REAL",
    "bool": "INTEGER",
}
