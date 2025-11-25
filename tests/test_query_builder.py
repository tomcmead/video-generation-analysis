import pytest
from video_generation_analysis.database_handler.query_builder import QueryBuilder, QueryType
from video_generation_analysis.database_handler.schema import OrderByType, WhereComparison, WhereLogical


def test_select_columns_list():
    qb = QueryBuilder().select_columns(["id", "name"])
    query, params = qb.build("users", QueryType.READ)
    assert query.startswith("SELECT id, name FROM users")
    assert params == []


def test_select_columns_string():
    qb = QueryBuilder().select_columns("id")
    query, params = qb.build("users", QueryType.READ)
    assert query.startswith("SELECT id FROM users")
    assert params == []


def test_where_compare_single():
    qb = (
        QueryBuilder()
        .select_columns("*")
        .where_compare("age", WhereComparison.GREATER_THAN, 18)
    )
    query, params = qb.build("users", QueryType.READ)

    assert query == "SELECT * FROM users WHERE age > ?"
    assert params == [18]


def test_where_compare_multiple_with_and():
    qb = (
        QueryBuilder()
        .select_columns("*")
        .where_compare("age", WhereComparison.GREATER_THAN, 18)
        .where_logical(WhereLogical.AND)
        .where_compare("country", WhereComparison.EQUAL, "USA")
    )

    query, params = qb.build("users", QueryType.READ)

    assert query == "SELECT * FROM users WHERE age > ? AND country = ?"
    assert params == [18, "USA"]


def test_where_compare_with_or():
    qb = (
        QueryBuilder()
        .select_columns("*")
        .where_compare("status", WhereComparison.EQUAL, "active")
        .where_logical(WhereLogical.OR)
        .where_compare("status", WhereComparison.EQUAL, "pending")
    )

    query, params = qb.build("users", QueryType.READ)

    assert query == "SELECT * FROM users WHERE status = ? OR status = ?"
    assert params == ["active", "pending"]


def test_order_by_ascending():
    qb = (
        QueryBuilder()
        .select_columns("*")
        .order_by("age", OrderByType.ASCENDING)
    )
    query, params = qb.build("users", QueryType.READ)

    assert query == "SELECT * FROM users ORDER BY age ASC"
    assert params == []


def test_order_by_descending():
    qb = (
        QueryBuilder()
        .select_columns("*")
        .order_by("name", OrderByType.DESCENDING)
    )
    query, params = qb.build("users", QueryType.READ)

    assert query == "SELECT * FROM users ORDER BY name DESC"
    assert params == []


def test_delete_query():
    qb = QueryBuilder().where_compare("id", WhereComparison.EQUAL, 10)

    query, params = qb.build("users", QueryType.DELETE)

    assert query == "DELETE FROM users WHERE id = ?"
    assert params == [10]


def test_invalid_where_clause_structure():
    qb = QueryBuilder()
    qb.where_compare("age", WhereComparison.GREATER_THAN, 18)
    # invalid missing AND/OR
    qb.where_compare("name", WhereComparison.EQUAL, "Bob")

    with pytest.raises(ValueError):
        qb.build("users", QueryType.READ)