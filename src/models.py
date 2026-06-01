from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class ScoredSignal:
    signal_id: str
    raw_signal: Any
    source: str
    composite_score: float
    authenticity_multiplier: float
    quarantined: bool = False
    topic: str | None = None
    kol_quotes: list[str] | None = None


@dataclass
class DigestItem:
    rank: int
    signal_id: str
    title: str
    composite_score: float
    what: str
    why_now: str
    who_cares: str
    key_metrics: dict[str, Any]
    source_urls: list[str]
    kol_quotes: list[str]
    authenticity: str
    generated_at: datetime
    topic: str | None = None
