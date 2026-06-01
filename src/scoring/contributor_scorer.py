from __future__ import annotations

from src.collectors.base import RawSignal


def compute_contributor_growth(raw_signal: RawSignal) -> float:
    contributors = int(raw_signal.raw_metrics.get("contributors_7d", 0) or 0)
    return max(0.0, min(1.0, contributors / 10.0))
