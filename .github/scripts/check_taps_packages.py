#!/usr/bin/env python3
"""Check that a final-mode build of a CHI Zen paper loads only packages
that ACM's TAPS accepts.

Usage (after compiling the paper in final mode with -recorder, which
latexmk does by default):

    python3 .github/scripts/check_taps_packages.py final-check.tex \
        [--engine lualatex] [--list CHIZen/taps-accepted-packages.txt]

Three checks:

1. Every package the paper itself asks for (\\usepackage between
   \\input{CHIZen/init.tex} and \\begin{document}; final mode logs them as
   "CHIZen TAPS package: [options]{name}") is in the [accepted] section of
   the list.
2. None of them is one acmart already loads: neither one in the list's
   [included-in-acmart] section nor one that a document with the paper's
   own \\DocumentMetadata and \\documentclass lines loads (probe 1).
3. Nothing else was loaded: every .sty/.cls in the paper's .fls is
   loaded by acmart (probe 1), or is an accepted package from check 1, or
   was loaded by one of those (final mode logs these as "CHIZen TAPS
   dependency: {name} of {package}"). This catches e.g.
   \\RequirePackage{tikz} in the preamble.

Exit status 0 if all pass, 1 otherwise. Writes a Markdown report to
$GITHUB_STEP_SUMMARY when that is set.
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REQ_RE = re.compile(r"^CHIZen TAPS package: \[(.*)\]\{(.+)\}\s*$")
DEP_RE = re.compile(r"^CHIZen TAPS dependency: \{(.+)\} of \{(.*)\}\s*$")


def read_list(path):
    sections = {}
    current = None
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        m = re.fullmatch(r"\[(.+)\]", line)
        if m:
            current = sections.setdefault(m.group(1), set())
        elif current is None:
            sys.exit(f"{path}: package name before the first [section]: {line}")
        else:
            current.add(line)
    for name in ("accepted", "included-in-acmart"):
        if name not in sections:
            sys.exit(f"{path}: no [{name}] section")
    return sections


def requested_packages(log_path):
    """[(name, options)] the paper asked for, and {dependency: top-level package}."""
    reqs, deps = [], {}
    for line in Path(log_path).read_text(encoding="utf-8", errors="replace").splitlines():
        m = REQ_RE.match(line)
        if m:
            reqs.append((m.group(2).strip(), m.group(1).strip()))
        m = DEP_RE.match(line)
        if m:
            deps.setdefault(m.group(1).strip(), set()).add(m.group(2).strip())
    return reqs, deps


def loaded_packages(fls_path):
    """Names of the .sty/.cls files a run read, from its .fls file."""
    names = set()
    for line in Path(fls_path).read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("INPUT "):
            p = line[6:].strip()
            if p.endswith((".sty", ".cls")):
                names.add(os.path.basename(p))
    return names


def preamble_head(tex_path):
    """The paper's lines up to and including \\documentclass[...]{...}."""
    out = []
    for line in Path(tex_path).read_text(encoding="utf-8").splitlines():
        out.append(line)
        if re.match(r"\s*\\documentclass\b", line):
            return "\n".join(out) + "\n"
    sys.exit(f"{tex_path}: no \\documentclass line")


def run_probe(engine, head, workdir, name):
    tex = Path(workdir) / f"{name}.tex"
    tex.write_text(head + "\\begin{document}\nProbe.\n\\end{document}\n", encoding="utf-8")
    cmd = [engine, "-recorder", "-interaction=nonstopmode", "-halt-on-error", tex.name]
    r = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True, errors="replace")
    fls = Path(workdir) / f"{name}.fls"
    if r.returncode != 0 or not fls.exists():
        print(r.stdout[-3000:])
        sys.exit(f"probe {name} failed to compile")
    return loaded_packages(fls)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("tex", help="the paper's main .tex file, already compiled in final mode")
    ap.add_argument("--engine", default="lualatex")
    ap.add_argument("--list", default="CHIZen/taps-accepted-packages.txt")
    args = ap.parse_args()

    tex = Path(args.tex)
    log, fls = tex.with_suffix(".log"), tex.with_suffix(".fls")
    for f in (log, fls):
        if not f.exists():
            sys.exit(f"{f} not found: compile {tex} first (with -recorder)")
    lists = read_list(args.list)
    accepted, in_acmart_list = lists["accepted"], lists["included-in-acmart"]

    if not re.search(r"^CHIZen: final mode", log.read_text(encoding="utf-8", errors="replace"), re.M):
        sys.exit(f"{log}: not a final-mode build (no 'CHIZen: final mode' line)")
    reqs, deps = requested_packages(log)

    head = preamble_head(tex)
    with tempfile.TemporaryDirectory() as tmp:
        acmart_pkgs = run_probe(args.engine, head, tmp, "probe-acmart")
    paper_pkgs = loaded_packages(fls)
    ok_top = {p for p, _ in reqs if p in accepted}
    closure = set(acmart_pkgs) | {f"{p}.sty" for p in ok_top}
    closure |= {f"{d}.sty" for d, parents in deps.items() if parents & ok_top}

    errors = []
    rows = []
    for pkg, opts in reqs:
        if pkg in in_acmart_list or f"{pkg}.sty" in acmart_pkgs:
            status = "NOT OK: acmart already loads it; remove the \\usepackage"
            errors.append(f"{pkg}: acmart already loads it")
        elif pkg in accepted:
            status = "ok: on ACM's accepted list"
        else:
            status = "NOT OK: not on ACM's accepted list"
            errors.append(f"{pkg}: not on ACM's accepted list ({args.list})")
        rows.append((pkg, opts, status))

    extra = sorted(paper_pkgs - closure)
    for f in extra:
        errors.append(f"{f}: loaded, but neither by acmart nor by an accepted package")

    lines = ["## TAPS package check (final mode)", "",
             f"Paper: `{tex}`; list: `{args.list}`", "",
             "| Package | Options | Result |", "|---|---|---|"]
    lines += [f"| {p} | {o or ''} | {s} |" for p, o, s in rows]
    lines += ["", f"Files read: {len(paper_pkgs)} .sty/.cls; acmart alone: {len(acmart_pkgs)}; "
              f"acmart, the accepted packages above and what they load: {len(closure)}."]
    if extra:
        lines += ["", "Loaded by neither acmart nor an accepted package:", ""]
        lines += [f"- `{f}`" for f in extra]
    lines += ["", "**PASS**" if not errors else "**FAIL**"]
    report = "\n".join(lines) + "\n"
    print(report)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fh:
            fh.write(report)
    for e in errors:
        print(f"::error::TAPS package check: {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
