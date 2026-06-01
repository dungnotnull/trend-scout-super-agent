from __future__ import annotations

from typing import Iterable

from src.models import ScoredSignal


def rank_signals(signals: Iterable[ScoredSignal], top_n: int = 10) -> list[ScoredSignal]:
    return sorted(signals, key=lambda item: item.composite_score, reverse=True)[:top_n]
