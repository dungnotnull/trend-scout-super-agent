from __future__ import annotations

from datetime import datetime
from typing import List

import httpx
from bs4 import BeautifulSoup

from src.collectors.base import BaseCollector, RawSignal
from src.utils.ids import make_signal_id


class GitHubCollector(BaseCollector):
    source = "github"
    _rate_limit_remaining = 0

    async def collect(self, since: datetime) -> List[RawSignal]:
        async with httpx.AsyncClient(headers={"User-Agent": "TrendScout/0.1"}, timeout=30.0) as client:
            response = await client.get("https://github.com/trending?since=daily")
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

        signals: List[RawSignal] = []
        for article in soup.select("article.Box-row")[:20]:
            header = article.find("h1")
            if header is None:
                continue
            anchor = header.find("a")
            if anchor is None or not anchor.get("href"):
                continue

            entity_path = anchor["href"].strip()
            repo_id = entity_path.strip("/")
            if not repo_id:
                continue

            title = repo_id
            description_tag = article.find("p", class_="col-9 color-fg-muted my-1 pr-4")
            description = description_tag.text.strip() if description_tag else None
            star_link = article.find("a", href=f"{entity_path}/stargazers")
            stars = 0
            if star_link and star_link.text:
                raw_stars = star_link.text.strip().replace(",", "")
                try:
                    stars = int(raw_stars.replace("k", "000").replace("K", "000"))
                except ValueError:
                    stars = 0

            collected_at = datetime.utcnow()
            signal_id = make_signal_id(self.source, repo_id, collected_at)
            signals.append(
                RawSignal(
                    signal_id=signal_id,
                    source=self.source,
                    entity_type="repository",
                    entity_id=repo_id,
                    entity_url=f"https://github.com/{repo_id}",
                    title=title,
                    description=description,
                    raw_metrics={"stars": stars},
                    collected_at=collected_at,
                    author_id=None,
                    author_followers=None,
                )
            )
        return signals

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get("https://github.com")
                return response.status_code == 200
        except httpx.HTTPError:
            return False

    @property
    def rate_limit_remaining(self) -> int:
        return self._rate_limit_remaining
