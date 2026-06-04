from __future__ import annotations

import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from typing import Any

from .models import FetchBatch, Item
from .utils import clean_text, parse_datetime, stable_fingerprint


ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
ARXIV_VERSION_RE = re.compile(r"v\d+$")


def fetch_all(config: dict[str, Any]) -> FetchBatch:
    batch = FetchBatch()

    if config.get("arxiv", {}).get("enabled", True):
        arxiv_batch = fetch_arxiv(config)
        batch.items.extend(arxiv_batch.items)
        batch.warnings.extend(arxiv_batch.warnings)

    if config.get("news", {}).get("enabled", True):
        news_batch = fetch_news(config)
        batch.items.extend(news_batch.items)
        batch.warnings.extend(news_batch.warnings)

    batch.items = dedupe_items(batch.items)
    return batch


def fetch_arxiv(config: dict[str, Any]) -> FetchBatch:
    arxiv_config = config.get("arxiv", {})
    categories = arxiv_config.get("categories", ["cs.AI", "cs.CL", "cs.LG"])
    queries = arxiv_config.get("queries", [])
    max_results = int(arxiv_config.get("max_results_per_query", 50))
    lookback_days = int(arxiv_config.get("lookback_days", 14))
    request_delay_seconds = float(arxiv_config.get("request_delay_seconds", 3.1))
    timeout_seconds = int(arxiv_config.get("timeout_seconds", 30))
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    api_enabled = bool(arxiv_config.get("api_enabled", True))

    batch = FetchBatch()
    if api_enabled:
        for index, query_group in enumerate(queries):
            if index > 0 and request_delay_seconds > 0:
                time.sleep(request_delay_seconds)

            terms = query_group.get("terms", [])
            if not terms:
                continue

            query = _build_arxiv_query(categories, terms)
            params = urllib.parse.urlencode(
                {
                    "search_query": query,
                    "start": 0,
                    "max_results": max_results,
                    "sortBy": "submittedDate",
                    "sortOrder": "descending",
                }
            )
            url = f"https://export.arxiv.org/api/query?{params}"

            try:
                xml_text = _http_get_text(url, timeout_seconds)
                batch.items.extend(_parse_arxiv_entries(xml_text, cutoff))
            except (ET.ParseError, urllib.error.URLError, TimeoutError, OSError) as exc:
                batch.warnings.append(f"arXiv query '{query_group.get('name', 'unnamed')}' failed: {exc}")

    fallback_config = arxiv_config.get("rss_fallback", {})
    if fallback_config.get("enabled", True) and (not api_enabled or not batch.items or batch.warnings):
        rss_batch = fetch_arxiv_rss(config)
        if rss_batch.items:
            batch.items.extend(rss_batch.items)
            if api_enabled:
                batch.warnings.append("arXiv API was incomplete; used arXiv RSS category fallback.")
        batch.warnings.extend(rss_batch.warnings)

    batch.items = dedupe_items(batch.items)
    return batch


def fetch_arxiv_rss(config: dict[str, Any]) -> FetchBatch:
    arxiv_config = config.get("arxiv", {})
    fallback_config = arxiv_config.get("rss_fallback", {})
    categories = fallback_config.get("categories") or arxiv_config.get("categories", ["cs.AI", "cs.CL", "cs.LG"])
    base_url = fallback_config.get("base_url", "https://rss.arxiv.org/rss").rstrip("/")
    lookback_days = int(fallback_config.get("lookback_days", arxiv_config.get("lookback_days", 14)))
    timeout_seconds = int(fallback_config.get("timeout_seconds", arxiv_config.get("timeout_seconds", 30)))
    max_items_per_category = int(fallback_config.get("max_items_per_category", 80))
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)

    batch = FetchBatch()
    for category in categories:
        url = f"{base_url}/{urllib.parse.quote(category)}"
        try:
            xml_text = _http_get_text(url, timeout_seconds)
            batch.items.extend(_parse_arxiv_rss_items(xml_text, category, cutoff, max_items_per_category))
        except (ET.ParseError, urllib.error.URLError, TimeoutError, OSError) as exc:
            batch.warnings.append(f"arXiv RSS category '{category}' failed: {exc}")

    batch.items = dedupe_items(batch.items)
    return batch


