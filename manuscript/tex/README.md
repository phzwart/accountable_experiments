# Manuscript source (LaTeX)

This folder is the source of the manuscript from 23 Nov 2026 on. Edit the files here directly, in TeXstudio, Overleaf or any LaTeX editor.

- `main.tex`: article with appendices.
- `supplement.tex`: supporting information.
- `refs.bib`: bibliography, shared by both.
- `iopjournal.cls`, `orcid.pdf`: IOP journal class for MLST.
- `figures/`: every figure the two documents include. `fig_hook4.svg` is the editable original of Fig. 1; `fig_hook4.pdf` is made from it with `rsvg-convert -f pdf -o fig_hook4.pdf fig_hook4.svg`.

## Build

```
latexmk -pdf main.tex
latexmk -pdf supplement.tex
```

Overleaf: upload the folder as it is and set `main.tex` as the main document.

## Figures

The figures are drawn by the scripts in `manuscript/figures/` from the results in `results/`. After a figure is redrawn there, copy its PDF (or PNG) into `figures/` here.

## History

Until 22 Nov 2026 the manuscript was written as markdown sections (`manuscript/*.md`) and converted to LaTeX by `manuscript/latex/build.py`. Those files are kept as an archive and are no longer the source. Running the old build writes only to `manuscript/latex/` and does not touch this folder.
