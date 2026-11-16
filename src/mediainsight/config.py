from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"

DATABASE_PATH = DATA_DIR / "mediainsight.duckdb"


def ensure_directories() -> None:
    """Cria os diretórios necessários para o projeto."""
    for directory in (BRONZE_DIR, SILVER_DIR, GOLD_DIR):
        directory.mkdir(parents=True, exist_ok=True)
