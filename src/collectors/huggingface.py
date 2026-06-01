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


class HuggingFaceCollector(BaseCollector):
    source = "huggingface"
    _rate_limit_remaining = 0

    async def collect(self, since: datetime) -> List[RawSignal]:
        settings = Settings()
        endpoint = "https://huggingface.co/api/models"
        params = {"sort": "downloads", "limit": 15}
        headers = {"User-Agent": "TrendScout/0.1"}
        if settings.huggingface_api_token:
            headers["Authorization"] = f"Bearer {settings.huggingface_api_token}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(endpoint, params=params, headers=headers)
                response.raise_for_status()
                payload = response.json()
        except Exception:
            return []

        signals: List[RawSignal] = []
        for item in payload[:15]:
            created_at = parse_iso_datetime(item.get("lastModified", item.get("updatedAt", ""))) if item.get("lastModified") or item.get("updatedAt") else datetime.utcnow()
            if created_at < since:
                continue

            model_id = str(item.get("id", ""))
            raw_metrics: dict[str, Any] = {
                "downloads": int(item.get("downloads", 0) or 0),
                "likes": int(item.get("likes", 0) or 0),
                "pipeline_tag": ",".join(item.get("pipeline_tag", []) or []),
            }
            signals.append(
                RawSignal(
                    signal_id=make_signal_id(self.source, model_id, created_at),
                    source=self.source,
                    entity_type="model",
                    entity_id=model_id,
                    entity_url=f"https://huggingface.co/{model_id}",
                    title=model_id,
                    description=item.get("pipeline_tag", ["Hugging Face model"])[0],
                    raw_metrics=raw_metrics,
                    collected_at=created_at,
                    author_id=str(item.get("author", "")),
                    author_followers=None,
                )
            )
        return signals

    async def health_check(self) -> bool:
        return True

    @property
    def rate_limit_remaining(self) -> int:
        return self._rate_limit_remaining
