#!/usr/bin/env python3
"""check_paper.py: deterministic checks on a LaTeX paper, after the CHI Zen guide.

    python3 check_paper.py PAPER_DIR                 # human-readable report
    python3 check_paper.py PAPER_DIR --json          # machine-readable, for Claude
    python3 check_paper.py PAPER_DIR --main paper.tex   # name the main file(s)
    python3 check_paper.py PAPER_DIR --prune-baseline   # drop fixed findings from the baseline
    python3 check_paper.py PAPER_DIR --write-baseline   # accept every current finding (see below)

Standard library only, so it runs anywhere Python 3.9+ does (a Claude Code
session, GitHub Actions); no TeX needed.

WHAT IT READS. Every top-level .tex file in PAPER_DIR that has an uncommented
\\documentclass (or the files given with --main), followed through \\input,
\\include and \\subfile. Files under CHIZen/ (the CHI Zen library itself, which
defines the palettes) are not checked; add more with --exclude. The ACM TAPS
package check is the exception: it covers every file TeX reads, because TAPS
receives the whole source. Its list is CHIZen/taps-accepted-packages.txt.

DRAFT AND FINAL MODE. TAPS only ever sees a paper in final mode
(\\def\\chizenmode{final}). Packages loaded only in draft mode, i.e. in the
\\else branch of \\ifchizenfinal ... \\else ... \\fi, or in a file that is only
\\input there (CHIZen/figures.tex), are not TAPS problems and are not reported.
Everything else is checked, including every package a paper loads in its own
preamble outside such a branch, and the \\ifchizenfinal branch itself.

ANONYMOUS SUBMISSIONS. With acmart's `anonymous` class option, the W-anon-* and
E-anon-ref checks (guide: TRN-5, REF-12) look for what the option doesn't hide: author and
institution names (from \\author and \\institution) in the body, first-person
self-citation, ethics and grant numbers, acknowledgments outside the acks environment, a
hand-set pdfauthor, an author in an included PDF's metadata, OSF links without view_only,
GitHub/GitLab links in a sentence that says "our", and .bib entries by "Anonymous". Text
inside \\anon{...} is hidden by acmart and not reported. One-word names, and phrases like
"our previous study" without a citation in the sentence, are left alone: they too often
refer to something else.

SEVERITIES.
  error    the PDF is wrong or breaks a venue rule (vertical rules, a p-value with
           a leading zero, a figure without a caption or \\Description, ...)
  warning  worth fixing (an unreferenced figure, TODO markers, ad-hoc colours, ...)
  style    words and phrases to avoid, from the CHI Zen checklist. Reported, never
           fails, never baselined: they are prompts to reread a sentence.

THE BASELINE. Errors and warnings fail (exit 1) unless the baseline file lists
them; a listed finding that no longer occurs also fails until its line is
deleted (--prune-baseline), so the file only shrinks. The default baseline is
PAPER_DIR/chizen-baseline.txt (a missing file means an empty baseline). Each
line identifies one occurrence without line numbers, so it survives edits
elsewhere; a line listed twice means the finding occurs twice.
--write-baseline accepts every current error and warning. Use it once, when an
author adopts the checker on an existing paper, never to make a new finding go
away.

Exit status: 0 clean (after the baseline), 1 otherwise, 2 bad usage.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

BASELINE_NAME = "chizen-baseline.txt"
DEFAULT_EXCLUDES = ("CHIZen/",)
BASELINE_HEADER = """\
# Accepted findings of check_paper.py (the CHI Zen linter) for this paper.
# CI fails on any error or warning not listed here, and on any line here that
# no longer occurs, so this file only shrinks. Fix the cause rather than adding
# a line. One line per occurrence: "<code> <file>: <message>".
"""

# Colours defined by CHIZen/figures.tex. tests/test_check_paper.py checks that
# this list matches that file, so keep the two in step.
PALETTE_COLOURS = {
    "RYB1", "RYB2", "RYB3", "RYB4", "RYB5", "RYB6", "RYB7",
    "AHSLight", "AHSDark", "ArtsLight", "ArtsDark", "EngineeringLight", "EngineeringDark",
    "EnvironmentLight", "EnvironmentDark", "MathLight", "MathDark", "ScienceLight",
    "ScienceDark", "SchoolRedLight", "SchoolRedDark",
    "OkabeItoOrange", "OkabeItoSkyBlue", "OkabeItoBluishGreen", "OkabeItoYellow",
    "OkabeItoBlue", "OkabeItoVermillion", "OkabeItoReddishPurple", "OkabeItoBlack",
    "Likert5_SD", "Likert5_D", "Likert5_N", "Likert5_A", "Likert5_SA",
    "Likert5_1_SD", "Likert5_1_D", "Likert5_1_N", "Likert5_1_A", "Likert5_1_SA",
    "Likert5_2_SD", "Likert5_2_D", "Likert5_2_N", "Likert5_2_A", "Likert5_2_SA",
    *[f"Likert7_{i}" for i in range(7)],
    *[f"Likert7_{k}_{i}" for k in (2, 3, 4) for i in range(7)],
    *[f"Cleric_{i}" for i in range(7)], *[f"Monster_{i}" for i in range(7)],
}
# Neutral colours are always fine (axes, text, greyscale fills).
NEUTRAL_COLOURS = {"black", "white", "gray", "grey", "darkgray", "lightgray", "none", "."}
# xcolor's base and dvipsnames-free named colours that signal an ad-hoc data colour.
XCOLOR_NAMES = {
    "red", "green", "blue", "cyan", "magenta", "yellow", "brown", "lime", "olive",
    "orange", "pink", "purple", "teal", "violet",
}

# From manual/CHIZen-Paper-Checklist.tex, "Words and Phrases to Avoid".
AVOID_WORDS = [
    "actually", "almost", "always", "anyway", "basically", "best", "believe", "can't",
    "clearly", "don't", "essentially", "feel", "folks", "good", "guy", "hassle", "I",
    "impossible", "kids", "kind of", "like", "lots", "many", "never", "nice", "obviously",
    "OK", "of course", "pretty good", "prove", "proven", "quite", "really", "so", "stuff",
    "thing", "totally", "user", "utilize", "various", "very", "well", "won't", "wouldn't",
    "you",
]
CASE_SENSITIVE_WORDS = {"I", "OK"}

# The TAPS list lives in CHIZen/taps-accepted-packages.txt. A paper made from the CHI Zen
# template has its own copy (preferred: it matches what the paper compiles with); the
# plugin's data/ entry is a symlink to the CHI Zen repository's copy, which Claude Code
# dereferences when it installs the plugin.
TAPS_NAME = "taps-accepted-packages.txt"
TAPS_FILE = Path(__file__).parent / "data" / TAPS_NAME


def load_taps(path: Path | None = None, paper: Path | None = None) -> tuple[set, set] | None:
    """(accepted, included in acmart) from the TAPS list, or None if no list is found."""
    if path is None:
        cands = ([paper / "CHIZen" / TAPS_NAME] if paper else []) + [TAPS_FILE]
        path = next((c for c in cands if c.is_file()), None)
    if path is None or not path.is_file():
        return None
    lists: dict[str, set] = {}
    current = None
    for ln in path.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        if ln.startswith("[") and ln.endswith("]"):
            current = lists.setdefault(ln[1:-1], set())
        elif current is not None:
            current.add(ln)
    return lists.get("accepted", set()), lists.get("included-in-acmart", set())


FLOAT_ENVS = ("figure", "figure*", "table", "table*", "wrapfigure", "wraptable")
FIGURE_ENVS = ("figure", "figure*", "wrapfigure")
SKIP_ENVS = ("verbatim", "verbatim*", "minted", "lstlisting", "comment", "Verbatim")
CODE_ENVS = ("tikzpicture", "axis", "groupplot", "ganttchart", "tabular", "tabular*",
             "tabularx", "longtable", "CCSXML", "acronym", "equation", "equation*",
             "align", "align*", "displaymath", "math")
PICTURE_RE = re.compile(r"\\begin\{(tikzpicture|ganttchart)\}|\\include(graphics|svg)\b")
REF_RE = re.compile(r"\\(?:ref|autoref|Autoref|cref|Cref|vref|pageref|subref|nameref|cpageref|Cpageref)\*?\{([^}]*)\}")
PICTURE_ENV_RE = re.compile(r"\\begin\{(tikzpicture|ganttchart)\}.*?\\end\{\1\}", re.S)
LABEL_RE = re.compile(r"\\label\{([^}]*)\}")
INPUT_RE = re.compile(r"\\(?:input|include|subfile)\{([^}]+)\}")


@dataclass
class Line:
    file: str   # path relative to the paper directory
    num: int    # 1-based line number in that file
    text: str   # the line with comments removed
    raw: str    # the original line
    # Mode of each part of the line: (start column, None | "draft" | "final"),
    # from \ifchizenfinal ... \else ... \fi (None: both modes).
    modes: list = field(default_factory=lambda: [(0, None)])

    def mode_at(self, col: int):
        mode = None
        for start, m in self.modes:
            if start > col:
                break
            mode = m
        return mode


@dataclass
class Finding:
    severity: str  # error | warning | style
    code: str
    file: str
    line: int
    msg: str       # no line numbers: it identifies the finding in the baseline

    def ident(self) -> str:
        return f"{self.code} {self.file}: {self.msg}"


@dataclass
class Doc:
    main: str
    lines: list = field(default_factory=list)


# ------------------------------------------------------------------ reading

def strip_comment(s: str) -> str:
    """Remove a TeX comment: the first % not preceded by a backslash."""
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            out.append(s[i:i + 2])
            i += 2
            continue
        if c == "%":
            break
        out.append(c)
        i += 1
    return "".join(out)


def resolve(root: Path, name: str) -> Path | None:
    name = name.strip()
    for cand in (name, name + ".tex"):
        p = (root / cand)
        if p.is_file():
            return p
    return None


def rel(root: Path, p: Path) -> str:
    try:
        return p.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return p.as_posix()


def excluded(relpath: str, excludes) -> bool:
    return any(relpath == e.rstrip("/") or relpath.startswith(e.rstrip("/") + "/") for e in excludes)


# TeX's conditionals (and iftex's), which end with \fi. Conditionals made with \newif
# are added as they are read. Others, like ifthen's \ifthenelse or etoolbox's
# \ifbool, take arguments instead and are ignored.
TEX_IFS = {
    "if", "ifcat", "ifnum", "ifdim", "ifodd", "ifvmode", "ifhmode", "ifmmode", "ifinner",
    "ifvoid", "ifhbox", "ifvbox", "ifx", "ifeof", "iftrue", "iffalse", "ifcase", "ifdefined",
    "ifcsname", "iffontchar", "ifincsname", "ifabsnum", "ifabsdim", "ifprimitive",
    "ifpdfprimitive", "ifpdfabsnum", "ifpdfabsdim", "ifLuaTeX", "ifPDFTeX", "ifXeTeX",
    "ifluatex", "ifpdftex", "ifxetex", "ifluahbtex", "ifpTeX", "ifupTeX", "ifeTeX",
}
MODE_IF = "ifchizenfinal"
COND_RE = re.compile(r"\\newif\s*\\(if[A-Za-z@]+)|\\(if[A-Za-z@]*|else|fi)(?![A-Za-z@])")


class Modes:
    """Tracks \\ifchizenfinal ... \\else ... \\fi across lines (and \\input files)."""

    def __init__(self, inherited=None, ifs=None):
        self.inherited = inherited
        self.ifs = ifs if ifs is not None else set(TEX_IFS)
        self.stack: list = []  # one entry per open conditional: None, or [branch] for \ifchizenfinal

    def current(self):
        for entry in reversed(self.stack):
            if entry is not None:
                return entry[0]
        return self.inherited

    def scan(self, text: str) -> list:
        """Update the state from one line; return its (column, mode) parts."""
        parts = [(0, self.current())]
        for m in COND_RE.finditer(text):
            if m.group(1):
                self.ifs.add(m.group(1))
                continue
            name = m.group(2)
            if name == "fi":
                if self.stack:
                    self.stack.pop()
            elif name == "else":
                if self.stack and self.stack[-1] is not None:
                    self.stack[-1][0] = "draft"
            elif name == MODE_IF:
                self.stack.append(["final"])
            elif name in self.ifs:
                self.stack.append(None)
            else:
                continue
            parts.append((m.end(), self.current()))
        return parts


def flatten(root: Path, path: Path, excludes, seen: set, out: list, mode=None, ifs=None) -> None:
    """Append the lines of `path` to `out`, expanding \\input and friends in place.
    Excluded files are expanded (they may define things) but marked as such.
    `mode` is the mode of the \\input line ("draft", "final" or None for both)."""
    key = path.resolve()
    if key in seen:
        return
    seen.add(key)
    modes = Modes(mode, ifs)
    r = rel(root, path)
    try:
        raw_lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return
    skip_env = None
    for i, raw in enumerate(raw_lines, 1):
        text = strip_comment(raw)
        if skip_env:
            if f"\\end{{{skip_env}}}" in text:
                skip_env = None
            out.append(Line(r, i, "", raw, [(0, modes.current())]))
            continue
        m = re.search(r"\\begin\{(" + "|".join(re.escape(e) for e in SKIP_ENVS) + r")\}", text)
        if m and f"\\end{{{m.group(1)}}}" not in text[m.end():]:
            skip_env = m.group(1)
            out.append(Line(r, i, text[:m.end()], raw, modes.scan(text[:m.end()])))
            continue
        text = re.sub(r"\\(?:verb|mint\{[^}]*\})(.)(.*?)\1", " ", text)
        ln = Line(r, i, text, raw, modes.scan(text))
        out.append(ln)
        for inc in INPUT_RE.finditer(text):
            p = resolve(root, inc.group(1))
            if p is not None:
                flatten(root, p, excludes, seen, out, ln.mode_at(inc.start()), modes.ifs)


def find_mains(root: Path) -> list[Path]:
    mains = []
    for p in sorted(root.glob("*.tex")):
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if any(re.match(r"\s*\\documentclass", strip_comment(ln)) for ln in txt.splitlines()):
            mains.append(p)
    return mains


# ------------------------------------------------------------------ helpers

def env_blocks(lines: list, envs) -> list[tuple[str, int, int]]:
    """(env, start index, end index) of each top-level environment in `envs`."""
    pat = re.compile(r"\\(begin|end)\{(" + "|".join(re.escape(e) for e in envs) + r")\}")
    blocks, stack = [], []
    for idx, ln in enumerate(lines):
        for m in pat.finditer(ln.text):
            if m.group(1) == "begin":
                stack.append((m.group(2), idx))
            elif stack:
                env, start = stack.pop()
                if not stack:
                    blocks.append((env, start, idx))
    return blocks


def balanced_arg(s: str, start: int) -> tuple[str, int] | None:
    """The {...} argument starting at s[start] == '{'; returns (content, end index)."""
    if start >= len(s) or s[start] != "{":
        return None
    depth = 0
    for j in range(start, len(s)):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return s[start + 1:j], j + 1
    return None


def short(s: str, n: int = 60) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def body_range(lines: list) -> tuple[int, int]:
    """Indices of the document body (between \\begin{document} and \\end{document})."""
    start, end = 0, len(lines)
    for i, ln in enumerate(lines):
        if "\\begin{document}" in ln.text:
            start = i
            break
    for i in range(len(lines) - 1, -1, -1):
        if "\\end{document}" in lines[i].text:
            end = i
            break
    return start, end


# ------------------------------------------------------------------ checks

def check_doc(doc: Doc, root: Path, excludes, add) -> None:
    lines = doc.lines
    checked = [not excluded(ln.file, excludes) for ln in lines]
    b0, b1 = body_range(lines)

    def lint(i):  # a line we report on
        return checked[i]

    # Whole-document text for label references (excluded files count as references too).
    refs = set()
    for ln in lines:
        for group in REF_RE.findall(ln.text):
            refs.update(x.strip() for x in group.split(","))

    # --- floats: caption, label, reference, \Description
    for env, s, e in env_blocks(lines, FLOAT_ENVS):
        if not lint(s):
            continue
        body = "\n".join(ln.text for ln in lines[s:e + 1])
        where = lines[s]
        # pgfplots also uses \label (for plot legends): ignore labels inside pictures.
        outside = PICTURE_ENV_RE.sub(" ", body)
        labels = LABEL_RE.findall(outside)
        kind = "figure" if env in FIGURE_ENVS else "table"
        cap = re.search(r"\\caption(of)?\b", outside)
        captext = balanced_arg(outside, outside.find("{", cap.end())) if cap else None
        ident = (labels[0] if labels else
                 short(re.sub(r"\\[A-Za-z]+\*?|[{}]", "", captext[0]), 40) if captext else
                 "with no caption or label")
        if not cap:
            add("error", "E-float-caption", where, f"{kind} '{ident}' has no \\caption")
        if not labels:
            add("warning", "W-float-label", where,
                f"{kind} '{ident}' has no \\label, so the text cannot refer to it")
        else:
            first_label = outside.find("\\label{")
            if cap and first_label < cap.start():
                add("warning", "W-label-order", where,
                    f"{kind} '{labels[0]}': \\label comes before \\caption, so \\ref gives the "
                    "section number; put \\label after \\caption")
            if not any(lb in refs for lb in labels):
                add("warning", "W-float-unref", where,
                    f"{kind} '{labels[0]}' is never referred to in the text (\\ref, \\autoref, \\cref)")
        if env in FIGURE_ENVS and PICTURE_RE.search(body) and "\\Description" not in body:
            add("error", "E-description", where,
                f"figure '{ident}' has no \\Description{{...}} (alt text; CHI requires one per figure)")

    # --- ACM TAPS: every file TeX reads in final mode counts, the CHI Zen library included
    taps = load_taps(paper=root)
    if taps:
        for ln in lines:
            check_taps(ln.text, ln, add, *taps)

    # --- per-line checks in the body
    stack: list[str] = []
    code_pat = re.compile(r"\\(begin|end)\{(" + "|".join(re.escape(e) for e in CODE_ENVS) + r")\}")
    for i, ln in enumerate(lines):
        t = ln.text
        in_body = b0 <= i <= b1
        was_code = bool(stack)
        for m in code_pat.finditer(t):
            if m.group(1) == "begin":
                stack.append(m.group(2))
            elif stack and stack[-1] == m.group(2):
                stack.pop()
        if not lint(i) or not t.strip():
            continue
        in_code = was_code or bool(stack)

        check_tabular(t, ln, add)
        check_colour(t, ln, add, preamble=not in_body)
        if re.search(r"\\usepackage(\[[^\]]*\])?\{[^}]*\bsubcaption\b", t):
            add("warning", "W-subfigure", ln, "\\usepackage{subcaption}: subfigures break PDF/UA "
                "tagging; use separate figures")
        if re.search(r"\\usepackage(\[[^\]]*\])?\{[^}]*\barydshln\b", t) or re.search(r"\\[hc]dashline\b", t):
            add("warning", "W-arydshln", ln, "arydshln dashed rules break PDF/UA tagging; use booktabs "
                "(\\cmidrule) or whitespace")
        if not in_body:
            continue
        if re.search(r"\\begin\{sub(figure|table)\}|\\subfloat\b", t):
            add("warning", "W-subfigure", ln, "subfigure: subfigures break PDF/UA tagging; use "
                "separate figures")
        for m in re.finditer(r"\\(newpage|pagebreak)\b", t):
            add("warning", "W-newpage", ln, f"\\{m.group(1)}: let the ACM template break pages; "
                "a forced break leaves gaps when the text changes")
        if not in_code:
            check_stats(t, ln, add)
            for m in re.finditer(r"(?<![A-Za-z])(TODO|FIXME|TBD|XXX)(?![A-Za-z])|\\todo\b", t):
                add("warning", "W-todo", ln, f"TODO marker in the text: '{short(t[m.start():], 40)}'")
            check_words(t, ln, add)

    # --- whole-document checks on the body text
    text, starts = joined(lines)
    if is_anonymous(lines):
        check_anonymity(lines, text, starts, checked, root, add)
    check_abstract_numbers(lines, text, starts, checked, add)


def check_tabular(t: str, ln: Line, add) -> None:
    for m in re.finditer(r"\\begin\{(tabular\*?|tabularx|tabulary|longtable)\}", t):
        pos = m.end()
        if m.group(1) in ("tabular*", "tabularx", "tabulary"):
            width = balanced_arg(t, pos)
            if width is None:
                continue
            pos = width[1]
        if pos < len(t) and t[pos] == "[":
            close = t.find("]", pos)
            pos = close + 1 if close > 0 else pos
        spec = balanced_arg(t, pos)
        if spec and "|" in re.sub(r"[<>]\{[^}]*\}|@\{[^}]*\}", "", spec[0]):
            add("error", "E-vrule", ln, f"vertical rule in column spec '{spec[0]}': drop the |, "
                "booktabs tables use no vertical lines")
    for m in re.finditer(r"\\(hline|cline)\b", t):
        add("error", "E-hline", ln, f"\\{m.group(1)}: use booktabs (\\toprule, \\midrule, "
            "\\cmidrule, \\bottomrule)")


PACKAGE_RE = re.compile(r"\\(?:usepackage|RequirePackage)\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}")


def check_taps(t: str, ln: Line, add, accepted: set, included: set) -> None:
    for m in PACKAGE_RE.finditer(t):
        if ln.mode_at(m.start()) == "draft":  # TAPS never sees draft mode
            continue
        for pkg in (x.strip() for x in m.group(1).split(",")):
            if not pkg:
                continue
            if pkg in included:
                add("warning", "W-taps-acmart", ln, f"\\usepackage{{{pkg}}}: acmart already loads {pkg}; "
                    "ACM's TAPS list says not to include it in your LaTeX source")
            elif pkg not in accepted:
                add("warning", "W-taps", ln, f"\\usepackage{{{pkg}}}: not on ACM's TAPS accepted-packages "
                    "list (April 2025); TAPS may reject the camera-ready source")


P_RE = re.compile(
    r"(?<![A-Za-z\\])(?:\\(?:textit|emph|mathit|mathrm|textrm)\{\s*)?p\s*\}?\s*\$?\s*"
    r"(=|<|>|\\leq?|\\geq?|\\lt|\\gt|≤|≥)\s*\$?\s*(0?)(\.\d+)")
F_RE = re.compile(r"(?<![A-Za-z\\])F\s*(?:_\{?\s*[\d.]+\s*,\s*[\d.]+\s*\}?|\(\s*[\d.]+\s*,\s*[\d.]+\s*\))?"
                  r"\s*\$?\s*=\s*\$?\s*(\d+\.\d{2,})")
CHI_RE = re.compile(r"\\chi\^\{?2\}?\s*(?:\([^)]*\))?\s*\$?\s*=\s*\$?\s*(\d+\.\d{2,})")
TREND_RE = re.compile(r"\b(trend(?:s|ed|ing)?\s+toward(?:s)?\s+significan\w*|marginally\s+significant"
                      r"|approach(?:es|ed|ing)?\s+(?:statistical\s+)?significance"
                      r"|almost\s+significant|nearly\s+significant)\b", re.I)


def check_stats(t: str, ln: Line, add) -> None:
    for m in P_RE.finditer(t):
        op, zero, frac = m.group(1), m.group(2), m.group(3)
        val = float("0" + frac)
        shown = short(m.group(0).replace("$", ""), 30)
        if zero:
            add("error", "E-p-zero", ln, f"'{shown}': no leading zero on p (it cannot exceed 1): "
                f"write p {op} {frac}, or use \\p{{{frac}}}")
        if op in ("<", "\\lt", "\\le", "\\leq", "≤") and val < 0.001:
            add("error", "E-p-threshold", ln, f"'{shown}': the smallest p to report is p < .001")
        elif op == "=" and val < 0.001:
            add("error", "E-p-threshold", ln, f"'{shown}': report p < .001, not an exact value below .001")
        elif op == "=" and len(frac) > 3:
            add("warning", "W-p-precision", ln, f"'{shown}': report p to two decimals "
                "(p < .01 below .01), as \\p{} does")
    for m in F_RE.finditer(t):
        add("warning", "W-F-precision", ln, f"'{short(m.group(0).replace('$', ''), 30)}': report F to "
            "one decimal, as \\F{} does")
    for m in CHI_RE.finditer(t):
        add("warning", "W-chisq-precision", ln, f"'{short(m.group(0).replace('$', ''), 30)}': report "
            "chi-square to one decimal, as \\chisq{} does")
    for m in TREND_RE.finditer(t):
        add("warning", "W-stats-trend", ln, f"'{m.group(0)}': a result is significant at your stated "
            "alpha or it is not; report the effect size and CI instead")


COLOUR_KEY_RE = re.compile(r"(?<![A-Za-z])(?:draw|fill|color|colour|text|top color|bottom color)\s*=\s*"
                           r"\{?([A-Za-z][\w!.]*)")
COLOUR_CMD_RE = re.compile(r"\\(?:textcolor|color|colorbox|rowcolor|cellcolor|columncolor|fcolorbox)"
                           r"(?:\[[^\]]*\])?\{([^}]*)\}")
DEFINE_RE = re.compile(r"\\(definecolor|colorlet|providecolor)\{([^}]*)\}(?:\[[^\]]*\])?(?:\{([^}]*)\})?")


def colour_ok(expr: str) -> bool:
    parts = [p for p in expr.split("!") if p and not re.fullmatch(r"\d+(\.\d+)?", p)]
    return all(p in PALETTE_COLOURS or p.lower() in NEUTRAL_COLOURS for p in parts)


def check_colour(t: str, ln: Line, add, preamble: bool) -> None:
    for m in DEFINE_RE.finditer(t):
        model = (m.group(3) or "").lower()
        if "cmyk" in model:
            add("warning", "W-cmyk", ln, f"colour '{m.group(2)}' is defined in CMYK; PDF/A-4f needs "
                "RGB colours")
        add("warning", "W-colour", ln, f"\\{m.group(1)}{{{m.group(2)}}}: a colour outside the CHI Zen "
            "palettes; use okabe-ito or another palette from CHIZen/figures.tex")
    if re.search(r"\{cmyk\}|\[cmyk\]", t) and not DEFINE_RE.search(t):
        add("warning", "W-cmyk", ln, "CMYK colour: PDF/A-4f needs RGB colours")
    if preamble:
        return
    seen = set()
    for m in list(COLOUR_KEY_RE.finditer(t)) + list(COLOUR_CMD_RE.finditer(t)):
        expr = m.group(1).strip()
        base = expr.split("!")[0]
        if base.lower() in XCOLOR_NAMES or (("!" in expr) and not colour_ok(expr) and
                                           any(p.lower() in XCOLOR_NAMES for p in expr.split("!"))):
            if expr not in seen:
                seen.add(expr)
                add("warning", "W-colour", ln, f"hard-coded colour '{expr}': use a colour from the "
                    "CHI Zen palettes (okabe-ito by default) or a cycle list")


PROSE_STRIP = [
    (re.compile(r"\$\$.*?\$\$|\$[^$]*\$|\\\(.*?\\\)|\\\[.*?\\\]"), " "),
    (re.compile(r"\\(?:label|ref|autoref|cref|Cref|pageref|eqref|cite\w*|input|include|"
                r"usepackage|url|includegraphics|includesvg|bibliography\w*|addbibresource|"
                r"documentclass|begin|end|newcommand|renewcommand|definecolor|href|"
                r"setcopyright|acm\w*|ccsdesc|keywords|Description|f|cd|ac\w*|texttt|mint)"
                r"\*?(\[[^\]]*\])*\{[^{}]*\}"), " "),
    (re.compile(r"\\[A-Za-z@]+\*?"), " "),
]


def check_words(t: str, ln: Line, add) -> None:
    s = t
    for pat, rep in PROSE_STRIP:
        s = pat.sub(rep, s)
    for w in AVOID_WORDS:
        flags = 0 if w in CASE_SENSITIVE_WORDS else re.I
        pat = r"(?<![\w'’-])" + re.escape(w).replace("'", "['’]").replace(r"\ ", r"\s+") + r"(?![\w'’-])"
        for m in re.finditer(pat, s, flags):
            add("style", "S-avoid", ln, f"'{m.group(0)}' is on the checklist's words to avoid")


# ------------------------------------------------------------------ anonymity (TRN-5)

def joined(lines: list) -> tuple[str, list]:
    """The comment-stripped text of all lines, one per row, and each line's start offset."""
    starts, pos = [], 0
    for ln in lines:
        starts.append(pos)
        pos += len(ln.text) + 1
    return "\n".join(ln.text for ln in lines), starts


