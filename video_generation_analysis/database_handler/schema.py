from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class VideoEngagementRecord:
    id: Optional[int] = None
    datetime_publish: Optional[datetime] = None
    title: str = ""
    description: str = ""
    urls: list[str] = field(default_factory=list)
    views: int = -1
    likes: int = -1
    comments: int = -1
    keywords: list[str] = field(default_factory=list)


SQLITE_TYPE_MAP = {
    "str": "TEXT",
    "int": "INTEGER",
    "float": "REAL",
    "bool": "INTEGER",
}
