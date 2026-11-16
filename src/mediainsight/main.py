from mediainsight.config import (
    DATABASE_PATH,
    ensure_directories,
)
from mediainsight.database import check_database


def main() -> None:
    """Executa o diagnóstico inicial do MediaInsight."""
    print("MediaInsight")
    print("Etapa 1 - Diagnóstico do ambiente")

    ensure_directories()

    if not check_database():
        raise RuntimeError("Falha na validação do DuckDB")

    print("Diretórios: OK")
    print("DuckDB: OK")
    print(f"Banco: {DATABASE_PATH}")
    print("Diagnóstico concluído com sucesso.")


if __name__ == "__main__":
    main()
