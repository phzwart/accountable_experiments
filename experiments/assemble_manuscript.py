"""Assemble the manuscript sections into one markdown file, without revision notes, and report word counts and citation keys."""
import re, sys
from pathlib import Path
M = Path(__file__).resolve().parents[1] / "manuscript"
MAIN = ["abstract", "introduction", "related_work", "framework", "experiments", "results", "discussion", "conclusion"]
APP = ["appendix_A", "appendix_B", "appendix_C"]
def body(name):
    t = (M / f"{name}.md").read_text()
    t = t.split("## Notes for revision")[0]
    t = re.sub(r"\n---\s*$", "", t.rstrip()) + "\n"
    t = re.sub(r"^(# .*?) \(draft[^)]*\)", r"\1", t, flags=re.M)
    return t
def words(t):
    t = re.sub(r"\$\$.*?\$\$", "", t, flags=re.S)
    t = "\n".join(l for l in t.splitlines() if not l.startswith("|"))
    return len(t.split())
out, keys = [], {}
for n in MAIN + APP:
    b = body(n); out.append(b)
    for k in re.findall(r"\[([A-Z][A-Za-z'\-]+\d{4}[a-z]?(?:[;,] ?[A-Z][A-Za-z'\-]+\d{4}[a-z]?)*)", b):
        for kk in re.split(r"[;,] ?", k): keys.setdefault(kk, set()).add(n)
    print(f"{n:15s} {words(b):5d}")
print("main text", sum(words(body(n)) for n in MAIN[1:]))
(M / "manuscript_assembled.md").write_text("\n\n".join(out))
print("\nkeys:", len(keys)); [print(" ", k, sorted(v)) for k, v in sorted(keys.items())]
