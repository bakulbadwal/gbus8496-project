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
  5. (pooled contrast)         same scorer, all donors — shows the organizations artefact
  6. src/reference_model.py    logistic floor on donations-file features, holdout scored once
  7. src/decision.py           break-even threshold, capacity vs threshold policies, Monday list
  8. src/features.py           Reid's projects join → cohorts_with_projects.parquet
     src/model.py              Rodolfo's gradient-boosted model, train-split dev loop only
  9. evals/calibration.py      measurement 2: calibration, error analysis by cohort year and
                               by first-gift size band, on the reference model's scores
 10. src/model.py --holdout    the final model scored on the 2017–18 holdout
 11. src/decision.py           decision layer on the model's own expected values
 12. evals/calibration.py      measurement 2 on the model's scores
 13. evals/qa_analyses.py      Q&A follow-ups: same teacher, who the model adds, capacity 5–30%, 2nd→3rd gift
 14. src/model.py --with-packet   sensitivity: thank-you packet as a feature (dev-val only)
 15. evals/thank_you_packet.py  packet by donor type, gift band, the $50 cutoff, project status

Each step's full output is saved to evals/results/<step>.txt so the numbers we quote in the
presentation are traceable to a file, not to memory. Steps 1–7 take about 1.5 minutes on a
laptop; step 8 adds about 8 minutes (6 for the join, 2 for the model), measured Sep 17.
"""

import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DONATIONS = REPO / "data" / "raw" / "ICPSR_37898" / "DS0001" / "37898-0001-Data.tsv"
COHORTS = REPO / "data" / "processed" / "cohorts.parquet"
RESULTS = REPO / "evals" / "results"

REF_SCORES = REPO / "data" / "processed" / "reference_scores.parquet"
PROJECTS = REPO / "data" / "raw" / "ICPSR_37898" / "DS0003" / "37898-0003-Data.tsv"
COHORTS_PROJ = REPO / "data" / "processed" / "cohorts_with_projects.parquet"
MODEL_SCORES = REPO / "data" / "processed" / "model_scores.parquet"

STEPS = [
    ("01_check_donor_id",  [sys.executable, "src/check_donor_id.py", str(DONATIONS)]),
    ("02_labels",          [sys.executable, "src/labels.py", str(DONATIONS), str(COHORTS)]),
    ("03_profile_cohorts", [sys.executable, "evals/profile_cohorts.py", str(COHORTS)]),
    ("04_score_citizen",   [sys.executable, "evals/score.py", str(COHORTS), "holdout"]),
    ("05_score_pooled",    [sys.executable, "evals/score.py", str(COHORTS), "holdout", "--all-donors"]),
    ("06_reference_model", [sys.executable, "src/reference_model.py", str(COHORTS), str(REF_SCORES)]),
    ("07_decision_layer",  [sys.executable, "src/decision.py", str(COHORTS), str(REF_SCORES)]),
    ("08_features",        [sys.executable, "src/features.py", str(COHORTS), str(PROJECTS), str(COHORTS_PROJ)]),
    ("08_model_dev",       [sys.executable, "src/model.py", str(COHORTS_PROJ)]),
    ("09_calibration",     [sys.executable, "evals/calibration.py", str(COHORTS), str(REF_SCORES),
                            "--out", "docs/slides/assets/slide7_calibration", "--ranking", "p_return"]),
    # Holdout — first scored Sep 22, after the model was frozen on dev-val. The model is
    # deterministic (fixed seed), so re-running reproduces the same scores; it does not re-peek.
    ("10_model_holdout",   [sys.executable, "src/model.py", str(COHORTS_PROJ), "--holdout"]),
    ("11_decision_model",  [sys.executable, "src/decision.py", str(COHORTS), str(MODEL_SCORES)]),
    ("12_calibration_model", [sys.executable, "evals/calibration.py", str(COHORTS), str(MODEL_SCORES),
                              "--out", "docs/slides/assets/slide7_calibration_model", "--ranking", "expected_value"]),
    ("13_qa_analyses",     [sys.executable, "evals/qa_analyses.py"]),
    ("14_packet_model_dev", [sys.executable, "src/model.py", str(COHORTS_PROJ), "--with-packet"]),
    ("15_thank_you_packet", [sys.executable, "evals/thank_you_packet.py"]),
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
