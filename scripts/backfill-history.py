#!/usr/bin/env python
"""
Backfill signal history from GitHub Archive and Hacker News API.
This seeds the signal database with 60 days of historical data.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta

from src.collectors.github import GitHubCollector
from src.collectors.hackernews import HackerNewsCollector
from src.storage.db import Database
from src.utils.config import Settings


async def main() -> None:
    settings = Settings()
    db = Database(settings.database_path)
    db.initialize()

    github = GitHubCollector()
    hn = HackerNewsCollector()

    since = datetime.utcnow() - timedelta(days=60)

    print(f"Backfilling signals since {since.isoformat()}...")

    github_signals = await github.collect(since)
    hn_signals = await hn.collect(since)

    all_signals = github_signals + hn_signals

    inserted = 0
    for signal in all_signals:
        if db.insert_raw_signal(signal):
            inserted += 1

    print(f"✓ Backfill complete: {inserted} new signals inserted into {settings.database_path}")
    print(f"  - GitHub: {len(github_signals)} signals")
    print(f"  - Hacker News: {len(hn_signals)} signals")


if __name__ == "__main__":
    asyncio.run(main())
