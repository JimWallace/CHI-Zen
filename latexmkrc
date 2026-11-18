# latexmk settings for CHI Zen (also read by Overleaf).
#
# Engine: LuaLaTeX. The documents start with \DocumentMetadata{...} and
# produce a tagged, accessible PDF (PDF/UA-2 + PDF/A-4f). That works best,
# and is only fully supported, with LuaLaTeX. pdfLaTeX still compiles them.
#
# On Overleaf the engine comes from the project settings, not from this
# file: Menu > Settings > Compiler > LuaLaTeX, and TeX Live version 2026 or
# later. See README.md.
$pdf_mode = 4;          # 4 = lualatex
$bibtex_use = 2;        # run BibTeX when needed, delete .bbl on clean

# minted runs `latexminted', which TeX Live allows in restricted shell
# escape, so -shell-escape is not needed. (Overleaf turns it on anyway; add
# it here if you use the svg package to convert .svg files with Inkscape.)

# `latexmk' with no file names builds both documents.
@default_files = ('CHIZen-Manual.tex', '00-my-new-paper.tex');

# Extra files to delete on `latexmk -c'.
$clean_ext .= ' %R.markdown.* _markdown_%R/* _minted* svg-inkscape/*';
