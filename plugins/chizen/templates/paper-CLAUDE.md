# <Paper short title>

<!-- Copy this file to the root of your paper's GitHub repository as CLAUDE.md and fill in
     the <...> parts. Claude Code reads it at the start of every session, and the CHI Zen
     reviewer agents read it before they review. Delete these comments when done. -->

A <full paper / late-breaking work / journal article> for **<venue and year, e.g. CHI 2027>**,
written with the CHI Zen template and its guide (the `chizen` Claude Code plugin,
github.com/JimWallace/CHI-Zen).

- **Authors:** <names and roles; who is the corresponding author>.
- **Deadline:** <date, time and time zone>. Camera-ready: <date, if known>.
- **Length:** <the venue's limit, e.g. CHI 2027 papers: 5,000–8,000 words encouraged, over
  12,000 desk-rejected unless justified, abstract ≤ 150 words>. Check the current call for
  papers.
- **Review:** <anonymous / not anonymous>. Anonymise the paper and all supplementary material
  until camera-ready.
- **Main file:** `<00-my-new-paper.tex>`. Sections are in `<submission/>`, data in `data/`,
  analysis scripts in `<analysis/>`, figures in `figures/`.
- **Contribution type:** <empirical / artifact / methodological / theoretical / dataset /
  survey / opinion> (Wobbrock & Kientz; see the guide's writing.md, WRT-2).
- **Ethics:** <REB number, or "TODO" until known; never invent one>. Data: <what is
  sensitive and must not be quoted or shared>.

## How we work (Overleaf ↔ GitHub ↔ Claude)

The paper is written on Overleaf, which is synced with this GitHub repository (Overleaf:
Menu → GitHub). Claude works on the GitHub copy.

1. Before asking Claude for changes, **push from Overleaf to GitHub** so Claude sees the
   latest text.
2. Claude works on a **branch** and opens a **pull request**; it never pushes to the default
   branch. An author reviews and merges the pull request on GitHub.
3. Then **pull from GitHub into Overleaf**. Overleaf syncs the default branch only, and
   pulling can disturb Overleaf comments and tracked changes, so resolve those first.
4. Keep pull requests small and focused, so they merge cleanly with co-authors' edits.

## Rules for Claude in this repository

1. **Never invent** citations, statistics, data, participant quotes, codes, themes, results or
   REB numbers. Leave a visible `TODO:` for the authors instead.
2. **Propose, don't silently rewrite.** Changes to prose are suggestions in a pull request or
   a comment; explain each with its CHI Zen rule ID.
3. **Keep diffs minimal**: no re-wrapping, reformatting or re-ordering of text you didn't need
   to change.
4. **The decisions below override the CHI Zen guide.** Don't raise them again.
5. **Generative AI:** remind the authors that ACM policy requires disclosing generative-AI use
   as the policy and the venue specify, and keep a note here of how Claude was used.

## Checks

- `python3 <path to>/check_paper.py .` — the CHI Zen linter (with the plugin installed, the
  `chizen:review` skill runs it; in a copied setup it is
  `.claude/skills/chizen-review/scripts/check_paper.py`). Fix new errors and warnings; don't
  add lines to `chizen-baseline.txt` to make them pass.
- `/chizen:review` — the full review: the linter plus four independent reviewer agents.
- The PDF compiles on Overleaf (LuaLaTeX, TeX Live 2026) without warnings. After a local
  `latexmk` (or with Overleaf's log downloaded), `python3 <path to>/warning_ratchet.py <main>`
  (next to `check_paper.py`) lists every LaTeX/BibTeX warning, undefined reference, overfull
  box and `CHIZen Warning`; fix them rather than adding lines to `chizen-warnings-baseline.txt`.

## Author's decisions

<!-- One line each: the decision, who made it, and when. The reviewers skip these. -->
- <e.g. "Figure 3's y-axis starts at 50%: the scale's floor is 50 (Jim, 2026-11-18).">
- <e.g. "We report means and SDs for the SUS score as interval data (Jim, 2026-11-18).">

## Generative-AI use (for the disclosure)

<!-- What Claude (or another tool) was used for, e.g. "copy-editing suggestions on sections 1–3;
     checking citations against Crossref". Update as you go. -->
- <...>
