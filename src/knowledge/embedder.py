from __future__ import annotations


class KnowledgeEmbedder:
    def embed(self, documents: list[dict[str, str]]) -> list[list[float]]:
        return [[float(len(doc["text"]))] for doc in documents]
