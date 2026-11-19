#!/usr/bin/env python3
"""warning_ratchet.py: a LaTeX/BibTeX build may not add a warning.

Run it after compiling (latexmk), on the jobs you built:

    python3 warning_ratchet.py paper                   # paper.log, paper.blg in .
    python3 warning_ratchet.py --dir build paper       # logs in build/
    python3 warning_ratchet.py paper paper-final 'figures/tikz/*'   # globs work too
    python3 warning_ratchet.py --label lualatex paper  # tag lines with the engine (CI)
    python3 warning_ratchet.py --show paper            # just print the current warnings
    python3 warning_ratchet.py --prune-baseline paper  # drop baseline lines that no longer occur

Standard library only (Python 3.9+), like check_paper.py; the CHI Zen manual and
starter paper run it in CI (.github/workflows/build.yml), and a paper made from
the template can run the same script on its own build.

THE RATCHET. Every warning found must be listed in the baseline file (default
DIR/chizen-warnings-baseline.txt; a missing file is an empty baseline), and every
line in the baseline must still occur, so the file only shrinks; --prune-baseline
deletes the lines that no longer occur. Exit status 1 on a new warning, a stale
baseline line, a LaTeX/BibTeX error or a missing log; 0 otherwise; 2 bad usage.
Each warning is one line, "<label> <file>: <message>", with input line numbers,
page numbers, sizes and paths normalised away, so it survives edits elsewhere;
a line listed twice means the warning occurs twice.

WHAT COUNTS, AND WHY.
  .log  every "LaTeX/Package/Class/Module ... Warning" (with its continuation
        lines), "LaTeX Font Warning", "pdfTeX warning", "Missing character"
        and any other line that says "warning:" (e.g. luaotfload), once per
        distinct message, since some repeat on every page. Undefined references
        and citations are LaTeX/natbib warnings, so they count. So does the
        CHIZen warning for a figure without a \\Description.
  .log  every Overfull box. TeX reports only boxes more than \\hfuzz (0.1pt)
        too wide, so each one is text in the margin.
        Underfull boxes are NOT counted (their number is printed): they mean
        loose spacing, not text outside the text block, and in acmart's narrow
        columns and ragged figure captions they come and go with every
        rewording, so a ratchet on them would only teach people to rephrase.
        Rerun hints are not counted either: latexmk reruns until the document
        is stable, so in the final log they are left over from an earlier pass.
  .blg  BibTeX's "Warning--" lines and errors.

TIKZ `EXTERNAL' FIGURE LOGS. A figure saved by TikZ external (figures/tikz/*.log
in draft mode) is made by running LaTeX on the whole paper again under another
job name, keeping only that picture. That run has no .aux file of its own, so
every \\ref and \\cite in the text around the picture is undefined there; the
main log reports the real state of those. In a figure log, undefined
references and citations are therefore counted only when they occur while the
picture itself is typeset (a \\ref inside a figure really does print "??").
Everything else in a figure log counts.

ALLOWLIST. Warnings that come from inside acmart or TeX Live and cannot be fixed
from the paper are listed in ALLOWLIST below, each with its source and reason.
They are printed but do not fail. Keep the list short and explicit.
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys
from collections import Counter
from pathlib import Path

BASELINE_NAME = "chizen-warnings-baseline.txt"
MAX_PRINT_LINE = 79  # TeX Live's default width of log lines
BASELINE_HEADER = """\
# Accepted build warnings: the baseline of warning_ratchet.py (CHI Zen).
# CI fails on any LaTeX/BibTeX warning not listed here, and on any line here
# that no longer occurs, so this file only shrinks. Fix the cause rather than
# adding a line. One line per occurrence: "<label> <file>: <warning>".
"""

# (regex on the normalised message, reason). Matched warnings are reported but
# never fail. Each entry must name where the warning comes from and why the
# document cannot avoid it. Empty is the goal.
ALLOWLIST: list[tuple[str, str]] = [
    # acmart.cls v2.21 (2026/11/01), line 538, loads hyperxmp unconditionally:
    #     \RequirePackage{hyperxmp}
    # With \DocumentMetadata, pdfmanagement-firstaid.sty v0.97d (2026-10-06),
    # line 137, blocks that load (the PDF management writes the XMP metadata
    # itself, which PDF/A needs) and warns:
    #     \disable@package@load{hyperxmp}{\msg_warning:nnn{pdfmanagement}{firstaid-disabled}{hyperxmp}}
    # Both happen inside \documentclass, before a paper or CHI Zen can act, and
    # hyperxmp is correctly not loaded. The only ways round it are to let
    # hyperxmp load (\DocumentMetadata{debug={firstaidoff=xmp}}), which breaks the
    # XMP metadata, or to pretend it is loaded before \documentclass, which
    # only hides the message. Remove this entry once acmart stops loading
    # hyperxmp under \DocumentMetadata.
    (r"^Package pdfmanagement Warning: The loading of package hyperxmp is disabled\. "
     r"It is not compatible with the PDF management\.$",
     "acmart.cls (v2.21, line 538) loads hyperxmp, which pdfmanagement-firstaid.sty "
     "(v0.97d, line 137) disables under \\DocumentMetadata, as it should"),
]

IGNORED = re.compile(
    r"Rerun to get|Label\(s\) may have changed|Please rerun LaTeX|Please \(re\)run"
    r"|Package rerunfilecheck Warning|Temporary extra page added")
UNDEFINED = re.compile(
    r"(?:Reference|Citation) `[^']*'(?: on page \S+)? undefined|There were undefined (?:references|citations)")
BOX = re.compile(r"^(Overfull|Underfull) \\([hv])box \((?:badness (\d+)|(-?[\d.]+)pt too (?:wide|high))\) (.*)$")
WARN = re.compile(r"^(?:(?:Package|Class|Module) (\S+)|LaTeX(?: Font)?(?: \S+)?) Warning: (.*)$")
OTHER_WARN = re.compile(r"^(?:pdfTeX warning|Missing character: |.*\bwarning:)", re.I)
BIBTEX_ERROR = re.compile(r"^(?:I couldn't open|I found no|I was expecting|Repeated entry|"
                          r"Illegal|.*---line \d+ of file)")
ERROR = re.compile(r"^! |^\.?/?[\w./-]+\.(?:tex|sty|cls|bbl|cfg|def|ltx):\d+: ")


# ---------------------------------------------------------------- baseline

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
    path.write_text(header + "".join(f"{k}\n" for k in sorted(lines.elements())), encoding="utf-8")


def source_of(line: str) -> str:
    return line.split(": ", 1)[0]


# ---------------------------------------------------------------- LaTeX log

def unwrap(raw: bytes) -> list[str]:
    """TeX breaks log lines at MAX_PRINT_LINE bytes; join them back up."""
    out: list[bytes] = []
    cont = False
    for ln in raw.split(b"\n"):
        ln = ln.rstrip(b"\r")
        if cont:
            out[-1] += ln
        else:
            out.append(ln)
        cont = len(ln) == MAX_PRINT_LINE
    return [x.decode("utf-8", errors="replace") for x in out]


def normalise(s: str, root: str) -> str:
    s = s.replace(root.rstrip("/") + "/", "") if root else s
    s = re.sub(r"\s+on input line \d+\.?", "", s)
    s = re.sub(r"\s+(?:at|on) lines? \d+(?:--\d+)?\.?", "", s)
    s = re.sub(r"\s+on page \S+?(?=[ .]|$)", "", s)
    s = re.sub(r"\(?-?\d+(?:\.\d+)?pt\)?", "#pt", s)
    s = re.sub(r"(?:(?<=^)|(?<=[\s`'\"(]))/(?:[\w.+-]+/)+", "", s)  # absolute paths: keep the file name
    return " ".join(s.split())


def excerpt(lines: list[str], i: int) -> str:
    """The text TeX prints after a box warning, normalised to an identifier."""
    parts = []
    for ln in lines[i + 1:i + 8]:
        if not ln.strip():
            break
        parts.append(ln)
    s = " ".join(parts)
    s = re.sub(r"\\[A-Za-z0-9]+(?:/[^\s/]+)+ ?", "", s)  # font selectors like \TU/LinLibertine(0)/m/n/9
    s = re.sub(r"\[\]|\$|-|\^\^[0-9a-f]{2}|\([+-]?\d+\)", "", s)  # rules, math, hyphens, font expansion
    s = " ".join(s.split())
    return s[:60].rstrip() or "(no text)"


def picture_span(lines: list[str], stem: str) -> tuple[int, int] | None:
    """In a TikZ external figure log: (first, last) line of the picture itself.
    None for other logs."""
    name = re.escape(Path(stem).name)
    # CHIZen/externalize.tex marks the picture in the log ...
    start = next((i for i, ln in enumerate(lines) if re.match(r"^CHIZen figure: " + name + r"\s*$", ln)), None)
    if start is not None:
        end = next((i for i in range(start, len(lines))
                    if re.match(r"^CHIZen figure end: " + name + r"\s*$", lines[i])), len(lines))
        return start, end
    # ... otherwise (plain TikZ external): from opening <stem>.dpth to the page shipped out.
    start = next((i for i, ln in enumerate(lines)
                  if re.match(r"^\\openout\d+ = `?.*" + name + r"\.dpth'?\.?\s*$", ln)), None)
    if start is None:
        return None
    end = next((i for i in range(start, len(lines)) if re.match(r"^\s*\[1\b", lines[i])), len(lines))
    return start, end


def latex_warnings(log: Path, label: str, root: str) -> tuple[list[str], list[str], Counter]:
    """(warnings, errors, not-counted tallies) from a LaTeX .log file."""
    lines = unwrap(log.read_bytes())
    span = picture_span(lines, log.stem)
    warns: list[str] = []
    errs: list[str] = []
    skipped: Counter = Counter()
    seen: set[str] = set()

    def once(i: int, msg: str) -> None:
        msg = normalise(msg, root)
        if span and UNDEFINED.search(msg) and not (span[0] <= i <= span[1]):
            skipped["undefined reference outside the picture (TikZ external run)"] += 1
            return
        if msg not in seen:
            seen.add(msg)
            warns.append(f"{label}: {msg}")

    for i, ln in enumerate(lines):
        if ERROR.match(ln):
            errs.append(f"{label}: {ln.strip()}")
            continue
        m = BOX.match(ln)
        if m:
            kind, hv, _badness, _size, where = m.groups()
            if kind == "Underfull":
                skipped["Underfull box"] += 1
            else:
                where = normalise(where, root)
                text = excerpt(lines, i) if hv == "h" else ""
                warns.append(f"{label}: Overfull \\{hv}box {where}" + (f': "{text}"' if text else ""))
            continue
        m = WARN.match(ln)
        if m:
            body = [m.group(0)]
            for nxt in lines[i + 1:]:
                if re.match(r"^\([^)\s]+\)\s", nxt):
                    body.append(re.sub(r"^\([^)\s]+\)\s+", "", nxt))
                else:
                    break
            msg = " ".join(body)
            if IGNORED.search(msg):
                skipped["rerun hint"] += 1
            else:
                once(i, msg)
            continue
        if OTHER_WARN.match(ln):
            once(i, ln)
    return warns, errs, skipped


# ---------------------------------------------------------------- BibTeX log

def bibtex_warnings(blg: Path, label: str, root: str) -> tuple[list[str], list[str]]:
    text = blg.read_text(encoding="utf-8", errors="replace").splitlines()
    warns, errs = [], []
    for ln in text:
        if ln.startswith("Warning--"):
            warns.append(f"{label}: {normalise(ln, root)}")
        elif BIBTEX_ERROR.match(ln):
            errs.append(f"{label}: {normalise(ln, root)}")
        m = re.match(r"^\[\d+\] \S+> (WARN|ERROR) - (.*)$", ln)  # biber, if a paper uses it
        if m:
            (warns if m.group(1) == "WARN" else errs).append(f"{label}: {normalise(m.group(2), root)}")
    return warns, errs


# ---------------------------------------------------------------- driver

def expand(docs: list[str], where: Path) -> list[Path]:
    """Job names (or globs) -> .log paths."""
    out: list[Path] = []
    for d in docs:
        d = d[:-4] if d.endswith(".log") else d
        if any(c in d for c in "*?["):
            out += [Path(p) for p in sorted(glob.glob(str(where / (d + ".log"))))]
        else:
            out.append(where / (d + ".log"))
    return out


def collect(logs: list[Path], where: Path, label: str) -> tuple[Counter, list[str], dict[str, Counter]]:
    current: Counter = Counter()
    errors: list[str] = []
    skipped: dict[str, Counter] = {}
    root = str(where.resolve())
    for log in logs:
        name = log.relative_to(where).as_posix() if log.is_relative_to(where) else log.as_posix()
        tag = f"{label} {name}" if label else name
        if not log.is_file():
            errors.append(f"{tag}: not found; did the document compile?")
            continue
        w, e, sk = latex_warnings(log, tag, root)
        current.update(w)
        errors += e
        skipped[tag] = sk
        blg = log.with_suffix(".blg")
        if blg.is_file():
            btag = tag[:-4] + ".blg"
            w, e = bibtex_warnings(blg, btag, root)
            current.update(w)
            errors += e
    return current, errors, skipped


def allowlisted(line: str) -> str | None:
    msg = line.split(": ", 1)[1] if ": " in line else line
    for pat, why in ALLOWLIST:
        if re.search(pat, msg):
            return why
    return None


def report(new, stale, errors, allowed, skipped, current, bpath: Path, logs) -> str:
    total = sum(current.values())
    out = [f"## Build warnings: {total} warning(s) in {len(logs)} log(s), "
           f"{len(new)} new, {len(stale)} fixed but still in the baseline, {len(errors)} error(s)", ""]
    if errors:
        out += ["### Errors", *[f"- `{e}`" for e in errors], ""]
    if new:
        out += [f"### New warnings (not in {bpath.name}): this fails",
                "Fix the cause; don't add the line to the baseline to make it pass.", "```",
                *new, "```", ""]
    if stale:
        out += [f"### Fixed warnings still listed in {bpath.name}: this fails",
                "Delete these lines (or run with --prune-baseline):", "```", *stale, "```", ""]
    if allowed:
        out += ["### Allowlisted (from acmart or TeX Live; see ALLOWLIST in warning_ratchet.py)",
                *[f"- `{w}`: {why}" for w, why in allowed], ""]
    if not (errors or new or stale):
        out += ["No errors, and no warnings beyond the baseline.", ""]
    notes = [f"- {src}: " + ", ".join(f"{n} × {k}" for k, n in sorted(sk.items()))
             for src, sk in skipped.items() if sk]
    if notes:
        out += ["Not counted (see the script's docstring for why):", *notes, ""]
    if total:
        out += [f"<details><summary>All current warnings ({total})</summary>", "", "```",
                *sorted(current.elements()), "```", "</details>", ""]
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="CHI Zen build-warning ratchet for LaTeX/BibTeX logs")
    ap.add_argument("docs", nargs="+", metavar="JOB",
                    help="job name of a compiled document (paper for paper.log); globs allowed")
    ap.add_argument("--dir", default=".", help="directory holding the logs (default: .)")
    ap.add_argument("--baseline", help=f"baseline file (default: DIR/{BASELINE_NAME})")
    ap.add_argument("--label", default="", help="prefix for each line, e.g. the engine (lualatex)")
    ap.add_argument("--show", action="store_true", help="print the current warnings and exit 0")
    ap.add_argument("--prune-baseline", action="store_true",
                    help="delete baseline lines (for these logs) that no longer occur")
    args = ap.parse_args(argv)

    where = Path(args.dir)
    if not where.is_dir():
        print(f"warning_ratchet: {where} is not a directory", file=sys.stderr)
        return 2
    logs = expand(args.docs, where)
    if not logs:
        print("warning_ratchet: no logs match " + " ".join(args.docs), file=sys.stderr)
        return 2
    current, errors, skipped = collect(logs, where, args.label)
    if args.show:
        print("\n".join(sorted(current.elements())))
        return 0

    allowed = [(w, why) for w in sorted(current) if (why := allowlisted(w))]
    counted = Counter({w: n for w, n in current.items() if not allowlisted(w)})
    bpath = Path(args.baseline) if args.baseline else where / BASELINE_NAME
    baseline = read_baseline(bpath)
    sources = {f"{args.label} {log.relative_to(where).as_posix() if log.is_relative_to(where) else log}"
               .strip()[:-4] for log in logs}
    mine = Counter({k: n for k, n in baseline.items() if source_of(k)[:-4] in sources})
    new = sorted((counted - mine).elements())
    stale = sorted((mine - counted).elements())

    if args.prune_baseline:
        write_baseline(bpath, baseline - Counter(stale))
        print(f"Removed {len(stale)} stale line(s) from {bpath}.")
        stale = []

    text = report(new, stale, errors, allowed, skipped, current, bpath, logs)
    print(text)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write(text + "\n")
    if os.environ.get("GITHUB_ACTIONS"):
        for e in errors:
            print(f"::error title=LaTeX error::{e}")
        for w in new:
            print(f"::error title=New build warning::{w}")
        for s in stale:
            print(f"::error title=Fixed warning still in the baseline::{s}")
    return 1 if (errors or new or stale) else 0


if __name__ == "__main__":
    sys.exit(main())
