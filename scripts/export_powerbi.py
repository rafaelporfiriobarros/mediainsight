from pathlib import Path

import duckdb

DATABASE_PATH = Path("data/mediainsight.duckdb")
OUTPUT_DIR = Path("data/exports/powerbi")

GOLD_TABLES = (
    "marketing_daily",
    "acquisition_performance",
    "device_performance",
    "conversion_funnel",
)


def export_gold_tables(
    database_path: Path = DATABASE_PATH,
    output_dir: Path = OUTPUT_DIR,
) -> dict[str, int]:
    """Exporta as tabelas Gold para arquivos CSV."""

    if not database_path.is_file():
        raise FileNotFoundError(f"Banco DuckDB nao encontrado: {database_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    results: dict[str, int] = {}

    with duckdb.connect(str(database_path), read_only=True) as con:
        for table in GOLD_TABLES:
            output_file = output_dir / f"{table}.csv"

            # Define uma ordenacao consistente para cada tabela.
            if table == "conversion_funnel":
                order_by = "event_date, step_order"
            elif table == "acquisition_performance":
                order_by = "event_date, first_user_source, first_user_medium"
            elif table == "device_performance":
                order_by = "event_date, device_category"
            else:
                order_by = "event_date"

            # Exporta os dados utilizando o mecanismo nativo do DuckDB.
            con.execute(
                f"""
                COPY (
                    SELECT *
                    FROM gold.{table}
                    ORDER BY {order_by}
                )
                TO ?
                (FORMAT CSV, HEADER TRUE)
                """,
                [str(output_file.resolve())],
            )

            # Consulta a quantidade de registros exportados.
            total_rows = con.execute(f"SELECT COUNT(*) FROM gold.{table}").fetchone()[0]

            results[table] = total_rows

    return results


def main() -> None:
    print("=" * 60)
    print("MEDIAINSIGHT 360 - EXPORTACAO POWER BI")
    print("=" * 60)

    results = export_gold_tables()

    for table, rows in results.items():
        print(f"{table}: {rows} registros exportados")

    print("\nExportacao concluida com sucesso.")


if __name__ == "__main__":
    main()
