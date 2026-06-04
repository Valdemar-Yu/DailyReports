from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Item


class SeenState:
    def __init__(self, path: Path):
        self.path = path
        self.data: dict[str, Any] = {"items": {}}

    @classmethod
    def load(cls, path: Path) -> "SeenState":
        state = cls(path)
        if path.exists():
            with path.open("r", encoding="utf-8") as handle:
                state.data = json.load(handle)
            state.data.setdefault("items", {})
        return state

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.path.with_suffix(".tmp")
        with tmp_path.open("w", encoding="utf-8") as handle:
            json.dump(self.data, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        tmp_path.replace(self.path)

    def push_count(self, item_id: str) -> int:
        record = self.data.get("items", {}).get(item_id, {})
        return int(record.get("push_count", 0))

    def can_push(self, item_id: str, max_pushes: int) -> bool:
        return self.push_count(item_id) < max_pushes

    def mark_pushed(self, item: Item, report_date: str) -> None:
        items = self.data.setdefault("items", {})
        record = items.setdefault(
            item.id,
            {
                "kind": item.kind,
                "title": item.title,
                "url": item.url,
                "push_count": 0,
                "dates": [],
            },
        )
        record["kind"] = item.kind
        record["title"] = item.title
        record["url"] = item.url
        dates = record.setdefault("dates", [])
        if report_date not in dates:
            dates.append(report_date)
            dates.sort()
            record["push_count"] = int(record.get("push_count", 0)) + 1


def filter_by_repeat_limit(items: list[Item], state: SeenState, max_pushes: int) -> list[Item]:
    return [item for item in items if state.can_push(item.id, max_pushes)]
