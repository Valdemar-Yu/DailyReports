from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .models import Item
from .utils import normalize_text, parse_datetime


def score_items(items: list[Item], config: dict[str, Any]) -> list[Item]:
    topics = config.get("topics", [])
    for item in items:
        item.score, item.matched_terms = score_item(item, topics)
    return items


def score_item(item: Item, topics: list[dict[str, Any]]) -> tuple[int, list[str]]:
    corpus = normalize_text(" ".join([item.title, item.summary, item.source]))
    score = 0
    matched_terms: set[str] = set()

    for topic in topics:
        weight = int(topic.get("weight", 1))
        for term in topic.get("terms", []):
            normalized = normalize_text(term)
            if normalized and normalized in corpus:
                score += weight
                matched_terms.add(term)

    published = parse_datetime(item.published)
    if published:
        age_days = max(0, (datetime.now(timezone.utc) - published).days)
        score += max(0, 7 - age_days)

    return score, sorted(matched_terms, key=str.casefold)


def select_ranked_items(
    items: list[Item],
    kind: str,
    config: dict[str, Any],
    max_items: int,
) -> list[Item]:
    ranking_config = config.get("ranking", {})
    min_scores = ranking_config.get("min_score", {})
    min_score = int(min_scores.get(kind, 1))

    candidates = [item for item in items if item.kind == kind and item.score >= min_score]
    candidates.sort(key=lambda item: (item.score, item.published), reverse=True)
    return candidates[:max_items]
