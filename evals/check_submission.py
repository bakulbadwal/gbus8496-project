"""
check_submission.py — pre-flight for the Oct 2 zip, and the command that builds it.

Albert's deliverables, one zip named Group_11.zip to Box by Fri Oct 2, 11:59 PM:
  1. the slides used in the presentation
  2. a notebook (or small repo) with the full pipeline, annotated
  3. the evaluation: test data / ground truth provenance / code that produces the reported numbers
  4. the dataset, or clear access instructions
  5. a one-page executive summary
  6. a short AI-use note

    python evals/check_submission.py          # checklist only
    python evals/check_submission.py --zip    # checklist, then build Group_11.zip from a clean tree

The zip is built with `git archive`, so it contains exactly what is committed and nothing from
data/ or .venv/. Run the checklist a week before the deadline, not the night of.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GROUP = "11"


def ok(msg):   print(f"  ✅ {msg}"); return True
def bad(msg):  print(f"  ❌ {msg}"); return False
def warn(msg): print(f"  ⚠️  {msg}")


def check_notebooks():
    nbs = sorted((REPO / "notebooks").glob("*.ipynb"))
    if not nbs:
        return bad("no notebooks in notebooks/")
    good = True
    for nb in nbs:
        d = json.loads(nb.read_text())
        code = [c for c in d["cells"] if c["cell_type"] == "code"]
        executed = sum(1 for c in code if c.get("execution_count"))
        errors = [o for c in code for o in c.get("outputs", []) if o.get("output_type") == "error"]
        md = sum(1 for c in d["cells"] if c["cell_type"] == "markdown")
        if errors:
            good = bad(f"{nb.name}: {len(errors)} error output(s) — re-execute cleanly")
        elif executed < len(code):
            good = bad(f"{nb.name}: {len(code) - executed} of {len(code)} code cells have no saved output — execute before zipping")
        else:
            if md < len(code) * 0.5:
                warn(f"{nb.name}: only {md} markdown cells for {len(code)} code cells — Albert wants annotation he can follow without asking")
            ok(f"{nb.name}: {len(code)} code cells executed, 0 errors, {md} markdown cells")
    return good


def check_file(path, label, must_not_contain=None):
    p = REPO / path
    if not p.exists():
        return bad(f"{label}: {path} is missing")
    if must_not_contain:
        txt = p.read_text(errors="replace")
        hits = [m for m in must_not_contain if m in txt]
        if hits:
            return bad(f"{label}: {path} still contains {hits} — fill it in")
    return ok(f"{label}: {path}")


def check_results():
    r = REPO / "evals" / "results"
    files = sorted(r.glob("*.txt")) if r.exists() else []
    if not files:
        return bad("evals/results/ is empty — run python evals/run_all.py")
    return ok(f"evals/results/: {len(files)} step outputs present")


def check_git_clean():
    st = subprocess.run(["git", "status", "--porcelain"], cwd=REPO, capture_output=True, text=True).stdout
    if st.strip():
        return bad(f"working tree has uncommitted changes — the zip is built from commits:\n{st}")
    return ok("git working tree clean")


def build_zip():
    out = REPO.parent / f"Group_{GROUP}.zip"
    if out.exists():
        out.unlink()
    subprocess.run(["git", "archive", "--format=zip", f"--prefix=Group_{GROUP}/", "-o", str(out), "HEAD"],
                   cwd=REPO, check=True)
    size = out.stat().st_size / 1e6
    print(f"\n📦 {out}  ({size:.1f} MB)")
    listing = subprocess.run(["unzip", "-l", str(out)], capture_output=True, text=True).stdout
    for bad_path in ["data/raw", ".tsv", ".venv", "ICPSR_37898"]:
        if bad_path in listing:
            print(f"  ❌ zip contains {bad_path} — data must not ship. Check .gitignore.")
            return False
    print("  ✅ no data, no venv inside")
    return True


def main(build=False):
    print(f"Submission pre-flight — Group_{GROUP}.zip, due Fri Oct 2 2026 11:59 PM to Box\n")
    checks = [
        ("1. Slides",          lambda: check_file("docs/slides/Group11_deck.pptx", "deck")),
        ("2. Notebook(s)",     check_notebooks),
        ("3. Evaluation",      lambda: check_file("evals/run_all.py", "reproduction command") and check_results()),
        ("4. Data access",     lambda: check_file("data/README.md", "fetch recipe")),
        ("5. Exec summary",    lambda: check_file("docs/EXEC-SUMMARY.md", "one-pager", must_not_contain=["[Fill in"])),
        ("6. AI-use note",     lambda: check_file("AI-USE-NOTE.md", "AI-use note")),
        ("Repo state",         check_git_clean),
    ]
    results = []
    for name, fn in checks:
        print(name)
        results.append(bool(fn()))
    passed = sum(results)
    print(f"\n{passed}/{len(results)} checks pass.")
    if build:
        if passed < len(results):
            print("Fix the ❌ items before building the zip."); sys.exit(1)
        sys.exit(0 if build_zip() else 1)
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main(build="--zip" in sys.argv)
