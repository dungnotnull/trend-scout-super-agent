from __future__ import annotations

import hashlib
from datetime import datetime


def make_signal_id(source: str, entity_id: str, collected_at: datetime) -> str:
    normalized = f"{source.strip().lower()}|{entity_id.strip().lower()}|{collected_at.isoformat()}"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
