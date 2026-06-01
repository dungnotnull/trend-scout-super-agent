from datetime import datetime

from src.collectors.base import RawSignal
from src.nlp.sentiment import estimate_sentiment


def test_estimate_sentiment_positive_text() -> None:
    signal = RawSignal(
        signal_id="1",
        source="github",
        entity_type="repository",
        entity_id="owner/repo",
        entity_url="https://github.com/owner/repo",
        title="Breakthrough AI launch",
        description="A strong new model with massive adoption momentum.",
        raw_metrics={"stars": 1200},
        collected_at=datetime.utcnow(),
        author_id=None,
        author_followers=None,
    )

    score = estimate_sentiment(signal)
    assert score > 0.5


def test_estimate_sentiment_negative_text() -> None:
    signal = RawSignal(
        signal_id="2",
        source="github",
        entity_type="repository",
        entity_id="owner/repo2",
        entity_url="https://github.com/owner/repo2",
        title="Abandoned library",
        description="This project has been deprecated and has many open issues.",
        raw_metrics={"stars": 50},
        collected_at=datetime.utcnow(),
        author_id=None,
        author_followers=None,
    )

    score = estimate_sentiment(signal)
    assert score < 0.5
