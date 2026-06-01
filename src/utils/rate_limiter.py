from __future__ import annotations

import asyncio
from time import monotonic


class TokenBucket:
    def __init__(self, rate: float, capacity: int) -> None:
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.updated_at = monotonic()
        self.lock = asyncio.Lock()

    async def consume(self, amount: int = 1) -> bool:
        async with self.lock:
            now = monotonic()
            elapsed = now - self.updated_at
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.updated_at = now
            if self.tokens >= amount:
                self.tokens -= amount
                return True
            return False
