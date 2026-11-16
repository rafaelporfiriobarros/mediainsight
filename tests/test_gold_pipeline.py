from pathlib import Path
from shutil import copy2

import duckdb
import pytest

from mediainsight.gold import GOLD_SQL_FILES, build_gold

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_SQL_DIR = PROJECT_ROOT / "sql" / "gold"


@pytest.fixture
def gold_environment(tmp_path):
    """Prepara banco e scripts isolados para testes."""

    database_path = tmp_path / "test_gold.duckdb"
    sql_dir = tmp_path / "sql" / "gold"
    sql_dir.mkdir(parents=True)

    for filename in GOLD_SQL_FILES:
        copy2(SOURCE_SQL_DIR / filename, sql_dir / filename)

    with duckdb.connect(str(database_path)) as con:
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

    return database_path, sql_dir


def test_gold_pipeline_success(gold_environment):
    database_path, sql_dir = gold_environment

    result = build_gold(
        database_path=database_path,
        sql_dir=sql_dir,
    )

    assert result["status"] == "SUCCESS"
    assert result["silver_events"] == 3

    assert result["gold_tables"] == {
        "marketing_daily": 1,
        "acquisition_performance": 2,
        "device_performance": 2,
        "conversion_funnel": 5,
    }


def test_gold_pipeline_is_idempotent(gold_environment):
    database_path, sql_dir = gold_environment

    first_result = build_gold(
        database_path=database_path,
        sql_dir=sql_dir,
    )

    second_result = build_gold(
        database_path=database_path,
        sql_dir=sql_dir,
    )

    assert first_result == second_result


def test_gold_pipeline_missing_sql(gold_environment):
    database_path, sql_dir = gold_environment

    missing_file = sql_dir / GOLD_SQL_FILES[0]
    missing_file.unlink()

    with pytest.raises(FileNotFoundError):
        build_gold(
            database_path=database_path,
            sql_dir=sql_dir,
        )


def test_gold_pipeline_missing_database(tmp_path):
    database_path = tmp_path / "missing.duckdb"

    with pytest.raises(FileNotFoundError):
        build_gold(database_path=database_path)


def test_gold_pipeline_rolls_back_on_error(
    gold_environment,
):
    database_path, sql_dir = gold_environment

    # Cria inicialmente as tabelas Gold validas.
    build_gold(
        database_path=database_path,
        sql_dir=sql_dir,
    )

    with duckdb.connect(str(database_path)) as con:
        before = con.execute("""
            SELECT *
            FROM gold.marketing_daily
            ORDER BY event_date
        """).fetchall()

        # Altera a Silver para que uma nova execucao
        # produza resultados diferentes.
        con.execute("""
            INSERT INTO silver.ga4_events
            SELECT
                event_date,
                event_timestamp,
                event_name,
                'user_3',
                300,
                first_user_source,
                first_user_medium,
                first_user_campaign,
                device_category,
                country,
                purchase_revenue
            FROM silver.ga4_events
            WHERE event_name = 'page_view'
            LIMIT 1
        """)

    # Provoca uma falha no ultimo script SQL.
    broken_sql = sql_dir / GOLD_SQL_FILES[-1]
    broken_sql.write_text(
        "SELECT * FROM tabela_inexistente;",
        encoding="utf-8",
    )

    with pytest.raises(duckdb.Error):
        build_gold(
            database_path=database_path,
            sql_dir=sql_dir,
        )

    # A transacao deve preservar a Gold anterior.
    with duckdb.connect(str(database_path)) as con:
        after = con.execute("""
            SELECT *
            FROM gold.marketing_daily
            ORDER BY event_date
        """).fetchall()

    assert before == after
