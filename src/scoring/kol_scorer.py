from __future__ import annotations

from src.collectors.base import RawSignal
from src.scoring.kol_registry import find_kol_weight


def compute_kol_score(raw_signal: RawSignal) -> float:
    """Compute a weighted KOL score from raw signal metadata."""
    mentions = int(raw_signal.raw_metrics.get("kol_mentions", 0) or 0)
    author_handle = raw_signal.author_id
    weight = find_kol_weight(author_handle)
    base = max(0.0, min(1.0, mentions / 4.0))
    return max(0.0, min(1.0, base * weight))


def extract_kol_quotes(raw_signal: RawSignal) -> list[str]:
    quotes = raw_signal.raw_metrics.get("kol_quotes") or []
    if isinstance(quotes, list):
        return [str(item) for item in quotes[:2]]
    return []
