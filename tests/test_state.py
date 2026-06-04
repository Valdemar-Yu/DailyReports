from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from daily_research_report.models import Item
from daily_research_report.state import SeenState


class SeenStateTests(unittest.TestCase):
    def test_same_day_is_idempotent_and_limit_blocks_third_push(self) -> None:
        with TemporaryDirectory() as tmpdir:
            state = SeenState.load(Path(tmpdir) / "seen.json")
            item = Item(id="arxiv:1", kind="paper", title="A", url="https://example.com", source="arXiv")

            state.mark_pushed(item, "2026-06-04")
            state.mark_pushed(item, "2026-06-04")
            self.assertEqual(state.push_count("arxiv:1"), 1)
            self.assertTrue(state.can_push("arxiv:1", 2))

            state.mark_pushed(item, "2026-06-05")
            self.assertEqual(state.push_count("arxiv:1"), 2)
            self.assertFalse(state.can_push("arxiv:1", 2))


if __name__ == "__main__":
    unittest.main()
