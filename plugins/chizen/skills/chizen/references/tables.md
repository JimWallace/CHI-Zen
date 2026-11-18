# Tables

Rules for tables. Rule IDs are `TAB-n`. The manual's "Tables" section has a worked example.

**TAB-1. If the data fit in a table, consider a table first.** Tables show the data
directly and are easy to read; a skeptical audience may even find them more persuasive than
charts [Pandey2014] (manual, §Tables).

**TAB-2. No vertical rules, no `\hline` grid.** Keep a high data-ink ratio [Tufte]: frame the
table with booktabs (`\toprule`, `\midrule` under the header, `\bottomrule`) and use
`\cmidrule(lr){2-4}` under a header that spans columns. No `|` in the column spec, no
`\hline` or `\cline`, no underlined or boxed headers. `check_paper.py` reports these as
errors.

**TAB-3. Group with whitespace, not lines.** Use `\addlinespace` or an empty row between
groups, and indent sub-rows, rather than adding rules.

**TAB-4. Align numbers on the decimal point and use one precision per column.** Use
siunitx `S` columns (`S[table-format=2.1]`) or right-align (`r`). Give units in the header,
not in every cell: `Time (s)`.

**TAB-5. Keep headers short** and put the explanation in the caption.

**TAB-6. Every table has `\caption`, then `\label`, and is referred to in the text**
(`\autoref{tab:…}`). `TODO(Jim): source` for where ACM wants table captions (above or below
the tabular); not verified this session, so this guide doesn't make it a rule. The caption says what the numbers are
(e.g. "Mean (SD) …") and what marks such as `*` mean.

**TAB-7. Statistics in tables follow [statistics.md](statistics.md)**: *M* (*SD*), *Mdn*,
`\p{}` (no leading zero, nothing below *p* < .001), *F* and χ² to one decimal. Mark
significant differences in the table itself (STAT-13).

**TAB-8. A table is a real table, not an image**, with its header row(s) marked, so the
tagged PDF reads it correctly (SIGCHI accessibility guide; see
[accessibility.md](accessibility.md), A11Y-4). acmart assumes the first row is the header;
for two header rows write `\tagpdfsetup{table/header-rows={1,2}}` before the table. Keep
every row the same number of cells (add empty `&` cells rather than ending a row early).

**TAB-9. No dashed rules from `arydshln`** (`\hdashline`, `\cdashline`): the package is listed
as currently incompatible with tagging [Tagging]. CHI Zen's `\cdashlinelr` draws a solid
`\cmidrule` when tagging is on.

**TAB-10. Use `[tb]` placement** (`\begin{table}[tb]`) so tables float to the top or bottom
of a page, and `table*` for a table that spans both columns.

Minimal example:

```latex
\begin{table}[tb]
  \caption{Mean (SD) selection time and errors by technique (n = 12).}
  \label{tab:time}
  \begin{tabular}{@{}l S[table-format=1.1] S[table-format=1.1] r@{}}
    \toprule
    & \multicolumn{2}{c}{Time (s)} & \\
    \cmidrule(lr){2-3}
    Technique & {M} & {SD} & Errors \\
    \midrule
    Depth cursor & 6.8 & 1.7 & 14 \\
    Tiltcasting  & 4.0 & 0.9 &  9 \\
    \bottomrule
  \end{tabular}
\end{table}
```

(Two header rows here, so this table needs `\tagpdfsetup{table/header-rows={1,2}}` before it.)

Writing tables by hand is tedious; a generator such as https://www.tablesgenerator.com is a
good start, then apply the rules above (manual, §Tables).

## Sources

- [Pandey2014] Anshul Vikram Pandey, Anjali Manivannan, Oded Nov, Margaret Satterthwaite,
  Enrico Bertini. 2014. The Persuasive Power of Data Visualization. *IEEE TVCG* 20(12):
  2211–2220. https://doi.org/10.1109/TVCG.2014.2346419
- [Tufte] Edward R. Tufte. *The Visual Display of Quantitative Information*. Graphics Press,
  1983. https://www.edwardtufte.com/book/the-visual-display-of-quantitative-information/
- [Tagging] LaTeX Project. LaTeX package/class tagging status (retrieved 2026-11-18): arydshln
  "currently-incompatible"; booktabs and siunitx "compatible".
  https://latex3.github.io/tagging-project/tagging-status/
- SIGCHI. Accessibility Guide for Authors.
  https://sigchi.org/resources/guides-for-authors/accessibility/
