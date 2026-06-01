from src.storage.db import Database


def test_archive_digest(tmp_path) -> None:
    db = Database(tmp_path / "signals.db")
    db.initialize()
    digest_id = db.archive_digest("test payload")

    rows = db.query("SELECT digest_id, generated_at, payload FROM digest_archive WHERE digest_id = ?", (digest_id,))
    assert len(rows) == 1
    assert rows[0][2] == "test payload"
