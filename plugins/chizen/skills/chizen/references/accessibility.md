# Accessibility

Short rules for an accessible paper. Rule IDs are `A11Y-n`. The mechanics (the
`\DocumentMetadata` block, LuaLaTeX, how CHI Zen turns `\Description` into PDF alt text,
veraPDF) are in the manual, §"Accessibility" and §"Overleaf Settings", and in
`CHIZen/accessibility.tex`. This file only states the rules an agent checks.

CHI asks authors to ensure basic accessibility and points to the SIGCHI Accessibility Guide
for Authors [SIGCHI-A11y]; CHI Zen papers are compiled as tagged PDFs aiming at PDF/UA-2
(accessibility) and PDF/A-4f (archiving), and the CHI Zen repository's CI validates both
documents with veraPDF.

**A11Y-1. Every figure has one `\Description{…}`, as the first thing in the `figure`
environment.** acmart sends it to ACM's TAPS for the HTML version; CHI Zen also uses it as
the alt text of the figure's picture in the tagged PDF and warns (`CHIZen Warning`) when a
figure with a picture has none (manual, §Accessibility). The description is not the
caption: it is an alternative to seeing the figure [SIGCHI-A11y]. Write it from the data:
chart type, axes and ranges, and the values or trends a reader needs. An agent may draft a
description only from the figure's own data file or code, and the author checks it.
`check_paper.py` reports a figure with a picture and no `\Description` as an error.

**A11Y-2. Don't rely on colour alone** in figures and legends: add shapes, patterns, dash
styles or direct labels [SIGCHI-A11y]. (FIG-3, FIG-13.)

**A11Y-3. No subfigures (Jim's decision).** Use separate figures, not `subcaption`
(`\begin{subfigure}`) or `subfig`: `subcaption` is listed as currently incompatible with
tagging [Tagging], and figures with subfigures fail PDF/UA validation (manual,
§Accessibility). `check_paper.py` warns about them. (CHIZen/figures.tex still loads
subcaption for old papers.)

**A11Y-4. Tables are real tables with marked headers** [SIGCHI-A11y]: never an image of a
table; acmart treats the first row as the header, and `\tagpdfsetup{table/header-rows=…}`
marks more; every row has the same number of cells (TAB-8).

**A11Y-5. No `arydshln` dashed rules** (`\hdashline`, `\cdashline`): listed as currently
incompatible with tagging [Tagging]. With tagging on, CHI Zen's `\cdashlinelr` draws a solid
`\cmidrule` instead (TAB-9).

**A11Y-6. RGB colours only.** PDF/A-4f does not allow device CMYK colours without a CMYK
output intent, so define colours in RGB (CHI Zen redefines acmart's CMYK colours in RGB when
tagging is on; see `CHIZen/accessibility.tex`). `check_paper.py` warns about `cmyk`.

**A11Y-7. Structure with markup**: `\section`, `itemize`/`enumerate`, real equations (not
images of equations), meaningful link text ("the SIGCHI Accessibility Guide", not "here"),
and the real title in `\title` [SIGCHI-A11y].

**A11Y-8. For camera-ready, also enter the figure descriptions in PCS** if the venue asks
(manual, §Accessibility).

## Sources

- [SIGCHI-A11y] SIGCHI. Accessibility Guide for Authors.
  https://sigchi.org/resources/guides-for-authors/accessibility/
- [Tagging] LaTeX Project. LaTeX package/class tagging status (retrieved 2026-11-18):
  subcaption and arydshln "currently-incompatible".
  https://latex3.github.io/tagging-project/tagging-status/
- CHI Zen manual, §"Accessibility" and §"Overleaf Settings" (`manual/02-background.tex`),
  and `CHIZen/accessibility.tex`.
