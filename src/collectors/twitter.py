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


class TwitterCollector(BaseCollector):
    source = "twitter"
    _rate_limit_remaining = 0

    async def collect(self, since: datetime) -> List[RawSignal]:
        settings = Settings()
        if not settings.twitter_bearer_token:
            return []

        endpoint = "https://api.twitter.com/2/tweets/search/recent"
        params = {
            "query": "(github OR ai OR ml OR producthunt OR huggingface) lang:en -is:retweet",
            "max_results": "20",
            "tweet.fields": "created_at,public_metrics,author_id,text",
        }
        headers = {
            "Authorization": f"Bearer {settings.twitter_bearer_token}",
            "User-Agent": "TrendScout/0.1",
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(endpoint, params=params, headers=headers)
                response.raise_for_status()
                payload = response.json()
        except Exception:
            return []

        signals: List[RawSignal] = []
        for tweet in payload.get("data", []):
            created_at = parse_iso_datetime(tweet.get("created_at", ""))
            if created_at < since:
                continue

            tweet_id = tweet.get("id", "")
            metrics = tweet.get("public_metrics", {})
            raw_metrics: dict[str, Any] = {
                "like_count": int(metrics.get("like_count", 0) or 0),
                "retweet_count": int(metrics.get("retweet_count", 0) or 0),
                "reply_count": int(metrics.get("reply_count", 0) or 0),
                "quote_count": int(metrics.get("quote_count", 0) or 0),
            }
            signals.append(
                RawSignal(
                    signal_id=make_signal_id(self.source, tweet_id, created_at),
                    source=self.source,
                    entity_type="tweet",
                    entity_id=tweet_id,
                    entity_url=f"https://twitter.com/i/web/status/{tweet_id}",
                    title=tweet.get("text", "Twitter signal")[:120],
                    description=tweet.get("text"),
                    raw_metrics=raw_metrics,
                    collected_at=created_at,
                    author_id=tweet.get("author_id"),
                    author_followers=None,
                )
            )
        return signals

    async def health_check(self) -> bool:
        settings = Settings()
        return bool(settings.twitter_bearer_token)

    @property
    def rate_limit_remaining(self) -> int:
        return self._rate_limit_remaining
