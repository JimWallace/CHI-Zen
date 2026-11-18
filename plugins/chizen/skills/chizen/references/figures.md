# Figures

Rules for data figures in a CHI Zen paper. Each rule has an ID (`FIG-n`) that reviewers cite.
The LaTeX manual (`CHIZen-Manual.tex`, section "Figures") is the gallery of worked examples;
this file is the rulebook. The styles live in `CHIZen/figures.tex`.

Figures are a reader's first impression of a paper and a "visual abstract" of its results
(manual, §Figures). The style follows Tufte's minimalist presentation of quantitative data
[Tufte] and the rules of thumb in Munzner's *Visualization Analysis and Design*, ch. 6
[Munzner].

## Principles

**FIG-1. Show the data.** Prefer a plot that shows the distribution (points, box plots,
diverging stacked bars) over a bar of means with error bars. Summary bars hide the shape of
the data, and very different distributions can produce the same bar [Weissgerber].
If you do show a summary, say in the caption what it summarises: the statistic, *n*, and
what the error bars are (SD, SE or a 95% CI).

**FIG-2. High data-ink ratio** [Tufte]. Remove ink that carries no data:
- thin axis lines (`axis line style = very thin`);
- only the left and bottom axes (`axis lines* = left`), no closed frame;
- light horizontal grid lines only (`ymajorgrids`);
- no tick marks on a categorical x axis (`major x tick style = transparent`);
- no 3-D, shadows, gradients or background fills.
A Tufte range frame (`range frame`) is fine.

**FIG-3. Get it right in black and white** [Munzner, ch. 6]. Series must be distinguishable
without colour: vary the dash pattern or the marker, or label each series directly. Fills
get a darker outline of the same hue (the CHI Zen cycle lists draw `<colour>!50!black`).
The SIGCHI accessibility guide says the same: "Don't rely only on colour" [SIGCHI-A11y].

**FIG-4. Eyes beat memory** [Munzner, ch. 6]. Put the legend next to what it labels, or
better, label lines directly. In CHI Zen the legend sits centred below the x-axis label,
without a border (`draw=none`), in up to 3–4 columns.

**FIG-5. Readable at print size.** Sans-serif text in the figure (`font = \sffamily`).
Nothing smaller than about `\scriptsize` at final size. Rotate tick labels only when they
would otherwise overlap (45°).

**FIG-6. Every axis is labelled with its unit or scale**, e.g. `Selection time (s)`,
`Responses (%)`. A bar chart's value axis starts at 0; any other axis that does not start at
0 needs a reason, stated in the caption.

