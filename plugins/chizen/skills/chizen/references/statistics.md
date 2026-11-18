# Statistics

Rules for planning, running and reporting quantitative analyses. Rule IDs are `STAT-n`.
The reporting macros are in `CHIZen/stats.tex`; the manual's "Reporting Measurements and
Statistics" section shows them typeset.

**Never invent or "tidy" a number.** Every statistic in the paper comes from the authors'
analysis output. An agent that cannot see that output asks for it; it does not fill in a
value, a degree of freedom or an effect size.

## Before the analysis

**STAT-1. State alpha up front**, in the method, once: "We used α = .05 for all tests."
Also state any correction for multiple comparisons and any data transformation
(checklist, "Data collection, analysis and results").

**STAT-2. Justify the sample size.** Say how *n* was chosen: an a-priori power analysis
(with the effect size it assumed and where that came from), a desired precision, resource
constraints, or a local standard for the method, and say so honestly when there was no
formal justification [Lakens2022]. At CHI 2014 sample sizes ranged widely and the most common
was 12 [Caine2016], so "we followed common practice" needs a citation and a reason.

**STAT-3. Separate planned from exploratory analyses.** Report which hypotheses and
analyses were planned (ideally preregistered, see [transparency.md](transparency.md)) and
label everything else as exploratory [Cockburn2018].

## Choosing a test

