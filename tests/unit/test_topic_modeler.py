from datetime import datetime

from src.collectors.base import RawSignal
from src.nlp.topic_modeler import TopicModeler


def test_topic_modeler_labels_ai_ml() -> None:
    raw_signal = RawSignal(
        signal_id="1",
        source="github",
        entity_type="repository",
        entity_id="owner/repo",
        entity_url="https://github.com/owner/repo",
        title="AI agent starter kit",
        description="A lightweight large language model wrapper for productivity.",
        raw_metrics={"stars": 1200},
        collected_at=datetime.utcnow(),
        author_id=None,
        author_followers=None,
    )

    topic = TopicModeler().label_topic(raw_signal)
    assert topic == "AI/ML"
