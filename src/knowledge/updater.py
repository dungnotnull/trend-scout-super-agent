from __future__ import annotations

from src.knowledge.crawler import KnowledgeCrawler
from src.knowledge.parser import KnowledgeParser
from src.knowledge.embedder import KnowledgeEmbedder


class KnowledgeUpdater:
    def update(self) -> dict[str, int]:
        crawler = KnowledgeCrawler()
        parser = KnowledgeParser()
        embedder = KnowledgeEmbedder()

        documents = crawler.crawl()
        parsed = parser.parse(documents)
        embeddings = embedder.embed(parsed)

        return {
            "documents_collected": len(documents),
            "parsed": len(parsed),
            "embeddings": len(embeddings),
        }
