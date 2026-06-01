#!/usr/bin/env python
"""
Seed the KOL registry with a curated list of tech influencers.
This script initializes the KOL registry with high-signal tech voices.
"""
from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    kol_registry_path = Path(__file__).resolve().parent.parent / "src" / "storage" / "kol_registry.json"

    kol_data = {
        "kols": [
            {
                "kol_id": "swyx",
                "display_name": "swyx",
                "weight": 0.85,
                "bridge_score": 1.0,
                "domain_tags": ["ai", "developer experience", "startups"],
                "metadata": {"handle": "@swyx", "platform": "twitter"},
            },
            {
                "kol_id": "karpathy",
                "display_name": "Andrej Karpathy",
                "weight": 0.9,
                "bridge_score": 1.0,
                "domain_tags": ["ai", "ml", "llm"],
                "metadata": {"handle": "@karpathy", "platform": "twitter"},
            },
            {
                "kol_id": "ylecun",
                "display_name": "Yann LeCun",
                "weight": 0.88,
                "bridge_score": 1.0,
                "domain_tags": ["ai", "ml", "deep learning"],
                "metadata": {"handle": "@ylecun", "platform": "twitter"},
            },
            {
                "kol_id": "kentcdodds",
                "display_name": "Kent C. Dodds",
                "weight": 0.75,
                "bridge_score": 1.0,
                "domain_tags": ["web", "javascript", "react", "developer experience"],
                "metadata": {"handle": "@kentcdodds", "platform": "twitter"},
            },
            {
                "kol_id": "bradleyf",
                "display_name": "Bradley Farias",
                "weight": 0.7,
                "bridge_score": 1.0,
                "domain_tags": ["nodejs", "javascript", "infrastructure"],
                "metadata": {"handle": "@bradleyf", "platform": "twitter"},
            },
            {
                "kol_id": "bradfitz",
                "display_name": "Brad Fitzpatrick",
                "weight": 0.8,
                "bridge_score": 1.0,
                "domain_tags": ["infrastructure", "open source", "golang"],
                "metadata": {"handle": "@bradfitz", "platform": "twitter"},
            },
            {
                "kol_id": "chrismessina",
                "display_name": "Chris Messina",
                "weight": 0.7,
                "bridge_score": 1.0,
                "domain_tags": ["product", "community", "ux"],
                "metadata": {"handle": "@chrism", "platform": "twitter"},
            },
            {
                "kol_id": "gvanrossum",
                "display_name": "Guido van Rossum",
                "weight": 0.85,
                "bridge_score": 1.0,
                "domain_tags": ["python", "programming languages"],
                "metadata": {"handle": "@gvanrossum", "platform": "twitter"},
            },
            {
                "kol_id": "rauchg",
                "display_name": "Guillermo Rauch",
                "weight": 0.8,
                "bridge_score": 1.0,
                "domain_tags": ["web", "javascript", "nextjs", "startups"],
                "metadata": {"handle": "@rauchg", "platform": "twitter"},
            },
            {
                "kol_id": "wycats",
                "display_name": "Yehuda Katz",
                "weight": 0.75,
                "bridge_score": 1.0,
                "domain_tags": ["javascript", "ruby", "web frameworks"],
                "metadata": {"handle": "@wycats", "platform": "twitter"},
            },
        ]
    }

    kol_registry_path.write_text(json.dumps(kol_data, indent=2), encoding="utf-8")
    print(f"✓ KOL registry seeded at {kol_registry_path}")
    print(f"  - {len(kol_data['kols'])} KOLs initialized")


if __name__ == "__main__":
    main()
