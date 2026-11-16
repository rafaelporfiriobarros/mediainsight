import duckdb

from mediainsight.database import (
    check_database,
    get_connection,
)


def test_database_connection(tmp_path) -> None:
    database_path = tmp_path / "test.duckdb"

    connection = get_connection(database_path)

    try:
        result = connection.execute("SELECT 10 + 20").fetchone()

        assert result == (30,)
    finally:
        connection.close()


def test_database_healthcheck(tmp_path) -> None:
    database_path = tmp_path / "health.duckdb"

    assert check_database(database_path) is True


def test_database_file_is_created(tmp_path) -> None:
    database_path = tmp_path / "created.duckdb"

    connection = get_connection(database_path)
    connection.close()

    assert database_path.is_file()


def test_database_supports_sql_aggregation() -> None:
    connection = duckdb.connect(":memory:")

    try:
        result = connection.execute(
            """
            SELECT SUM(clicks) AS total_clicks
            FROM (
                VALUES (10), (20), (30)
            ) AS campaign(clicks)
            """
        ).fetchone()

        assert result == (60,)
    finally:
        connection.close()
