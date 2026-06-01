from datetime import datetime

from src.digest.formatter import format_digest
from src.models import DigestItem


def test_format_digest_includes_topic_and_quarantine_footer() -> None:
    item = DigestItem(
        rank=1,
        signal_id="1",
        title="Test Signal",
        composite_score=0.83,
        what="A short description.",
        why_now="The project gained momentum this morning.",
        who_cares="Engineers tracking infrastructure.",
        key_metrics={"stars": 3400},
        source_urls=["https://github.com/owner/repo"],
        kol_quotes=["Great signal."],
        authenticity="VERIFIED",
        topic="AI/ML",
        generated_at=datetime.utcnow(),
    )
    formatted = format_digest([item], quarantined_count=2)
    assert "Topic: AI/ML" in formatted
    assert "Quarantined signals excluded from today's digest: 2" in formatted
