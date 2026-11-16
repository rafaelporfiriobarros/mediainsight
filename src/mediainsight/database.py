from pathlib import Path

import duckdb

from mediainsight.config import DATABASE_PATH, ensure_directories


def get_connection(
    database_path: Path | None = None,
) -> duckdb.DuckDBPyConnection:
    """Abre uma conexão com o banco analítico DuckDB."""
    ensure_directories()

    path = database_path or DATABASE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    return duckdb.connect(str(path))


def check_database(
    database_path: Path | None = None,
) -> bool:
    """Verifica se o DuckDB consegue executar uma consulta."""
    connection = get_connection(database_path)

    try:
        result = connection.execute("SELECT 1").fetchone()
        return result == (1,)
    finally:
        connection.close()
