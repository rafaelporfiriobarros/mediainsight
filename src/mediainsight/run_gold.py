from mediainsight.gold import build_gold


def main() -> None:
    """Executa a camada Gold e apresenta os resultados."""

    print("=" * 55)
    print("MEDIAINSIGHT 360 - PIPELINE GOLD")
    print("=" * 55)

    result = build_gold()

    print(f"Status: {result['status']}")
    print(f"Eventos Silver: {result['silver_events']:,}")

    print("\nTabelas Gold:")

    for table, count in result["gold_tables"].items():
        print(f"  gold.{table}: {count:,} registros")

    print("\nPipeline Gold concluido com sucesso.")


if __name__ == "__main__":
    main()
