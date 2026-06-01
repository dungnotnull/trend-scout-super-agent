from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _registry_path() -> Path:
    return Path(__file__).resolve().parent.parent / "storage" / "kol_registry.json"


def load_kol_registry() -> list[dict[str, Any]]:
    path = _registry_path()
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload.get("kols", [])


def find_kol_weight(handle: str | None) -> float:
    if not handle:
        return 0.5
    handle = handle.lower().lstrip("@")
    for kol in load_kol_registry():
        metadata = kol.get("metadata", {})
        entry_handle = str(metadata.get("handle", "")).lower().lstrip("@")
        if entry_handle == handle or kol.get("kol_id", "").lower() == handle:
            return float(kol.get("weight", 0.5))
    return 0.5
