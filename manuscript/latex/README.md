# LaTeX sources for MLST

Generated from the markdown manuscript by `build.py` (run from the repository root: `python manuscript/latex/build.py`).

- `main.tex`: article with appendices; `supplement.tex`: supporting information (SI 1–7); `refs.bib`: bibliography built from `manuscript/references.md`.
- Class: `iopjournal.cls` from the IOP Publishing LaTeX template (Overleaf: "Template for IOP Publishing journals"). It is not included here; upload these files to that template, or compile locally against the stand-in with `TEXINPUTS=./stub//: latexmk -pdf main.tex supplement.tex`.
- Bibliography style: `iopart-num` if present, else `unsrt`.
- Edit the markdown, not the .tex files; rerun `build.py` to regenerate.
