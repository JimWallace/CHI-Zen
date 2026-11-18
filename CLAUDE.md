# CHI Zen

Jim Wallace's HCI lab style guide (University of Waterloo, Faculty of Health) and ACM paper
template. This file is for people and agents changing CHI Zen itself; students writing a
paper use the `chizen` plugin and their paper's own `CLAUDE.md` (template:
`plugins/chizen/templates/paper-CLAUDE.md`).

## What's where

| Path | What |
|---|---|
| `CHIZen/` | The LaTeX library a paper loads with `\input{CHIZen/init.tex}`: `figures.tex` (pgfplots styles and palettes), `stats.tex` (reporting macros), `tables.tex`, `text.tex`, `accessibility.tex` (`\Description` → PDF alt text). `taps-accepted-packages.txt` is ACM's TAPS package list, read by the linter. |
| `CHIZen-Manual.tex`, `manual/*.tex` | The manual: the **gallery** of worked examples. Ends with the paper checklist (`manual/CHIZen-Paper-Checklist.tex`). |
| `00-my-new-paper.tex`, `submission/` | The starter paper students copy. |
| `data/` | CSV data for the manual's figures. |
| `.claude-plugin/marketplace.json` | Makes this repository the `chizen` Claude Code marketplace. |
| `plugins/chizen/` | The plugin: `skills/chizen/` (authoring skill; **the guide** in `references/*.md`, matplotlib/ggplot styles in `styles/`), `skills/review/` (review skill; the linter `scripts/check_paper.py`), `agents/` (four read-only reviewers), `templates/` (paper `CLAUDE.md`, `settings.json`), `scripts/copy_into_paper.py`. |
| `tests/` | Linter and copy-script tests, with fixture papers and expected output. |
| `chizen-baseline.txt` | Linter findings accepted for the manual and starter paper. Only shrinks. |
| `.github/workflows/build.yml` | Builds both PDFs (LuaLaTeX and pdfLaTeX, TeX Live 2026) and validates PDF/UA-2 and PDF/A-4f with veraPDF. |
| `.github/workflows/checks.yml` | Linter tests, the linter on the manual and starter, `claude plugin validate`, the style examples. |

## Guide and gallery

The Markdown guide in `plugins/chizen/skills/chizen/references/` is the **single source of
truth** for the rules (rule IDs like `FIG-3`, `STAT-11`). The LaTeX manual is the gallery: it
shows the rules working and should link to the guide rather than restate rules in different
words (pointing the manual's sections at the guide is a follow-up).
It lives inside the plugin directory because an installed plugin is copied and can't read
files outside it.

When a rule changes, change it in the guide first, then the gallery example, the reviewer agent
that checks it, and `check_paper.py` if it is deterministic, in the same pull request.

## Hard rules

1. **Never invent** citations, statistics, data, participant quotes or results, in the guide,
   the manual or a fixture. Every literature claim or venue rule in the guide cites a source
   retrieved and checked (DOI record, publisher or venue page) when it was written; if it
   can't be verified, leave it out or write `TODO(Jim): source`.
2. **Agents propose; authors decide.** Skills and agents suggest changes to a student's prose
   as diffs or comments and never silently rewrite it. Reviewer agents are read-only.
3. **Keep diffs minimal**: no reformatting, re-wrapping or re-ordering of lines you didn't need
   to change. Overleaf users merge these files.
4. **The paper's `CLAUDE.md` wins** over the guide for that paper ("Author's decisions").
5. Skills and agents **remind authors to disclose generative-AI use** as ACM policy and the
   venue require (guide: `writing.md`, WRT-13).
6. **Style names: `chizen …`, with `IDEA …` aliases.** The pgfplots styles are `chizen bar`,
   `chizen stacked bar`, `chizen box`, `chizen tufte box`, `chizen tufte panel`, `chizen line`,
   `chizen Likert` and the `chizen lines` cycle list. The old `IDEA …` names are aliases at
   the end of `CHIZen/figures.tex` so existing papers compile; never remove one while the
   manual, the starter or a known paper uses it. New text and examples use `chizen` names.
7. Don't put personal data (emails, student names, private feedback) in this public
   repository.

## Checks

```sh
python3 -m unittest discover -s tests                         # linter and copy-script tests
python3 plugins/chizen/skills/review/scripts/check_paper.py .  # the linter on the manual + starter
claude plugin validate . && claude plugin validate plugins/chizen
latexmk                                                        # both PDFs (LuaLaTeX; see latexmkrc)
```

- A new linter finding in the manual or starter: fix it (if you own that file) rather than
  adding a baseline line; a fixed one: `check_paper.py . --prune-baseline`.
- A linter change: update `tests/fixtures/*/expected.txt` and say why in the commit.
- `PALETTE_COLOURS` in `check_paper.py` must match the `\definecolor`s in `CHIZen/figures.tex`
  (a test checks).
- `claude plugin validate` warns that the plugin has no `version`: deliberate, so installs
  follow the latest commit.
- CI is the reference for the LaTeX build (TeX Live 2026, like Overleaf).
- Next step (not done yet): a LaTeX/biber build-warning ratchet like the CV repository's
  `scripts/warning_ratchet.py`.
