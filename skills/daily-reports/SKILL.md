---
name: daily-reports
description: Generate, inspect, troubleshoot, customize, schedule, and sync the DailyReports AI research daily report project. Use when the user asks to generate today's DailyReports report, view the latest report, adjust research keywords or RSS/arXiv sources, manage duplicate paper limits, update local/GitHub automation, or push the DailyReports repository to GitHub.
---

# DailyReports

## Core Context

Use the DailyReports project at `D:\DailyReports`.

The project generates a Markdown daily report about large/small model collaboration, agents, frontier papers, and AI lab/company news. Reports and deduplication state are written under the same directory:

- Report files: `D:\DailyReports\YYYY-MM-DD.md`
- Latest report: `D:\DailyReports\latest.md`
- Deduplication state: `D:\DailyReports\state\seen.json`
- Config: `D:\DailyReports\config\default_config.json`

For details about files, commands, and GitHub sync, read `references/project.md` only when needed.

## Generate A Report

Prefer the bundled script:

```powershell
powershell -ExecutionPolicy Bypass -File D:\DailyReports\skills\daily-reports\scripts\run_daily_report.ps1
```

Useful options:

```powershell
powershell -ExecutionPolicy Bypass -File D:\DailyReports\skills\daily-reports\scripts\run_daily_report.ps1 -Date 2026-06-04
powershell -ExecutionPolicy Bypass -File D:\DailyReports\skills\daily-reports\scripts\run_daily_report.ps1 -DryRun
powershell -ExecutionPolicy Bypass -File D:\DailyReports\skills\daily-reports\scripts\run_daily_report.ps1 -Sample
```

When running inside Codex, request elevated permission if writing to `D:\DailyReports` or accessing the network requires it.

After generation, inspect `D:\DailyReports\latest.md` or the date-specific report and summarize the important papers/news for the user.

## Customize The Research Profile

Edit `config/default_config.json` for:

- `topics`: research interest terms and weights.
- `ranking.min_score`: filtering threshold for papers/news.
- `arxiv.rss_fallback.categories`: arXiv categories.
- `news.feeds`: company/lab RSS feeds.
- `report.max_paper_repeats`: same-paper push limit, default `2`.

Run tests after config or code changes:

```powershell
python -m unittest discover -s tests
```

## GitHub And Automation

The repository remote is expected to be `https://github.com/Valdemar-Yu/DailyReports.git`.

Before pushing changes:

1. Run `python -m unittest discover -s tests`.
2. Check `git status --short --branch`.
3. Commit source/config/skill changes, but do not commit generated local report files (`latest.md`, date reports, `state/`).
4. Push `main` to `origin`.

For local Windows scheduling, use:

```powershell
powershell -ExecutionPolicy Bypass -File D:\DailyReports\scripts\Register-DailyReportTask.ps1 -At 08:30
```
