> **Archived 23 Nov 2026.** The manuscript source is now `manuscript/tex/`. This folder and the markdown sections are kept for history; edits here are not carried into the paper.

# LaTeX sources for MLST

Generated from the markdown manuscript by `build.py` (run from the repository root: `python manuscript/latex/build.py`).

- `main.tex`: article with appendices; `supplement.tex`: supporting information (SI 1–7); `refs.bib`: bibliography built from `manuscript/references.md`.
- Class: `iopjournal.cls` (2024/01/31) and `orcid.pdf` from the official IOP Publishing LaTeX template, included here; the template, its example file and `iopjournal-guidelines.pdf` are in `iop_template/`. Compile with `latexmk -pdf main.tex supplement.tex`. The title is typeset by `\title` itself (no `\maketitle`). References may follow any style that gives complete entries (guidelines, section 4); the build uses numbered references. `stub/` holds the old stand-in class and is no longer needed.
- Bibliography style: `iopart-num` if present, else `unsrt`.
- Edit the markdown, not the .tex files; rerun `build.py` to regenerate.
