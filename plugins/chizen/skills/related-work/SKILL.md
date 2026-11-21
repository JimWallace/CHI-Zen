---
description: Find candidate related work for an HCI paper from scholarly records (Crossref, Semantic Scholar, OpenAlex, doi.org), never from memory - keyword searches built from the paper's own claims, backward and forward snowballing from papers it already cites, de-duplicated against its .bib, returned as a reading list with DOIs and deposited abstracts. Proposes; doesn't write the related-work section or cite anything the author hasn't read.
when_to_use: For example "find related work on X", "what am I missing in my related work", "who has cited Y since", "snowball from my key papers", "is there prior work on Z", "a reviewer says I missed related work".
argument-hint: "[paper-dir] [topic or DOI]"
allowed-tools: Read Grep Glob Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/find_papers.py *)
---

# Find related work with CHI Zen

Arguments: `$ARGUMENTS`: an optional paper directory (default: the repository root) and an
optional topic, question or DOI to start from.

You build a **reading list** for the author. Every paper on it comes from a record a
scholarly service returned in this session, with its DOI. You never add a paper from memory,
never describe what a paper found beyond its retrieved title and abstract, and never edit the
paper or its `.bib` unless the author asks for specific entries (step 6).

## 0. Context
- Read the paper's `CLAUDE.md` (venue, **Author's decisions**) if there is one.
- The guide is in `${CLAUDE_SKILL_DIR}/../chizen/references/`: read `references.md` (REF-13
  on finding related work, REF-9 and REF-10 for entries) and, in `writing.md`, WRT-4
  (related work positions, it doesn't list).
- Read the abstract, the introduction's contribution list and the related-work section, so
  the searches come from the paper's own claims, not from the topic in general.

## 1. Plan the searches, and show the plan
From the paper (or the author's request), write down:
- **Claims that need prior work**: each contribution, and each related-work theme (one per
  paragraph or subsection), in a line.
- **Queries**: two to four short keyword queries per theme, using the field's terms and
  their synonyms (e.g. "older adults" / "seniors" / "aging"; "smart speaker" / "voice
  assistant").
- **Seeds**: the paper's key citations, from `python3 ${CLAUDE_SKILL_DIR}/scripts/find_papers.py
  seeds <paper-dir>` (the DOIs in its `.bib`). Ask the author which three to six are central
  if it isn't obvious.
Show this plan in a few lines before running it, unless the author asked for one quick search.

## 2. Search and snowball
Run, with `--bib` pointing at the paper's `.bib` file(s) so known papers are marked:

```
S=${CLAUDE_SKILL_DIR}/scripts/find_papers.py
python3 $S search "<query>" --since <year> --venue "Human Factors in Computing Systems" --bib <bib> --md
python3 $S refs <seed DOI> --bib <bib> --md     # backward: what the seed cites
python3 $S cites <seed DOI> --bib <bib> --md    # forward: what has cited the seed since
```

Search defaults to conference papers and journal articles (`--any-type` widens it);
`--venue` ranks a venue first without excluding others, so also search without it. Forward
snowballing finds the newest work, which a keyword search ranks low. Keep the number of
requests modest (tens, not hundreds): the services rate-limit. If one refuses or a command
fails, say so and carry on with the others; don't fill the gap from memory.

## 3. Screen
Using **only** each record's title, venue, year and abstract:
- drop what is off-topic, and duplicates (the same work as a preprint and as a paper: keep
  the published version, REF-7);
- keep what a reviewer would expect to see cited for one of the claims in step 1, and what
  contradicts or complicates the paper's claims (those matter most);
- prefer peer-reviewed papers; flag preprints, extended abstracts and workshop papers as such.
When a record has no abstract ("not deposited"), judge from the title and venue only and say
so; never write a summary for it.

## 4. Report
For each theme from step 1, a table:

| Paper (authors, year, title) | Venue | DOI | Why it may matter here | Basis |
|---|---|---|---|---|

- "Why it may matter here" names the paper's own claim or theme it bears on, in a few words
  ("prior study of the same population", "contradicts our claim that …"). It never states a
  finding the abstract doesn't state.
- "Basis" is `abstract`, `title only` or `cited by <seed>` / `cites <seed>`.
- Then: papers already in the `.bib` that the searches surfaced again (a sign the theme is
  covered), and gaps: themes where the searches found little, with the queries tried.
- End with: "These are candidates to read, not citations. Cite a paper only for what you
  have read it say (REF-13)." and the generative-AI disclosure reminder (WRT-13): if the
  venue's policy covers AI-assisted literature search, the authors may need to disclose it.

## 5. What you don't do
- Don't draft the related-work section or sentences about what a paper found. If the author
  asks for help with positioning (WRT-4), comment on their draft paragraphs against the
  papers they say they have read, as suggestions.
- Don't add `\cite`s to the paper.
- Don't search the web for a participant's quote, or put any of the paper's unpublished
  content (data, quotes, findings) into a search query; queries are topic words only.

## 6. BibTeX, when the author asks for specific papers
```
python3 $S bibtex <DOI> [<DOI> ...]
```
returns the registration agency's record from doi.org. Before proposing it as an entry:
rename the key to the paper's convention (REF-10), keep the DOI (REF-9), protect acronyms in
the title with braces, and check the entry type (ACM proceedings are `@inproceedings`, PACM
journals `@article`). Show the new entries as a diff to the `.bib` for the author to accept.
Never edit a field by hand to "fix" it; if the record looks wrong, say so.
