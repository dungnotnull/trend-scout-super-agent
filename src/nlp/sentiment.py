from __future__ import annotations

from src.collectors.base import RawSignal

POSITIVE_KEYWORDS = {
    "gain",
    "accelerat",
    "strong",
    "breakthrough",
    "surge",
    "launch",
    "adoption",
    "momentum",
    "confidence",
    "stable",
    "trusted",
}

NEGATIVE_KEYWORDS = {
    "risk",
    "leak",
    "bug",
    "failure",
    "slow",
    "spam",
    "scam",
    "issue",
    "abandon",
    "deprecated",
}


def estimate_sentiment(raw_signal: RawSignal) -> float:
    text = " ".join(filter(None, [raw_signal.title, raw_signal.description or ""]))
    text = text.lower().strip()
    if not text:
        return 0.5

    score = 0.5
    for keyword in POSITIVE_KEYWORDS:
        if keyword in text:
            score += 0.08
    for keyword in NEGATIVE_KEYWORDS:
        if keyword in text:
            score -= 0.12

    return max(0.0, min(1.0, score))