def line_at(starts: list, offset: int) -> int:
    lo, hi = 0, len(starts) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if starts[mid] <= offset:
            lo = mid
        else:
            hi = mid - 1
    return lo


def is_anonymous(lines: list) -> bool:
    """True when the acmart class options include `anonymous` (or anonymous=true)."""
    for ln in lines:
        m = re.search(r"\\documentclass\s*\[([^\]]*)\]", ln.text)
        if m:
            opts = [o.strip().replace(" ", "") for o in m.group(1).split(",")]
            return "anonymous" in opts or "anonymous=true" in opts
    return False


def blank(text: str, spans) -> str:
    """`text` with each (start, end) span replaced by spaces (newlines kept, so offsets still
    map to lines)."""
    chars = list(text)
    for a, b in spans:
        for k in range(a, b):
            if chars[k] != "\n":
                chars[k] = " "
    return "".join(chars)


def command_spans(text: str, names) -> list[tuple[int, int, str]]:
    """(start, end, first argument) of each \\name[opt]{arg}..., for the given commands."""
    out = []
    pat = re.compile(r"\\(" + "|".join(names) + r")\*?(?![A-Za-z@])")
    for m in pat.finditer(text):
        pos = m.end()
        while True:
            while pos < len(text) and text[pos] in " \t\n":
                pos += 1
            if pos < len(text) and text[pos] == "[":
                close = text.find("]", pos)
                if close < 0:
                    break
                pos = close + 1
                continue
            break
        arg = balanced_arg(text, pos)
        if arg is not None:
            out.append((m.start(), arg[1], arg[0]))
    return out


