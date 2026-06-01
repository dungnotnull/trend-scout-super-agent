from __future__ import annotations


def compute_composite_score(*scores: float) -> float:
    """Combine component scores into a normalized composite score."""
    if not scores:
        return 0.0
    total = sum(scores)
    return min(max(total / len(scores), 0.0), 1.0)
