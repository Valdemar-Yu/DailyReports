from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


DEFAULT_CONFIG_FILE = Path(__file__).resolve().parents[1] / "config" / "default_config.json"


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    config_path = Path(path) if path else DEFAULT_CONFIG_FILE
    with config_path.open("r", encoding="utf-8") as handle:
        config: dict[str, Any] = json.load(handle)

    config.setdefault("report", {})
    config.setdefault("ranking", {})
    config.setdefault("topics", [])
    config.setdefault("arxiv", {})
    config.setdefault("news", {})
    config.setdefault("notifications", {})

    env_output_dir = os.getenv("DAILY_REPORT_OUTPUT_DIR")
    if env_output_dir:
        config["report"]["output_dir"] = env_output_dir

    return config


def output_dir_from_config(config: dict[str, Any], override: str | Path | None = None) -> Path:
    if override:
        return Path(override).expanduser()
    return Path(config.get("report", {}).get("output_dir", "~/DailyReports")).expanduser()


def state_file_from_config(config: dict[str, Any], output_dir: Path) -> Path:
    configured = config.get("report", {}).get("state_dir")
    state_dir = Path(configured).expanduser() if configured else output_dir / "state"
    return state_dir / "seen.json"