# acmart drops these in anonymous mode (\author's names, \thanks, the acks and anonsuppress
# environments, \anon{...}), or they are citations and labels rather than prose.
ANON_HIDDEN_CMDS = ("author", "affiliation", "institution", "department", "streetaddress",
                    "city", "state", "postcode", "country", "email", "orcid", "thanks",
                    "additionalaffiliation", "anon", "shortauthors", "authorsaddresses",
                    "cite[A-Za-z]*", "label", "ref", "autoref", "cref", "Cref", "url",
                    "href", "input", "include", "includegraphics", "bibliography",
                    "addbibresource", "title", "grantsponsor", "grantnum")
ANON_HIDDEN_ENVS = ("acks", "anonsuppress")
NAME_CMDS = ("author", "institution")
# First person about the authors' earlier publications: always self-citation.
SELF_CITE_RE = re.compile(
    r"\b(?:our|my)\s+(?:own\s+)?(?:prior|previous|past|earlier|former)\s+(?:published\s+)?"
    r"(?:work|works|paper|papers|publication|publications|research)\b", re.I)
# Phrases that can also refer to this paper ("our previous study" may be Study 1): only
# self-citation when the same sentence cites something.
SELF_CITE_WEAK_RE = re.compile(
    r"\b(?:our|my)\s+(?:own\s+)?(?:prior|previous|past|former)\s+(?:study|studies|system|"
    r"systems|tool|tools|survey|findings|results)\b"
    r"|\bwe\s+(?:have\s+)?(?:previously|earlier|already)\s+(?:showed|shown|found|reported|"
    r"developed|proposed|built|published|presented|introduced|described|studied|designed|"
    r"demonstrated)\b"
    r"|\b(?:in|see|from)\s+our\s+(?:own\s+)?(?:work|study|paper|research)\b", re.I)
