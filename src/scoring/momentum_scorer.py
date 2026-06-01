from __future__ import annotations

from src.collectors.base import RawSignal


def compute_momentum_score(raw_signal: RawSignal) -> float:
    co_spike = int(raw_signal.raw_metrics.get("co_spike_count", 0) or 0)
    return max(0.0, min(1.0, co_spike / 5.0))
