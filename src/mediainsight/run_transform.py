from mediainsight.transform import transform_ga4


def main() -> None:
    print("MediaInsight 360 - Transformação Silver")

    result = transform_ga4()

    print(f"Registros Bronze: {result['bronze']}")
    print(f"Registros Silver: {result['silver']}")
    print(f"Registros rejeitados: {result['rejected']}")
    print("Transformação concluída com sucesso.")


if __name__ == "__main__":
    main()