ETHICS_ID_RE = re.compile(
    r"\b(?:REB|IRB|ORE|HREB|ethics(?:\s+(?:board|committee|clearance|approval))?)\b"
    r"[^.;]{0,40}?(?:\#|\\\#|\bno\.?|\bnumber|\bprotocol|\bfile)\s*:?\s*[A-Z]*-?\d{3,}", re.I)
GRANT_ID_RE = re.compile(r"\bgrants?\s+(?:\#|\\\#|no\.?|number|ID)\s*:?\s*[A-Z0-9][A-Z0-9-]{3,}", re.I)
LINK_RE = re.compile(r"(?:https?://)?(?:www\.)?(github\.com|gitlab\.com|bitbucket\.org|"
                     r"huggingface\.co|osf\.io)/[^\s}{\\]+", re.I)
ACK_HEADING_RE = re.compile(r"\\(?:section|subsection|paragraph)\*?\s*\{\s*acknowledge?ments?\b", re.I)


SENTENCE_END_RE = re.compile(r"[.!?](?=\s)|\n\s*\n")


def sentence_at(text: str, offset: int) -> str:
    """The sentence of `text` around `offset`: from the last full stop (or blank line) before
    it to the next one. Abbreviations ("et al.") end it early, which only makes it shorter."""
    window = text[max(0, offset - 600):offset]
    starts = [m.end() for m in SENTENCE_END_RE.finditer(window)]
    a = offset - len(window) + (starts[-1] if starts else 0)
    m = SENTENCE_END_RE.search(text, offset)
    return text[a:m.start() if m else len(text)]


