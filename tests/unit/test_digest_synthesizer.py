from datetime import datetime

from src.digest.synthesizer import DigestSynthesizer
from src.models import DigestItem


def test_digest_synthesizer_generates_text() -> None:
    item = DigestItem(
        rank=1,
        signal_id="1",
        title="Test Signal",
        composite_score=0.9,
        what="A short summary.",
        why_now="Momentum accelerated after announcement.",
        who_cares="Engineers monitoring AI tooling.",
        key_metrics={"stars": 1200},
        source_urls=["https://github.com/owner/repo"],
        kol_quotes=["This is interesting."],
        authenticity="VERIFIED",
        topic="AI/ML",
        generated_at=datetime.utcnow(),
    )
    output = DigestSynthesizer().synthesize([item])
    assert "TrendScout AI Digest" in output
    assert "Topic: AI/ML" in output
