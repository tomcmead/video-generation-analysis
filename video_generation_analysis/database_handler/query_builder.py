from enum import Enum, auto
from typing import Any, List, Tuple


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


class QueryType(Enum):
    READ = auto()
    DELETE = auto()


class QueryBuilder:
    """Build SQL queries SELECT DELETE operations with WHERE and ORDER BY clauses"""

    def __init__(self):
        self._columns = "*"
        self._where_clauses = []
        self._params = []
        self._order_clause = ""
        self._limit_clause = ""

    def select_columns(self, columns: List[str] | Tuple[str] | str):
        """Specify columns to select in the query"""
        if isinstance(columns, (list, tuple)):
            self._columns = ", ".join(columns)
        else:
            self._columns = columns
        return self

    def where_compare(self, column: str, comparison: WhereComparison, value: Any):
        """Add comparison condition to WHERE clause"""
        condition = f"{column} {comparison.value} ?"
        self._where_clauses.append(condition)
        self._params.append(value)
        return self

    def where_logical(self, logical: WhereLogical):
        """Add logical operator (AND/OR) to WHERE clause"""
        if (
            self._where_clauses
            and self._where_clauses[-1] != WhereLogical.AND.value
            and self._where_clauses[-1] != WhereLogical.OR.value
        ):
            self._where_clauses.append(logical.value)
        return self

    def order_by(self, column: str, direction: OrderByType = OrderByType.ASCENDING):
        """Add ORDER BY clause to query"""
        self._order_clause = f" ORDER BY {column} {direction.value}"
        return self

    def limit(self, count: int):
        """Add LIMIT clause to query"""
        self._limit_clause = f" LIMIT {count}"
        return self

    def build(self, table: str, query_type: QueryType) -> Tuple[str, List[Any]]:
        """Construct final SQL query and return it with parameters"""
        if query_type == QueryType.READ:
            query = f"SELECT {self._columns} FROM {table}"
        elif query_type == QueryType.DELETE:
            query = f"DELETE FROM {table}"
        else:
            raise ValueError("Unsupported query type")

        for idx, where_clause in enumerate(self._where_clauses):
            if idx == 0:
                query += " WHERE"
            if idx % 2 == 0 and where_clause not in (
                WhereLogical.AND.value,
                WhereLogical.OR.value,
            ):
                query += f" {where_clause}"
            elif idx % 2 == 1 and where_clause in (
                WhereLogical.AND.value,
                WhereLogical.OR.value,
            ):
                query += f" {where_clause}"
            else:
                raise ValueError("Invalid WHERE clause structure")

        query += self._order_clause
        query += self._limit_clause
        return query, self._params
