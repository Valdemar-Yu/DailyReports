from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Item:
    """A paper or news item gathered from an external source."""

    id: str
    kind: str
    title: str
    url: str
    source: str
    published: str = ""
    authors: list[str] = field(default_factory=list)
    summary: str = ""
    score: int = 0
    matched_terms: list[str] = field(default_factory=list)
    extra: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class FetchBatch:
    items: list[Item] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
