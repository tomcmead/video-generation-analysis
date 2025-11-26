from dataclasses import dataclass
from datetime import datetime
from enum import Enum
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


class OrderByType(Enum):
    ASCENDING = "ASC"
    DESCENDING = "DESC"


class WhereComparison(Enum):
    EQUAL = "="
    NOT_EQUAL = "!="
    GREATER_THAN = ">"
    GREATER_THAN_EQUAL = ">="
    LESS_THAN = "<"
    LESS_THAN_EQUAL = "<="


class WhereLogical(Enum):
    AND = "AND"
    OR = "OR"