| Design and data | Test | Effect size to report |
|---|---|---|
| Two independent groups, continuous, roughly normal | Welch's *t*-test | Cohen's *d* (or Hedges' *g*) with 95% CI |
| Two independent groups, ordinal or non-normal | Mann–Whitney *U* | *r* = *Z*/√*N*, or the rank-biserial correlation |
| Two paired conditions, continuous | paired *t*-test | *d* for paired data (say which) [Lakens2013] |
| Two paired conditions, ordinal or non-normal | Wilcoxon signed-rank | *r* |
| One or more factors, continuous | (RM-)ANOVA; Greenhouse–Geisser if sphericity fails | η²<sub>p</sub> or generalized η² |
| Factorial design, nonparametric (Likert items, error counts) | Aligned Rank Transform (ART) ANOVA [Wobbrock2011]; ART-C for post hoc contrasts, since contrasts on ART-aligned data give incorrect results [Elkin2021] | η²<sub>p</sub> |
| Repeated measures with unbalanced or missing data, or crossed random effects (participants × items) | Linear mixed model, e.g. `lme4` [Bates2015]; generalized LMM for counts and binary outcomes | Model estimates with 95% CIs; say how *p* was computed |
| Categorical outcome by group | χ² test of independence (Fisher's exact test for small expected counts) | Cramér's *V* |

**STAT-4. Name the test, the software and the model.** "A two-way repeated-measures ANOVA
(R 4.4, `afex`)" or "a linear mixed model with random intercepts for participants". For a
mixed model give the formula, the random-effects structure and how *p*-values were obtained.

**STAT-5. Check and report assumptions** (normality of residuals, sphericity, homogeneity of
variance) and what you did when one failed (a correction, a transformation, a
nonparametric test).

**STAT-6. Correct for multiple comparisons.** Post hoc pairwise tests and families of
related tests need a correction: Holm's step-down procedure (controls the family-wise error
rate) or Benjamini–Hochberg (controls the false discovery rate) [Benjamini1995]. Name the
correction and report adjusted *p*-values.

## Reporting

**STAT-7. Report effect sizes and confidence intervals, not just *p*.** A *p*-value does not
measure the size of an effect or the importance of a result [ASA2016, principle 5]. Report
the estimate, its 95% CI and a standardized effect size for every test, as estimation-based
reporting recommends [Cumming2014; Lakens2013; Dragicevic2016].

**STAT-8. Report descriptive statistics** of the actual data (*M* and *SD*, or *Mdn* and
IQR for ordinal data) alongside every test, and the *n* each is based on.

**STAT-9. No "trending toward significance", "marginally significant" or "approaching
significance".** A result is significant at the alpha you stated or it is not; conclusions
should not rest only on whether *p* crosses a threshold [ASA2016, principle 3;
Wasserstein2019]. Report *p* = .07 with its effect size and CI and discuss the estimate.
`check_paper.py` flags these phrases.

**STAT-10. Don't conclude "no difference" from *p* > .05.** A non-significant result means
the data are compatible with a range of effects that the CI shows. To claim equivalence,
plan and run an equivalence test.

**STAT-11. Precision (Jim's decision; what the `stats.tex` macros print):**
- *F* and χ² to **one** decimal: `\F{2}{18}{16.16}` → *F*<sub>2,18</sub> = 16.2.
- *p* to **two** decimals with no leading zero: `\p{.034}` → *p* = .03; below .01 it prints
  *p* < .01 and below .001 *p* < .001. Never *p* = .000, *p* < .0001 or *p* = 0.03.
- Effect sizes bounded by 1 (η²<sub>p</sub>, *r*, *V*) to two decimals with no leading zero:
  `\etasqp{.012}` → η²<sub>p</sub> = .01. Effect sizes that can exceed 1 (*d*) keep the zero.
- Means and SDs to one decimal by default (`\sisetup{round-precision=1}` in `stats.tex`),
  with units: `\mean[\s]{3.24}`.

**STAT-12. Use the macros** rather than typing numbers, so precision is consistent:

| Macro | Prints |
|---|---|
| `\p{.03}` | *p* = .03 (or < .01, < .001) |
| `\F{df1}{df2}{value}`, `\owF{df}{value}` | *F*<sub>1,12</sub> = 2.3 |
| `\anova{df1}{df2}{F}{p}`, `\anovae{df1}{df2}{F}{p}{η²p}` | *F*, *p* (and η²<sub>p</sub>) |
| `\owanova{df}{F}{p}{η²p}` | one-way *F*, *p*, η²<sub>p</sub> |
| `\chisq{df}{value}`, `\chisquare{df}{value}{p}` | χ²(df) = 3.3, *p* |
| `\etasqp{.67}` | η²<sub>p</sub> = .67 |
| `\mean[unit]{x}`, `\sd[unit]{x}`, `\msd[unit]{m}{sd}`, `\mdn[unit]{x}` | *M* = 32.1 cm, *SD* = 4.1 |
| `\ages{23}{51}`, `\gender{12}{women}`, `\genderlist{12;7;1}{women, men, and non-binary people}` | Ages 23–51; 12 identified as women |
| `\size[pixels]{1920}{1080}`, `\sizen[\cm]{13;12;5}`, `\by` | 1920 × 1080 pixels |

There is no macro for *t*, *U*, *W* or CIs yet; write them out with the same precision:
`$t(23) = 2.41$, \p{.024}, $d = 0.49$, 95\,\% CI [0.07, 0.91]`.
`TODO(Jim): add \tstat, \ustat and \ci macros to stats.tex?`

**STAT-13. Mark significant differences on the figure or table** and say what the marks
mean (see FIG-7).

## Likert and other rating data

**STAT-14. Treat a single Likert item as ordinal.** Show the distribution (a diverging
stacked bar, FIG table, [figures.md](figures.md)), summarise with the median and IQR, and
test with a nonparametric test (Mann–Whitney *U*, Wilcoxon, ART for factorial designs) or
an ordinal model. Parametric tests on Likert data at the sample sizes common in HCI can
give wrong answers [Kaptein2010], and analysing ordinal ratings with metric models can
mislead [Liddell2018].

**STAT-15. Score validated multi-item questionnaires as their authors specify** (e.g. the
SUS 0–100 score) and cite the instrument; report its reliability in your sample if you
report it at all for the scale. `TODO(Jim): source for treating summed multi-item scales as
interval data, if the lab wants a rule on it.`

## Sources

- [ASA2016] Ronald L. Wasserstein, Nicole A. Lazar. 2016. The ASA Statement on p-Values:
  Context, Process, and Purpose. *The American Statistician* 70(2): 129–133.
  https://doi.org/10.1080/00031305.2016.1154108
- [Wasserstein2019] Ronald L. Wasserstein, Allen L. Schirm, Nicole A. Lazar. 2019. Moving to a
  World Beyond "p < 0.05". *The American Statistician* 73(sup1): 1–19.
  https://doi.org/10.1080/00031305.2019.1583913
- [Cumming2014] Geoff Cumming. 2014. The New Statistics: Why and How. *Psychological Science*
  25(1): 7–29. https://doi.org/10.1177/0956797613504966
- [Lakens2013] Daniël Lakens. 2013. Calculating and reporting effect sizes to facilitate
  cumulative science: a practical primer for t-tests and ANOVAs. *Frontiers in Psychology* 4.
  https://doi.org/10.3389/fpsyg.2013.00863
- [Lakens2022] Daniël Lakens. 2022. Sample Size Justification. *Collabra: Psychology* 8(1):
  33267. https://doi.org/10.1525/collabra.33267
- [Caine2016] Kelly Caine. 2016. Local Standards for Sample Size at CHI. *CHI 2016*: 981–992.
  https://doi.org/10.1145/2858036.2858498
- [Dragicevic2016] Pierre Dragicevic. 2016. Fair Statistical Communication in HCI. In *Modern
  Statistical Methods for HCI*, Springer, 291–330.
  https://doi.org/10.1007/978-3-319-26633-6_13
- [Wobbrock2011] Jacob O. Wobbrock, Leah Findlater, Darren Gergle, James J. Higgins. 2011. The
  Aligned Rank Transform for Nonparametric Factorial Analyses Using Only ANOVA Procedures.
  *CHI 2011*: 143–146. https://doi.org/10.1145/1978942.1978963
- [Elkin2021] Lisa A. Elkin, Matthew Kay, James J. Higgins, Jacob O. Wobbrock. 2021. An Aligned
  Rank Transform Procedure for Multifactor Contrast Tests. *UIST 2021*: 754–768.
  https://doi.org/10.1145/3472749.3474784
- [Bates2015] Douglas Bates, Martin Mächler, Ben Bolker, Steve Walker. 2015. Fitting Linear
  Mixed-Effects Models Using lme4. *Journal of Statistical Software* 67(1).
  https://doi.org/10.18637/jss.v067.i01
- [Benjamini1995] Yoav Benjamini, Yosef Hochberg. 1995. Controlling the False Discovery Rate: A
  Practical and Powerful Approach to Multiple Testing. *Journal of the Royal Statistical
  Society, Series B* 57(1): 289–300. https://doi.org/10.1111/j.2517-6161.1995.tb02031.x
  (Holm's procedure: `TODO(Jim): source` — Holm 1979, *Scandinavian Journal of Statistics*,
  not verified in this session.)
- [Kaptein2010] Maurits Clemens Kaptein, Clifford Nass, Panos Markopoulos. 2010. Powerful and
  Consistent Analysis of Likert-Type Rating Scales. *CHI 2010*: 2391–2394.
  https://doi.org/10.1145/1753326.1753686
- [Liddell2018] Torrin M. Liddell, John K. Kruschke. 2018. Analyzing ordinal data with metric
  models: What could possibly go wrong? *Journal of Experimental Social Psychology* 79:
  328–348. https://doi.org/10.1016/j.jesp.2018.08.009
- [Cockburn2018] Andy Cockburn, Carl Gutwin, Alan Dix. 2018. HARK No More: On the
  Preregistration of CHI Experiments. *CHI 2018*. https://doi.org/10.1145/3173574.3173715