**FIG-7. Mark significant differences on the figure itself** (asterisks or brackets), and say
in the caption what the marks mean and which test produced them (checklist, "Data
collection, analysis and results").

**FIG-8. Read numbers from a data file, not typed coordinates.** Put the data in
`data/*.csv` and read it with `\pgfplotstableread[col sep=comma]{data/x.csv}\mytable` or
`table [col sep=comma, x=…, y=…] {data/x.csv}`. The figure then updates with the analysis and
a reviewer can check it. Never invent, round off or "smooth" data to improve a figure.

**FIG-9. One figure, one environment.** Use separate `figure` environments, not
`subcaption`/`subfigure`: subfigures break the tagged (PDF/UA) PDF (see
[accessibility.md](accessibility.md), rule A11Y-3). Put related plots side by side inside
one `tikzpicture` (two `axis` environments or a `groupplot`) with one caption.

## Captions and references

**FIG-10. The caption makes the figure self-contained.** It says what is plotted, the unit,
the sample (*n*), what marks and error bars mean, and the take-away. It does not have to
repeat the text, but the figure should be (mostly) understandable without it (checklist,
"Figures and tables").

**FIG-11. Every figure has `\caption`, then `\label`, and is referred to in the text**
(`\autoref{fig:…}`), in the order the figures are numbered. `\label` after `\caption`,
or `\ref` gives the section number. `check_paper.py` checks all three.

**FIG-12. Every figure has `\Description{…}`** (alt text). See [accessibility.md](accessibility.md).

## Choosing a style

`CHIZen/init.tex` loads the styles. Use the style by name in the axis options and add only
what the figure needs (labels, limits, ticks).

| Data | Style | Notes |
|---|---|---|
| Comparing conditions (one value per condition) | `chizen bar` | Clustered bars; `okabe-ito` fills with darker outlines; legend below the x label. Prefer `chizen box` when you have the raw data (FIG-1). |
| Parts of a whole per condition | `chizen stacked bar` | Same layout as `chizen bar`. |
| Distributions per condition | `chizen box` (preferred) | Filled boxes, white median line, single-line whiskers, outliers as dots. Put conditions side by side with `lshift`/`rshift`. |
| Distributions, minimal | `chizen tufte box` | Tufte's box plot: a dot for the median and whiskers, no box. |
| Likert responses | `chizen Likert` | Diverging stacked bars centred on neutral, x from −100 to 100 % with "← Disagree / Agree →" labels [Heiberger]. Use the ColorBrewer diverging colours (`Likert5_*`, `Likert7_*`). |
| Trends over time | `chizen line` | `chizen lines` cycle: colour **and** dash pattern **and** marker differ per series. For dense data add `no markers`. |
| Several trends or categories over time | `groupplot` + `chizen tufte panel` or `chizen line` | Small multiples with shared axes (`x descriptions at=edge bottom`). |
| Flow of records (systematic review) | TikZ PRISMA diagram | See the manual's PRISMA example. |
| Schedule | `pgfgantt` | See the manual's Gantt example. |

The old names (`IDEA bar`, `IDEA lines`, …) still work as aliases. Use the `chizen` names in
new figures.

Minimal bar chart from a CSV file:

```latex
\begin{figure}
  \Description{Bar chart of mean selection time in seconds for three techniques: ...}
  \begin{tikzpicture}
    \begin{axis}[chizen bar,
        xlabel = {Technique}, ylabel = {Selection time (s)},
        ymin = 0, symbolic x coords = {Depth, Tilt, Smart}, xtick = data]
      \addplot table [col sep=comma, x=technique, y=mean] {data/time.csv};
    \end{axis}
  \end{tikzpicture}
  \caption{Mean selection time by technique (n = 12; error bars: 95\% CI).}
  \label{fig:time}
\end{figure}
```

Two conditions as box plots, side by side:

```latex
\begin{axis}[chizen box, ylabel = {Heart rate ($z$)}, xtick = {1,2,3},
             xticklabels = {Baseline, Stressor, Game}]
  \addplot+[boxplot, lshift] table [y=P0_HR] {\nature};  % first condition
  \addplot+[boxplot, rshift] table [y=P0_HR] {\urban};   % second condition
\end{axis}
```

## Palettes

Colours come from the palettes in `CHIZen/figures.tex`, never ad-hoc mixes such as
`blue!70!black` (`check_paper.py` warns about xcolor names and `\definecolor` in a paper).
Choose a palette with `cycle list name = …`.

| Cycle list | Use | Greyscale |
|---|---|---|
| `okabe-ito` (default for bar, stacked bar, box, panel) | Categorical data. Distinguishable with the common forms of colour blindness [Okabe-Ito]. | **Not** greyscale-safe: orange and sky blue print as the same grey. |
| `chizen lines` (default for `chizen line`) | Lines. Okabe–Ito colours, darkest first, plus dash pattern and marker per series; yellow left out (too faint as a thin line). | Safe: dashes and markers differ. |
| `waterloo-light`, `waterloo-dark` | University of Waterloo faculty colours; AHS (Faculty of Health) first. | Not safe: ArtsLight ≈ SchoolRedLight, MathLight ≈ ScienceLight; most of `waterloo-dark` prints as one grey. |
| `colorbrewer-RYB` | ColorBrewer qualitative. | Not safe. RYB2 (pale yellow) is almost invisible on white: use this list, which outlines fills, not `colorbrewer-RYB-plain`. |
| `Likert5_*`, `Likert5_2_*`, `Likert7_*` colours | Diverging (Likert) scales: two hues meeting at a light neutral. | Order is carried by position, so greyscale is acceptable. |

Okabe–Ito RGB values as defined in `CHIZen/figures.tex`: orange 230,159,0 · sky blue
86,180,233 · bluish green 0,158,115 · yellow 240,228,66 · blue 0,114,178 · vermillion
213,94,0 · reddish purple 204,121,167 · black 0,0,0.

**FIG-13. Colour is never the only cue.** Since no categorical palette is greyscale-safe,
pair colour with marks, dash patterns, hatching or direct labels (FIG-3).

**FIG-14. Don't use rainbow colour maps** for ordered data: their uneven lightness creates
false boundaries and they are unreadable with colour-vision deficiencies [Crameri]. Use a
sequential or diverging map.

**FIG-15. Use colour for meaning, not decoration.** One emphasis colour on a grey figure is
often enough (the manual's Tufte panel example).

## Figures made outside LaTeX

Prefer pgfplots reading a CSV file (FIG-8). When a figure must come from Python or R (a
complex model plot, a map), make it match the CHI Zen style with the files in this skill's
`styles/` folder, and include it as a vector PDF:

- **matplotlib:** `styles/chizen.mplstyle` and the example `styles/example_matplotlib.py`.
  `plt.style.use("path/to/chizen.mplstyle")`, then put the legend below the plot with
  `fig.legend(loc="outside lower center", ncols=3)` on a figure made with
  `layout="constrained"`.
- **ggplot2:** `styles/theme_chizen.R` (`theme_chizen()`, `scale_colour_chizen()`,
  `scale_fill_chizen()`) and the example `styles/example_ggplot.R`.

Both give: sans-serif text at 8 pt, left and bottom axes only, a light horizontal grid,
the Okabe–Ito colours in the `chizen lines` order, and the legend below without a frame.
Size the figure at its final size (one ACM column is 241 pt ≈ 3.3 in wide; CHI Zen figures
are 6 cm ≈ 2.4 in tall) so the text is not scaled, and save as PDF:

```latex
\begin{figure}
  \Description{...}
  \includegraphics[width=\columnwidth]{figures/model.pdf}
  \caption{...}
  \label{fig:model}
\end{figure}
```

Keep the script and its data in the repository (e.g. `analysis/`), so the figure can be
regenerated and reviewed.

## Camera-ready: pre-built figure PDFs

**FIG-16. Write figures in pgfplots, externalise them, and switch to final mode for
camera-ready.** pgfplots and TikZ are not on ACM's TAPS list of accepted packages, so the
source you upload to TAPS must include figures as pre-built PDFs. CHI Zen's figure macro
(`\chizenfigure`, `TODO(Jim): confirm macro name`) builds each figure into
`figures/tikz/<name>.pdf` while you draft; the final switch includes those PDFs with
`\includegraphics` instead. Keep the pgfplots source and the data in the repository: the
PDFs are build products. The steps are in [checklist.md](checklist.md), CHECK-TAPS, and the
mechanics in the manual (`TODO(Jim): confirm the manual section`).

## Sources

- [Tufte] Edward R. Tufte. *The Visual Display of Quantitative Information*. Graphics Press,
  1983 (2nd ed. 2001). https://www.edwardtufte.com/book/the-visual-display-of-quantitative-information/
- [Munzner] Tamara Munzner. *Visualization Analysis and Design*. A K Peters/CRC Press, 2014.
  https://doi.org/10.1201/b17511 (ch. 6, rules of thumb, as cited in the manual)
- [Weissgerber] Tracey L. Weissgerber, Natasa M. Milic, Stacey J. Winham, Vesna D. Garovic.
  2015. Beyond Bar and Line Graphs: Time for a New Data Presentation Paradigm. *PLOS Biology*
  13(4): e1002128. https://doi.org/10.1371/journal.pbio.1002128
- [Heiberger] Richard M. Heiberger, Naomi B. Robbins. 2014. Design of Diverging Stacked Bar
  Charts for Likert Scales and Other Applications. *Journal of Statistical Software* 57(5).
  https://doi.org/10.18637/jss.v057.i05
- [Okabe-Ito] Masataka Okabe, Kei Ito. Color Universal Design (CUD): How to make figures and
  presentations that are friendly to colorblind people. 2002, revised 2008.
  https://jfly.uni-koeln.de/color/
- [Crameri] Fabio Crameri, Grace E. Shephard, Philip J. Heron. 2020. The misuse of colour in
  science communication. *Nature Communications* 11: 5444.
  https://doi.org/10.1038/s41467-020-19160-7
- [SIGCHI-A11y] SIGCHI. Accessibility Guide for Authors.
  https://sigchi.org/resources/guides-for-authors/accessibility/
