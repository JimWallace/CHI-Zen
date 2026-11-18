# CHI Zen

Examples, tips and hacks for HCI research papers, built on the ACM `acmart`
class that SIGCHI conferences use. The repository holds two documents:

| File | What it is |
|---|---|
| `CHIZen-Manual.tex` | The CHI Zen manual (inputs `manual/*.tex`, ends with the paper checklist). |
| `00-my-new-paper.tex` | A starter paper for a CHI submission (inputs `submission/`). |
| `CHIZen/init.tex` | Loads the CHI Zen packages: `text`, `figures`, `tables`, `stats`, `accessibility`. |

`acmart` is **not** copied into this repository any more: both documents use the
`acmart` class and its biblatex styles (`acmnumeric`, run with biber) that come
with TeX Live (and so with Overleaf).

## Overleaf settings

Students use Overleaf (the University of Waterloo provides Overleaf for
everyone). Set these once per project, under **Menu > Settings**:

| Setting | Value | Why |
|---|---|---|
| Compiler | **LuaLaTeX** | The documents produce a tagged, accessible PDF. The LaTeX tagging code and `acmart` need LuaLaTeX for full tagging (and for accessible maths). pdfLaTeX still compiles, but the tags are less complete. |
| TeX Live version | **2026** (or later) | Tagging and `acmart`'s tagging support are recent. On an older TeX Live, comment out the `\DocumentMetadata{...}` block at the top of the file. |
| Main document | `00-my-new-paper.tex` (your paper) or `CHIZen-Manual.tex` (the manual) | The manual used to be `CHIZen-Manual-chi2022.tex`. |

With LuaLaTeX, shell escape is not needed: `minted` runs `latexminted`, which
TeX Live allows in restricted mode, and `markdown` runs its Lua code directly.
pdfLaTeX needs shell escape for `markdown`; Overleaf turns it on anyway. `latexmkrc` sets
the same engine for local builds, but Overleaf takes the engine from the
project settings.

## Accessibility: PDF/UA and PDF/A

Both documents start with

```latex
\DocumentMetadata{
  lang          = en,
  pdfstandard   = ua-2,
  pdfstandard   = a-4f,
  tagging       = on,
  tagging-setup = {math/setup=mathml-SE},
}
```

which is what the `acmart` documentation (v2.17 and later) and Overleaf's
TeX Live 2026 announcement recommend. It asks for two different things:

- **PDF/UA** (Universal Accessibility, ISO 14289; here PDF/UA-2) is the
  *accessibility* standard: a tagged PDF with a logical structure (headings,
  lists, tables with header cells, figures with alternative text), a document
  language and a title, so that screen readers can read it.
- **PDF/A** (ISO 19005; here PDF/A-4f) is the *archival* standard: fonts
  embedded, colours device-independent, metadata in XMP, so the file renders
  the same in the future. It says nothing about accessibility on its own.

They are compatible: both are PDF 2.0, and one file can claim both.

**Alt text.** Put one `\Description{...}` at the start of every `figure`,
`figure*` and `subfigure`. `acmart` passes it to ACM's TAPS (for the HTML
version), and CHI Zen also uses it as the alt text of the first picture in the
PDF. A figure with a picture but no `\Description` gives a `CHIZen Warning` in
the log. See the manual's Accessibility section and checklist.

### What validates

Checked with veraPDF 1.30 against PDF/UA-2 and PDF/A-4f, built with LuaLaTeX
on TeX Live 2026 (`acmart` 2.21):

| Document | PDF/UA-2 | PDF/A-4f |
|---|---|---|
| `00-my-new-paper.tex` | passes | passes |
| `CHIZen-Manual.tex` | fails 2 rules, on the 2 figures that use `subfigure` | passes |

PDF/UA validation is necessary, not sufficient: a validator cannot tell whether
alt text is meaningful or the reading order makes sense.

### Package status for tagging

From the LaTeX tagging project's
[tagging status list](https://latex3.github.io/tagging-project/tagging-status/)
(retrieved November 2026), for the packages CHI Zen loads:

| Package | Status | What CHI Zen does |
|---|---|---|
| `subcaption` | currently incompatible | Still loaded. Figures with subfigures get several captions in one float, which fails PDF/UA. Avoid subfigures when you need a valid PDF/UA file. |
| `arydshln` | currently incompatible | Only loaded without tagging. With tagging, `\cdashlinelr` draws a solid `\cmidrule` instead. |
| `pgfplots` | currently incompatible | Loaded. Plots are tagged as one figure with alt text (from `\Description`); their contents are artifacts. Validates. |
| `minted` | currently incompatible | Loaded. Listings are not tagged as code, only as text. Validates. |
| `changes` | currently incompatible | Loaded. Tracked changes are not tagged meaningfully; do not submit a PDF with visible changes as your accessible version. |
| `paracol` | currently incompatible | Loaded, not used by the manual. |
| `markdown` | unchecked | Loaded; the manual and starter validate. |
| `CJK` / `CJKutf8` | only works with pdfTeX | Only loaded with pdfLaTeX. With LuaLaTeX, `\cjk{...}` uses the Harano Aji font from TeX Live. |
| `svg`, `bbding`, `fontawesome5`, `acronym`, `tikz`, `pgfgantt` | partially compatible | Loaded. `bbding` symbols have no Unicode mapping (the manual no longer uses them in figures). |
| `siunitx`, `float`, `multicol`, `colortbl`, `longtable`, `etoolbox`, `savesym`, `letltxmacro`, `lipsum` | compatible | Loaded. |

`inputenc` is no longer loaded (UTF-8 is LaTeX's default), and the old
`accessibility` package must not be used.

### ACM TAPS accepted packages

ACM's TAPS only accepts packages on its
[accepted LaTeX packages list](https://www.acm.org/publications/taps/accepted-latex-packages).
That page could not be retrieved while this was written, so the comparison
below uses the copy of the list (dated October 2019) that used to be in this
repository. Not on that list: `pgfplots`, `pgfplotstable`, `pgfgantt`, `tikz`,
`subcaption`, `svg`, `siunitx`, `etoolbox`, `longtable`, `multicol`,
`colortbl`, `arydshln`, `iftex`, `fontspec`, `CJKutf8`, `markdown`,
`paracol`, `minted`, `fontawesome5`, `savesym`, `changes`, `letltxmacro`,
`lipsum`, `relsize`. Check the current list before submitting a
camera-ready version to TAPS, and remove what you do not use.

## Building locally

```sh
latexmk                       # both documents, with LuaLaTeX (see latexmkrc)
latexmk -lualatex 00-my-new-paper.tex
```

You need a recent TeX Live (2026) and Python for `minted`. GitHub Actions
(`.github/workflows/build.yml`) builds both PDFs on every push, validates them
with veraPDF, and uploads them as an artifact.

## Changes

- 2026: current `acmart` from TeX Live instead of a copy from April 2021;
  CHI 2027 class options; tagged PDF (PDF/UA-2, PDF/A-4f); alt text for every
  figure; accessibility section and checklist items in the manual.
- Version 0.1: initial upload to GitHub.
