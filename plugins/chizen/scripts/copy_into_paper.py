#!/usr/bin/env python3
"""Copy the CHI Zen skills and agents into a paper repository's .claude/ directory.

Use this where the plugin can't be installed: Claude Code on the web (claude.ai/code) and
other cloud sessions don't install plugins, not even ones a repository enables in
.claude/settings.json, but they do load skills and agents committed to the repository.

    python3 copy_into_paper.py PAPER_DIR          # copy (or update) and list what changed
    python3 copy_into_paper.py PAPER_DIR --check  # exit 1 if the copy is missing or stale

It writes, replacing earlier copies:
    PAPER_DIR/.claude/skills/chizen/          the guide (authoring skill)
    PAPER_DIR/.claude/skills/chizen-review/   the review skill, check_paper.py, warning_ratchet.py
    PAPER_DIR/.claude/skills/chizen-related-work/   the related-work skill, find_papers.py
    PAPER_DIR/.claude/agents/chizen-*.md      the four reviewer agents
Commit them; re-run after CHI Zen updates. Nothing else in .claude/ is touched.
"""
from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
COPIES = [  # (source in the plugin, destination under PAPER_DIR/.claude)
    (PLUGIN / "skills" / "chizen", Path("skills") / "chizen"),
    (PLUGIN / "skills" / "review", Path("skills") / "chizen-review"),
    (PLUGIN / "skills" / "related-work", Path("skills") / "chizen-related-work"),
]
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pdf")


def same_tree(a: Path, b: Path) -> bool:
    if not b.is_dir():
        return False
    cmp = filecmp.dircmp(a, b, ignore=["__pycache__"])
    if cmp.left_only or cmp.right_only or cmp.funny_files:
        return False
    _, mismatch, errors = filecmp.cmpfiles(a, b, cmp.common_files, shallow=False)
    return not mismatch and not errors and all(same_tree(a / d, b / d) for d in cmp.common_dirs)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paper", type=Path)
    ap.add_argument("--check", action="store_true", help="only report whether the copy is current")
    args = ap.parse_args(argv)
    claude = args.paper / ".claude"
    if not args.paper.is_dir():
        print(f"{args.paper} is not a directory", file=sys.stderr)
        return 2

    stale = []
    for src, dst in COPIES:
        if not same_tree(src, claude / dst):
            stale.append(dst.as_posix())
    agents = sorted((PLUGIN / "agents").glob("*.md"))
    for a in agents:
        dst = claude / "agents" / a.name
        if not dst.is_file() or not filecmp.cmp(a, dst, shallow=False):
            stale.append(f"agents/{a.name}")

    if args.check:
        for s in stale:
            print(f"out of date: .claude/{s}")
        return 1 if stale else 0

    for src, dst in COPIES:
        target = claude / dst
        if target.exists():
            shutil.rmtree(target)
        # symlinks=False copies the files that symlinks point to (the TAPS list).
        shutil.copytree(src, target, symlinks=False, ignore=IGNORE)
    (claude / "agents").mkdir(parents=True, exist_ok=True)
    for a in agents:
        shutil.copyfile(a, claude / "agents" / a.name)
    print("Updated:" if stale else "Already current:")
    for s in stale or [d.as_posix() for _, d in COPIES]:
        print(f"  .claude/{s}")
    print("Commit .claude/ so cloud sessions (claude.ai/code) load CHI Zen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
