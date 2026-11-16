import csv

import pytest

from mediainsight.database import get_connection
from mediainsight.ingestion import (
    REQUIRED_COLUMNS,
    calculate_sha256,
    ingest_csv,
    validate_csv,
)


def create_sample_csv(file_path):
    """Cria um CSV mínimo para testes."""
    columns = sorted(REQUIRED_COLUMNS)

    row = {column: "" for column in columns}
    row.update(
        {
            "event_date": "20201101",
            "event_timestamp": "1604188800000000",
            "event_name": "page_view",
            "user_pseudo_id": "test_user",
        }
    )

    with file_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerow(row)


def test_validate_csv(tmp_path):
    file_path = tmp_path / "events.csv"
    create_sample_csv(file_path)

    assert validate_csv(file_path) == 1


def test_missing_file(tmp_path):
    file_path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        validate_csv(file_path)


def test_missing_columns(tmp_path):
    file_path = tmp_path / "invalid.csv"
    file_path.write_text(
        "event_date,event_name\n20201101,page_view\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Colunas"):
        validate_csv(file_path)


def test_sha256_is_deterministic(tmp_path):
    file_path = tmp_path / "events.csv"
    create_sample_csv(file_path)

    first_hash = calculate_sha256(file_path)
    second_hash = calculate_sha256(file_path)

    assert first_hash == second_hash
    assert len(first_hash) == 64


def test_ingestion_loads_data(tmp_path):
    file_path = tmp_path / "events.csv"
    database_path = tmp_path / "test.duckdb"

    create_sample_csv(file_path)

    loaded = ingest_csv(file_path, database_path)

    assert loaded == 1

    connection = get_connection(database_path)

    try:
        count = connection.execute("SELECT COUNT(*) FROM bronze.ga4_events").fetchone()[
            0
        ]

        assert count == 1
    finally:
        connection.close()


def test_ingestion_is_idempotent(tmp_path):
    file_path = tmp_path / "events.csv"
    database_path = tmp_path / "test.duckdb"

    create_sample_csv(file_path)

    ingest_csv(file_path, database_path)
    ingest_csv(file_path, database_path)

    connection = get_connection(database_path)

    try:
        count = connection.execute("SELECT COUNT(*) FROM bronze.ga4_events").fetchone()[
            0
        ]

        assert count == 1
    finally:
        connection.close()
