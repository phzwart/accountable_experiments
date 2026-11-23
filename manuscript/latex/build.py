"""
Build the MLST LaTeX sources from the markdown manuscript.

    python manuscript/latex/build.py            # writes main.tex, supplement.tex, refs.bib, figures/
    cd manuscript/latex && latexmk -pdf main.tex supplement.tex

The documents use iopjournal.cls (IOP Publishing template). For a local test without the class,
TEXINPUTS=./stub//: points LaTeX at a minimal stand-in in stub/.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
M = HERE.parent
TITLE = "Accountable experiments: autonomous measurement with error bounds set in advance"
MAIN = ["introduction", "related_work", "framework", "experiments", "results", "discussion", "conclusion"]
APP = ["appendix_A", "appendix_B", "appendix_C"]
SI = [f"supplement_SI{i}" for i in range(1, 11)]
FIGS = {1: "fig_hook4", 2: "fig1_schematic", 3: "fig_datasets_claims", 4: "fig_stated", 5: "fig5_maps", 6: "fig_cost",
        "S1": "figS1_gp_std", "S3": "fig3_forms", "S6": "figS6_sampling", "S7": "figS7_cost", "S7b": "fig_hook_three", "S7c": "figS_paired_maps_matern", "S8": "figS8_measured"}
NBSP = "\u00a0"

UNI = {"ε": r"\ensuremath{\varepsilon}", "δ": r"\ensuremath{\delta}", "σ": r"\ensuremath{\sigma}",
       "β": r"\ensuremath{\beta}", "α": r"\ensuremath{\alpha}", "γ": r"\ensuremath{\gamma}",
       "θ": r"\ensuremath{\theta}", "Δ": r"\ensuremath{\Delta}", "Σ": r"\ensuremath{\Sigma}",
       "λ": r"\ensuremath{\lambda}", "φ": r"\ensuremath{\phi}", "ν": r"\ensuremath{\nu}",
       "µ": r"\ensuremath{\mu}", "μ": r"\ensuremath{\mu}", "≤": r"\ensuremath{\le}", "≥": r"\ensuremath{\ge}",
       "±": r"\ensuremath{\pm}", "×": r"\ensuremath{\times}", "−": r"\ensuremath{-}", "°": r"\ensuremath{^\circ}",
       "Å": r"\AA{}", "⁻¹": r"\ensuremath{^{-1}}", "⁻": r"\ensuremath{^{-}}", "¹": r"\ensuremath{^{1}}",
       "²": r"\ensuremath{^{2}}", "³": r"\ensuremath{^{3}}", "⁴": r"\ensuremath{^{4}}", "⁵": r"\ensuremath{^{5}}",
       "₀": r"\ensuremath{_{0}}", "₁": r"\ensuremath{_{1}}", "₂": r"\ensuremath{_{2}}", "₃": r"\ensuremath{_{3}}",
       "₄": r"\ensuremath{_{4}}", "→": r"\ensuremath{\rightarrow}", "≈": r"\ensuremath{\approx}",
       "·": r"\ensuremath{\cdot}", "∧": r"\ensuremath{\wedge}", "∨": r"\ensuremath{\vee}",
       "✓": r"\checkmark{}", "…": r"\ldots{}", "′": r"\ensuremath{'}", "≠": r"\ensuremath{\neq}",
       "∈": r"\ensuremath{\in}", "∞": r"\ensuremath{\infty}", "√": r"\ensuremath{\surd}"}


def body(name: str) -> str:
    t = (M / f"{name}.md").read_text()
    t = t.split("## Notes for revision")[0]
    t = re.sub(r"\n---\s*$", "", t.rstrip()) + "\n"
    return t


def pandoc(md: str) -> str:
    r = subprocess.run(["pandoc", "-f", "markdown+tex_math_dollars+raw_tex-subscript-superscript-smart",
                        "-t", "latex", "--wrap=none"], input=md, capture_output=True, text=True, check=True)
    return r.stdout


def cites(t: str) -> str:
    key = r"[A-Za-z][A-Za-z'\-]*\d{4}[a-z]?"

    def rep(m):
        keys = [k.strip() for k in re.split(r";", m.group(1))]
        loc = None
        if "," in keys[-1] and not re.fullmatch(key, keys[-1]):
            k, loc = keys[-1].split(",", 1)
            keys[-1] = k.strip()
        keys = [k.replace("'", "") for k in keys]
        if loc:
            return r"\cite[" + loc.strip().replace(" ", NBSP) + "]{" + ",".join(keys) + "}"
        return r"\cite{" + ",".join(keys) + "}"
    t = re.sub(r"\[(" + key + r"(?:; ?" + key + r")*(?:, [^\]]+)?)\]", rep, t)
    # keys without a year (datasets): only those in the bibliography, never a markdown link
    return re.sub(r"\[([A-Za-z][A-Za-z0-9]+)\](?!\()",
                  lambda m: r"\cite{" + m.group(1) + "}" if m.group(1) in KNOWN_KEYS else m.group(0), t)


KNOWN_KEYS: set = set()


def xrefs(t: str) -> str:
    t = re.sub(r"Sections (\d)\.(\d)[–-](\d)\.(\d)", lambda m: f"Sections{NBSP}\\ref{{sec:{m[1]}-{m[2]}}}--\\ref{{sec:{m[3]}-{m[4]}}}", t)
    t = re.sub(r"Sections (\d)\.(\d) and (\d)\.(\d)", lambda m: f"Sections{NBSP}\\ref{{sec:{m[1]}-{m[2]}}} and \\ref{{sec:{m[3]}-{m[4]}}}", t)
    t = re.sub(r"Section (\d)\.(\d)", lambda m: f"Section{NBSP}\\ref{{sec:{m[1]}-{m[2]}}}", t)
    t = re.sub(r"Section (\d)\b", lambda m: f"Section{NBSP}\\ref{{sec:{m[1]}}}", t)
    t = re.sub(r"Appendix ([A-D])\b", lambda m: f"Appendix{NBSP}\\ref{{app:{m[1]}}}", t)
    t = re.sub(r"Fig\. (\d)\b", lambda m: f"Fig.{NBSP}\\ref{{fig:{m[1]}}}", t)
    t = re.sub(r"Figure (\d)\b", lambda m: f"Figure{NBSP}\\ref{{fig:{m[1]}}}", t)
    t = re.sub(r"Table (\d)\b", lambda m: f"Table{NBSP}\\ref{{tab:{m[1]}}}", t)
    return t


def caption_tex(text: str, refs: bool) -> str:
    text = re.sub(r"\s*File: `[^`]*`\.?", "", text).strip()
    text = cites(text)
    if refs:
        text = xrefs(text)
    return uni(pandoc(text).strip())


def figures_and_tables(t: str, refs: bool) -> str:
    # figures: a caption paragraph "**Figure N.** ..." becomes a float
    def fig(m):
        n = m.group(1)
        key = int(n) if n.isdigit() else n
        cap = caption_tex(m.group(2), refs)
        label = f"fig:{n}"
        num = "" if n.isdigit() else f"\\renewcommand{{\\thefigure}}{{{n}}}"
        return ("\n```{=latex}\n\\begin{figure}[tbp]" + num + "\n\\centering\n"
                f"\\includegraphics[width=\\textwidth,height=0.44\\textheight,keepaspectratio]{{figures/{FIGS[key]}}}\n"
                f"\\caption{{{cap}}}\\label{{{label}}}\n\\end{{figure}}\n```\n")
    t = re.sub(r"^\*\*Figure (S?\d+[a-z]?)\.\*\* (.+)$", fig, t, flags=re.M)

    # tables: "**Table N.** caption" followed by a pipe table
    def tab(m):
        n, cap, table = m.group(1), m.group(2), m.group(3)
        capt = caption_tex(cap, refs)
        num = "" if n.isdigit() else f"\\renewcommand{{\\thetable}}{{{n}}}"
        tex = pandoc(table)
        tex = tex.replace("\\begin{longtable}", "\\begin{longtable}", 1)
        head = f"\\caption{{{capt}}}\\label{{tab:{n}}}\\\\\n"
        i = tex.index("\\begin{longtable}")
        j = tex.index("@{}}", i) + len("@{}}")
        tex = tex[:j] + "\n" + head + tex[j:]
        return "\n```{=latex}\n{" + num + "\\small\n" + uni(tex) + "}\n```\n"
    t = re.sub(r"^\*\*Table (S?[\d.]+?)\.\*\* (.+?)\n\n((?:\|.*\n)+)", tab, t, flags=re.M)
    return t


def headings(t: str, kind: str) -> str:
    def h(m):
        hashes, title = m.group(1), m.group(2)
        title = re.sub(r"\s*\(draft[^)]*\)", "", title).strip()
        if kind == "main":
            mm = re.match(r"(\d)(?:\.(\d))?\s+(.*)", title)
            if mm:
                lab = f"sec:{mm[1]}" + (f"-{mm[2]}" if mm[2] else "")
                return f"{hashes} {mm[3]} {{#{lab}}}"
            mm = re.match(r"Appendix ([A-D])\.\s+(.*)", title)
            if mm:
                return f"{hashes} {mm[2]} {{#app:{mm[1]}}}"
            mm = re.match(r"[A-D]\.\d\s+(.*)", title)
            if mm:
                return f"{hashes} {mm[1]}"
            return f"{hashes} {title}"
        # supplement: keep SI numbers, unnumbered headings
        return f"{hashes} {title} {{.unnumbered}}"
    return re.sub(r"^(#{1,3}) (.+)$", h, t, flags=re.M)


def uni(t: str) -> str:
    for k in sorted(UNI, key=len, reverse=True):
        t = t.replace(k, UNI[k])
    return t


def convert(name: str, kind: str) -> str:
    t = body(name)
    t = re.sub(r"^\*Notation:.*\*\n", "", t, flags=re.M)
    t = re.sub(r"^\*(All numbers below.*)\*$", r"\1", t, flags=re.M)
    t = headings(t, kind)
    t = figures_and_tables(t, refs=(kind == "main"))
    t = cites(t)
    if kind == "main":
        t = xrefs(t)
    tex = pandoc(t)
    tex = uni(tex)
    tex = re.sub(r"\\begin\{longtable\}.*?\\end\{longtable\}",
                 lambda m: m.group(0).replace(r"\_", r"\_\allowbreak{}"), tex, flags=re.S)
    # pandoc writes \section{...}\label{...}; demote supplement and appendix levels as needed
    return tex


# ------------------------------------------------------------------ bibliography
def bib() -> tuple[str, set]:
    lines = [l for l in (M / "references.md").read_text().splitlines() if l.startswith("- [")]
    out, keys = [], set()
    for l in lines:
        m = re.match(r"- \[([^\]]+)\]\s*(?:\*\*[VM?]\*\*)?\s*(.*)", l)
        key, rest = m.group(1), m.group(2)
        keys.add(key)
        rest = re.sub(r"\((?:[^()]*\b(?:confirm|verified|check|SI only|from memory|Author list)[^()]*)\)\.?", "", rest)
        rest = re.sub(r"\s*SI only\.?", "", rest).strip()
        doi = re.search(r"doi:\s*(\S+?)\.?(?:\s|$)", rest)
        rest_nodoi = re.sub(r"\s*doi:\s*\S+", "", rest).strip()
        ym = re.match(r"(.+?)\s*\((\d{4})\)\.\s*(.*)", rest_nodoi)
        if ym:
            authors, year, tail = ym.group(1), ym.group(2), ym.group(3)
            parts = tail.split(". ", 1)
            title = parts[0].rstrip(".")
            venue = parts[1].rstrip(". ") if len(parts) > 1 else ""
        else:
            authors, year, title, venue = "", "", rest_nodoi.rstrip("."), ""
        auth = authors.replace(" et al.", " and others")
        if auth and "and others" not in auth:
            auth = " and ".join(a.strip() for a in auth.split(","))
        elif auth:
            first = auth.replace(" and others", "")
            auth = " and ".join([a.strip() for a in first.split(",")] + ["others"])
        f = [f"  title = {{{{{uni(title)}}}}}"]
        if auth:
            f.append(f"  author = {{{uni(auth)}}}")
        if year:
            f.append(f"  year = {{{year}}}")
        if venue:
            f.append(f"  howpublished = {{{uni(venue)}}}")
        if doi:
            f.append(f"  note = {{doi:{doi.group(1)}}}")
        out.append(f"@misc{{{key},\n" + ",\n".join(f) + "\n}\n")
    return "\n".join(out), keys


PREAMBLE = r"""\documentclass{iopjournal}
\usepackage{amsmath,amssymb}
% figures share their page with text: no float page unless it is mostly full, at most one float on top
\renewcommand{\topfraction}{0.7}
\renewcommand{\bottomfraction}{0.5}
\renewcommand{\textfraction}{0.3}
\renewcommand{\floatpagefraction}{0.8}
\setcounter{topnumber}{2}
\setcounter{totalnumber}{3}
\usepackage{longtable,booktabs,array,calc}
\usepackage{textcomp}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\def\LTcaptype{table}
"""


def main():
    out = HERE
    (out / "figures").mkdir(exist_ok=True)
    for f in FIGS.values():
        for ext in (".pdf", ".png"):
            src = M / "figures" / (f + ext)
            if src.exists():
                shutil.copy(src, out / "figures" / src.name)
    btxt, keys = bib()
    KNOWN_KEYS.update(keys)
    (out / "refs.bib").write_text(btxt)

    abstract = (M / "abstract.md").read_text().split("## Notes for revision")[0]
    abstract = abstract.split("*\n", 1)[1] if "*Working title" in abstract else abstract
    abstract = uni(pandoc(abstract.strip()).strip())
    sections = "\n".join(convert(n, "main") for n in MAIN)
    appendices = "\n".join(convert(n, "main") for n in APP)
    back = (M / "back_matter.md").read_text().split("## Notes for revision")[0]
    data = uni(pandoc(cites(back.split("\n", 1)[1].strip())).strip())

    main_tex = PREAMBLE + r"""
