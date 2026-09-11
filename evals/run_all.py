"""
run_all.py — the one command that reproduces every reported number.

Albert, on deliverable 3: "the code that produces your reported numbers. I should be able to
re-run your evaluation." This is that command. From a clean clone with the data in place:

    python evals/run_all.py

It runs, in order, and stops at the first failure:

  1. src/check_donor_id.py     the blocking check — donor ids must link across projects
  2. src/labels.py             donations → data/processed/cohorts.parquet
  3. evals/profile_cohorts.py  who is in the table, where the dollars sit
  4. evals/score.py            measurement 1 on citizen donors, then pooled for contrast

Each step's full output is saved to evals/results/<step>.txt so the numbers we quote in the
presentation are traceable to a file, not to memory. Total runtime on a laptop is about ten
minutes; the label step is most of it.

When the modelling workstream lands, add its scoring step here as step 5 so the model and the
baselines are always produced by the same command.
"""

import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DONATIONS = REPO / "data" / "raw" / "ICPSR_37898" / "DS0001" / "37898-0001-Data.tsv"
COHORTS = REPO / "data" / "processed" / "cohorts.parquet"
RESULTS = REPO / "evals" / "results"

STEPS = [
    ("01_check_donor_id",  [sys.executable, "src/check_donor_id.py", str(DONATIONS)]),
    ("02_labels",          [sys.executable, "src/labels.py", str(DONATIONS), str(COHORTS)]),
    ("03_profile_cohorts", [sys.executable, "evals/profile_cohorts.py", str(COHORTS)]),
    ("04_score_citizen",   [sys.executable, "evals/score.py", str(COHORTS), "holdout"]),
    ("05_score_pooled",    [sys.executable, "evals/score.py", str(COHORTS), "holdout", "--all-donors"]),
]


def main():
    if not DONATIONS.exists():
        sys.exit(f"Data not found: {DONATIONS}\nSee data/README.md for the download recipe.")
    RESULTS.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    for name, cmd in STEPS:
        print(f"\n{'=' * 78}\n{name}\n{'=' * 78}")
        t = time.time()
        proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
        out = proc.stdout + ("\n[stderr]\n" + proc.stderr if proc.stderr.strip() else "")
        (RESULTS / f"{name}.txt").write_text(out)
        # echo the last lines so a human watching sees the verdict, not the chunk counter
        tail = [l for l in proc.stdout.splitlines() if not l.startswith("  chunk")]
        print("\n".join(tail[-22:]))
        print(f"\n→ {name}: {'OK' if proc.returncode == 0 else 'FAILED'} in {time.time() - t:.0f}s, "
              f"output saved to evals/results/{name}.txt")
        if proc.returncode != 0:
            sys.exit(f"\nStopped at {name}. Fix it and re-run; later steps depend on it.")
    print(f"\nAll steps reproduced in {(time.time() - t0) / 60:.1f} minutes. Numbers are in evals/results/.")


if __name__ == "__main__":
    main()
