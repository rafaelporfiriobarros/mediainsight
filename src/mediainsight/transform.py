from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE = PROJECT_ROOT / "data" / "mediainsight.duckdb"
TRANSFORM_SQL = PROJECT_ROOT / "sql" / "silver" / "001_ga4_events.sql"


def transform_ga4(
    database_path: Path | None = None,
    sql_path: Path | None = None,
) -> dict[str, int]:
    """Transforma eventos Bronze em Silver e audita as contagens."""
    db_path = database_path or DEFAULT_DATABASE
    query_path = sql_path or TRANSFORM_SQL

    if not db_path.is_file():
        raise FileNotFoundError(f"Banco não encontrado: {db_path}")

    sql = query_path.read_text(encoding="utf-8")

    connection = duckdb.connect(str(db_path))

    try:
        bronze_count = connection.execute(
            "SELECT COUNT(*) FROM bronze.ga4_events"
        ).fetchone()[0]

        if bronze_count == 0:
            raise ValueError("A tabela Bronze está vazia.")

        connection.execute("BEGIN TRANSACTION")

        try:
            connection.execute(sql)

            silver_count = connection.execute(
                "SELECT COUNT(*) FROM silver.ga4_events"
            ).fetchone()[0]

            rejected_count = bronze_count - silver_count

            if rejected_count < 0:
                raise ValueError("Silver possui mais registros que Bronze.")

            connection.execute("COMMIT")

        except Exception:
            connection.execute("ROLLBACK")
            raise

        return {
            "bronze": bronze_count,
            "silver": silver_count,
            "rejected": rejected_count,
        }

    finally:
        connection.close()
