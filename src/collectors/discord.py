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


class DiscordCollector(BaseCollector):
    source = "discord"
    _rate_limit_remaining = 0

    async def collect(self, since: datetime) -> List[RawSignal]:
        settings = Settings()
        if not settings.discord_bot_token or not settings.discord_channel_id:
            return []

        endpoint = f"https://discord.com/api/v10/channels/{settings.discord_channel_id}/messages"
        headers = {
            "Authorization": f"Bot {settings.discord_bot_token}",
            "User-Agent": "TrendScout/0.1",
        }
        params = {"limit": 25}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(endpoint, params=params, headers=headers)
                response.raise_for_status()
                payload = response.json()
        except Exception:
            return []

        signals: List[RawSignal] = []
        for message in payload:
            timestamp = message.get("timestamp")
            if not timestamp:
                continue
            created_at = parse_iso_datetime(timestamp)
            if created_at < since:
                continue

            signal_id = make_signal_id(self.source, message.get("id", ""), created_at)
            content = message.get("content", "Discord message")
            raw_metrics: dict[str, Any] = {
                "attachments": len(message.get("attachments", []) or []),
                "reactions": sum(int(reaction.get("count", 0) or 0) for reaction in message.get("reactions", []) or []),
            }
            signals.append(
                RawSignal(
                    signal_id=signal_id,
                    source=self.source,
                    entity_type="message",
                    entity_id=str(message.get("id", "")),
                    entity_url="",
                    title=content[:120],
                    description=content,
                    raw_metrics=raw_metrics,
                    collected_at=created_at,
                    author_id=message.get("author", {}).get("id") if isinstance(message.get("author"), dict) else None,
                    author_followers=None,
                )
            )
        return signals

    async def health_check(self) -> bool:
        settings = Settings()
        return bool(settings.discord_bot_token and settings.discord_channel_id)

    @property
    def rate_limit_remaining(self) -> int:
        return self._rate_limit_remaining
