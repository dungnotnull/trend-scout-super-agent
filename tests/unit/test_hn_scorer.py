from datetime import datetime

from src.collectors.base import RawSignal
from src.scoring.hn_scorer import compute_hackernews_score


def test_hackernews_score_combines_points_and_comments() -> None:
    raw_signal = RawSignal(
        signal_id="hn-1",
        source="hackernews",
        entity_type="story",
        entity_id="123",
        entity_url="https://news.ycombinator.com/item?id=123",
        title="HN story",
        description="Discussion thread",
        raw_metrics={"points": 80, "num_comments": 40},
        collected_at=datetime.utcnow(),
        author_id="author",
        author_followers=None,
    )

    assert compute_hackernews_score(raw_signal) == 1.0
