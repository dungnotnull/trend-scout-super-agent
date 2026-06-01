from __future__ import annotations

from src.collectors.base import RawSignal


class TopicModeler:
    KEYWORD_TOPICS: dict[str, str] = {
        "ai": "AI/ML",
        "llm": "AI/ML",
        "large language model": "AI/ML",
        "agent": "AI/ML",
        "robot": "AI/ML",
        "web3": "Web3",
        "blockchain": "Web3",
        "crypto": "Web3",
        "security": "Security",
        "privacy": "Security",
        "devops": "DevOps",
        "api": "APIs",
        "ml": "AI/ML",
    }

    def label_topic(self, raw_signal: RawSignal) -> str:
        text = " ".join(
            filter(None, [raw_signal.title, raw_signal.description or ""]) 
        ).lower()
        for keyword, topic in self.KEYWORD_TOPICS.items():
            if keyword in text:
                return topic
        if raw_signal.source == "hackernews":
            return "News"
        if raw_signal.source == "github":
            return "Open Source"
        return "General"
