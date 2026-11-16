from pathlib import Path

import duckdb
import pytest

from mediainsight.transform import transform_ga4

COLUMNS = [
    "event_date",
    "event_timestamp",
    "event_name",
    "user_pseudo_id",
    "ga_session_id",
    "first_user_source",
    "first_user_medium",
    "first_user_campaign",
    "device_category",
    "country",
    "purchase_revenue",
]


@pytest.fixture
def test_database(tmp_path: Path) -> Path:
    db_path = tmp_path / "test_silver.duckdb"

    connection = duckdb.connect(str(db_path))
    connection.execute("CREATE SCHEMA bronze")

    column_definitions = ", ".join(f"{column} VARCHAR" for column in COLUMNS)

    connection.execute(f"CREATE TABLE bronze.ga4_events ({column_definitions})")

    connection.execute(
        """
        INSERT INTO bronze.ga4_events (
            event_date,
            event_timestamp,
            event_name,
            user_pseudo_id,
            ga_session_id,
            device_category,
            country,
            purchase_revenue
        )
        VALUES
            (
                '20201101',
                '1604188800000000',
                'page_view',
                'user_1',
                '123',
                'desktop',
                'Brazil',
                NULL
            ),
            (
                '20201101',
                '1604188801000000',
                'purchase',
                'user_2',
                '124',
                'mobile',
                'Brazil',
                '150.50'
            )
        """
    )

    connection.close()
    return db_path


def test_transform_creates_silver(test_database):
    result = transform_ga4(test_database)

    assert result["bronze"] == 2
    assert result["silver"] == 2
    assert result["rejected"] == 0


def test_transform_converts_types(test_database):
    transform_ga4(test_database)

    connection = duckdb.connect(str(test_database))

    try:
        columns = dict(
            connection.execute(
                """
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'silver'
                  AND table_name = 'ga4_events'
                """
            ).fetchall()
        )

        assert columns["event_date"] == "DATE"
        assert columns["event_timestamp"] == "TIMESTAMP"
        assert columns["ga_session_id"] == "BIGINT"
        assert columns["purchase_revenue"] == "DOUBLE"

    finally:
        connection.close()


def test_transform_preserves_bronze(test_database):
    transform_ga4(test_database)

    connection = duckdb.connect(str(test_database))

    try:
        count = connection.execute("SELECT COUNT(*) FROM bronze.ga4_events").fetchone()[
            0
        ]

        assert count == 2

    finally:
        connection.close()


def test_transform_is_idempotent(test_database):
    transform_ga4(test_database)
    transform_ga4(test_database)

    connection = duckdb.connect(str(test_database))

    try:
        count = connection.execute("SELECT COUNT(*) FROM silver.ga4_events").fetchone()[
            0
        ]

        assert count == 2

    finally:
        connection.close()


def test_transform_rejects_invalid_date(test_database):
    connection = duckdb.connect(str(test_database))

    try:
        connection.execute(
            """
            INSERT INTO bronze.ga4_events (
                event_date,
                event_timestamp,
                event_name
            )
            VALUES (
                'invalid',
                '1604188800000000',
                'page_view'
            )
            """
        )
    finally:
        connection.close()

    result = transform_ga4(test_database)

    assert result["bronze"] == 3
    assert result["silver"] == 2
    assert result["rejected"] == 1