def anon_mask(text: str, cmds=ANON_HIDDEN_CMDS) -> str:
    """The text with what acmart hides in anonymous mode (and, by default, citations and other
    non-prose arguments) blanked out."""
    spans = [(m.start(), m.end()) for env in ANON_HIDDEN_ENVS for m in re.finditer(
        r"\\begin\{" + env + r"\}.*?(?:\\end\{" + env + r"\}|\Z)", text, re.S)]
    spans += [(a, b) for a, b, _ in command_spans(text, cmds)]
    text = blank(text, spans)
    return text


def identity_names(text: str) -> list[str]:
    """Author names and institutions from \\author{} and \\institution{}, as they'd appear in
    prose. acmart hides these in the header; the body must not repeat them."""
    names = set()
    for _, _, arg in command_spans(text, NAME_CMDS):
        arg = re.sub(r"\\[A-Za-z@]+\*?(\[[^\]]*\])?(\{[^{}]*\})?|[{}~]", " ", arg)
        arg = re.sub(r"\s+", " ", arg).strip(" ,")
        # One-word names ("Google") are too often a product or a place, not the authors.
        if len(arg.split()) >= 2 and not re.search(r"anonym", arg, re.I):
            names.add(arg)
    return sorted(names, key=len, reverse=True)


def check_anonymity(lines: list, text: str, starts: list, checked: list, root: Path, add) -> None:
    """TRN-5: what acmart's `anonymous` option doesn't hide (CHI anonymization policy)."""
    b0, b1 = body_range(lines)
    body0 = starts[b0]
    body1 = starts[b1] + len(lines[b1].text) if b1 < len(lines) else len(text)
    names = identity_names(text)
    prose = anon_mask(text)

    def report(sev, code, offset, msg):
        i = line_at(starts, offset)
        if checked[i] and body0 <= offset <= body1:
            add(sev, code, lines[i], msg)

    for name in names:
        pat = re.compile(r"(?<![\w-])" + re.escape(name).replace(r"\ ", r"\s+") + r"(?![\w-])", re.I)
        for m in pat.finditer(prose):
            report("warning", "W-anon-name", m.start(), f"'{short(m.group(0), 40)}' (an author or "
                   "institution) in an anonymous submission: wrap it in \\anon{...}, which acmart "
                   "hides until camera-ready")
    selfcites = list(SELF_CITE_RE.finditer(prose)) + [
        m for m in SELF_CITE_WEAK_RE.finditer(prose)
        if re.search(r"\\cite|\\citet|\\citep", sentence_at(text, m.start()))]
    for m in sorted(selfcites, key=lambda m: m.start()):
        report("warning", "W-anon-selfcite", m.start(), f"'{short(m.group(0), 40)}': cite your own work "
               "in the third person in an anonymous submission (\"Chetty et al. [10] showed\")")
    for m in ETHICS_ID_RE.finditer(prose):
        report("warning", "W-anon-id", m.start(), f"'{short(m.group(0), 40)}': an ethics approval number "
               "identifies the institution; wrap it in \\anon{...} until camera-ready")
    for m in GRANT_ID_RE.finditer(prose):
        report("warning", "W-anon-id", m.start(), f"'{short(m.group(0), 40)}': a grant number identifies "
               "the authors; put it in the acks environment or \\anon{...}")
    for m in ACK_HEADING_RE.finditer(prose):
        report("warning", "W-anon-acks", m.start(), "acknowledgments in a \\section: put them in the "
               "acks environment, which acmart leaves out of anonymous submissions")
    for m in re.finditer(r"pdfauthor\s*=\s*\{?\s*([^,}\s][^,}]*)", text):
        i = line_at(starts, m.start())
        if checked[i] and not re.search(r"anonym|\\authors\b", m.group(1), re.I):
            add("warning", "W-anon-metadata", lines[i], "pdfauthor is set by hand: in an anonymous "
                "submission let acmart set it (to \"Anonymous Author(s)\")")
    # Links: GitHub and the like name the owner; an OSF project link shows its contributors.
    shown = anon_mask(text, ("anon",))
    for m in LINK_RE.finditer(shown):
        url = m.group(0)
        if m.group(1).lower() == "osf.io" and "view_only" in url:
            continue
        # A GitHub link to someone else's tool is fine; flag it when the sentence says "our".
        if m.group(1).lower() != "osf.io" and not re.search(
                r"\b(?:our|my)\b", sentence_at(shown, m.start()), re.I):
            continue
        what = ("an OSF link without view_only shows the project's contributors; use an "
                "anonymised view-only link" if m.group(1).lower() == "osf.io" else
                f"a {m.group(1)} link names its owner; link an anonymised copy for review")
        report("warning", "W-anon-link", m.start(), f"'{short(url, 40)}': {what}")
    check_anon_bib(lines, root, add)
    check_anon_figures(lines, starts, checked, text, root, add)


