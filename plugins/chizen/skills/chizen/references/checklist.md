# Pre-submission checklist

The CHI Zen paper checklist (`manual/CHIZen-Paper-Checklist.tex`), as rules an agent can
check, with the extra items from the other guide files. Use it a week before the deadline
(WRT-11). Items marked ⚙ are checked by `check_paper.py`; the rest need a reader (an
author, a friend, or the `chizen` reviewer agents).

## The big picture ([writing.md](writing.md))
- [ ] The abstract, introduction and related work answer: what problem, who cares, what
      solution, what specific contribution, what findings (WRT-1).
- [ ] The contribution type is named (empirical, artifact, methodological, theoretical,
      dataset, survey, opinion) and the evaluation fits it (WRT-2, WRT-3).
- [ ] Limitations are specific (WRT-5).

## Data collection, analysis and results ([statistics.md](statistics.md), [qualitative.md](qualitative.md))
- [ ] What data was collected, and how (logs, recordings, field notes, questionnaires)?
- [ ] Which qualitative method, which variant, and who did the analysis (QUAL-1, QUAL-4)?
      Reliability reported in a way that fits it (QUAL-2); no unearned saturation claim (QUAL-3).
- [ ] Which quantitative tests (STAT-4)? Alpha stated up front with any corrections and
      transformations (STAT-1, STAT-6); sample size justified (STAT-2).
- [ ] Descriptive statistics and test results with effect sizes and CIs (STAT-7, STAT-8).
- [ ] ⚙ *p* without a leading zero and nothing below *p* < .001; *F* and χ² to one decimal
      (STAT-11); no "trending toward significance" (STAT-9).
- [ ] Significant differences are marked on the figures and tables (FIG-7, STAT-13).

## Figures and tables ([figures.md](figures.md), [tables.md](tables.md))
- [ ] Each figure and table highlights the relevant information and can be (mostly)
      understood without the paper (FIG-10).
- [ ] ⚙ Each has a caption and a label, and is referred to in the text, in number order (FIG-11, TAB-6).
- [ ] Axes labelled with units or scale; non-zero baselines justified (FIG-6).
- [ ] Legible when printed, in black and white (FIG-3, FIG-5, FIG-13).
- [ ] ⚙ Colours from the CHI Zen palettes (FIG palette rules); no vertical rules or `\hline` (TAB-2).

## Accessibility ([accessibility.md](accessibility.md))
- [ ] ⚙ Every figure has a `\Description` that describes the data, not the caption (A11Y-1).
- [ ] ⚙ No subfigures, no `arydshln`, no CMYK colours (A11Y-3, A11Y-5, A11Y-6).
- [ ] Tables have marked header rows; link text is meaningful (A11Y-4, A11Y-7).
- [ ] The tagged PDF compiles with LuaLaTeX without a `CHIZen Warning` in the log.

## References ([references.md](references.md))
- [ ] The reference list has been checked thoroughly: every entry real, with a DOI where one
      exists, no duplicates (REF-7, REF-9, REF-10).
- [ ] Authors' names in the text are spelled correctly (REF-7).
- [ ] Citations follow the YES/NO table (REF-1 to REF-6).

## Ethics and transparency ([ethics.md](ethics.md), [transparency.md](transparency.md))
- [ ] REB approval and consent are stated (ETH-1, ETH-2).
- [ ] Quotes from public online posts are protected from being searched back (ETH-3, ETH-4);
      every quote and description is de-identified (ETH-5).
- [ ] Materials, data and code are shared, or the paper says why not (TRN-1, TRN-2).
- [ ] Everything, including supplementary material, is anonymised for review (TRN-5).
- [ ] Generative-AI use is disclosed as ACM policy and the venue require (WRT-13).

## Venue
- [ ] The current call for papers has been read. For CHI 2027 papers: submissions of 5,000
      to 8,000 words are encouraged; above 12,000 words is desk-rejected unless the length is
      justified; the abstract is 150 words or fewer [CHI2027]. Record the venue's limits in
      the paper's `CLAUDE.md`.
- [ ] ⚙ No TODO markers left in the text; no forced page breaks (`\newpage`).

## Before you submit (WRT-11)
- [ ] **1 week before:** you checked the paper against everything above.
- [ ] **1 week before:** a friend checked it too.
- [ ] **1 day before:** co-authors confirmed everything is ready.
- [ ] **After the deadline:** co-authors got a copy of the submitted PDF.

## Camera-ready: ACM TAPS

**CHECK-TAPS. The source you upload to TAPS may only load packages on ACM's accepted list.**
After acceptance, ACM's TAPS builds the published paper from your LaTeX source and generates
both the PDF and an HTML5 version, so it must be able to process every package; CHI tells
authors to "Remove packages that are not listed as the source will not be processed on upload
to TAPS" [CHI2025-TAPS]. Packages that acmart already loads must not be loaded again (the
list's own instruction). The list, copied from ACM's page (last updated April 2025), is in
`CHIZen/taps-accepted-packages.txt`; ⚙ `check_paper.py` warns about every package that is not
on it (W-taps) or that acmart already loads (W-taps-acmart).

The CHI Zen library loads several packages that are not on the list (pgfplots, TikZ via
pgfplots, minted, markdown, biblatex and others), so the camera-ready workflow is:

1. **Write figures in pgfplots** as usual, and **externalise** them: each figure is built once
   into its own PDF under `figures/tikz/` (CHI Zen's figure macro,
   `\chizenfigure` — `TODO(Jim): confirm macro name` — does this in draft mode).
2. **Switch to final mode** for camera-ready. In final mode the figures are included as the
   pre-built PDFs with `\includegraphics` (on the list), and pgfplots/TikZ are not loaded.
   The manual describes the switch (`TODO(Jim): confirm the name of the draft/final switch
   and the manual section`).
3. **Use `listings`, not `minted`, for code**, and **no `markdown` environments** in the final
   source: neither package is on the list.
4. **Use BibTeX with `ACM-Reference-Format`**, not biblatex (REF-8).
5. Remove the `manuscript`, `review` and `anonymous` class options as the venue's
   camera-ready instructions say, and de-anonymise (TRN-5).
6. Run `check_paper.py` and fix every W-taps and W-taps-acmart finding in the files TAPS will
   receive. Then check both the PDF and the HTML5 output TAPS returns [CHI2025-TAPS].

## Sources

- CHI Zen checklist (`manual/CHIZen-Paper-Checklist.tex`).
- [CHI2027] ACM CHI 2027. Papers (call for papers). https://chi2027.acm.org/authors/papers/
  (retrieved 2026-11-18)
- [CHI2025-TAPS] ACM CHI 2025. Publication-Ready Author Instructions ("TAPS will generate PDF
  and HTML5 outputs"; "Remove packages that are not listed as the source will not be
  processed on upload to TAPS").
  https://chi2025.acm.org/for-authors/publication-ready-author-instructions/
- ACM. The ACM Publishing System (TAPS) List of Accepted LaTeX Packages (last updated April
  2025). https://authors.acm.org/proceedings/production-information/accepted-latex-packages
  (copied into `CHIZen/taps-accepted-packages.txt` as pasted by Jim).
