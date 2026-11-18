# latexmk settings for CHI Zen (also read by Overleaf).
#
# Engine: LuaLaTeX. The documents start with \DocumentMetadata{...} and
# produce a tagged, accessible PDF (PDF/UA-2 + PDF/A-4f). That works best,
# and is only fully supported, with LuaLaTeX. pdfLaTeX still compiles them.
#
# On Overleaf the engine comes from the project settings, not from this
# file: Menu > Settings > Compiler > LuaLaTeX, and TeX Live version 2026 or
# later. See the manual, Section "Overleaf Settings".
$pdf_mode = 4;          # 4 = lualatex
$bibtex_use = 2;        # run BibTeX when needed, delete .bbl on clean

# With LuaLaTeX, -shell-escape is not needed: minted runs `latexminted',
# which TeX Live allows in restricted shell escape, and markdown runs its Lua
# code directly. pdfLaTeX needs -shell-escape for markdown (Overleaf turns
# shell escape on anyway), and so does the svg package.
$pdflatex = 'pdflatex -shell-escape %O %S';

# `latexmk' with no file names builds both documents.
@default_files = ('CHIZen-Manual.tex', '00-my-new-paper.tex');

# Extra files to delete on `latexmk -c'.
$clean_ext .= ' %R.markdown.* _markdown_%R/* _minted* svg-inkscape/*';
