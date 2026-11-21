---
description: CHI Zen, the Waterloo HCI lab's style guide for LaTeX research papers (ACM acmart, pgfplots, siunitx, booktabs). Use when making or editing a figure, a table, a statistics report, qualitative findings or quotes, citations and the bibliography, an ethics or open-science statement, alt text, or when preparing a paper for submission or camera-ready. Loads only the guide section the task needs.
when_to_use: For example "make a bar chart / box plot / Likert figure", "format this table", "report this ANOVA / t-test", "write up the themes", "add the REB statement", "check my citations", "is this ready to submit", "camera-ready for TAPS", matplotlib or ggplot figures for a paper.
---

# CHI Zen: writing a paper the lab's way

You are helping a student write an HCI paper that uses the CHI Zen template (an ACM
`acmart` paper on Overleaf, synced to GitHub). The rules are in `references/`; load only
the file(s) the task needs, then apply their rules and cite their IDs (e.g. `FIG-3`) when
you explain a change.

| Task | Read |
|---|---|
| A figure (pgfplots, or matplotlib/ggplot) | [references/figures.md](references/figures.md) |
| A table | [references/tables.md](references/tables.md) |
| Statistics: tests, effect sizes, reporting, Likert data | [references/statistics.md](references/statistics.md) |
| Qualitative analysis, themes, quotes | [references/qualitative.md](references/qualitative.md) |
| Ethics: REB, consent, online and health data, quoting posts | [references/ethics.md](references/ethics.md) |
| Open materials, data, preregistration, anonymising | [references/transparency.md](references/transparency.md) |
| Citations and the bibliography | [references/references.md](references/references.md) |
| Finding related work (candidates to read) | the `related-work` skill; rules in [references/references.md](references/references.md), REF-13 |
| Framing, contributions, prose, words to avoid | [references/writing.md](references/writing.md) |
| Alt text and the tagged PDF | [references/accessibility.md](references/accessibility.md) |
| Before submission, camera-ready and TAPS | [references/checklist.md](references/checklist.md) |

The matplotlib style and ggplot theme that match the pgfplots styles are in `styles/`
(`${CLAUDE_SKILL_DIR}/styles/chizen.mplstyle`, `${CLAUDE_SKILL_DIR}/styles/theme_chizen.R`).

## Hard rules (always)

1. **Never invent** citations, statistics, data, participant quotes, codes, themes or
   results. If a number, a quote or a reference is needed and you don't have it from the
   authors' files or a record you retrieved, leave a visible `TODO:` for the author and say so.
2. **Propose, don't silently rewrite.** Show changes to the student's prose as a diff or a
   suggested replacement they accept, and explain each with the rule ID. Code-like changes
   (a table's column spec, a pgfplots option, a `\p{}` macro) may be edited directly when the
   student asked for them, still as a small reviewable diff.
3. **Keep diffs minimal**: no reformatting, re-wrapping or re-ordering of text you didn't need
   to touch. Overleaf merges small diffs cleanly; big ones conflict with co-authors' edits.
4. **The paper's `CLAUDE.md` wins.** Read it first if it exists: its venue, page or word
   limit, and its "Author's decisions" override the general rules here. Don't re-raise a
   recorded decision.
5. **Generative-AI disclosure.** When you help with writing or analysis, remind the authors
   once per session that ACM policy requires disclosing generative-AI use as the policy and
   the venue specify (WRT-13).

## After editing

Run the linter on the paper and fix what it reports in the lines you touched:

```
python3 ${CLAUDE_SKILL_DIR}/../review/scripts/check_paper.py <paper-dir>
```

(If this skill was copied into a paper repository as `.claude/skills/chizen`, the script is
at `.claude/skills/chizen-review/scripts/check_paper.py`.) For a full review with the
independent reviewer agents, use the `review` skill.
