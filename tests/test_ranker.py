import unittest

from daily_research_report.models import Item
from daily_research_report.ranker import score_item


class RankerTests(unittest.TestCase):
    def test_scores_relevant_agent_model_collaboration_item(self) -> None:
        item = Item(
            id="arxiv:1",
            kind="paper",
            title="Large and Small Language Model Collaboration for Multi-Agent Tool Use",
            url="https://example.com",
            source="arXiv",
            published="2026-06-03T00:00:00Z",
            summary="A router coordinates agent planning and tool use.",
        )
        topics = [
            {"weight": 5, "terms": ["small language model", "model collaboration"]},
            {"weight": 5, "terms": ["multi-agent", "tool use", "agent"]},
        ]

        score, terms = score_item(item, topics)

        self.assertGreaterEqual(score, 20)
        self.assertIn("tool use", terms)
        self.assertIn("small language model", terms)


if __name__ == "__main__":
    unittest.main()
