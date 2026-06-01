from __future__ import annotations

from datetime import datetime
from typing import List

import httpx

from src.collectors.base import BaseCollector, RawSignal
from src.utils.ids import make_signal_id


def parse_iso_datetime(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)


class HackerNewsCollector(BaseCollector):
    source = "hackernews"
    _rate_limit_remaining = 0

    async def collect(self, since: datetime) -> List[RawSignal]:
        endpoint = "https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=30"
        async with httpx.AsyncClient(headers={"User-Agent": "TrendScout/0.1"}, timeout=30.0) as client:
            response = await client.get(endpoint)
            response.raise_for_status()
            payload = response.json()

        signals: List[RawSignal] = []
        for hit in payload.get("hits", []):
            created_at = parse_iso_datetime(hit.get("created_at", ""))
            if created_at < since:
                continue
            object_id = str(hit.get("objectID", ""))
            title = hit.get("title") or hit.get("story_title") or "Hacker News story"
            url = hit.get("url") or f"https://news.ycombinator.com/item?id={object_id}"
            description = hit.get("story_text")
            points = int(hit.get("points") or 0)
            comments = int(hit.get("num_comments") or 0)
            signal_id = make_signal_id(self.source, object_id, created_at)
            signals.append(
                RawSignal(
                    signal_id=signal_id,
                    source=self.source,
                    entity_type="story",
                    entity_id=object_id,
                    entity_url=url,
                    title=title,
                    description=description,
                    raw_metrics={
                        "points": points,
                        "num_comments": comments,
                        "hn_url": f"https://news.ycombinator.com/item?id={object_id}",
                    },
                    collected_at=created_at,
                    author_id=hit.get("author"),
                    author_followers=None,
                )
            )
        return signals

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get("https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=1")
                return response.status_code == 200
        except httpx.HTTPError:
            return False

    @property
    def rate_limit_remaining(self) -> int:
        return self._rate_limit_remaining