def fetch_news(config: dict[str, Any]) -> FetchBatch:
    news_config = config.get("news", {})
    feeds = news_config.get("feeds", [])
    lookback_days = int(news_config.get("lookback_days", 14))
    timeout_seconds = int(news_config.get("timeout_seconds", 30))
    max_workers = max(1, int(news_config.get("max_workers", min(6, len(feeds) or 1))))
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)

    batch = FetchBatch()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(_fetch_one_news_feed, feed, timeout_seconds, cutoff)
            for feed in feeds
            if feed.get("url")
        ]
        for future in as_completed(futures):
            feed_batch = future.result()
            batch.items.extend(feed_batch.items)
            batch.warnings.extend(feed_batch.warnings)

    batch.items = dedupe_items(batch.items)
    return batch


def _fetch_one_news_feed(feed: dict[str, Any], timeout_seconds: int, cutoff: datetime) -> FetchBatch:
    name = feed.get("name", "Unnamed feed")
    url = feed.get("url")
    batch = FetchBatch()
    try:
        xml_text = _http_get_text(url, timeout_seconds)
        batch.items.extend(_parse_feed_items(xml_text, name, cutoff))
    except (ET.ParseError, urllib.error.URLError, TimeoutError, OSError) as exc:
        batch.warnings.append(f"RSS feed '{name}' failed: {exc}")
    return batch


def dedupe_items(items: list[Item]) -> list[Item]:
    by_id: dict[str, Item] = {}
    for item in items:
        key = item.id or f"{item.kind}:{stable_fingerprint(item.title, item.url)}"
        item.id = key
        existing = by_id.get(key)
        if not existing:
            by_id[key] = item
            continue
        if len(item.summary) > len(existing.summary):
            existing.summary = item.summary
        existing.matched_terms = sorted(set(existing.matched_terms) | set(item.matched_terms))
    return list(by_id.values())


def _http_get_text(url: str, timeout_seconds: int) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "daily-research-report/0.1 (+https://github.com/)",
            "Accept": "application/atom+xml, application/rss+xml, application/xml, text/xml;q=0.9, */*;q=0.5",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def _build_arxiv_query(categories: list[str], terms: list[str]) -> str:
    category_query = " OR ".join(f"cat:{category}" for category in categories)
    term_query = " OR ".join(_arxiv_term(term) for term in terms)
    return f"({category_query}) AND ({term_query})"


def _arxiv_term(term: str) -> str:
    cleaned = term.strip().strip('"')
    if " " in cleaned:
        return f'all:"{cleaned}"'
    return f"all:{cleaned}"


def _parse_arxiv_entries(xml_text: str, cutoff: datetime) -> list[Item]:
    root = ET.fromstring(xml_text)
    items: list[Item] = []
    for entry in root.findall("atom:entry", ATOM_NS):
        id_url = _find_text(entry, "id") or ""
        raw_id = id_url.rstrip("/").rsplit("/", 1)[-1]
        base_id = ARXIV_VERSION_RE.sub("", raw_id)
        title = clean_text(_find_text(entry, "title"))
        summary = clean_text(_find_text(entry, "summary"))
        published = _find_text(entry, "published") or _find_text(entry, "updated") or ""
        parsed_published = parse_datetime(published)
        if parsed_published and parsed_published < cutoff:
            continue

        authors = [
            clean_text(author_name.text)
            for author_name in entry.findall("atom:author/atom:name", ATOM_NS)
            if author_name.text
        ]
        categories = [
            category.attrib.get("term", "")
            for category in entry.findall("atom:category", ATOM_NS)
            if category.attrib.get("term")
        ]
        pdf_url = ""
        for link in entry.findall("atom:link", ATOM_NS):
            if link.attrib.get("title") == "pdf":
                pdf_url = link.attrib.get("href", "")

        items.append(
            Item(
                id=f"arxiv:{base_id}",
                kind="paper",
                title=title,
                url=id_url or f"https://arxiv.org/abs/{base_id}",
                source="arXiv",
                published=published,
                authors=authors,
                summary=summary,
                extra={"categories": ", ".join(categories), "pdf": pdf_url},
            )
        )
    return items


