# Ethics for human participants, online and health data

Rules for reporting research ethics, with extra care for the lab's common case: online
community data (e.g. Reddit) about health and mental health. Rule IDs are `ETH-n`.

These rules are about what the *paper* says and shows. They don't replace the research
ethics board (REB). When the paper and the approved protocol differ, the protocol wins and
the author talks to the REB.

## Approval and consent

**ETH-1. State the ethics review.** Say which board reviewed the study and its decision:
"This study was reviewed and received ethics clearance through a University of Waterloo
Research Ethics Board (REB #NNNNN)", or, for work that was exempt, why. In an anonymous
submission, wrap the board's name and number in `\anon{...}` (TRN-5). In Canada, research
that relies only on information that is in the public domain, where the people it refers to
have no reasonable expectation of privacy, does not require REB review (TCPS 2, Article
2.2); but online groups with restricted membership carry a stronger expectation of privacy,
and research using them "shall be submitted for REB review" [TCPS2]. The REB, not the
author, decides when an exemption applies. Leave the number as `REB #TODO` for the author
to fill in; an agent never invents one. Anonymise the board's name and number for
double-blind review if the venue asks.

**ETH-2. Describe consent and compensation**: how participants were informed and consented
(written, verbal, online), whether they could withdraw, and what they were paid. For
online data collected without consent, say so, and say why that was appropriate and
approved.

## Quoting online posts

**ETH-3. Assume a verbatim quote from a public post can be traced back to its author.**
Searching for quoted content led to the person who posted it in 84% of cases in a review of
health studies that quoted tweets [Ayers2018]. Users of public platforms often don't know
their posts are used in research and many think researchers should ask; their views depend
on context, such as how the research is disseminated and what it is about [Fiesler2018].
For health and mental-health communities the harm of being identified is greater.

**ETH-4. Protect quotes from public forums.** Unless participants consented to being quoted
verbatim, do one or more of the following, and say in the method which you did:
- paraphrase the quote (and say quotes are paraphrased) and check that the paraphrase does
  not return the post in a web or site search;
- use short fragments rather than whole posts;
- create composite or fictionalised accounts where exact wording isn't needed, which
  internet research ethics discusses as "fabrication" for exactly this problem
  [Markham2012; AoIR2020].
Don't quote usernames, post titles, links or timestamps, and don't name small communities
if naming them makes people identifiable. Never alter a quote's meaning, and never present
a paraphrase as verbatim.

**ETH-5. De-identify every quote and description**: participant IDs instead of names (P7);
remove or generalise places, employers, rare conditions, dates and other details that
could identify someone in combination. Report demographics in aggregate.

**ETH-6. Handle health data as sensitive data**: say where data are stored, who can access
them, and when they will be deleted, as approved by the REB. Don't share raw posts or
transcripts publicly unless consent and approval cover it (see
[transparency.md](transparency.md), TRN-3).

**ETH-7. Consider the community, not only the individual.** Where the paper might affect a
community (e.g. a recovery forum), say how you considered the potential harm, and follow
the platform's terms of use [TCPS2; AoIR2020].

**ETH-8. Research team wellbeing and content warnings.** If the paper quotes distressing
content (self-harm, suicide, abuse), add a content note at the start. `TODO(Jim): lab policy
on content notes and on reporting researcher wellbeing support, with a source if wanted.`

## Sources

- [TCPS2] Canadian Institutes of Health Research, Natural Sciences and Engineering Research
  Council of Canada, Social Sciences and Humanities Research Council. *Tri-Council Policy
  Statement: Ethical Conduct for Research Involving Humans (TCPS 2, 2022)*, Chapter 2,
  Article 2.2. https://ethics.gc.ca/eng/tcps2-eptc2_2022_chapter2-chapitre2.html
- [AoIR2020] aline shakti franzke, Anja Bechmann, Michael Zimmer, Charles Ess and the
  Association of Internet Researchers. 2020. *Internet Research: Ethical Guidelines 3.0*.
  https://aoir.org/reports/ethics3.pdf
- [Ayers2018] John W. Ayers, Theodore L. Caputi, Camille Nebeker, Mark Dredze. 2018. Don't
  quote me: reverse identification of research participants in social media studies.
  *npj Digital Medicine* 1: 30. https://doi.org/10.1038/s41746-018-0036-2
- [Fiesler2018] Casey Fiesler, Nicholas Proferes. 2018. "Participant" Perceptions of Twitter
  Research Ethics. *Social Media + Society* 4(1). https://doi.org/10.1177/2056305118763366
- [Markham2012] Annette Markham. 2012. Fabrication as ethical practice: Qualitative inquiry
  in ambiguous internet contexts. *Information, Communication & Society* 15(3): 334–353.
  https://doi.org/10.1080/1369118X.2011.641993
