# 端云协同 Omni · Agent 记忆与自进化 前沿日报

这是一个每日研究情报生成器。它面向下面几个方向抓取论文与产业资讯，按研究画像打分排序，产出 Markdown 日报：

- 端云协同（edge-cloud）的 omni 基础模型，偏向视频，兼顾语音
- 实时全双工交互（full-duplex / turn-taking / barge-in / 打断转交）
- Agent 记忆：对话记忆 / 工作记忆 / 长期记忆
- Agent 自进化（self-evolving / self-improving / continual learning）

它有两种用法：

- **Agent 技能**（`skills/daily-reports/`）：由 agent 读画像、检索、去重并撰写中文日报，适合交互式、带解读的推送。
- **Python 自动生成器**（`daily_research_report/`）：抓取 arXiv RSS/API 与实验室 RSS，按 `config/default_config.json` 打分，适合无人值守跑批或生成候选列表。

## 研究画像

- 画像文件：`config/research-profile.md`（唯一事实源；方向变了改这里）。
- 关键词与来源图谱：`skills/daily-reports/references/source-map.md`。
- Python 自动路径的画像与阈值：`config/default_config.json` 的 `topics` / `ranking.min_score` / `arxiv.categories`。

## 快速开始（macOS / Linux）

```bash
# 示例数据（不联网）
python3 -m daily_research_report --sample

# 真实抓取（默认输出到 ~/DailyReports）
python3 -m daily_research_report --config config/default_config.json

# 或用封装脚本
scripts/run_daily_report.sh
scripts/run_daily_report.sh --dry-run
```

Windows（PowerShell）：

```powershell
python -m daily_research_report --config config\default_config.json
```

安装为命令行工具：

```bash
python3 -m pip install -e .
daily-research-report --config config/default_config.json
```

## 输出与去重

- 报告默认写到 `~/DailyReports/`（可用环境变量 `DAILY_REPORT_OUTPUT_DIR` 覆盖，或改 `config/default_config.json` 的 `report.output_dir`）。
- Python 路径产出 `YYYY-MM-DD.md` 与 `latest.md`；agent 技能产出 `YYYY-MM-DD-daily-report.md` 与 `YYYY-MM-DD-papers.json`。
- 同一篇论文默认最多推送 2 次；agent 技能的去重计数由 `skills/daily-reports/scripts/paper_history.py` 维护（默认 `~/DailyReports/paper-history.json`，可用 `DAILY_REPORT_HISTORY` 覆盖）。

## 配置要点（`config/default_config.json`）

- `topics`：研究兴趣画像与权重（视频、记忆、自进化为最高权重）。
- `arxiv.categories` / `rss_fallback.categories`：arXiv 分类，已含 cs.CV / cs.MM / cs.MA / eess.AS / cs.SD。
- `arxiv.api_enabled`：是否启用 arXiv Search API，默认 `false`（用 RSS 兜底更稳，避免超时和 429）。
- `news.feeds`：实验室 / 公司 RSS，可自行增删。
- `ranking.min_score`：论文 / 资讯进入日报的最低相关度。

## 定时任务

- **GitHub Actions**：内置 `.github/workflows/daily-report.yml`，每天 00:00 UTC（北京时间 08:00）运行，把报告写到仓库 `reports/` 并提交。
- **macOS / Linux**：用 `cron` 或 `launchd` 每天调用 `scripts/run_daily_report.sh`，例如 crontab：`30 8 * * * /path/to/repo/scripts/run_daily_report.sh`。
- **Windows**：`scripts/Register-DailyReportTask.ps1` 注册任务计划程序。

如需把日报发成 GitHub Issue，在 `config/default_config.json` 打开：

```json
"notifications": {
  "github_issue": {
    "enabled": true,
    "repository": "你的用户名/你的仓库名",
    "labels": ["daily-report", "research"]
  }
}
```

## 开发与测试

```bash
python3 -m unittest discover -s tests
python3 -m daily_research_report --sample --dry-run --date 2026-06-04
```

## 数据源说明

- 论文抓取使用 arXiv API：<https://arxiv.org/help/api/user-manual>
- 定时任务使用 GitHub Actions schedule：<https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions#onschedule>

RSS 源偶尔会改版或失效，脚本会跳过失败源并在日报的“抓取告警”中记录。你可以在 `news.feeds` 中继续增加公司博客、模型发布页、团队新闻或 Google News RSS。

## License

本项目使用 [MIT License](./LICENSE)。
