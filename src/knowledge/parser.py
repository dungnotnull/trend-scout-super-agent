from __future__ import annotations


class KnowledgeParser:
    def parse(self, documents: list[str]) -> list[dict[str, str]]:
        return [{"text": doc} for doc in documents]
