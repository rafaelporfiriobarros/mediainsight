from mediainsight.config import BRONZE_DIR
from mediainsight.ingestion import ingest_csv


def main() -> None:
    file_path = BRONZE_DIR / "ga4_events_20201101.csv"

    print("MediaInsight - Ingestão GA4")
    print(f"Arquivo: {file_path.name}")

    loaded_rows = ingest_csv(file_path)

    print(f"Registros carregados: {loaded_rows}")
    print("Ingestão concluída com sucesso.")


if __name__ == "__main__":
    main()
