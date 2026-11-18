"""Tests for check_paper.py.   python3 -m unittest discover -s tests"""
from __future__ import annotations

import io
import json
import re
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "plugins" / "chizen" / "skills" / "review" / "scripts"))
import check_paper  # noqa: E402

FIXTURES = REPO / "tests" / "fixtures"


def run(*args) -> tuple[int, str]:
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = check_paper.main([str(a) for a in args])
    return code, buf.getvalue()


def findings(paper: Path) -> list[str]:
    code, out = run(paper, "--json", "--baseline", paper / "no-such-baseline.txt")
    return [f"{f['severity']} {f['code']} {f['file']}:{f['line']}" for f in json.loads(out)["findings"]]


class Fixtures(unittest.TestCase):
    def test_good_paper_is_clean(self):
        self.assertEqual(findings(FIXTURES / "good-paper"), [])
        code, _ = run(FIXTURES / "good-paper")
        self.assertEqual(code, 0)

    def test_bad_paper_matches_expected(self):
        expected = [ln for ln in (FIXTURES / "bad-paper" / "expected.txt").read_text().splitlines()
                    if ln and not ln.startswith("#")]
        self.assertEqual(findings(FIXTURES / "bad-paper"), expected)

    def test_comments_are_ignored(self):
        # paper.tex line 8 has "TODO" and "p = 0.05" in a comment
        self.assertFalse([f for f in findings(FIXTURES / "bad-paper") if f.endswith("paper.tex:8")])


class Baseline(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        shutil.copytree(FIXTURES / "bad-paper", self.dir / "p")
        self.paper = self.dir / "p"

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_findings_fail_without_baseline(self):
        code, out = run(self.paper)
        self.assertEqual(code, 1)
        self.assertIn("New findings", out)

    def test_written_baseline_passes_and_excludes_style(self):
        run(self.paper, "--write-baseline")
        text = (self.paper / check_paper.BASELINE_NAME).read_text()
        self.assertNotIn("S-avoid", text)
        self.assertNotRegex(text, r":\d+")  # no line numbers in identifiers
        code, _ = run(self.paper)
        self.assertEqual(code, 0)

    def test_baseline_survives_edits_elsewhere(self):
        run(self.paper, "--write-baseline")
        p = self.paper / "paper.tex"
        p.write_text(p.read_text().replace("\\section{Results}", "\\section{Results}\n\nA new paragraph.\n"))
        code, _ = run(self.paper)
        self.assertEqual(code, 0)

    def test_new_finding_fails(self):
        run(self.paper, "--write-baseline")
        p = self.paper / "paper.tex"
        p.write_text(p.read_text().replace("See \\autoref", "Also $p = 0.20$. See \\autoref"))
        code, out = run(self.paper)
        self.assertEqual(code, 1)
        self.assertIn("E-p-zero", out)

    def test_fixed_finding_is_stale_until_pruned(self):
        run(self.paper, "--write-baseline")
        p = self.paper / "paper.tex"
        p.write_text(p.read_text().replace("\\newpage\n", ""))
        code, out = run(self.paper)
        self.assertEqual(code, 1)
        self.assertIn("Fixed findings", out)
        run(self.paper, "--prune-baseline")
        code, _ = run(self.paper)
        self.assertEqual(code, 0)


class Units(unittest.TestCase):
    def test_strip_comment_keeps_escaped_percent(self):
        self.assertEqual(check_paper.strip_comment(r"50\% of them % a comment"), r"50\% of them ")

    def test_p_values(self):
        found = []
        line = check_paper.Line("x.tex", 1, "", "")

        def add(sev, code, ln, msg):
            found.append(code)
        for text, codes in [("$p = .03$", []), ("$p < .001$", []), ("$p=0.03$", ["E-p-zero"]),
                            ("p < .0005", ["E-p-threshold"]), ("$p = .0004$", ["E-p-threshold"]),
                            ("$p = .034$", ["W-p-precision"]), (r"\p{.0001}", []),
                            (r"$\mathit{p} = 0.5$", ["E-p-zero"])]:
            found.clear()
            check_paper.check_stats(text, line, add)
            self.assertEqual(found, codes, text)

    def test_tabular_specs(self):
        found = []
        line = check_paper.Line("x.tex", 1, "", "")
        for text, n in [(r"\begin{tabular}{@{}lrr@{}}", 0), (r"\begin{tabular}{|l|r|}", 1),
                        (r"\begin{tabularx}{\linewidth}{lX}", 0), (r"\begin{tabular}[t]{l|r}", 1),
                        (r"\begin{tabular}{p{6cm} p{4cm}}", 0)]:
            found.clear()
            check_paper.check_tabular(text, line, lambda *a: found.append(a[1]))
            self.assertEqual(len(found), n, text)


class PaletteInStep(unittest.TestCase):
    def test_palette_matches_figures_tex(self):
        tex = (REPO / "CHIZen" / "figures.tex").read_text(encoding="utf-8")
        defined = {m.group(1) for m in re.finditer(r"^\s*\\definecolor\{([^}]+)\}", tex, re.M)}
        self.assertEqual(defined, check_paper.PALETTE_COLOURS)


if __name__ == "__main__":
    unittest.main()
