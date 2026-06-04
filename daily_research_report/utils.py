from __future__ import annotations

import hashlib
import html
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo


HTML_TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    text = html.unescape(value)
    text = HTML_TAG_RE.sub(" ", text)
    return SPACE_RE.sub(" ", text).strip()


def normalize_text(value: str | None) -> str:
    return SPACE_RE.sub(" ", clean_text(value).casefold()).strip()


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    candidate = value.strip()
    if not candidate:
        return None

    iso_candidate = candidate.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(iso_candidate)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        pass

    try:
        parsed = parsedate_to_datetime(candidate)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except (TypeError, ValueError):
        return None


def format_date(value: str | None, timezone_name: str) -> str:
    parsed = parse_datetime(value)
    if not parsed:
        return value or "未知"
    return parsed.astimezone(ZoneInfo(timezone_name)).strftime("%Y-%m-%d")


def stable_fingerprint(*parts: str) -> str:
    payload = "\n".join(normalize_text(part) for part in parts if part)
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]


def first_sentences(text: str, limit: int = 2, max_chars: int = 520) -> str:
    text = clean_text(text)
    if len(text) <= max_chars:
        return text
    pieces = re.split(r"(?<=[.!?])\s+", text)
    summary = " ".join(piece for piece in pieces[:limit] if piece).strip()
    if summary and len(summary) <= max_chars:
        return summary
    return text[: max_chars - 3].rstrip() + "..."
