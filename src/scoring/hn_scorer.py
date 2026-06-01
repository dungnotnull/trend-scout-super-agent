from __future__ import annotations

from src.collectors.base import RawSignal


def compute_hackernews_score(raw_signal: RawSignal) -> float:
    """Compute a Hacker News score based on points and comments."""
    points = int(raw_signal.raw_metrics.get("points", 0) or 0)
    comments = int(raw_signal.raw_metrics.get("num_comments", 0) or 0)
    if points <= 0 and comments <= 0:
        return 0.0

    engagement = points + comments * 0.5
    return max(0.0, min(1.0, engagement / 100.0))
