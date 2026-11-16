from pathlib import Path

import duckdb

from mediainsight.ingestion import calculate_sha256

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CSV_PATH = PROJECT_ROOT / "data" / "bronze" / "ga4_events_20201101.csv"

DATABASE_PATH = PROJECT_ROOT / "data" / "mediainsight.duckdb"


def main() -> None:
    print("=" * 55)
    print("MEDIAINSIGHT 360 - AUDITORIA DA CAMADA BRONZE")
    print("=" * 55)

    if not CSV_PATH.is_file():
        raise FileNotFoundError(f"Arquivo CSV não encontrado: {CSV_PATH}")

    if not DATABASE_PATH.is_file():
        raise FileNotFoundError(f"Banco DuckDB não encontrado: {DATABASE_PATH}")

    current_hash = calculate_sha256(CSV_PATH)

    connection = duckdb.connect(
        str(DATABASE_PATH),
        read_only=True,
    )

    try:
        # 1. Total de eventos carregados
        total_events = connection.execute(
            """
            SELECT COUNT(*)
            FROM bronze.ga4_events
            """
        ).fetchone()[0]

        # 2. Período dos eventos
        period = connection.execute(
            """
            SELECT
                MIN(event_date),
                MAX(event_date)
            FROM bronze.ga4_events
            """
        ).fetchone()

        # 3. Distribuição por tipo de evento
        event_distribution = connection.execute(
            """
            SELECT
                event_name,
                COUNT(*) AS total
            FROM bronze.ga4_events
            GROUP BY event_name
            ORDER BY total DESC
            LIMIT 10
            """
        ).fetchall()

        # 4. Metadados disponíveis
        metadata_columns = {
            row[1]
            for row in connection.execute(
                """
                PRAGMA table_info('bronze.ingestion_metadata')
                """
            ).fetchall()
        }

        print("\n[1] VOLUME")
        print(f"Total de eventos: {total_events:,}")

        print("\n[2] PERÍODO")
        print(f"Data inicial: {period[0]}")
        print(f"Data final:   {period[1]}")

        print("\n[3] DISTRIBUIÇÃO DE EVENTOS")
        for event_name, total in event_distribution:
            print(f"{event_name}: {total:,}")

        print("\n[4] INTEGRIDADE DO ARQUIVO")
        print(f"Arquivo: {CSV_PATH.name}")
        print(f"SHA-256 atual: {current_hash}")

        print("\n[5] METADADOS")
        print(
            "Colunas disponíveis:",
            ", ".join(sorted(metadata_columns)),
        )

        metadata_rows = connection.execute(
            """
            SELECT
                source_file,
                sha256,
                row_count,
                CAST(ingested_at AS VARCHAR)
            FROM bronze.ingestion_metadata
            """
        ).fetchall()

        print(f"Registros de metadados: {len(metadata_rows)}")

        if len(metadata_rows) != 1:
            raise ValueError(
                "Esperado exatamente um registro de metadados para a carga atual."
            )

        source_file, stored_hash, stored_count, ingested_at = metadata_rows[0]

        print(f"Arquivo registrado: {source_file}")
        print(f"Registros registrados: {stored_count}")
        print(f"SHA-256 registrado: {stored_hash}")
        print(f"Data da carga: {ingested_at}")

        if source_file != CSV_PATH.name:
            raise ValueError("O arquivo registrado não corresponde ao CSV.")

        if stored_count != total_events:
            raise ValueError(
                "A quantidade registrada não corresponde "
                "à quantidade de eventos na Bronze."
            )

        if stored_hash != current_hash:
            raise ValueError("O SHA-256 registrado não corresponde ao CSV.")

        print("Metadados e SHA-256: OK")

        # 6. Regras de qualidade
        if total_events == 0:
            raise ValueError("A tabela Bronze está vazia.")

        if period != ("20201101", "20201101"):
            raise ValueError(f"Período inesperado na Bronze: {period}")

        print("\n" + "=" * 55)
        print("VALIDAÇÕES BÁSICAS APROVADAS")
        print("=" * 55)

    finally:
        connection.close()


if __name__ == "__main__":
    main()
