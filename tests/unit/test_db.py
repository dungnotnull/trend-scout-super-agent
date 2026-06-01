from pathlib import Path

def test_database_initializes(tmp_path: Path) -> None:
    from src.storage.db import Database

    db_path = tmp_path / "signals.db"
    db = Database(db_path)
    db.initialize()

    assert db_path.exists()
    rows = db.query("SELECT name FROM sqlite_master WHERE type='table'")
    table_names = {row[0] for row in rows}
    assert {"signal_history", "quarantine", "digest_archive"}.issubset(table_names)
