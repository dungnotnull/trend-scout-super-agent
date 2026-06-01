from __future__ import annotations

from src.collectors.base import RawSignal


def compute_commit_velocity(raw_signal: RawSignal) -> float:
    """Placeholder commit velocity score."""
    commits = int(raw_signal.raw_metrics.get("commits_7d", 0) or 0)
    return max(0.0, min(1.0, commits / 50.0))
