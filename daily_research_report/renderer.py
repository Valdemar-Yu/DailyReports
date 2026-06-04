from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from .models import Item
from .utils import first_sentences, format_date


def render_report(
    report_date: date,
    papers: list[Item],
    news: list[Item],
    config: dict[str, Any],
    warnings: list[str] | None = None,
) -> str:
    report_config = config.get("report", {})
    timezone_name = report_config.get("timezone", "Asia/Shanghai")
    title = report_config.get("title", "大小模型协同与 Agent 前沿日报")
    topic_names = [topic.get("name", "") for topic in config.get("topics", []) if topic.get("name")]

    lines: list[str] = [
        f"# {title} - {report_date.isoformat()}",
        "",
        f"- 研究画像：{', '.join(topic_names)}",
        f"- 去重策略：同一论文最多推送 {report_config.get('max_paper_repeats', 2)} 次；同日重复运行不重复计数。",
        f"- 生成时间基准：{timezone_name}",
        "",
        "## 今日重点论文",
        "",
    ]

    if papers:
        for index, item in enumerate(papers, start=1):
            lines.extend(_render_item(index, item, timezone_name))
    else:
        lines.append("今日没有发现达到阈值且未超过重复次数限制的论文。")
        lines.append("")

    lines.extend(["## 产业与实验室动态", ""])
    if news:
        for index, item in enumerate(news, start=1):
            lines.extend(_render_item(index, item, timezone_name))
    else:
        lines.append("今日没有发现达到阈值且未超过重复次数限制的资讯。")
        lines.append("")

    if warnings:
        lines.extend(["## 抓取告警", ""])
        for warning in warnings:
            lines.append(f"- {warning}")
        lines.append("")

    lines.extend(
        [
            "## 下一步建议",
            "",
            "- 对高相关论文做精读：优先关注方法是否涉及模型路由、大小模型协作推理、工具调用、记忆或多智能体协调。",
            "- 对产业动态做二次核验：模型发布、API 变更和 benchmark 结论建议回到官方技术报告或仓库确认。",
            "",
        ]
    )
    return "\n".join(lines)


def write_report(report_text: str, output_dir: Path, report_date: date) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"{report_date.isoformat()}.md"
    latest_path = output_dir / "latest.md"
    report_path.write_text(report_text, encoding="utf-8")
    latest_path.write_text(report_text, encoding="utf-8")
    return report_path


def _render_item(index: int, item: Item, timezone_name: str) -> list[str]:
    authors = ", ".join(item.authors[:8])
    if len(item.authors) > 8:
        authors += " 等"
    if not authors:
        authors = item.source

    matched = ", ".join(item.matched_terms[:12]) if item.matched_terms else "未记录"
    published = format_date(item.published, timezone_name)
    summary = first_sentences(item.summary)
    link = item.url or item.extra.get("pdf") or ""

    lines = [
        f"{index}. **{item.title}**",
        f"   - 来源：{item.source}；日期：{published}；相关度：{item.score}",
        f"   - 作者/机构：{authors}",
        f"   - 链接：{link}",
        f"   - 命中关键词：{matched}",
    ]
    if summary:
        lines.append(f"   - 摘要摘录：{summary}")
    if item.extra.get("pdf"):
        lines.append(f"   - PDF：{item.extra['pdf']}")
    lines.append("")
    return lines
