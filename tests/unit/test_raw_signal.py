from datetime import datetime

from src.collectors.base import RawSignal
from src.utils.ids import make_signal_id


def test_raw_signal_and_signal_id() -> None:
    collected_at = datetime.fromisoformat("2026-06-01T12:00:00")
    signal_id = make_signal_id("github", "owner/repo", collected_at)

    signal = RawSignal(
        signal_id=signal_id,
        source="github",
        entity_type="repository",
        entity_id="owner/repo",
        entity_url="https://github.com/owner/repo",
        title="Test repo",
        description="A repo for testing.",
        raw_metrics={"stars": 100},
        collected_at=collected_at,
        author_id="owner",
        author_followers=1200,
    )

    assert signal.signal_id == signal_id
    assert signal.source == "github"
    assert signal.raw_metrics["stars"] == 100
