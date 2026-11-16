from pathlib import Path

import duckdb
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]

GOLD_SQL_FILES = [
    "sql/gold/001_marketing_daily.sql",
    "sql/gold/002_acquisition_performance.sql",
    "sql/gold/003_device_performance.sql",
    "sql/gold/004_conversion_funnel.sql",
]


@pytest.fixture
def gold_connection():
    """Cria um DuckDB isolado com dados sintéticos."""

    con = duckdb.connect(":memory:")

    con.execute("""
        CREATE SCHEMA silver;

        CREATE TABLE silver.ga4_events (
            event_date DATE,
            event_timestamp TIMESTAMP,
            event_name VARCHAR,
            user_pseudo_id VARCHAR,
            ga_session_id BIGINT,
            first_user_source VARCHAR,
            first_user_medium VARCHAR,
            first_user_campaign VARCHAR,
            device_category VARCHAR,
            country VARCHAR,
            purchase_revenue DOUBLE
        );
    """)

    con.execute("""
        INSERT INTO silver.ga4_events VALUES
        (
            '2020-11-01',
            '2020-11-01 10:00:00',
            'page_view',
            'user_1',
            100,
            'google',
            'organic',
            NULL,
            'desktop',
            'Brazil',
            NULL
        ),
        (
            '2020-11-01',
            '2020-11-01 10:05:00',
            'purchase',
            'user_1',
            100,
            'google',
            'organic',
            NULL,
            'desktop',
            'Brazil',
            100.0
        ),
        (
            '2020-11-01',
            '2020-11-01 10:10:00',
            'purchase',
            'user_1',
            100,
            'google',
            'organic',
            NULL,
            'desktop',
            'Brazil',
            50.0
        ),
        (
            '2020-11-01',
            '2020-11-01 11:00:00',
            'page_view',
            'user_2',
            200,
            'direct',
            '(none)',
            NULL,
            'mobile',
            'Brazil',
            NULL
        );
    """)

    try:
        for relative_path in GOLD_SQL_FILES:
            sql_path = PROJECT_ROOT / relative_path
            con.execute(sql_path.read_text(encoding="utf-8"))

        yield con

    finally:
        con.close()


def test_gold_tables_are_created(gold_connection):
    tables = gold_connection.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'gold'
    """).fetchall()

    table_names = {row[0] for row in tables}

    assert "marketing_daily" in table_names
    assert "acquisition_performance" in table_names
    assert "device_performance" in table_names


def test_marketing_daily_metrics(gold_connection):
    result = gold_connection.execute("""
        SELECT
            total_events,
            unique_users,
            total_sessions,
            page_views,
            purchases,
            purchasing_sessions,
            total_revenue
        FROM gold.marketing_daily
    """).fetchone()

    assert result == (
        4,  # Eventos
        2,  # Usuarios
        2,  # Sessoes
        2,  # Page views
        2,  # Eventos de compra
        1,  # Sessao com compra
        150.0,  # Receita
    )


def test_session_conversion_rate(gold_connection):
    conversion_rate = gold_connection.execute("""
        SELECT session_conversion_rate
        FROM gold.marketing_daily
    """).fetchone()[0]

    assert conversion_rate == pytest.approx(0.5)


def test_revenue_per_session(gold_connection):
    revenue_per_session = gold_connection.execute("""
        SELECT revenue_per_session
        FROM gold.marketing_daily
    """).fetchone()[0]

    assert revenue_per_session == pytest.approx(75.0)


@pytest.mark.parametrize(
    "table_name",
    [
        "marketing_daily",
        "acquisition_performance",
        "device_performance",
    ],
)
def test_gold_reconciliation(gold_connection, table_name):
    result = gold_connection.execute(f"""
        SELECT
            SUM(total_events),
            SUM(page_views),
            SUM(purchases),
            SUM(total_revenue)
        FROM gold.{table_name}
    """).fetchone()

    assert result == (4, 2, 2, 150.0)


def test_acquisition_segments(gold_connection):
    result = gold_connection.execute("""
        SELECT
            first_user_source,
            total_events,
            total_revenue
        FROM gold.acquisition_performance
        ORDER BY first_user_source
    """).fetchall()

    assert result == [
        ("direct", 1, 0.0),
        ("google", 3, 150.0),
    ]


def test_device_segments(gold_connection):
    result = gold_connection.execute("""
        SELECT
            device_category,
            total_events,
            total_revenue
        FROM gold.device_performance
        ORDER BY device_category
    """).fetchall()

    assert result == [
        ("desktop", 3, 150.0),
        ("mobile", 1, 0.0),
    ]


def test_gold_is_idempotent(gold_connection):
    sql_path = PROJECT_ROOT / GOLD_SQL_FILES[0]
    sql = sql_path.read_text(encoding="utf-8")

    before = gold_connection.execute("""
        SELECT *
        FROM gold.marketing_daily
    """).fetchall()

    gold_connection.execute(sql)

    after = gold_connection.execute("""
        SELECT *
        FROM gold.marketing_daily
    """).fetchall()

    assert before == after


def test_conversion_funnel_has_five_steps(gold_connection):
    result = gold_connection.execute("""
        SELECT
            step_order,
            event_name
        FROM gold.conversion_funnel
        ORDER BY step_order
    """).fetchall()

    assert result == [
        (1, "view_item"),
        (2, "add_to_cart"),
        (3, "begin_checkout"),
        (4, "add_payment_info"),
        (5, "purchase"),
    ]


def test_conversion_funnel_counts(gold_connection):
    result = gold_connection.execute("""
        SELECT
            event_name,
            total_events,
            unique_users,
            distinct_sessions
        FROM gold.conversion_funnel
        ORDER BY step_order
    """).fetchall()

    assert result == [
        ("view_item", 0, 0, 0),
        ("add_to_cart", 0, 0, 0),
        ("begin_checkout", 0, 0, 0),
        ("add_payment_info", 0, 0, 0),
        ("purchase", 2, 1, 1),
    ]


def test_conversion_funnel_is_idempotent(gold_connection):
    sql_path = PROJECT_ROOT / "sql/gold/004_conversion_funnel.sql"
    sql = sql_path.read_text(encoding="utf-8")

    before = gold_connection.execute("""
        SELECT *
        FROM gold.conversion_funnel
        ORDER BY event_date, step_order
    """).fetchall()

    gold_connection.execute(sql)

    after = gold_connection.execute("""
        SELECT *
        FROM gold.conversion_funnel
        ORDER BY event_date, step_order
    """).fetchall()

    assert before == after
