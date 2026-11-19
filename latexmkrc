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

# Shell escape: TikZ `external' needs it to save each \chizenfigure as a PDF
# in figures/tikz/ (draft mode; see CHIZen/externalize.tex). Overleaf turns
# it on anyway. pdfLaTeX also needs it for markdown and the svg package.
# (minted alone would not: it runs `latexminted', which TeX Live allows in
# restricted shell escape.)
$lualatex = 'lualatex -shell-escape %O %S';
$pdflatex = 'pdflatex -shell-escape %O %S';

# `latexmk' with no file names builds both documents.
@default_files = ('CHIZen-Manual.tex', '00-my-new-paper.tex');

# Extra files to delete on `latexmk -c'.
$clean_ext .= ' %R.markdown.* _markdown_%R/* _minted* svg-inkscape/*';
# TikZ `external' bookkeeping (the figure PDFs in figures/tikz/ are kept).
$clean_ext .= ' %R.auxlock figures/tikz/*.md5 figures/tikz/*.dpth figures/tikz/*.log';