def _parse_arxiv_rss_items(xml_text: str, category: str, cutoff: datetime, limit: int) -> list[Item]:
    root = ET.fromstring(xml_text)
    items: list[Item] = []
    for entry in _descendants_named(root, "item")[:limit]:
        title = clean_text(_child_text(entry, "title"))
        link = clean_text(_child_text(entry, "link"))
        summary = clean_text(
            _child_text(entry, "description")
            or _child_text(entry, "summary")
            or _child_text(entry, "encoded")
        )
        summary = re.sub(r"^arXiv:\S+\s+Announce Type:\s+\w+\s+Abstract:\s*", "", summary)
        published = (
            _child_text(entry, "pubDate")
            or _child_text(entry, "published")
            or _child_text(entry, "updated")
            or _child_text(entry, "date")
            or ""
        )
        parsed_published = parse_datetime(published)
        if parsed_published and parsed_published < cutoff:
            continue
        raw_id = _arxiv_id_from_url(link) or stable_fingerprint(title, link)
        base_id = ARXIV_VERSION_RE.sub("", raw_id)
        creator = clean_text(_child_text(entry, "creator"))
        authors = [part.strip() for part in re.split(r",| and ", creator) if part.strip()] if creator else []
        items.append(
            Item(
                id=f"arxiv:{base_id}",
                kind="paper",
                title=title,
                url=link or f"https://arxiv.org/abs/{base_id}",
                source=f"arXiv RSS {category}",
                published=published,
                authors=authors,
                summary=summary,
                extra={"categories": category, "pdf": f"https://arxiv.org/pdf/{base_id}" if raw_id else ""},
            )
        )
    return items


def _parse_feed_items(xml_text: str, source_name: str, cutoff: datetime) -> list[Item]:
    root = ET.fromstring(xml_text)
    root_name = _local_name(root.tag)
    if root_name == "feed":
        return _parse_atom_feed(root, source_name, cutoff)
    return _parse_rss_feed(root, source_name, cutoff)


def _parse_atom_feed(root: ET.Element, source_name: str, cutoff: datetime) -> list[Item]:
    items: list[Item] = []
    for entry in _children_named(root, "entry"):
        title = clean_text(_child_text(entry, "title"))
        summary = clean_text(_child_text(entry, "summary") or _child_text(entry, "content"))
        published = _child_text(entry, "published") or _child_text(entry, "updated") or ""
        parsed_published = parse_datetime(published)
        if parsed_published and parsed_published < cutoff:
            continue
        link = _atom_link(entry)
        item_id = _child_text(entry, "id") or link or title
        items.append(
            Item(
                id=f"news:{stable_fingerprint(source_name, item_id)}",
                kind="news",
                title=title,
                url=link,
                source=source_name,
                published=published,
                summary=summary,
            )
        )
    return items


def _parse_rss_feed(root: ET.Element, source_name: str, cutoff: datetime) -> list[Item]:
    items: list[Item] = []
    for entry in _descendants_named(root, "item"):
        title = clean_text(_child_text(entry, "title"))
        summary = clean_text(
            _child_text(entry, "description")
            or _child_text(entry, "summary")
            or _child_text(entry, "encoded")
        )
        published = (
            _child_text(entry, "pubDate")
            or _child_text(entry, "published")
            or _child_text(entry, "updated")
            or _child_text(entry, "date")
            or ""
        )
        parsed_published = parse_datetime(published)
        if parsed_published and parsed_published < cutoff:
            continue
        link = clean_text(_child_text(entry, "link"))
        guid = clean_text(_child_text(entry, "guid"))
        item_id = guid or link or title
        items.append(
            Item(
                id=f"news:{stable_fingerprint(source_name, item_id)}",
                kind="news",
                title=title,
                url=link,
                source=source_name,
                published=published,
                summary=summary,
            )
        )
    return items


def _find_text(element: ET.Element, child_name: str) -> str:
    child = element.find(f"atom:{child_name}", ATOM_NS)
    return child.text.strip() if child is not None and child.text else ""


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _children_named(element: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in list(element) if _local_name(child.tag) == name]


def _descendants_named(element: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in element.iter() if _local_name(child.tag) == name]


def _child_text(element: ET.Element, name: str) -> str:
    for child in list(element):
        if _local_name(child.tag) == name and child.text:
            return child.text.strip()
    return ""


def _atom_link(entry: ET.Element) -> str:
    for child in list(entry):
        if _local_name(child.tag) != "link":
            continue
        href = child.attrib.get("href")
        rel = child.attrib.get("rel", "alternate")
        if href and rel == "alternate":
            return href
    for child in list(entry):
        if _local_name(child.tag) == "link" and child.attrib.get("href"):
            return child.attrib["href"]
    return ""


def _arxiv_id_from_url(url: str) -> str:
    if not url:
        return ""
    normalized = url.rstrip("/")
    for marker in ("/abs/", "/pdf/"):
        if marker in normalized:
            return normalized.rsplit(marker, 1)[-1].replace(".pdf", "")
    return ""
