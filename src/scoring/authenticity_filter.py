from __future__ import annotations

from src.collectors.base import RawSignal


def compute_authenticity_score(raw_signal: RawSignal) -> tuple[float, str | None]:
    """Return an authenticity multiplier and optional quarantine reason."""
    def clamp(score: float) -> float:
        return max(0.0, min(1.0, score))

    if raw_signal.source == "github":
        stars = int(raw_signal.raw_metrics.get("stars", 0) or 0)
        mentions = int(raw_signal.raw_metrics.get("kol_mentions", 0) or 0)
        if stars >= 100_000:
            return 0.6, "Very high star count without corroborating social signals."
        if stars >= 50_000 and mentions < 1:
            return 0.7, "High star count with no verified influencer mentions."
        if stars >= 10_000 and mentions == 0:
            return 0.85, "Rapid growth with insufficient social context."
        return 1.0, None

    if raw_signal.source == "hackernews":
        points = int(raw_signal.raw_metrics.get("points", 0) or 0)
        comments = int(raw_signal.raw_metrics.get("num_comments", 0) or 0)
        if points < 10:
            return 0.85, "Low HN engagement; may be noise."
        if points < 30 and comments < 5:
            return 0.75, "Sparse HN engagement; likely early noise."
        return 1.0, None

    if raw_signal.source == "twitter":
        likes = int(raw_signal.raw_metrics.get("like_count", 0) or 0)
        retweets = int(raw_signal.raw_metrics.get("retweet_count", 0) or 0)
        if likes + retweets < 15:
            return 0.8, "Low tweet engagement for a social signal."
        return 1.0, None

    if raw_signal.source in {"producthunt", "huggingface", "discord"}:
        suspicious = raw_signal.raw_metrics.get("is_sponsored") or raw_signal.raw_metrics.get("has_suspicious_pattern")
        if suspicious:
            return 0.6, "Suspicious signal characteristics detected."
        return 1.0, None

    return 1.0, None
