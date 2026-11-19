"""Tests for warning_ratchet.py.   python3 -m unittest discover -s tests"""
from __future__ import annotations

import io
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "plugins" / "chizen" / "skills" / "review" / "scripts"))
import warning_ratchet  # noqa: E402

LOG = """\
This is LuaHBTeX, Version 1.24.0 (TeX Live 2026)
(./paper.tex
LaTeX Font Info:    Trying to load font information for TU+inconsolata on input line 12.

Package natbib Warning: Citation `smith2020' on page 3 undefined on input line 4
2.

LaTeX Warning: Reference `fig:x' on page 3 undefined on input line 57.

Class acmart Warning: \\vspace should only be used to provide space above/below
(acmart)              surrounding objects on input line 88.

Overfull \\hbox (12.5pt too wide) in paragraph at lines 90--91
[]\\TU/LinLibertine(0)/m/n/9 Some long words that do not fit in the col-umn width
 []

Underfull \\hbox (badness 10000) in paragraph at lines 95--95
 []

Missing character: There is no ^^A in font nullfont!
LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right.
)
"""

BLG = """\
This is BibTeX, Version 0.99e
Database file #1: refs.bib
Warning--empty journal in smith2020
(There was 1 warning)
"""

FIGURE_LOG = """\
This is LuaHBTeX, Version 1.24.0 (TeX Live 2026)
LaTeX Warning: Reference `fig:example' on page 1 undefined on input line 166.

\\openout7 = figures/tikz/fig-a.dpth

LaTeX Warning: Reference `tab:inside' on page 1 undefined on input line 170.

[1.1
LaTeX Warning: There were undefined references.
"""

# The same, with the markers CHIZen/externalize.tex writes (no .dpth line).
FIGURE_LOG_MARKED = """\
LaTeX Warning: Reference `fig:example' on page 1 undefined on input line 166.

CHIZen figure: fig-other
CHIZen figure end: fig-other
CHIZen figure: fig-a

LaTeX Warning: Reference `tab:inside' on page 1 undefined on input line 170.

[1.1
CHIZen figure end: fig-a
LaTeX Warning: There were undefined references.
"""


def run(*args) -> tuple[int, str]:
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = warning_ratchet.main([str(a) for a in args])
    return code, buf.getvalue()


class Ratchet(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        (self.dir / "paper.log").write_text(LOG)
        (self.dir / "paper.blg").write_text(BLG)
        self.baseline = self.dir / warning_ratchet.BASELINE_NAME

    def tearDown(self):
        shutil.rmtree(self.dir)

    def show(self, *docs) -> list[str]:
        code, out = run("--dir", self.dir, "--show", *(docs or ["paper"]))
        self.assertEqual(code, 0)
        return out.splitlines()

    def test_collects_and_normalises(self):
        self.assertEqual(self.show(), [
            "paper.blg: Warning--empty journal in smith2020",
            "paper.log: Class acmart Warning: \\vspace should only be used to provide space "
            "above/below surrounding objects",
            "paper.log: LaTeX Warning: Reference `fig:x' undefined",
            "paper.log: Missing character: There is no ^^A in font nullfont!",
            'paper.log: Overfull \\hbox in paragraph: "Some long words that do not fit in the '
            'column width"',
            "paper.log: Package natbib Warning: Citation `smith2020' undefined",
        ])

    def test_label_prefixes_lines(self):
        code, out = run("--dir", self.dir, "--show", "--label", "pdflatex", "paper")
        self.assertTrue(all(ln.startswith("pdflatex paper.") for ln in out.splitlines()))

    def test_new_warnings_fail_and_baselined_pass(self):
        code, out = run("--dir", self.dir, "paper")
        self.assertEqual(code, 1)
        self.assertIn("New warnings", out)
        self.assertIn("1 × Underfull box", out)
        self.baseline.write_text("\n".join(self.show()) + "\n")
        code, out = run("--dir", self.dir, "paper")
        self.assertEqual(code, 0, out)

    def test_stale_baseline_fails_until_pruned(self):
        self.baseline.write_text("\n".join(self.show()) + "\npaper.log: LaTeX Warning: fixed\n")
        code, out = run("--dir", self.dir, "paper")
        self.assertEqual(code, 1)
        self.assertIn("Fixed warnings still listed", out)
        run("--dir", self.dir, "--prune-baseline", "paper")
        self.assertNotIn("fixed", self.baseline.read_text())
        code, _ = run("--dir", self.dir, "paper")
        self.assertEqual(code, 0)

    def test_other_logs_baseline_lines_are_left_alone(self):
        self.baseline.write_text("\n".join(self.show()) + "\nother.log: LaTeX Warning: x\n")
        code, _ = run("--dir", self.dir, "paper")
        self.assertEqual(code, 0)

    def test_missing_log_is_an_error(self):
        code, out = run("--dir", self.dir, "nosuch")
        self.assertEqual(code, 1)
        self.assertIn("not found", out)

    def test_latex_error_fails(self):
        (self.dir / "paper.log").write_text(LOG + "! Undefined control sequence.\n")
        self.baseline.write_text("\n".join(self.show()) + "\n")
        code, out = run("--dir", self.dir, "paper")
        self.assertEqual(code, 1)
        self.assertIn("Undefined control sequence", out)

    def test_tikz_external_log(self):
        (self.dir / "figures" / "tikz").mkdir(parents=True)
        (self.dir / "figures" / "tikz" / "fig-a.log").write_text(FIGURE_LOG)
        # Only the reference made inside the picture counts.
        self.assertEqual(self.show("figures/tikz/*"),
                         ["figures/tikz/fig-a.log: LaTeX Warning: Reference `tab:inside' undefined"])

    def test_tikz_external_log_with_chizen_markers(self):
        (self.dir / "figures" / "tikz").mkdir(parents=True)
        (self.dir / "figures" / "tikz" / "fig-a.log").write_text(FIGURE_LOG_MARKED)
        self.assertEqual(self.show("figures/tikz/*"),
                         ["figures/tikz/fig-a.log: LaTeX Warning: Reference `tab:inside' undefined"])

    def test_hyperxmp_is_allowlisted(self):
        line = ("Package pdfmanagement Warning: The loading of package hyperxmp is disabled. "
                "It is not compatible with the PDF management.")
        self.assertTrue(warning_ratchet.allowlisted("x.log: " + line))
        self.assertFalse(warning_ratchet.allowlisted("x.log: Package pdfmanagement Warning: other"))

    def test_allowlist(self):
        saved = list(warning_ratchet.ALLOWLIST)
        try:
            warning_ratchet.ALLOWLIST[:] = [(r"^Class acmart Warning: \\vspace", "test")]
            self.baseline.write_text("\n".join(w for w in self.show() if "vspace" not in w) + "\n")
            code, out = run("--dir", self.dir, "paper")
            self.assertEqual(code, 0, out)
            self.assertIn("Allowlisted", out)
        finally:
            warning_ratchet.ALLOWLIST[:] = saved


if __name__ == "__main__":
    unittest.main()
