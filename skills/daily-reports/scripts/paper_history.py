#!/usr/bin/env python3
"""Maintain paper recommendation counts for DailyReports."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


DEFAULT_HISTORY = Path(
    os.environ.get("DAILY_REPORT_HISTORY")
    or (
        Path(os.environ.get("DAILY_REPORT_OUTPUT_DIR", "~/DailyReports")).expanduser()
        / "paper-history.json"
    )
)
DEFAULT_MAX_COUNT = 2


def normalize_title(title: str) -> str:
    title = title.casefold()
    title = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", title)
    return re.sub(r"\s+", " ", title).strip()


def normalize_url(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url.strip())
    host = parsed.netloc.casefold()
    path = re.sub(r"/+$", "", parsed.path)
    if host.endswith("arxiv.org"):
        path = path.replace("/pdf/", "/abs/")
        path = re.sub(r"\.pdf$", "", path)
    return f"{host}{path}".strip("/")


def paper_key(item: dict[str, Any]) -> str:
    arxiv_id = str(item.get("arxiv_id") or "").strip().lower()
    if arxiv_id:
        arxiv_id = re.sub(r"^arxiv:", "", arxiv_id)
        arxiv_id = re.sub(r"v\d+$", "", arxiv_id)
        return f"arxiv:{arxiv_id}"

    doi = str(item.get("doi") or "").strip().lower()
    if doi:
        doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)
        return f"doi:{doi}"

    url = normalize_url(str(item.get("url") or ""))
    if url:
        return f"url:{url}"

    title = normalize_title(str(item.get("title") or ""))
    if title:
        digest = hashlib.sha1(title.encode("utf-8")).hexdigest()[:16]
        return f"title:{digest}"

    raise ValueError("paper item needs at least one of arxiv_id, doi, url, or title")


def load_history(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "max_recommendations_per_paper": DEFAULT_MAX_COUNT, "papers": {}}
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("version", 1)
    data.setdefault("max_recommendations_per_paper", DEFAULT_MAX_COUNT)
    data.setdefault("papers", {})
    return data


def save_history(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def read_items(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "papers" in data and isinstance(data["papers"], list):
        data = data["papers"]
    if not isinstance(data, list):
        raise ValueError("input JSON must be a list, or an object with a papers list")
    return data


def check(args: argparse.Namespace) -> int:
    history = load_history(args.history)
    max_count = args.max_count or int(history.get("max_recommendations_per_paper", DEFAULT_MAX_COUNT))
    items = read_items(args.input)
    papers = history["papers"]
    allowed: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []

    for item in items:
        key = paper_key(item)
        count = int(papers.get(key, {}).get("count", 0))
        enriched = dict(item)
        enriched["paper_key"] = key
        enriched["current_count"] = count
        enriched["max_count"] = max_count
        if count < max_count:
            enriched["next_count"] = count + 1
            allowed.append(enriched)
        else:
            excluded.append(enriched)

    json.dump({"allowed": allowed, "excluded": excluded}, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


def record(args: argparse.Namespace) -> int:
    history = load_history(args.history)
    items = read_items(args.input)
    papers = history["papers"]
    today = args.date or date.today().isoformat()

    recorded: list[dict[str, Any]] = []
    for item in items:
        key = paper_key(item)
        entry = papers.setdefault(
            key,
            {
                "title": item.get("title", ""),
                "urls": [],
                "count": 0,
                "recommended_dates": [],
                "sources": [],
            },
        )
        if item.get("title") and not entry.get("title"):
            entry["title"] = item["title"]
        if item.get("url") and item["url"] not in entry.setdefault("urls", []):
            entry["urls"].append(item["url"])
        if item.get("source") and item["source"] not in entry.setdefault("sources", []):
            entry["sources"].append(item["source"])
        entry["count"] = int(entry.get("count", 0)) + 1
        entry.setdefault("recommended_dates", []).append(today)
        entry["last_recommended"] = today
        recorded.append({"paper_key": key, "count": entry["count"], "title": entry.get("title", "")})

    save_history(args.history, history)
    json.dump({"recorded": recorded, "history": str(args.history)}, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


def status(args: argparse.Namespace) -> int:
    history = load_history(args.history)
    json.dump(history, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history", type=Path, default=DEFAULT_HISTORY)
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="filter candidate papers by recommendation count")
    check_parser.add_argument("--input", type=Path, required=True)
    check_parser.add_argument("--max-count", type=int, default=None)
    check_parser.set_defaults(func=check)

    record_parser = subparsers.add_parser("record", help="record delivered paper recommendations")
    record_parser.add_argument("--input", type=Path, required=True)
    record_parser.add_argument("--date", default=None)
    record_parser.set_defaults(func=record)

    status_parser = subparsers.add_parser("status", help="print the complete history JSON")
    status_parser.set_defaults(func=status)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except Exception as exc:
        parser.exit(2, f"paper_history.py: error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
