# CHI Zen

Examples, tips and hacks for HCI research papers: the Waterloo HCI lab's style guide and ACM
paper template. CHI Zen has three parts:

- **A LaTeX template** built on ACM's `acmart` class (as SIGCHI venues use), with pgfplots figure
  styles (`chizen bar`, `chizen box`, `chizen Likert`, `chizen line`, …), colour palettes
  (Okabe–Ito by default), statistics macros (`\p{}`, `\F{}`, `\anovae{}`, …) and a tagged,
  accessible PDF (PDF/UA-2 and PDF/A-4f). `00-my-new-paper.tex` is the starter paper.
- **A manual** (`CHIZen-Manual.tex`): a gallery of worked examples, ending with the CHI paper
  checklist.
- **A Claude Code plugin** (`chizen`) for students' AI agents: the style guide as Markdown
  rules, a paper linter (`check_paper.py`) and four read-only reviewer agents for figures and
  tables, statistics, writing (including qualitative reporting and ethics) and references.
  The guide is in [`plugins/chizen/skills/chizen/references/`](plugins/chizen/skills/chizen/references/)
  and readable on GitHub without Claude.

## Quick start for students

The workflow: you write on **Overleaf**; Overleaf syncs with a **GitHub** repository; **Claude
Code** works on the GitHub copy and proposes changes as a pull request; you merge it and pull
it back into Overleaf. You don't need TeX on your computer.

### 1. Start the paper on Overleaf, linked to GitHub

1. Download this repository as a ZIP (on GitHub: **Code → Download ZIP**).
2. On Overleaf: **New Project → Upload Project**, and choose the ZIP. You can delete what a
   paper doesn't need: `manual/`, `CHIZen-Manual.tex`, `plugins/`, `tests/`, `.github/`,
   `chizen-baseline.txt`, `chizen-warnings-baseline.txt`, `CLAUDE.md` (this repository's,
   not your paper's).
3. Set **Menu → Settings**: Compiler **LuaLaTeX**, TeX Live **2026** or later, main document
   `00-my-new-paper.tex` (see the manual, §"Overleaf Settings").
4. Link it to GitHub: **Menu → GitHub → Create a GitHub repository**. Overleaf can create a
   new repository from a project (or import a repository into a new project), but it can't
   link an existing project to an existing repository. Overleaf's GitHub sync is a premium
   feature; University of Waterloo accounts have it. See
   [Overleaf's GitHub synchronization guide](https://docs.overleaf.com/integrations-and-add-ons/git-integration-and-github-synchronization/github-synchronization).
5. In the new GitHub repository, add a `CLAUDE.md` from
   [`plugins/chizen/templates/paper-CLAUDE.md`](plugins/chizen/templates/paper-CLAUDE.md)
   (venue, length limit, your decisions) and `.claude/settings.json` from
   [`plugins/chizen/templates/settings.json`](plugins/chizen/templates/settings.json), which
   prompts collaborators to install the plugin.

Sync is manual: use **Menu → GitHub → Push to GitHub** before asking Claude for anything, and
**Pull GitHub changes into Overleaf** after merging. Overleaf syncs the default branch; if both
sides changed, it pushes its version to a new branch for you to merge. Pulling can disturb
Overleaf comments and tracked changes, so resolve those first.

### 2. Install the plugin

**Claude Code on your computer** (terminal or IDE), once:

```
/plugin marketplace add JimWallace/CHI-Zen
/plugin install chizen@chizen
```

(or in one step on Claude Code 2.1.275 or later: `/plugin install chizen --marketplace JimWallace/CHI-Zen`).
With the `settings.json` above, Claude Code offers the marketplace when you trust the
repository folder, but you still install the plugin yourself. Plugins don't update
automatically from third-party marketplaces unless you turn on auto-update for the `chizen`
marketplace in `/plugin`; otherwise run `/plugin marketplace update chizen`.

**Claude Code on the web** (claude.ai/code) and other cloud sessions don't install plugins,
not even ones a repository's settings enable. Copy the skills and agents into the paper
repository instead, and commit them (re-run after CHI Zen updates):

```sh
git clone --depth 1 https://github.com/JimWallace/CHI-Zen /tmp/chizen
python3 /tmp/chizen/plugins/chizen/scripts/copy_into_paper.py .
git add .claude && git commit -m "Add CHI Zen skills and agents"
```

You can ask Claude in a cloud session to run those commands. The copy puts the guide in
`.claude/skills/chizen/`, the review skill and linter in `.claude/skills/chizen-review/` and the
reviewers in `.claude/agents/`.

### 3. Write with it

Ask Claude for what you need ("make a box plot of `data/time.csv` by condition", "report this
ANOVA", "format Table 2", "write up the REB statement"). The `chizen` skill loads the relevant
part of the guide and proposes changes as diffs, citing rule IDs (e.g. `FIG-3`). It never
invents data, statistics, quotes or citations: where it needs one, it leaves a `TODO` for you.

### 4. Review before a deadline

1. Push from Overleaf to GitHub.
2. In Claude Code, open the paper's repository and run `/chizen:review` (or `/chizen-review`
   in a copied setup), or ask "review my paper with CHI Zen". It runs the linter, then the four
   reviewers in parallel, and reports what to fix, with exact suggested changes and questions.
3. Ask Claude to apply the fixes you accept **on a branch** and open a **pull request**.
4. Review and merge the pull request on GitHub, then pull into Overleaf.

The linter also runs on its own: `python3 plugins/chizen/skills/review/scripts/check_paper.py <paper-dir>`
(Python 3.9+, no TeX needed). Errors and warnings fail unless your `chizen-baseline.txt` lists
them; the checklist's words to avoid are shown as style notes and never fail.
After compiling with `latexmk`, `python3 plugins/chizen/skills/review/scripts/warning_ratchet.py
00-my-new-paper` does the same for the build: every LaTeX and BibTeX warning, undefined
reference and overfull box fails unless your `chizen-warnings-baseline.txt` lists it. (Add
`--dir` for logs elsewhere, e.g. Overleaf's downloaded output files.)

Remember that ACM policy requires disclosing the use of generative AI as the policy and your
venue specify: keep a note in your paper's `CLAUDE.md` of what Claude did.

## Figures made outside LaTeX

pgfplots reading a CSV file is the default. For figures from Python or R, use
[`chizen.mplstyle`](plugins/chizen/skills/chizen/styles/chizen.mplstyle) (matplotlib) or
[`theme_chizen.R`](plugins/chizen/skills/chizen/styles/theme_chizen.R) (ggplot2), which match
the pgfplots styles; each has a small example next to it.

## Accessibility

The template produces a tagged PDF aimed at PDF/UA-2 and PDF/A-4f; compile with LuaLaTeX.
Give every figure a `\Description{…}` (alt text) as its first line, and use separate figures
instead of subfigures. Details are in the manual, §"Accessibility", and in the guide's
[`accessibility.md`](plugins/chizen/skills/chizen/references/accessibility.md).
GitHub Actions builds both documents on every push and validates them with veraPDF.

## For contributors

See [`CLAUDE.md`](CLAUDE.md): what's where, the hard rules, the guide/gallery relationship, the
`chizen`/`IDEA` style names, and how to run the checks.

## Changes

- 2026: Claude Code plugin with the Markdown style guide, linter and reviewer agents; pgfplots
  styles renamed `chizen …` (the `IDEA …` names still work); `acmart` from TeX Live; tagged PDF
  (PDF/UA-2, PDF/A-4f); alt text for every figure.
- Version 0.1: initial upload to GitHub, a modified version of the ACM SIGCHI paper template.
