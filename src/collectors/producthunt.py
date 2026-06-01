from __future__ import annotations

from datetime import datetime
from typing import Any, List

import httpx

from src.collectors.base import BaseCollector, RawSignal
from src.utils.config import Settings
from src.utils.ids import make_signal_id


def parse_iso_datetime(value: str) -> datetime:
    if not value:
        return datetime.utcnow()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)


class ProductHuntCollector(BaseCollector):
    source = "producthunt"
    _rate_limit_remaining = 0

    async def collect(self, since: datetime) -> List[RawSignal]:
        settings = Settings()
        if not settings.producthunt_api_key:
            return []

        endpoint = "https://api.producthunt.com/v2/api/graphql"
        query = {
            "query": "query { posts(order:POPULARITY, first:20) { edges { node { id name tagline website_url createdAt votesCount commentsCount } } } }"
        }
        headers = {
            "Authorization": f"Bearer {settings.producthunt_api_key}",
            "Content-Type": "application/json",
            "User-Agent": "TrendScout/0.1",
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(endpoint, json=query, headers=headers)
                response.raise_for_status()
                payload = response.json()
        except Exception:
            return []

        signals: List[RawSignal] = []
        for edge in payload.get("data", {}).get("posts", {}).get("edges", []):
            node = edge.get("node", {})
            created_at = parse_iso_datetime(node.get("createdAt", ""))
            if created_at < since:
                continue

            post_id = str(node.get("id", ""))
            raw_metrics: dict[str, Any] = {
                "votes": int(node.get("votesCount", 0) or 0),
                "comments": int(node.get("commentsCount", 0) or 0),
            }
            signals.append(
                RawSignal(
                    signal_id=make_signal_id(self.source, post_id, created_at),
                    source=self.source,
                    entity_type="product",
                    entity_id=post_id,
                    entity_url=node.get("website_url") or "",
                    title=node.get("name", "Product Hunt launch"),
                    description=node.get("tagline"),
                    raw_metrics=raw_metrics,
                    collected_at=created_at,
                    author_id=None,
                    author_followers=None,
                )
            )
        return signals

    async def health_check(self) -> bool:
        settings = Settings()
        return bool(settings.producthunt_api_key)

    @property
    def rate_limit_remaining(self) -> int:
        return self._rate_limit_remaining
