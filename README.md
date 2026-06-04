# 大小模型协同与 Agent 前沿日报

这是一个面向“大模型/小模型协同、Agent、多智能体、工具调用、推理与评测、基础模型发布动态”的每日研究报告生成器。它会抓取论文与实验室/公司资讯，按你的研究画像打分排序，并把 Markdown 日报保存到 `D:\DailyReports`。

## 功能

- 每日抓取 arXiv 分类 RSS 与 AI 实验室/公司 RSS 动态；也可手动开启 arXiv Search API 做更精准检索。
- 面向“大小模型协同 + Agent”关键词画像做相关度排序。
- 同一篇论文默认最多推送 2 次，第三次开始跳过；同一天多次运行不重复计数。
- 本地默认输出到 `D:\DailyReports\YYYY-MM-DD.md`，同时写入 `latest.md`。
- 可用 GitHub Actions 每天自动运行，并把 `reports/` 与去重状态提交回仓库。
- 可选 GitHub Issue 推送，便于把日报当成订阅流。

## 快速开始

```powershell
cd D:\DailyReports
python -m daily_research_report --sample --output-dir D:\DailyReports
```

真实抓取：

```powershell
python -m daily_research_report --config config\default_config.json --output-dir D:\DailyReports
```

安装为命令行工具：

```powershell
python -m pip install -e .
daily-research-report --config config\default_config.json --output-dir D:\DailyReports
```

## 配置

主要配置在 `config/default_config.json`：

- `report.output_dir`：本地报告目录，默认 `D:\DailyReports`。
- `report.max_paper_repeats`：同一论文最多进入日报的次数，默认 `2`。
- `topics`：你的研究兴趣画像及权重。
- `arxiv.queries`：arXiv 检索主题。
- `arxiv.api_enabled`：是否启用 arXiv Search API，默认 `false`，避免本地网络下的超时和 429。
- `arxiv.rss_fallback`：默认论文源，按 arXiv 分类 RSS 抓取后再用关键词画像筛选。
- `news.feeds`：OpenAI、Google Research、DeepMind、Meta AI、Microsoft Research、NVIDIA 等资讯源；Anthropic、Mistral、Qwen、DeepSeek、Kimi 等可在确认 RSS 后自行追加。
- `ranking.min_score`：论文/资讯进入日报的最低相关度。

## GitHub Actions

仓库内置 `.github/workflows/daily-report.yml`，每天 00:00 UTC 运行一次，也就是北京时间 08:00。GitHub Actions 环境没有 `D:` 盘，所以工作流会把报告写到仓库内的 `reports/`，并提交报告与 `reports/state/seen.json` 去重状态。

如需把日报发成 GitHub Issue，把 `config/default_config.json` 中的配置改为：

```json
"notifications": {
  "github_issue": {
    "enabled": true,
    "repository": "你的用户名/你的仓库名",
    "labels": ["daily-report", "research"]
  }
}
```

## Windows 本地定时

可以用任务计划程序每天本地生成到 `D:\DailyReports`：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\Register-DailyReportTask.ps1 -At 08:30
```

## 开发与测试

```powershell
python -m unittest discover -s tests
python -m daily_research_report --sample --dry-run --date 2026-06-04
```

## 开源发布到 GitHub

如果你已经在 GitHub 上创建了空仓库：

```powershell
git branch -M main
git remote add origin https://github.com/<your-name>/<repo-name>.git
git add .
git commit -m "feat: initial daily research reporter"
git push -u origin main
```

如果你安装了 GitHub CLI，也可以直接创建公开仓库：

```powershell
gh repo create <repo-name> --public --source . --remote origin --push
```

## 数据源说明

- 论文抓取使用 arXiv API：<https://arxiv.org/help/api/user-manual>
- 定时任务使用 GitHub Actions schedule：<https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions#onschedule>

RSS 源偶尔会改版或失效，脚本会跳过失败源并在日报的“抓取告警”中记录。你可以在 `news.feeds` 中继续增加公司博客、模型发布页、团队新闻或 Google News RSS。
