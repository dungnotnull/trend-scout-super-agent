from datetime import datetime

from src.collectors.base import RawSignal
from src.scoring.authenticity_filter import compute_authenticity_score


def test_compute_authenticity_score_github_high_star() -> None:
    signal = RawSignal(
        signal_id="1",
        source="github",
        entity_type="repository",
        entity_id="owner/repo",
        entity_url="https://github.com/owner/repo",
        title="Repo",
        description="Test",
        raw_metrics={"stars": 50000},
        collected_at=datetime.utcnow(),
        author_id=None,
        author_followers=None,
    )

    score, reason = compute_authenticity_score(signal)
    assert score == 0.7
    assert reason is not None


def test_compute_authenticity_score_hackernews_low_points() -> None:
    signal = RawSignal(
        signal_id="2",
        source="hackernews",
        entity_type="story",
        entity_id="123",
        entity_url="https://news.ycombinator.com/item?id=123",
        title="HN story",
        description=None,
        raw_metrics={"points": 5},
        collected_at=datetime.utcnow(),
        author_id="author",
        author_followers=None,
    )

    score, reason = compute_authenticity_score(signal)
    assert score == 0.85
    assert reason is not None
