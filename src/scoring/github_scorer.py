from __future__ import annotations

from src.collectors.base import RawSignal


def _normalize(value: float, max_value: float) -> float:
    if max_value <= 0:
        return 0.0
    return max(0.0, min(1.0, value / max_value))


def _commit_velocity(raw_signal: RawSignal) -> float:
    return _normalize(int(raw_signal.raw_metrics.get("commits_7d", 0) or 0), 20.0)


def _contributor_growth(raw_signal: RawSignal) -> float:
    return _normalize(int(raw_signal.raw_metrics.get("contributors_7d", 0) or 0), 6.0)


def _fork_ratio(raw_signal: RawSignal) -> float:
    forks = int(raw_signal.raw_metrics.get("forks", 0) or 0)
    stars = int(raw_signal.raw_metrics.get("stars", 0) or 0)
    if stars == 0:
        return 0.0
    ratio = forks / stars
    return max(0.0, min(1.0, ratio * 10.0))


def _release_cadence(raw_signal: RawSignal) -> float:
    recency_days = int(raw_signal.raw_metrics.get("days_since_release", 90) or 90)
    return max(0.0, min(1.0, (90.0 - recency_days) / 90.0))


def _issue_health(raw_signal: RawSignal) -> float:
    open_issues = int(raw_signal.raw_metrics.get("open_issues", 0) or 0)
    closed_issues = int(raw_signal.raw_metrics.get("closed_issues_30d", 0) or 0)
    total = open_issues + closed_issues
    if total == 0:
        return 0.5
    return max(0.0, min(1.0, closed_issues / total))


def _readme_quality(raw_signal: RawSignal) -> float:
    return max(0.0, min(1.0, float(raw_signal.raw_metrics.get("readme_quality", 0.0) or 0.0)))


def compute_github_score(raw_signal: RawSignal) -> float:
    stars = int(raw_signal.raw_metrics.get("stars", 0) or 0)
    if stars <= 0:
        return 0.0

    star_score = _normalize(stars, 5000.0)
    if not any(
        raw_signal.raw_metrics.get(key) is not None
        for key in [
            "commits_7d",
            "contributors_7d",
            "forks",
            "days_since_release",
            "open_issues",
            "closed_issues_30d",
            "readme_quality",
        ]
    ):
        return star_score

    commit_score = _commit_velocity(raw_signal)
    contributor_score = _contributor_growth(raw_signal)
    fork_score = _fork_ratio(raw_signal)
    release_score = _release_cadence(raw_signal)
    issue_score = _issue_health(raw_signal)
    readme_score = _readme_quality(raw_signal)

    weights = {
        "star": 0.35,
        "commit": 0.18,
        "contributor": 0.12,
        "fork": 0.12,
        "release": 0.1,
        "issue": 0.08,
        "readme": 0.05,
    }
    total = (
        star_score * weights["star"]
        + commit_score * weights["commit"]
        + contributor_score * weights["contributor"]
        + fork_score * weights["fork"]
        + release_score * weights["release"]
        + issue_score * weights["issue"]
        + readme_score * weights["readme"]
    )
    return max(0.0, min(1.0, total))
