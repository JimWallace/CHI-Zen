---
description: Review a LaTeX paper against the CHI Zen lab style guide - runs the deterministic linter (check_paper.py), then four independent read-only reviewer agents in parallel (figures and tables, statistics, writing and framing incl. qualitative reporting and ethics, references and citations), merges their findings and reports them with exact suggested fixes. Read-only unless the author asks for fixes.
when_to_use: For example "review my paper", "is my paper ready to submit", "check my draft against CHI Zen", "run the CHI Zen review", before a deadline or a co-author handoff.
argument-hint: "[paper-dir] [figures|statistics|writing|references|all]"
allowed-tools: Read Grep Glob Agent Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/check_paper.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/warning_ratchet.py *) Bash(git diff *) Bash(git log *) Bash(git status *) Bash(git show *)
---

# Review a paper with CHI Zen

Arguments: `$ARGUMENTS`: an optional paper directory (default: the repository root, or the
directory holding the main `.tex` file) and an optional scope (`figures`, `statistics`,
`writing`, `references`; default `all`).

You coordinate the review; the reviewer agents do the reading. Report findings and propose
fixes. **Don't edit the paper** unless the author asks you to apply specific fixes, and then
only those, as minimal diffs.

## 0. Context
- Read the paper's `CLAUDE.md` if there is one (paper root or repository root): venue, length
  limit, and the **Author's decisions**, which override the general rules. If there is none,
  say that `templates/paper-CLAUDE.md` in the CHI Zen plugin is a starting point.
- Find the main file(s): top-level `.tex` files with `\documentclass`.
- The guide is in `${CLAUDE_SKILL_DIR}/../chizen/references/`. Give its absolute path to each
  reviewer (step 2): they can't find it on their own when the plugin was copied into the
  paper repository.

## 1. Deterministic checks first
Run:

```
python3 ${CLAUDE_SKILL_DIR}/scripts/check_paper.py <paper-dir>
```

(add `--json` to read it programmatically). Errors are definite problems (vertical rules,
`\hline`, *p* with a leading zero, a figure without a caption or `\Description`, …);
warnings are worth fixing; style notes are the checklist's words to avoid and never block.
A `chizen-baseline.txt` in the paper directory lists findings the author has accepted; only
new findings and stale baseline lines fail. Carry the linter's output into the report as is;
don't re-check by hand what it checks.

If the paper has been compiled (its main file's `.log` is in the paper directory, or the
author gives you Overleaf's log), also run the build-warning ratchet on it:

```
python3 ${CLAUDE_SKILL_DIR}/scripts/warning_ratchet.py --dir <paper-dir> <main-file-without-.tex>
```

It lists every LaTeX and BibTeX warning, undefined reference and citation, overfull box and
missing `\Description` (`CHIZen Warning`), against `chizen-warnings-baseline.txt` (add
`'figures/tikz/*'` for the figure runs of draft mode). Report its new warnings under **Fix
first**. Don't compile the paper yourself unless the author asks.

## 2. Independent reviewers, in parallel, in one message
Launch these together. Give each **only**: the paper directory, the main file(s), the path
of the guide's `references/` directory, the path of the paper's `CLAUDE.md` (if any), the
linter's output for its own codes, and the scope. **Don't** give them your own opinion of the
paper: they are useful because they read it fresh.

| Agent | Scope | Linter codes to pass on |
|---|---|---|
| `chizen:chizen-figures` | every figure and table | E-vrule, E-hline, E-float-caption, E-description, W-float-*, W-label-order, W-colour, W-cmyk, W-subfigure, W-arydshln |
| `chizen:chizen-statistics` | every quantitative result, and numbers that must agree across the paper | E-p-*, W-p-precision, W-F-precision, W-chisq-precision, W-stats-trend, W-abstract-number |
| `chizen:chizen-writing` | framing, contribution, prose, qualitative reporting, ethics, transparency, anonymity | S-avoid (summary only), W-todo, W-newpage, W-anon-name, W-anon-id, W-anon-link, W-anon-acks, W-anon-metadata |
| `chizen:chizen-references` | citations and the bibliography | W-taps, W-taps-acmart (camera-ready only), W-anon-selfcite, E-anon-ref |

With a narrower scope argument, launch only that reviewer. Agent names: in a paper repository
that has the agents copied into `.claude/agents/`, they are `chizen-figures`, etc., without
the `chizen:` prefix. If neither form is available, start general-purpose agents instead,
each given the full text of `agents/chizen-<name>.md` (below the front matter) as its
instructions, followed by its inputs.

## 3. Merge
- Collect each reviewer's verdict and table. Remove duplicates (keep the more specific row).
- A finding that conflicts with an **Author's decision** in the paper's `CLAUDE.md` is dropped.
- Two reviewers disagreeing, or a fix that needs information the paper doesn't contain (raw
  data, an REB number, a missing reference), becomes a **question for the author**, not a fix.
- Never turn a finding into a made-up fix: no invented numbers, quotes, citations or DOIs.

## 4. Report
Reply with (and, if asked, write to `chizen-review.md` in the paper directory; never commit it
unless asked):
1. **Summary**: one line per reviewer with its verdict, plus the linter's counts.
2. **Fix first**: errors and FAIL rows, grouped by file, each with `file:line`, the rule ID,
   and the exact suggested change as a small diff.
3. **Worth fixing**: warnings and judgment calls.
4. **Questions for the author**: one line each, answerable yes/no where possible.
5. **Reminders**: ACM's generative-AI disclosure (WRT-13), and that suggestions are
   suggestions: the authors decide.
Put the full reviewer tables in a collapsed `<details>` block.

## 5. Applying fixes (only when asked)
Apply exactly the fixes the author accepts, as minimal diffs (no reformatting), re-run step 1,
and re-run only the reviewer whose findings changed, on only those files. At most two rounds.
On a GitHub copy of an Overleaf project, commit on a branch and open a pull request so the
author can review it before pulling into Overleaf.
