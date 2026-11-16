from mediainsight.config import (
    BRONZE_DIR,
    DATA_DIR,
    GOLD_DIR,
    SILVER_DIR,
    ensure_directories,
)


def test_data_directories_are_inside_data() -> None:
    assert BRONZE_DIR.parent == DATA_DIR
    assert SILVER_DIR.parent == DATA_DIR
    assert GOLD_DIR.parent == DATA_DIR


def test_ensure_directories_creates_folders() -> None:
    ensure_directories()

    assert BRONZE_DIR.is_dir()
    assert SILVER_DIR.is_dir()
    assert GOLD_DIR.is_dir()
