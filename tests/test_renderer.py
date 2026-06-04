from datetime import date
import unittest

from daily_research_report.models import Item
from daily_research_report.renderer import render_report


class RendererTests(unittest.TestCase):
    def test_renders_chinese_sections(self) -> None:
        config = {
            "report": {"title": "测试日报", "timezone": "Asia/Shanghai", "max_paper_repeats": 2},
            "topics": [{"name": "Agent"}],
        }
        item = Item(
            id="arxiv:1",
            kind="paper",
            title="Agent Paper",
            url="https://example.com",
            source="arXiv",
            published="2026-06-03T00:00:00Z",
            score=12,
            matched_terms=["agent"],
        )

        rendered = render_report(date(2026, 6, 4), [item], [], config)

        self.assertIn("# 测试日报 - 2026-06-04", rendered)
        self.assertIn("## 今日重点论文", rendered)
        self.assertIn("Agent Paper", rendered)


if __name__ == "__main__":
    unittest.main()