def bib_files(lines: list, root: Path) -> list[Path]:
    out = []
    for ln in lines:
        for m in re.finditer(r"\\(bibliography|addbibresource)\s*(?:\[[^\]]*\])?\{([^}]*)\}", ln.text):
            for name in m.group(2).split(","):
                name = name.strip()
                for cand in (name, name + ".bib"):
                    p = root / cand
                    if cand.endswith(".bib") and p.is_file() and p not in out:
                        out.append(p)
    return out


def check_anon_bib(lines: list, root: Path, add) -> None:
    """CHI: "the use of any references marked 'anonymous' is grounds for desk rejection"."""
    for p in bib_files(lines, root):
        try:
            raw = p.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        key = None
        for i, s in enumerate(raw, 1):
            m = re.match(r"\s*@\w+\s*[{(]\s*([^,\s]+)", s)
            if m:
                key = m.group(1)
            if re.match(r"\s*author\s*=\s*[{\"]\s*\{?\s*anonymous\b", s, re.I):
                add("error", "E-anon-ref", Line(rel(root, p), i, s, s),
                    f"'{key}' is a reference marked anonymous: CHI desk-rejects these; cite your "
                    "own work normally, in the third person")


PDF_AUTHOR_RE = re.compile(rb"/Author\s*(\((?:\\.|[^\\)])*\)|<[0-9A-Fa-f\s]*>)")
XMP_CREATOR_RE = re.compile(rb"<dc:creator>\s*<rdf:Seq>(.*?)</rdf:Seq>", re.S)


