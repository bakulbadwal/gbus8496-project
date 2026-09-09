"""
make_fixture.py — synthetic donations with the real schema, so the pipeline can be tested today.

ICPSR access is not set up yet, and waiting for it to find out whether the code runs would waste
days. This generates a small file with the same shape as the real one — same column names, month
granularity, donors recurring across projects — so `check_donor_id.py`, `labels.py` and `score.py`
can be run end to end and their mechanics verified before the real data lands.

    python evals/make_fixture.py data/raw/fixture_donations.csv

🔴 EVERY NUMBER PRODUCED FROM THIS FILE IS MEANINGLESS. It is fake data with signal deliberately
baked in. It proves the code runs and the arithmetic is self-consistent; it proves nothing about
donor behaviour. Never quote a figure derived from it. The moment the real file is available, rerun
everything against that and discard these outputs.

Deliberate structure, so a broken pipeline shows up as a failed assertion rather than a plausible
number:
  • donors recur across DIFFERENT projects  → check_donor_id.py should PASS
  • larger first gifts repeat more often    → the gift_amount baseline should beat random
  • a slow upward drift in repeat rate      → the time trend should be visible across cohorts
  • some donors first appear in 2019        → labels.py should drop them (unclosed window)
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

N_DONORS = 40_000
SEED = 201


def make(n_donors=N_DONORS, seed=SEED):
    rng = np.random.default_rng(seed)
    rows = []

    for donor in range(n_donors):
        donor_id = f"d{donor:07d}"

        # First gift somewhere in 2003-01 .. 2019-06 (some deliberately past the labelable cutoff).
        first_month = int(rng.integers(36, 234))  # months since 2000-01
        first_amount = float(np.round(np.exp(rng.normal(3.4, 0.9)), 2))  # lognormal, median ~$30

        # Repeat probability rises with gift size and drifts up slightly over the years — both
        # effects are invented, and both exist so a working pipeline can detect them.
        size_effect = 0.18 * (np.log1p(first_amount) - 3.4) / 1.5
        drift = 0.0008 * (first_month - 36)
        p_repeat = float(np.clip(0.22 + size_effect + drift, 0.02, 0.85))

        # First giving event: sometimes several classrooms in one checkout.
        n_first = 1 + int(rng.random() < 0.18) + int(rng.random() < 0.05)
        for _ in range(n_first):
            rows.append((donor_id, f"p{rng.integers(0, 300_000):06d}", first_month,
                         round(first_amount / n_first, 2)))

        if rng.random() < p_repeat:
            # One to three later gifts, inside the 12-month window, to DIFFERENT projects — this is
            # what makes the donor-ID link check meaningful.
            for _ in range(1 + int(rng.random() < 0.4) + int(rng.random() < 0.15)):
                gap = int(rng.integers(1, 13))
                amount = float(np.round(first_amount * np.exp(rng.normal(0, 0.5)), 2))
                rows.append((donor_id, f"p{rng.integers(0, 300_000):06d}", first_month + gap, amount))

        # A few donors return well after the window — they must NOT be labelled positive.
        if rng.random() < 0.08:
            rows.append((donor_id, f"p{rng.integers(0, 300_000):06d}",
                         first_month + int(rng.integers(14, 40)), first_amount))

    df = pd.DataFrame(rows, columns=["DONOR_ID", "PROJECTID", "_month_index", "AMOUNT"])
    df["CREATED_MONTH"] = df["_month_index"].map(lambda m: f"{2000 + m // 12:04d}-{m % 12 + 1:02d}")
    df = df.drop(columns=["_month_index"]).sample(frac=1.0, random_state=seed)  # shuffle row order
    return df[["DONOR_ID", "PROJECTID", "CREATED_MONTH", "AMOUNT"]]


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/raw/fixture_donations.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    df = make()
    df.to_csv(out, index=False)
    print(f"Wrote {len(df):,} synthetic donation rows for {df['DONOR_ID'].nunique():,} donors → {out}")
    print("Reminder: numbers from this file are meaningless. Mechanics only.")
