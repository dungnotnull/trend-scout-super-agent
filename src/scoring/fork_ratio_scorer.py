from __future__ import annotations

from src.collectors.base import RawSignal


def compute_fork_ratio(raw_signal: RawSignal) -> float:
    forks = int(raw_signal.raw_metrics.get("forks", 0) or 0)
    stars = int(raw_signal.raw_metrics.get("stars", 0) or 0)
    if stars == 0:
        return 0.0
    ratio = forks / stars
    return max(0.0, min(1.0, ratio * 10.0))