def pdf_author(path: Path) -> str | None:
    """The author in a PDF's (uncompressed) Info dictionary or XMP metadata, if any. Best
    effort: an Info dictionary inside a compressed object stream is not read."""
    try:
        data = path.read_bytes()
    except OSError:
        return None
    for m in PDF_AUTHOR_RE.finditer(data):
        v = m.group(1)
        if v.startswith(b"<"):
            h = re.sub(rb"\s", b"", v[1:-1])
            try:
                b = bytes.fromhex(h.decode())
                s = b[2:].decode("utf-16-be") if b[:2] == b"\xfe\xff" else b.decode("latin-1")
            except ValueError:
                continue
        else:
            b = v[1:-1]
            s = (b[2:].decode("utf-16-be", "replace") if b[:2] == b"\xfe\xff"
                 else b.decode("latin-1"))
        s = s.strip()
        if s and not re.search(r"anonym", s, re.I):
            return s
    for m in XMP_CREATOR_RE.finditer(data):
        for li in re.findall(rb"<rdf:li[^>]*>(.*?)</rdf:li>", m.group(1), re.S):
            s = li.decode("utf-8", "replace").strip()
            if s and not re.search(r"anonym", s, re.I):
                return s
    return None


def check_anon_figures(lines: list, starts: list, checked: list, text: str, root: Path, add) -> None:
    """pdfTeX and LuaTeX copy an included PDF's Info dictionary into the paper's PDF."""
    seen = set()
    for a, _, arg in command_spans(text, ("includegraphics", "chizenfigure")):
        i = line_at(starts, a)
        if not checked[i]:
            continue
        name = arg.strip()
        cands = ([root / "figures" / "tikz" / f"{name}.pdf"] if text[a:a + 13] == "\\chizenfigure"
                 else [root / name, root / f"{name}.pdf"])
        p = next((c for c in cands if c.suffix.lower() == ".pdf" and c.is_file()), None)
        if p is None or p in seen:
            continue
        seen.add(p)
        who = pdf_author(p)
        if who:
            add("warning", "W-anon-metadata", lines[i], f"{rel(root, p)} names an author in its PDF "
                f"metadata ('{short(who, 30)}'), which the paper's PDF carries; clear the Author field")



# ------------------------------------------------------------------ numbers (WRT-14)

NUMBER_WORDS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
    "fifteen sixteen seventeen eighteen nineteen".split())}
