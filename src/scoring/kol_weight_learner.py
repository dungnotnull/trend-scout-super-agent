from __future__ import annotations

import json
from pathlib import Path

from src.storage.db import Database
from src.scoring.kol_registry import load_kol_registry


def _registry_path() -> Path:
    return Path(__file__).resolve().parent.parent / "storage" / "kol_registry.json"


def _clamp_weight(weight: float) -> float:
    return max(0.1, min(1.0, weight))


def learn_kol_weights(db: Database) -> dict[str, float]:
    registry = load_kol_registry()
    if not registry:
        return {}

    weights: dict[str, float] = {kol["kol_id"]: float(kol.get("weight", 0.5)) for kol in registry}
    signal_rows = db.query("SELECT raw_metrics, signal_id FROM signal_history")
    for raw_metrics_text, signal_id in signal_rows:
        try:
            raw_metrics = json.loads(raw_metrics_text)
        except json.JSONDecodeError:
            continue

        mentions = int(raw_metrics.get("kol_mentions", 0) or 0)
        if mentions <= 0:
            continue

        for kol in registry:
            kol_id = kol["kol_id"]
            if mentions >= 1:
                weights[kol_id] = _clamp_weight(weights[kol_id] + 0.005)

    output = []
    for kol in registry:
        kol_id = kol["kol_id"]
        new_weight = _clamp_weight(weights[kol_id])
        output.append({**kol, "weight": new_weight})

    path = _registry_path()
    with path.open("w", encoding="utf-8") as handle:
        json.dump({"kols": output}, handle, indent=2)

    return {kol["kol_id"]: kol["weight"] for kol in output}
