from __future__ import annotations

from typing import Sequence

from src.models import DigestItem


def format_digest(items: Sequence[DigestItem], quarantined_count: int = 0) -> str:
    lines: list[str] = ["TrendScout Digest", "================"]
    for item in items:
        lines.append(f"{item.rank}. {item.title}")
        lines.append(f"   Score: {item.composite_score:.2f} | Authenticity: {item.authenticity}")
        if item.topic:
            lines.append(f"   Topic: {item.topic}")
        lines.append(f"   What: {item.what}")
        lines.append(f"   Why now: {item.why_now}")
        lines.append(f"   Who cares: {item.who_cares}")
        if item.key_metrics:
            metrics_text = ", ".join(f"{k}: {v}" for k, v in item.key_metrics.items())
            lines.append(f"   Metrics: {metrics_text}")
        if item.source_urls:
            lines.append(f"   Sources: {', '.join(item.source_urls)}")
        lines.append("")

    if quarantined_count:
        lines.append(f"Quarantined signals excluded from today's digest: {quarantined_count}")
    return "\n".join(lines)