NUMBER_WORDS.update({w: 10 * i for i, w in enumerate(
    "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()) if w != "_"})
NUM_WORD_RE = (r"(?:(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)(?:[- ](?:one|two|"
               r"three|four|five|six|seven|eight|nine))?|" + "|".join(
                   w for w in NUMBER_WORDS if w != "zero") + r"|\d{1,3}(?:,\d{3})*|\d+)")
PEOPLE = (r"(?:participants?|people|persons|users|respondents|interviewees|informants|students|"
          r"workers|employees|clinicians|nurses|physicians|doctors|patients|caregivers|carers|"
          r"adults|children|teens|teenagers|adolescents|parents|experts|designers|developers|"
          r"practitioners|researchers|teachers|volunteers|subjects|players|members|individuals)")
COUNT_RE = re.compile(r"(?<![\w.,])(" + NUM_WORD_RE + r")(?!\s*(?:hundred|thousand|million|billion|"
                      r"[kKMB]\b|\.\d))(?:\s+[A-Za-z-]+){0,3}?\s+" + PEOPLE + r"\b"
                      r"|\b[Nn]\s*\$?\s*=\s*\$?\s*(\d{1,3}(?:,\d{3})*|\d+)\b", re.I)
PERCENT_RE = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)\s*(?:\\,|~)?\s*(?:\\%|\\percent\b|percent\b)"
                        r"|\\(?:SI|qty)\s*\{\s*(\d+(?:\.\d+)?)\s*\}\s*\{\s*\\percent\s*\}", re.I)


def number_value(s: str) -> int | None:
    s = s.lower().replace(",", "").strip()
    if s.isdigit():
        return int(s)
    total = 0
    for part in re.split(r"[- ]", s):
        if part not in NUMBER_WORDS:
            return None
        total += NUMBER_WORDS[part]
    return total


def check_abstract_numbers(lines: list, text: str, starts: list, checked: list, add) -> None:
    """WRT-14: a participant count or a percentage in the abstract should appear in the body,
    so a reader (and a reviewer) can find where it comes from. Rounding is allowed: an abstract's
    "35%" matches the body's "34.8%"."""
    m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", text, re.S)
    if not m:
        return
    abstract, a0 = m.group(1), m.start(1)
    body = anon_mask(blank(text, [(m.start(), m.end())]), ("cite[A-Za-z]*", "label", "ref", "autoref", "cref", "Cref"))
    counts = {number_value(x.group(1) or x.group(2)) for x in COUNT_RE.finditer(body)}
    percents = [x.group(1) or x.group(2) for x in PERCENT_RE.finditer(body)]

    def rounds_to(shown: str, value: str) -> bool:
        places = len(shown.split(".")[1]) if "." in shown else 0
        return abs(round(float(value), places) - float(shown)) < 1e-9

    for x in COUNT_RE.finditer(abstract):
        n = number_value(x.group(1) or x.group(2))
        i = line_at(starts, a0 + x.start())
        if n is not None and n not in counts and checked[i]:
            add("warning", "W-abstract-number", lines[i], f"the abstract's '{short(x.group(0), 40)}' "
                "appears nowhere else as a count of people: check it matches the method and results")
    for x in PERCENT_RE.finditer(abstract):
        v = x.group(1) or x.group(2)
        i = line_at(starts, a0 + x.start())
        if not any(rounds_to(v, b) for b in percents) and checked[i]:
            add("warning", "W-abstract-number", lines[i], f"the abstract's '{short(x.group(0).replace(chr(92), ''), 30)}' "
                "appears nowhere else in the paper: check it matches the results")


# ------------------------------------------------------------------ driver

def run(root: Path, mains: list[Path], excludes) -> list[Finding]:
    findings: dict[tuple, Finding] = {}

    def add(sev, code, ln, msg):
        f = Finding(sev, code, ln.file, ln.num, msg)
        findings.setdefault((code, ln.file, ln.num, msg), f)

    for m in mains:
        doc = Doc(rel(root, m))
        flatten(root, m, excludes, set(), doc.lines)
        check_doc(doc, root, excludes, add)
    return sorted(findings.values(), key=lambda f: (f.file, f.line, f.code, f.msg))


def read_baseline(path: Path) -> Counter:
    if not path.is_file():
        return Counter()
    return Counter(ln.rstrip() for ln in path.read_text(encoding="utf-8").splitlines()
                   if ln.strip() and not ln.lstrip().startswith("#"))


def write_baseline(path: Path, lines: Counter) -> None:
    """Write the baseline, keeping the comment block at the top of an existing file."""
    header = BASELINE_HEADER
    if path.is_file():
        old = []
        for ln in path.read_text(encoding="utf-8").splitlines():
            if not ln.startswith("#"):
                break
            old.append(ln + "\n")
        header = "".join(old) or header
    body = "".join(f"{k}\n" for k in sorted(lines.elements()))
    path.write_text(header + body, encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="CHI Zen checks on a LaTeX paper")
    ap.add_argument("paper", nargs="?", default=".", help="paper directory (default: .)")
    ap.add_argument("--main", action="append", default=[], help="main .tex file (repeatable)")
    ap.add_argument("--exclude", action="append", default=[], help="path prefix not to check (repeatable)")
    ap.add_argument("--baseline", help=f"baseline file (default: PAPER/{BASELINE_NAME})")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--prune-baseline", action="store_true", help="delete baseline lines that no longer occur")
    ap.add_argument("--write-baseline", action="store_true", help="accept every current error and warning")
    args = ap.parse_args(argv)

    root = Path(args.paper)
    if not root.is_dir():
        print(f"check_paper: {root} is not a directory", file=sys.stderr)
        return 2
    mains = [root / m for m in args.main] if args.main else find_mains(root)
    missing = [str(m) for m in mains if not m.is_file()]
    if missing or not mains:
        print("check_paper: no main .tex file found" + (f" ({', '.join(missing)})" if missing else
              " (none with \\documentclass in the paper directory; use --main)"), file=sys.stderr)
        return 2
    excludes = list(DEFAULT_EXCLUDES) + args.exclude
    found = run(root, mains, excludes)

    bpath = Path(args.baseline) if args.baseline else root / BASELINE_NAME
    current = Counter(f.ident() for f in found if f.severity != "style")
    if args.write_baseline:
        write_baseline(bpath, current)
        print(f"Wrote {sum(current.values())} line(s) to {bpath}.")
        return 0
    baseline = read_baseline(bpath)
    new = current - baseline
    stale = baseline - current
    if args.prune_baseline:
        write_baseline(bpath, baseline - stale)
        print(f"Removed {sum(stale.values())} stale line(s) from {bpath}.")
        stale = Counter()

    # Mark which findings are accepted by the baseline (first occurrences first).
    budget = Counter(baseline)
    for f in found:
        f.accepted = False
        if f.severity != "style" and budget[f.ident()] > 0:
            budget[f.ident()] -= 1
            f.accepted = True

    if args.json:
        print(json.dumps({
            "mains": [rel(root, m) for m in mains],
            "findings": [dict(severity=f.severity, code=f.code, file=f.file, line=f.line, msg=f.msg,
                              baselined=f.accepted) for f in found],
            "new": sorted(new.elements()), "stale_baseline": sorted(stale.elements()),
        }, indent=2, ensure_ascii=False))
    else:
        report(found, new, stale, bpath, mains, root)
    return 1 if (new or stale) else 0


def report(found, new, stale, bpath, mains, root) -> None:
    n = Counter(f.severity for f in found)
    out = [f"## CHI Zen check: {n['error']} error(s), {n['warning']} warning(s), {n['style']} style note(s)",
           f"Main file(s): {', '.join(rel(root, m) for m in mains)}", ""]
    titles = {"error": "Errors", "warning": "Warnings", "style": "Style: words to avoid (never fails)"}
    for sev in ("error", "warning", "style"):
        items = [f for f in found if f.severity == sev]
        if not items:
            continue
        out.append(f"### {titles[sev]}")
        if sev == "style":  # one line per source line: "file:12: like, you"
            by_line: dict[tuple, list] = {}
            for f in items:
                by_line.setdefault((f.file, f.line), []).append(f.msg[1:f.msg.index("' is on")])
            out += [f"- `{fl}:{ln}` {', '.join(ws)}" for (fl, ln), ws in by_line.items()]
            out.append("")
            continue
        for f in items:
            tag = " (baseline)" if getattr(f, "accepted", False) else ""
            out.append(f"- `{f.file}:{f.line}` **{f.code}** {f.msg}{tag}")
        out.append("")
    if new:
        out += [f"### New findings: not in {bpath.name}, so this fails",
                "Fix the cause. Don't add the line to the baseline to make it pass.",
                *[f"- `{x}`" for x in sorted(new.elements())], ""]
    if stale:
        out += [f"### Fixed findings still listed in {bpath.name}, so this fails",
                "Run with --prune-baseline to delete them.", *[f"- `{x}`" for x in sorted(stale.elements())], ""]
    if not new and not stale:
        out.append("No new errors or warnings.")
    text = "\n".join(out)
    print(text)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write(text + "\n")


if __name__ == "__main__":
    sys.exit(main())
