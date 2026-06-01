from __future__ import annotations

from src.models import ScoredSignal


def score_raw_signal(raw_signal: object, authenticity_multiplier: float) -> ScoredSignal:
    raw_metrics = getattr(raw_signal, "raw_metrics", {})
    source = getattr(raw_signal, "source", "")
    stars = float(raw_metrics.get("stars", 0) or 0)
    points = float(raw_metrics.get("points", 0) or 0)

    if source == "github":
        base_score = min(stars / 1000.0, 1.0)
    elif source == "hackernews":
        base_score = min(points / 100.0, 1.0)
    else:
        base_score = 0.0

    composite_score = max(0.0, min(1.0, base_score * authenticity_multiplier))
    return ScoredSignal(
        signal_id=getattr(raw_signal, "signal_id", ""),
        raw_signal=raw_signal,
        source=source,
        composite_score=composite_score,
        authenticity_multiplier=authenticity_multiplier,
        quarantined=authenticity_multiplier < 0.7,
    )
