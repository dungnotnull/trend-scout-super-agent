from __future__ import annotations

from typing import Sequence

from src.models import DigestItem


class DigestSynthesizer:
    def synthesize(self, items: Sequence[DigestItem]) -> str:
        lines: list[str] = ["TrendScout AI Digest", "==================="]
        for item in items:
            lines.append(f"{item.rank}. {item.title}")
            lines.append(f"   Score: {item.composite_score:.2f} | Topic: {item.topic or 'General'} | Authenticity: {item.authenticity}")
            lines.append(f"   Summary: {item.what}")
            lines.append(f"   Why now: {item.why_now}")
            if item.kol_quotes:
                lines.append(f"   KOL quotes: {' | '.join(item.kol_quotes)}")
            if item.source_urls:
                lines.append(f"   Sources: {', '.join(item.source_urls)}")
            lines.append("")
        return "\n".join(lines)
