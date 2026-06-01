from datetime import datetime

from src.collectors.base import RawSignal
from src.scoring.kol_scorer import compute_kol_score, extract_kol_quotes


def test_compute_kol_score_ramps_with_mentions() -> None:
    signal = RawSignal(
        signal_id="1",
        source="github",
        entity_type="repository",
        entity_id="owner/repo",
        entity_url="https://github.com/owner/repo",
        title="KOL signal",
        description="A signal from a known influencer.",
        raw_metrics={"kol_mentions": 3},
        collected_at=datetime.utcnow(),
        author_id=None,
        author_followers=None,
    )

    assert 0.0 < compute_kol_score(signal) <= 1.0


def test_extract_kol_quotes_returns_two_quotes() -> None:
    signal = RawSignal(
        signal_id="2",
        source="github",
        entity_type="repository",
        entity_id="owner/repo2",
        entity_url="https://github.com/owner/repo2",
        title="Quote signal",
        description="Testing quote extraction.",
        raw_metrics={"kol_quotes": ["Quote 1", "Quote 2", "Quote 3"]},
        collected_at=datetime.utcnow(),
        author_id=None,
        author_followers=None,
    )

    assert extract_kol_quotes(signal) == ["Quote 1", "Quote 2"]
