from __future__ import annotations

from src.collectors.base import RawSignal


def compute_release_cadence(raw_signal: RawSignal) -> float:
    recency_days = int(raw_signal.raw_metrics.get("days_since_release", 90) or 90)
    return max(0.0, min(1.0, (90 - recency_days) / 90.0))
