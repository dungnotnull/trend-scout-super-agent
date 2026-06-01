from __future__ import annotations

import abc
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class RawSignal:
    signal_id: str
    source: str
    entity_type: str
    entity_id: str
    entity_url: str
    title: str
    description: str | None
    raw_metrics: dict[str, Any]
    collected_at: datetime
    author_id: str | None
    author_followers: int | None


class BaseCollector(abc.ABC):
    source: str

    @abc.abstractmethod
    async def collect(self, since: datetime) -> list[RawSignal]:
        """Collect raw signals since the given timestamp."""

    @abc.abstractmethod
    async def health_check(self) -> bool:
        """Return True if source API is reachable and healthy."""

    @property
    @abc.abstractmethod
    def rate_limit_remaining(self) -> int:
        """Current API rate limit remaining for this source."""
