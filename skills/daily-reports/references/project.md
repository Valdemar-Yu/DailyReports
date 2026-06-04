# DailyReports Project Reference

## Project Paths

- Project root: `D:\DailyReports`
- Python package: `D:\DailyReports\daily_research_report`
- Main config: `D:\DailyReports\config\default_config.json`
- GitHub workflow: `D:\DailyReports\.github\workflows\daily-report.yml`
- Windows scheduler helper: `D:\DailyReports\scripts\Register-DailyReportTask.ps1`
- Skill folder: `D:\DailyReports\skills\daily-reports`

## Common Commands

Generate today's real report:

```powershell
python -m daily_research_report --config config\default_config.json --output-dir D:\DailyReports
```

Dry run without writing files:

```powershell
python -m daily_research_report --config config\default_config.json --output-dir D:\DailyReports --dry-run
```

Generate sample data:

```powershell
python -m daily_research_report --sample --output-dir D:\DailyReports
```

Run tests:

```powershell
python -m unittest discover -s tests
```

## Important Behavior

- Same paper/news item defaults to at most 2 pushes.
- Same-day repeated runs do not increment push count again.
- Local generated files are ignored by git: `latest.md`, `????-??-??.md`, `state/`.
- GitHub Actions writes reports into repository `reports/`, not `D:\DailyReports`.
- arXiv Search API is disabled by default; arXiv RSS fallback is the stable default source.

## GitHub Sync

Remote:

```text
https://github.com/Valdemar-Yu/DailyReports.git
```

Preferred update flow:

```powershell
git status --short --branch
python -m unittest discover -s tests
git add <changed-source-files>
git commit -m "<message>"
git push
```
