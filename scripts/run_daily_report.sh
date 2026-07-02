#!/usr/bin/env bash
# Generate a daily research report on macOS/Linux.
#
# Usage:
#   scripts/run_daily_report.sh                 # real fetch, today
#   scripts/run_daily_report.sh --date 2026-06-04
#   scripts/run_daily_report.sh --dry-run       # print, do not write files/state
#   scripts/run_daily_report.sh --sample        # built-in sample items, no network
#
# Output goes to $DAILY_REPORT_OUTPUT_DIR (default ~/DailyReports), configurable
# in config/default_config.json.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python3 -m daily_research_report --config config/default_config.json "$@"
