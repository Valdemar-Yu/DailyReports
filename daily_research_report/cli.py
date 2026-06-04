from __future__ import annotations

import argparse
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .config import load_config, output_dir_from_config, state_file_from_config
from .fetchers import fetch_all
from .models import FetchBatch, Item
from .notifiers import maybe_create_github_issue
from .ranker import score_items, select_ranked_items
from .renderer import render_report, write_report
from .state import SeenState, filter_by_repeat_limit


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config = load_config(args.config)
    output_dir = output_dir_from_config(config, args.output_dir)
    report_date = resolve_report_date(args.date, config.get("report", {}).get("timezone", "Asia/Shanghai"))
    state = SeenState.load(state_file_from_config(config, output_dir))

    batch = sample_batch() if args.sample else fetch_all(config)
    scored_items = score_items(batch.items, config)

    report_config = config.get("report", {})
    max_papers = int(report_config.get("max_papers", 12))
    max_news = int(report_config.get("max_news", 10))
    max_paper_repeats = int(report_config.get("max_paper_repeats", 2))
    max_news_repeats = int(report_config.get("max_news_repeats", 2))

    ranked_papers = select_ranked_items(scored_items, "paper", config, max_papers * 3)
    ranked_news = select_ranked_items(scored_items, "news", config, max_news * 3)
    papers = filter_by_repeat_limit(ranked_papers, state, max_paper_repeats)[:max_papers]
    news = filter_by_repeat_limit(ranked_news, state, max_news_repeats)[:max_news]

    report_text = render_report(report_date, papers, news, config, batch.warnings)
    if args.dry_run:
        sys.stdout.write(report_text)
        if not report_text.endswith("\n"):
            sys.stdout.write("\n")
        return 0

    report_path = write_report(report_text, output_dir, report_date)
    report_date_text = report_date.isoformat()
    for item in papers + news:
        state.mark_pushed(item, report_date_text)
    state.save()

    notify_warnings: list[str] = []
    if not args.no_notify:
        notify_warnings = maybe_create_github_issue(
            f"{report_config.get('title', 'Daily Research Report')} - {report_date_text}",
            report_text,
            config,
        )
    for warning in batch.warnings + notify_warnings:
        print(f"warning: {warning}", file=sys.stderr)

    print(f"Report written to {report_path}")
    print(f"State written to {state.path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a daily AI research frontier report.")
    parser.add_argument("--config", help="Path to JSON config. Defaults to config/default_config.json.")
    parser.add_argument("--output-dir", help="Directory for reports and state. Defaults to D:\\DailyReports.")
    parser.add_argument("--date", help="Report date in YYYY-MM-DD. Defaults to today in configured timezone.")
    parser.add_argument("--sample", action="store_true", help="Use built-in sample items instead of network sources.")
    parser.add_argument("--dry-run", action="store_true", help="Print report without writing files or state.")
    parser.add_argument("--no-notify", action="store_true", help="Disable notification adapters for this run.")
    return parser


def resolve_report_date(value: str | None, timezone_name: str) -> date:
    if value:
        return date.fromisoformat(value)
    return datetime.now(ZoneInfo(timezone_name)).date()


def sample_batch() -> FetchBatch:
    return FetchBatch(
        items=[
            Item(
                id="arxiv:2601.00001",
                kind="paper",
                title="Coordinated Large and Small Language Models for Tool-Using Agents",
                url="https://arxiv.org/abs/2601.00001",
                source="arXiv",
                published="2026-06-03T08:00:00Z",
                authors=["A. Researcher", "B. Scientist"],
                summary=(
                    "This paper studies a routing framework where a small language model handles "
                    "routine agent steps and escalates difficult tool-use decisions to a larger model."
                ),
                extra={"categories": "cs.AI, cs.CL", "pdf": "https://arxiv.org/pdf/2601.00001"},
            ),
            Item(
                id="arxiv:2601.00002",
                kind="paper",
                title="Memory-Augmented Multi-Agent Planning with Compact Expert Models",
                url="https://arxiv.org/abs/2601.00002",
                source="arXiv",
                published="2026-06-02T08:00:00Z",
                authors=["C. Engineer"],
                summary=(
                    "The work proposes a multi-agent planning system that combines compact expert "
                    "models, shared memory, and a larger verifier for long-horizon reasoning."
                ),
                extra={"categories": "cs.MA, cs.LG", "pdf": "https://arxiv.org/pdf/2601.00002"},
            ),
            Item(
                id="news:sample-frontier-model",
                kind="news",
                title="Example AI Lab announces a new agentic foundation model",
                url="https://example.com/frontier-model",
                source="Example AI Lab",
                published="Wed, 03 Jun 2026 08:00:00 GMT",
                summary=(
                    "The lab says the model improves tool use, computer control, and long-context "
                    "reasoning for enterprise agent workflows."
                ),
            ),
        ]
    )
