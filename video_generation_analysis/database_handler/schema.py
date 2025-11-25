from enum import Enum

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