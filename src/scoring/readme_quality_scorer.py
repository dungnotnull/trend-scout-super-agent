from __future__ import annotations

from src.collectors.base import RawSignal


def compute_readme_quality(raw_signal: RawSignal) -> float:
    readme_score = float(raw_signal.raw_metrics.get("readme_quality", 0.0) or 0.0)
    return max(0.0, min(1.0, readme_score))
