# References and citations

Rules for citing the literature and managing the bibliography. Rule IDs are `REF-n`.

**Never invent a citation.** Every reference must be a real work that an author or agent
has retrieved (DOI landing page, ACM DL, Crossref, DBLP, publisher page). An agent never
writes a bibliography entry from memory, never "completes" missing fields by guessing, and
never cites a work for a claim it has not checked the work makes. If a source can't be
found, leave a visible `TODO: source` for the author.

## Citing in the text

From the CHI Zen checklist's "References" table:

| Rule | Yes | No |
|---|---|---|
| **REF-1.** Citations sit inside the sentence. | your claim [1]. | your claim. [1]. |
| **REF-2.** A citation follows the authors' name. | Bauer et al. [1] claimed X, Y, and Z. | Bauer et al. claimed X, Y, and Z [1]. |
| **REF-3.** Citations are not nouns. | … as Bauer et al. [1] found … | … as [1] found … |
| **REF-4.** Citations immediately follow the claims they support. | Previous research has found X [1], Y [2,3], and Z [4, 5]. | Previous research has found X, Y, and Z [1, 2, 3, 4, 5]. |
| **REF-5.** Every claim is backed by a citation. | The long-term use of smartphones causes increased anxiety [1, 2, 4]. | The long-term use of smartphones causes anxiety. |
| **REF-6.** Summarize what cited work found, not just that it exists. | Bauer et al. [1] previously showed that FitBits have long-term benefits for mental health. They found … | Bauer et al. [1] previously studied the impact of FitBit on long-term mental health. |

With acmart's natbib (the default), write REF-2 and REF-3 as `\citet{bauer2020}` (prints
"Bauer et al. [1]") and REF-1/REF-4 as `\cite{…}` placed right after the claim, before the
full stop.

**REF-7. Check the reference list thoroughly**, and the spelling of authors' names in the
text (checklist). Common faults: preprint instead of published version, missing DOI,
wrong year, title case lost (protect acronyms with braces: `{HCI}`), duplicate entries.

## Tooling

**REF-8. Use BibTeX with ACM's `ACM-Reference-Format` style and natbib, as acmart provides
(Jim's decision).** This replaces the earlier choice of biblatex, because biblatex is not on
ACM's TAPS list of accepted packages (see CHECK-TAPS in [checklist.md](checklist.md)):

```latex
\documentclass[manuscript,review,anonymous]{acmart}   % natbib is on by default
...
\bibliographystyle{ACM-Reference-Format}
\bibliography{bibliography}   % bibliography.bib
```

Don't load biblatex or natbib yourself (acmart loads natbib), and don't mix `\printbibliography`
with `\bibliography` in one document. Overleaf runs BibTeX automatically. (The starter paper
`00-my-new-paper.tex` still loads biblatex at the time of writing; follow this rule, not the
starter, until the starter is switched.)

**REF-9. Every entry has a DOI when one exists**, taken from the publisher's record (the
ACM DL "Export citation" BibTeX is a good source for ACM papers). Use `@inproceedings` for
conference papers and `@article` for journals, including PACM.

**REF-10. One key per work, in a consistent form** (e.g. `familyYYYYfirstword`:
`wobbrock2016research`). With two entries under the same key, BibTeX keeps only the first
(with a "Repeated entry" warning that is easy to miss).

**REF-11. Cite software, datasets and materials** you used or released (R packages, ARTool,
your OSF project), with versions.

**REF-12. Follow the venue's anonymity policy for review.** CHI 2027 requires anonymised
submissions, including supplementary material [CHI2027]. Its anonymization policy asks
authors to cite their own work in the third person and leave those references unanonymised,
so reviewers can see that the prior work was considered: "As described by Chetty et al.
[10]", not "As described in our previous work [10]". A reference marked "anonymous" is
grounds for desk rejection [CHI2027-Anon]. `check_paper.py` flags first-person
self-citation (`W-anon-selfcite`) and `.bib` entries by "Anonymous" (`E-anon-ref`) when the
class option `anonymous` is on. See TRN-5 for the rest of the policy.

**REF-13. Find related work from records, then read it.** Search scholarly databases with
the field's terms and their synonyms, and snowball from the papers you already know are
central: "using the references and the citations respectively is referred to as backward
and forward snowballing" [Wohlin2014]. Forward snowballing finds recent work that a keyword
search ranks low. A list of candidates from a search, or from an agent, is a reading list:
cite a paper only for what you have read it say (the rule at the top of this file). The
`related-work` skill runs these searches (Crossref, Semantic Scholar, OpenAlex, doi.org) and
returns candidates with DOIs; it doesn't write the section (WRT-4 is the author's work).

## Sources

- [Wohlin2014] Claes Wohlin. 2014. Guidelines for snowballing in systematic literature
  studies and a replication in software engineering. *EASE '14*: 1–10.
  https://doi.org/10.1145/2601248.2601268 (quote from the author's copy,
  http://www.wohlin.eu/ease14.pdf, retrieved 2026-11-21)
- [CHI2027] ACM CHI 2027. Papers (call for papers). https://chi2027.acm.org/authors/papers/
  (retrieved 2026-11-18)
- [CHI2027-Anon] ACM CHI 2027. CHI Anonymization Policy.
  https://chi2027.acm.org/chi-anonymization-policy/ (retrieved 2026-11-21)
- CHI Zen checklist, "References" (`manual/CHIZen-Paper-Checklist.tex`).
- acmart's bibliography setup: `\bibliographystyle{ACM-Reference-Format}` with natbib, as
  acmart provides (Jim's decision, 2026-11-18; the manual and starter paper still use
  biblatex at the time of writing).
- ACM TAPS accepted packages (biblatex not listed): `CHIZen/taps-accepted-packages.txt`.
