from pathlib import Path

import duckdb

from mediainsight.config import DATA_DIR

PROJECT_ROOT = Path(__file__).resolve().parents[2]

GOLD_SQL_FILES = (
    "001_marketing_daily.sql",
    "002_acquisition_performance.sql",
    "003_device_performance.sql",
    "004_conversion_funnel.sql",
)

GOLD_TABLES = (
    "marketing_daily",
    "acquisition_performance",
    "device_performance",
)


def build_gold(
    database_path: Path | None = None,
    sql_dir: Path | None = None,
) -> dict:
    """Executa e valida as transformacoes Gold."""

    if database_path is None:
        database_path = DATA_DIR / "mediainsight.duckdb"

    if sql_dir is None:
        sql_dir = PROJECT_ROOT / "sql" / "gold"

    database_path = Path(database_path)
    sql_dir = Path(sql_dir)

    if not database_path.is_file():
        raise FileNotFoundError(f"Banco de dados nao encontrado: {database_path}")

    sql_scripts = []

    for filename in GOLD_SQL_FILES:
        path = sql_dir / filename

        if not path.is_file():
            raise FileNotFoundError(f"Script SQL nao encontrado: {path}")

        sql_scripts.append(path.read_text(encoding="utf-8"))

    with duckdb.connect(str(database_path)) as con:
        con.execute("BEGIN TRANSACTION")

        try:
            silver_totals = con.execute("""
                SELECT
                    COUNT(*),
                    COUNT(*) FILTER (
                        WHERE event_name = 'page_view'
                    ),
                    COUNT(*) FILTER (
                        WHERE event_name = 'purchase'
                    ),
                    COALESCE(SUM(purchase_revenue), 0)
                FROM silver.ga4_events
            """).fetchone()

            for sql in sql_scripts:
                con.execute(sql)

            counts = {}

            for table in GOLD_TABLES:
                totals = con.execute(f"""
                    SELECT
                        COALESCE(SUM(total_events), 0),
                        COALESCE(SUM(page_views), 0),
                        COALESCE(SUM(purchases), 0),
                        COALESCE(SUM(total_revenue), 0)
                    FROM gold.{table}
                """).fetchone()

                if totals != silver_totals:
                    raise ValueError(
                        f"Falha de reconciliacao em gold.{table}: "
                        f"Silver={silver_totals}, Gold={totals}"
                    )

                counts[table] = con.execute(
                    f"SELECT COUNT(*) FROM gold.{table}"
                ).fetchone()[0]

            funnel_totals = con.execute("""
                SELECT
                    COALESCE(SUM(total_events), 0)
                FROM gold.conversion_funnel
            """).fetchone()[0]

            silver_funnel_total = con.execute("""
                SELECT COUNT(*)
                FROM silver.ga4_events
                WHERE event_name IN (
                    'view_item',
                    'add_to_cart',
                    'begin_checkout',
                    'add_payment_info',
                    'purchase'
                )
            """).fetchone()[0]

            if funnel_totals != silver_funnel_total:
                raise ValueError(
                    "Falha de reconciliacao no funil: "
                    f"Silver={silver_funnel_total}, "
                    f"Gold={funnel_totals}"
                )

            counts["conversion_funnel"] = con.execute("""
                SELECT COUNT(*)
                FROM gold.conversion_funnel
            """).fetchone()[0]

            con.execute("COMMIT")

        except Exception:
            con.execute("ROLLBACK")
            raise

    return {
        "silver_events": silver_totals[0],
        "gold_tables": counts,
        "status": "SUCCESS",
    }
