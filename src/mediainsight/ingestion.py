import csv
import hashlib
from pathlib import Path

from mediainsight.database import get_connection

REQUIRED_COLUMNS = {
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
}


def validate_csv(file_path: Path) -> int:
    """Valida a estrutura básica do CSV."""
    if not file_path.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    with file_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, restkey="__extra__")

        columns = reader.fieldnames

        if not columns:
            raise ValueError("CSV sem cabeçalho")

        if len(columns) != len(set(columns)):
            raise ValueError("CSV com colunas duplicadas")

        missing = REQUIRED_COLUMNS - set(columns)

        if missing:
            raise ValueError(f"Colunas obrigatórias ausentes: {sorted(missing)}")

        total_rows = 0

        for row in reader:
            if None in row or "__extra__" in row:
                raise ValueError(
                    f"Quantidade inválida de campos na linha {total_rows + 2}"
                )

            total_rows += 1

    if total_rows == 0:
        raise ValueError("CSV não contém registros")

    return total_rows


def calculate_sha256(file_path: Path) -> str:
    """Calcula a assinatura do arquivo."""
    digest = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def ingest_csv(
    file_path: Path,
    database_path: Path | None = None,
) -> int:
    """Ingere um CSV validado na camada Bronze."""
    total_rows = validate_csv(file_path)
    file_hash = calculate_sha256(file_path)

    connection = get_connection(database_path)

    try:
        connection.execute("BEGIN TRANSACTION")

        connection.execute(
            """
            CREATE SCHEMA IF NOT EXISTS bronze
            """
        )

        connection.execute(
            """
            CREATE OR REPLACE TABLE bronze.ga4_events AS
            SELECT *
            FROM read_csv(
                ?,
                header = true,
                all_varchar = true
            )
            """,
            [str(file_path.resolve())],
        )

        loaded_rows = connection.execute(
            """
            SELECT COUNT(*)
            FROM bronze.ga4_events
            """
        ).fetchone()[0]

        if loaded_rows != total_rows:
            raise ValueError(
                f"Divergência entre CSV e DuckDB: {total_rows} != {loaded_rows}"
            )

        connection.execute(
            """
            CREATE OR REPLACE TABLE bronze.ingestion_metadata AS
            SELECT
                ?::VARCHAR AS source_file,
                ?::VARCHAR AS sha256,
                ?::BIGINT AS row_count,
                CURRENT_TIMESTAMP AS ingested_at
            """,
            [
                file_path.name,
                file_hash,
                loaded_rows,
            ],
        )

        connection.execute("COMMIT")
        return loaded_rows

    except Exception:
        connection.execute("ROLLBACK")
        raise

    finally:
        connection.close()
