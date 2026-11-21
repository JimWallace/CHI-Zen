"""Tests for plugins/chizen/scripts/copy_into_paper.py.   python3 -m unittest discover -s tests"""
from __future__ import annotations

import io
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "plugins" / "chizen" / "scripts"))
import copy_into_paper  # noqa: E402


def run(*args) -> int:
    with redirect_stdout(io.StringIO()):
        return copy_into_paper.main([str(a) for a in args])


class CopyIntoPaper(unittest.TestCase):
    def setUp(self):
        self.paper = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.paper)

    def test_copy_then_check_is_current(self):
        self.assertEqual(run(self.paper, "--check"), 1)
        self.assertEqual(run(self.paper), 0)
        self.assertEqual(run(self.paper, "--check"), 0)
        c = self.paper / ".claude"
        self.assertTrue((c / "skills" / "chizen" / "references" / "figures.md").is_file())
        self.assertTrue((c / "skills" / "chizen-review" / "scripts" / "check_paper.py").is_file())
        self.assertTrue((c / "skills" / "chizen-related-work" / "scripts" / "find_papers.py").is_file())
        for name in ("figures", "statistics", "writing", "references"):
            self.assertTrue((c / "agents" / f"chizen-{name}.md").is_file())
        taps = c / "skills" / "chizen-review" / "scripts" / "data" / "taps-accepted-packages.txt"
        self.assertTrue(taps.is_file() and not taps.is_symlink(), "the TAPS list is copied, not linked")

    def test_other_files_untouched_and_stale_detected(self):
        (self.paper / ".claude" / "agents").mkdir(parents=True)
        mine = self.paper / ".claude" / "agents" / "my-agent.md"
        mine.write_text("mine")
        run(self.paper)
        self.assertEqual(mine.read_text(), "mine")
        (self.paper / ".claude" / "skills" / "chizen" / "SKILL.md").write_text("edited")
        self.assertEqual(run(self.paper, "--check"), 1)


if __name__ == "__main__":
    unittest.main()
