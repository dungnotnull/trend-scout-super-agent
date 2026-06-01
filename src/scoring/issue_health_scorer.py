from __future__ import annotations

from src.collectors.base import RawSignal


def compute_issue_health(raw_signal: RawSignal) -> float:
    open_issues = int(raw_signal.raw_metrics.get("open_issues", 0) or 0)
    closed_issues = int(raw_signal.raw_metrics.get("closed_issues_30d", 0) or 0)
    total = open_issues + closed_issues
    if total == 0:
        return 0.5
    ratio = closed_issues / total
    return max(0.0, min(1.0, ratio))
