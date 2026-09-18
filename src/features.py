"""
features.py — the projects join as a script, so `run_all.py` can reproduce it.

This is the join from Reid's notebook 02 (`notebooks/02_feature_joining_and_effects.ipynb`),
lifted verbatim in logic so the model (src/model.py) has a reproducible input. It reads
`cohorts.parquet`, pulls the matching rows from the ICPSR Projects file (DS0003) in chunks, and
writes `cohorts_with_projects.parquet` with a `project_record_missing` flag for the ~0.26% of
first-project ids that are absent from the public-use Projects file.

    python src/features.py data/processed/cohorts.parquet \
        data/raw/ICPSR_37898/DS0003/37898-0003-Data.tsv data/processed/cohorts_with_projects.parquet

Kept-at-first-gift only: no post-outcome project fields (status, completion timing, thank-you
notes, impact letters) are read. TEACHER_ID is kept in the parquet for diagnostics but must not be
used as a predictor (memorization, not generalization).
"""

import sys
from pathlib import Path

import pandas as pd

PROJECT_KEEP = [
    "PROJECT_ID", "GRADE_LEVEL", "SUBJECT_CATEGORY", "SUBJECT_SUBCATEGORY",
    "OPTIONAL_SUBJECT_CATEGORY", "OPTIONAL_SUBJECT_SUBCATEGORY", "CATEGORY",
    "COST_OF_REQUESTED_RESOURCES", "VENDOR_SHIPPING_CHARGES",
    "PAYMENT_PROCESSING_CHARGES", "SALES_TAX", "FULFILLMENT_AND_LABOR_MATERIALS",
    "OPTIONAL_SUPPORT", "TOTAL_PRICE_EXCLUDING_OPTIONAL_1",
    "SCHOOL_PERCENTAGE_FREE_AND_RED_1", "STUDENTS_REACHED", "POSTED_MONTH",
    "SCHOOL_STATE", "TEACHER_ID",
]


def build(cohorts_path, projects_path, out_path, chunksize=200_000):
    cohorts = pd.read_parquet(cohorts_path)
    cohorts["first_project_id"] = cohorts["first_project_id"].astype("string")
    wanted = set(cohorts["first_project_id"].dropna())
    print(f"cohorts {len(cohorts):,} rows · unique first-project ids {len(wanted):,}")

    parts = []
    for i, chunk in enumerate(pd.read_csv(projects_path, sep="\t", usecols=PROJECT_KEEP,
                                          dtype="string", chunksize=chunksize)):
        hit = chunk[chunk["PROJECT_ID"].isin(wanted)]
        if not hit.empty:
            parts.append(hit)
        if i % 5 == 0:
            print(f"  chunk {i}: {sum(len(p) for p in parts):,} matched so far")
    projects = pd.concat(parts, ignore_index=True).rename(columns={"PROJECT_ID": "first_project_id"})
    assert projects["first_project_id"].is_unique, "Projects file has duplicate PROJECT_IDs"
    print(f"matched project rows {len(projects):,}")

    merged = cohorts.merge(projects, on="first_project_id", how="left", validate="many_to_one")
    merged["project_record_missing"] = ~merged["first_project_id"].isin(set(projects["first_project_id"]))
    print(f"match rate {(~merged['project_record_missing']).mean():.2%} · "
          f"missing {int(merged['project_record_missing'].sum()):,}")

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    merged.to_parquet(out_path, index=False)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    build(sys.argv[1], sys.argv[2], sys.argv[3])
