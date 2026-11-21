# Writing and framing

Rules for the argument of a paper and its prose. Rule IDs are `WRT-n`. Qualitative reporting
is in [qualitative.md](qualitative.md), research ethics in [ethics.md](ethics.md).

**Agents propose, authors write.** An agent suggests changes to a student's prose as a diff
or a comment that the author accepts or rejects; it never silently rewrites a paragraph,
and it never adds claims, findings, numbers or quotes the authors didn't give it.

## The big picture

**WRT-1. Answer the five questions in the abstract, the introduction and the related
work**, at increasing depth: about a sentence each in the abstract, a paragraph each in the
introduction, one to three paragraphs in the related work (checklist, "The Big Picture"):
1. What problem are you trying to solve?
2. Who cares if you do?
3. What's the solution to the problem?
4. What is the specific contribution of the paper? (How does the design build on existing
   work? What do the findings add to similar studies?)
5. Have you summarized the findings? Are the take-home messages clear and meaningful?
If reviewers can't answer these after the introduction, the odds that they argue for
accepting the paper drop sharply (checklist).

**WRT-2. Name the contribution type.** Frame the contribution as one or more of the seven
HCI research contribution types [Wobbrock2016]: **empirical** (new findings from data),
**artifact** (a system, tool or technique), **methodological** (a new way of doing
research), **theoretical** (frameworks, models, principles), **dataset**, **survey**
(a synthesis of prior work, e.g. a systematic review) and **opinion** (an argument).
The contribution statement in the introduction says which, and the evaluation matches it.

**WRT-3. State the contributions as a short list** at the end of the introduction, each one
specific and checkable ("We contribute a dataset of 1,203 posts …", not "We explore …").

**WRT-4. Related work positions, it doesn't list.** Each paragraph ends by saying how this
paper differs from or builds on the work just summarized (see REF-6).

**WRT-5. Limitations are specific**: name each threat to validity, its likely effect on the
findings, and what was done about it. Don't end with a generic "future work should use a
larger sample".

## Prose

**WRT-6. Words and phrases to avoid** (checklist, "BONUS"): actually, almost, always,
anyway, basically, best, believe, can't, clearly, don't, essentially, feel, folks, good, guy,
hassle, I, impossible, kids, kind of, like, lots, many, never, nice, obviously, OK, of
course, pretty good, prove(n), quite, really, so, stuff, thing, totally, user, utilize,
various, very, well, won't, wouldn't, you.
Why: they are vague (many, various, lots, stuff, thing), overclaim (clearly, obviously,
prove, always, never, impossible, best), are informal (folks, guy, kids, OK, pretty good,
contractions), or hedge without information (basically, essentially, kind of, quite,
really, very). "User" is on the list because it reduces people to their use of a system:
say participants, people, patients, players, members. `check_paper.py` lists these as
style notes; they are prompts to reread the sentence, not automatic errors. Some uses are
fine ("well-being", "like" in a Likert item, a participant's quote).

**WRT-7. Use "we" for the authors**, even with one author, and the past tense for what you
did and found.

**WRT-8. Hedge in proportion to the evidence.** "Suggests" for one study; "shows" for a
robust, replicated effect; never "proves".

**WRT-9. Define acronyms on first use**, and don't define ones you use once. The CHI Zen
`acronym` package (`\ac{HCI}`) does this automatically.

**WRT-10. Write for a reader outside your subfield**: define terms, give an example before
an abstraction, and put the take-away first in a paragraph.

## Process

**WRT-11. Get feedback early.** One week before the deadline, check the paper against the
checklist yourself and ask a friend to check it too; one day before, confirm with
co-authors that everything is ready; after the deadline, send co-authors the submitted PDF
(checklist, "Before You Submit").

**WRT-12. Track changes in revisions.** For a revise-and-resubmit (PACM venues), mark changes
with the `changes` package (`\added{}`, `\deleted{}`, `\replaced{}{}`), as the manual
describes. Don't submit a tracked-changes PDF as the accessible final version (the package
is not yet tagged meaningfully; manual §Accessibility).

**WRT-13. Disclose generative-AI use as ACM policy requires.** ACM's Policy on Authorship
governs AI use in ACM publications. SIGCHI's 2023 guidance quotes it as: "The use of
generative AI tools and technologies to create content is permitted but must be fully
disclosed in the Work", with basic word processing exempt [SIGCHI-ACM2023]. A 2027 ACM
venue page reports a newer version: AI used in the research must be described in detail in
the methods section, and AI used only to help with writing no longer has to be disclosed
[SIGCSE2027]. CHI 2027's call for papers says "Authors must follow the ACM policy on the use of artificial
intelligence, such as large language models" [CHI2027]. Check the current policy and the
venue's call for papers before submitting;
when in doubt, disclose (in the acknowledgements, or the methods section for research use).
`TODO(Jim): confirm the current ACM policy text; acm.org refused automated requests.`

**WRT-14. Report the same numbers everywhere.** The numbers in the abstract, the
introduction, the contribution list, the discussion and the conclusion (participants,
headline percentages, effects) match the method, the results, the tables, the figures and
their `\Description`s, at the same precision (STAT-11). The participant flow adds up
(recruited, excluded, analysed), and degrees of freedom fit the *n* (STAT checks). A number
the paper repeats can be defined once, e.g. `\newcommand{\nparticipants}{24}`, so an edit
changes it everywhere. `check_paper.py` warns when a count of people or a percentage in the
abstract appears nowhere else in the paper (`W-abstract-number`; rounding is allowed); the
statistics reviewer checks the rest.

## Sources

- [Wobbrock2016] Jacob O. Wobbrock, Julie A. Kientz. 2016. Research contributions in
  human-computer interaction. *interactions* 23(3): 38–44. https://doi.org/10.1145/2907069
- CHI Zen checklist (`manual/CHIZen-Paper-Checklist.tex`): "The Big Picture", "Before You
  Submit", "Words and Phrases to Avoid".
- [SIGCHI-ACM2023] Regan Mandryk. 2023-07-06. ACM Publications Policy: Guidance for SIGCHI
  Venues. https://sigchi.org/news/blog/acm-publications-policy-guidance-for-sigchi-venues/
- [CHI2027] ACM CHI 2027. Papers (call for papers). https://chi2027.acm.org/authors/papers/
  (retrieved 2026-11-18)
- [SIGCSE2027] SIGCSE TS 2027. Policies on Generative AI, LLMs, and Related Tools.
  https://2027.sigcse-ts.acm.org/info/policies-ai (links to
  https://www.acm.org/publications/policies/new-acm-policy-on-authorship)