\begin{document}

\articletype{Paper}

\title{""" + TITLE + r"""}

\author{Petrus H. Zwart$^{1,*}$}
% TODO: co-authors, ORCID iDs (\orcid{...})

\affil{$^1$Molecular Biophysics and Integrated Bioimaging Division, Lawrence Berkeley National Laboratory, Berkeley, CA, USA}

\affil{$^*$Author to whom any correspondence should be addressed.}

\email{phzwart@lbl.gov}

\keywords{accountable experiments, autonomous experimentation, distribution-free risk control, conformal prediction, adaptive sampling, hierarchical design, self-driving laboratories}

\begin{abstract}
""" + abstract + r"""
\end{abstract}

""" + sections + r"""

\appendix
""" + appendices + r"""

% \ack{TODO}
% \funding{TODO}
% \roles{TODO}

\data{""" + data + r"""}

\suppdata{Supporting information: SI 1 interpolators; SI 2 dataset processing; SI 3 full tables; SI 4 adding a form of guarantee; SI 5 the run record; SI 6 the certified metric; SI 7 campaigns guided by Gaussian-process uncertainty; SI 8 the record of measured sites; SI 9 the map bound; SI 10 checks beyond the level.}

\IfFileExists{iopart-num.bst}{\bibliographystyle{iopart-num}}{\bibliographystyle{unsrt}}
\bibliography{refs}

\end{document}
"""
    (out / "main.tex").write_text(main_tex)

    si = "\n".join(convert(n, "si") for n in SI)
    supp_tex = PREAMBLE + r"""
\begin{document}

\articletype{Supporting information}

\title{Supporting information for: """ + TITLE + r"""}

\author{Petrus H. Zwart$^{1}$}

\affil{$^1$Molecular Biophysics and Integrated Bioimaging Division, Lawrence Berkeley National Laboratory, Berkeley, CA, USA}

""" + si + r"""

\IfFileExists{iopart-num.bst}{\bibliographystyle{iopart-num}}{\bibliographystyle{unsrt}}
\bibliography{refs}

\end{document}
"""
    (out / "supplement.tex").write_text(supp_tex)
    print("wrote", out / "main.tex", out / "supplement.tex", out / "refs.bib", f"({len(keys)} references)")


if __name__ == "__main__":
    main()
