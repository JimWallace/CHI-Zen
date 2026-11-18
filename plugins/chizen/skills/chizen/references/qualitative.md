# Qualitative reporting

Rules for reporting interviews, focus groups, open-ended responses and qualitative analyses
of online content. Rule IDs are `QUAL-n`. Ethics of quoting online data is in
[ethics.md](ethics.md).

**Never invent or alter a participant quote**, a code, a theme or a count. An agent may
suggest shortening a quote with an ellipsis or choosing among quotes the authors supplied;
it never paraphrases a quote and presents it as verbatim, and it never writes a "typical"
quote.

## Method

**QUAL-1. Name the analysis and its variant.** "Thematic analysis" is a family of methods
that differ in their philosophy and procedure; quality criteria for one don't apply to
another [Braun2021quality]. Say which you used and cite it:
- **reflexive thematic analysis** [Braun2006; Braun2019], in which themes are developed by the
  researchers through interpretation and the researcher's subjectivity is a resource;
- **codebook** approaches (e.g. template or framework analysis), with a structured codebook
  developed partly in advance;
- **coding reliability** approaches, which use a fixed codebook and measure agreement
  between coders [Braun2021quality].
"We followed Braun and Clarke" without saying which version is not enough.

**QUAL-2. Report reliability in a way that fits the method.** Inter-rater reliability (IRR,
e.g. Cohen's κ) suits coding-reliability approaches; in reflexive TA, coding reliability
measures are not a quality requirement and don't fit its assumptions [Braun2021quality].
How and whether to establish reliability depends on the method; in CSCW and HCI papers IRR
is the exception, not the rule (about 1 in 9 qualitative papers in 2016–2018)
[McDonald2019]. If you used IRR, report the statistic, what was double-coded and how
disagreements were resolved; if you didn't, say how the team reached and checked its
interpretations (e.g. discussion, memoing, a critical friend).

**QUAL-3. No unearned saturation claims.** Data or thematic saturation ("no new themes
emerged") belongs to coding-reliability thinking and is not consistent with reflexive TA
[Braun2021saturate]. Justify the sample by the richness of the data and the aims of the
study instead, and don't claim saturation unless your method defines and tested it.

**QUAL-4. Describe the process**: who did the coding (by role), how many coders, the
software, how codes became themes, and a table of themes (and sub-themes) with a short
description of each.

**QUAL-5. Describe the participants and the context** (recruitment, inclusion criteria,
demographics as relevant, setting, interview length) so readers can judge transferability.
Follow a reporting standard where the venue or field expects one, e.g. APA's JARS-Qual
[Levitt2018].

**QUAL-6. Positionality.** Say briefly who the researchers are in relation to the topic and
the participants (relevant experience, insider or outsider status) and how that shaped the
analysis, especially for reflexive TA, where subjectivity is part of the method
[Braun2019]. `TODO(Jim): an HCI-specific source on positionality statements, if wanted.`

## Writing up

**QUAL-7. Quote conventions.** Attribute every quote to a participant ID (P7, or P7 with a
relevant attribute: "P7, nurse"), never a name. Use double quotation marks inline for short
quotes and an indented block for long ones. Mark omissions with "[…]" and your insertions
with square brackets. Don't correct participants' grammar silently; use "[sic]" sparingly.

**QUAL-8. Spread the quotes.** Draw quotes from across participants, and say when a quote is
from someone with a minority view. Don't build a theme on one participant.

**QUAL-9. Counts: use them consistently or not at all.** If you give counts ("12 of 20
participants"), give them for every theme and say what was counted. Don't use vague
quantifiers ("many", "most") as if they were counts (see WRT-6). In reflexive TA,
prevalence is not what makes a theme important; say why a theme matters.

**QUAL-10. Themes are interpretations, not topics.** A theme heading says something
("Players used the avatar to rehearse disclosure"), not just names an area ("Avatars").

**QUAL-11. For online community data, quote ethically**: see [ethics.md](ethics.md),
ETH-3 to ETH-5, before putting any post text in the paper.

## Sources

- [Braun2006] Virginia Braun, Victoria Clarke. 2006. Using thematic analysis in psychology.
  *Qualitative Research in Psychology* 3(2): 77–101. https://doi.org/10.1191/1478088706qp063oa
- [Braun2019] Virginia Braun, Victoria Clarke. 2019. Reflecting on reflexive thematic
  analysis. *Qualitative Research in Sport, Exercise and Health* 11(4): 589–597.
  https://doi.org/10.1080/2159676X.2019.1628806
- [Braun2021quality] Virginia Braun, Victoria Clarke. 2021. One size fits all? What counts as
  quality practice in (reflexive) thematic analysis? *Qualitative Research in Psychology*
  18(3): 328–352. https://doi.org/10.1080/14780887.2020.1769238
- [Braun2021saturate] Virginia Braun, Victoria Clarke. 2021. To saturate or not to saturate?
  Questioning data saturation as a useful concept for thematic analysis and sample-size
  rationales. *Qualitative Research in Sport, Exercise and Health* 13(2): 201–216.
  https://doi.org/10.1080/2159676X.2019.1704846
- [McDonald2019] Nora McDonald, Sarita Schoenebeck, Andrea Forte. 2019. Reliability and
  Inter-rater Reliability in Qualitative Research: Norms and Guidelines for CSCW and HCI
  Practice. *Proc. ACM Hum.-Comput. Interact.* 3(CSCW): 1–23. https://doi.org/10.1145/3359174
- [Levitt2018] Heidi M. Levitt, Michael Bamberg, John W. Creswell, David M. Frost, Ruthellen
  Josselson, Carola Suárez-Orozco. 2018. Journal article reporting standards for
  qualitative primary, qualitative meta-analytic, and mixed methods research in psychology.
  *American Psychologist* 73(1): 26–46. https://doi.org/10.1037/amp0000151
