from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Iterable

from src.collectors.base import RawSignal


INITIAL_SCHEMA = [
    "CREATE TABLE IF NOT EXISTS signal_history ("
    "signal_id TEXT PRIMARY KEY,"
    "source TEXT NOT NULL,"
    "entity_type TEXT NOT NULL,"
    "entity_id TEXT NOT NULL,"
    "entity_url TEXT NOT NULL,"
    "title TEXT NOT NULL,"
    "description TEXT,"
    "raw_metrics TEXT NOT NULL,"
    "collected_at TEXT NOT NULL,"
    "author_id TEXT,"
    "author_followers INTEGER,"
    "created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP"
    ");",
    "CREATE TABLE IF NOT EXISTS quarantine ("
    "signal_id TEXT PRIMARY KEY,"
    "source TEXT NOT NULL,"
    "reason TEXT NOT NULL,"
    "score REAL NOT NULL,"
    "quarantined_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP"
    ");",
    "CREATE TABLE IF NOT EXISTS kol_registry ("
    "kol_id TEXT PRIMARY KEY,"
    "display_name TEXT NOT NULL,"
    "weight REAL NOT NULL DEFAULT 0.5,"
    "bridge_score REAL NOT NULL DEFAULT 1.0,"
    "domain_tags TEXT NOT NULL,"
    "metadata TEXT NOT NULL"
    ");",
    "CREATE TABLE IF NOT EXISTS digest_archive ("
    "digest_id TEXT PRIMARY KEY,"
    "generated_at TEXT NOT NULL,"
    "payload TEXT NOT NULL"
    ");",
    "CREATE TRIGGER IF NOT EXISTS forbid_signal_history_update "
    "BEFORE UPDATE ON signal_history "
    "BEGIN "
    "  SELECT RAISE(FAIL, 'signal_history is append-only'); "
    "END;",
    "CREATE TRIGGER IF NOT EXISTS forbid_signal_history_delete "
    "BEFORE DELETE ON signal_history "
    "BEGIN "
    "  SELECT RAISE(FAIL, 'signal_history is append-only'); "
    "END;",
    "CREATE TRIGGER IF NOT EXISTS forbid_quarantine_update "
    "BEFORE UPDATE ON quarantine "
    "BEGIN "
    "  SELECT RAISE(FAIL, 'quarantine is append-only'); "
    "END;",
    "CREATE TRIGGER IF NOT EXISTS forbid_quarantine_delete "
    "BEFORE DELETE ON quarantine "
    "BEGIN "
    "  SELECT RAISE(FAIL, 'quarantine is append-only'); "
    "END;",
]


class Database:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.connection: sqlite3.Connection | None = None

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.execute("PRAGMA foreign_keys = ON")
        for statement in INITIAL_SCHEMA:
            self.connection.execute(statement)
        self.connection.commit()

    def execute(self, sql: str, params: Iterable | None = None) -> sqlite3.Cursor:
        if self.connection is None:
            raise RuntimeError("Database is not initialized")
        cursor = self.connection.cursor()
        if params is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, params)
        self.connection.commit()
        return cursor

    def query(self, sql: str, params: Iterable | None = None) -> list[tuple]:
        if self.connection is None:
            raise RuntimeError("Database is not initialized")
        cursor = self.connection.cursor()
        if params is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, params)
        return cursor.fetchall()

    def signal_exists(self, signal_id: str) -> bool:
        result = self.query("SELECT 1 FROM signal_history WHERE signal_id = ?", (signal_id,))
        return bool(result)

    def insert_raw_signal(self, raw_signal: RawSignal) -> bool:
        if self.signal_exists(raw_signal.signal_id):
            return False
        self.execute(
            "INSERT INTO signal_history (signal_id, source, entity_type, entity_id, entity_url, title, description, raw_metrics, collected_at, author_id, author_followers) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                raw_signal.signal_id,
                raw_signal.source,
                raw_signal.entity_type,
                raw_signal.entity_id,
                raw_signal.entity_url,
                raw_signal.title,
                raw_signal.description,
                json.dumps(raw_signal.raw_metrics),
                raw_signal.collected_at.isoformat(),
                raw_signal.author_id,
                raw_signal.author_followers,
            ),
        )
        return True

    def insert_quarantine(self, signal_id: str, source: str, reason: str, score: float) -> None:
        self.execute(
            "INSERT OR IGNORE INTO quarantine (signal_id, source, reason, score) VALUES (?, ?, ?, ?)",
            (signal_id, source, reason, score),
        )

    def list_quarantined(self, limit: int = 25) -> list[tuple]:
        return self.query(
            "SELECT signal_id, source, reason, score, quarantined_at FROM quarantine ORDER BY quarantined_at DESC LIMIT ?",
            (limit,),
        )

    def archive_digest(self, payload: str) -> str:
        digest_id = uuid.uuid4().hex
        self.execute(
            "INSERT INTO digest_archive (digest_id, generated_at, payload) VALUES (?, ?, ?)",
            (digest_id, datetime.utcnow().isoformat(), payload),
        )
        return digest_id
