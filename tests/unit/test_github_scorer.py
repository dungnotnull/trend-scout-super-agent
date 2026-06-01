from datetime import datetime

from src.collectors.base import RawSignal
from src.scoring.github_scorer import compute_github_score


def test_github_score_normalizes_star_count() -> None:
    raw_signal = RawSignal(
        signal_id="github-1",
        source="github",
        entity_type="repository",
        entity_id="owner/repo",
        entity_url="https://github.com/owner/repo",
        title="Repo",
        description="Test repo",
        raw_metrics={"stars": 2500},
        collected_at=datetime.utcnow(),
        author_id=None,
        author_followers=None,
    )

    assert compute_github_score(raw_signal) == 0.5
