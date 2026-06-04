from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


def maybe_create_github_issue(title: str, body: str, config: dict[str, Any]) -> list[str]:
    issue_config = config.get("notifications", {}).get("github_issue", {})
    if not issue_config.get("enabled", False):
        return []

    token = os.getenv("GITHUB_TOKEN")
    repository = issue_config.get("repository") or os.getenv("GITHUB_REPOSITORY")
    if not token or not repository:
        return ["GitHub issue notification skipped: missing GITHUB_TOKEN or repository."]

    api_root = os.getenv("GITHUB_API_URL", "https://api.github.com").rstrip("/")
    url = f"{api_root}/repos/{repository}/issues"
    payload = {
        "title": title,
        "body": body[:64000],
        "labels": issue_config.get("labels", ["daily-report"]),
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "daily-research-report/0.1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.status >= 300:
                return [f"GitHub issue notification failed with HTTP {response.status}."]
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return [f"GitHub issue notification failed: {exc}"]
    return []
