"""
profile_cohorts.py — who is actually in the cohort table, and where the dollars sit.

Run this before believing any ranking result. It exists because the first real run of
`score.py` reported that ranking by gift size found 80% of all subsequent giving at 10% capacity,
which looked like a triumph and was actually an artefact: a few hundred corporate matching
programs hold most of the dollars, and they are trivially identifiable by first-gift size.

    python evals/profile_cohorts.py data/processed/cohorts.parquet [split]

Prints, for the chosen split:
  1. the three donor types — share of donors, repeat rate, share of subsequent value
  2. value concentration — what share of all subsequent giving the top X% of donors hold
  3. the largest second-gift totals, so the whales are visible by name (well, by type)
  4. the same concentration for citizen donors only, so the residual skew is honest too

Every number here is reproducible from the cohort table; nothing is typed in by hand.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import config  # noqa: E402

pd.set_option("display.width", 160)
pd.set_option("display.float_format", lambda v: f"{v:,.3f}")


def concentration(values, label, shares=(0.0001, 0.001, 0.01, 0.05, 0.10)):
    v = np.sort(np.asarray(values, dtype=float))[::-1]
    tot, n = v.sum(), len(v)
    print(f"\n=== VALUE CONCENTRATION — {label}: share of subsequent giving held by the top X% of donors ===")
    for p in shares:
        k = max(1, int(n * p))
        print(f"  top {p:>7.2%} of donors ({k:>8,}) → {v[:k].sum() / tot:6.1%}")


def main(path, split="holdout"):
    c = pd.read_parquet(path)
    h = c[c["split"] == split].copy()
    print(f"{split.upper()}: {len(h):,} donors, {h.gave_again.mean():.1%} gave again, "
          f"${h.second_gift_amount.sum():,.0f} of subsequent giving\n")

    if "donor_type" in h.columns:
        print("=== BY DONOR TYPE ===")
        g = h.groupby("donor_type").agg(donors=("donor_id", "size"),
                                        repeat_rate=("gave_again", "mean"),
                                        median_first_gift=("first_gift_amount", "median"),
                                        subsequent_value=("second_gift_amount", "sum"))
        g["donor_share"] = g.donors / g.donors.sum()
        g["value_share"] = g.subsequent_value / g.subsequent_value.sum()
        print(g[["donors", "donor_share", "repeat_rate", "median_first_gift",
                 "subsequent_value", "value_share"]].to_string())

    concentration(h.second_gift_amount, "ALL DONOR TYPES")

    print("\n=== 12 LARGEST SECOND-GIFT TOTALS ===")
    cols = [c for c in ["donor_type", "cohort", "first_gift_amount", "second_gift_count", "second_gift_amount"] if c in h.columns]
    print(h.nlargest(12, "second_gift_amount")[cols].to_string(index=False))

    pop = config.STAKEHOLDER_POPULATION
    if pop and "donor_type" in h.columns:
        sub = h[h.donor_type == pop]
        concentration(sub.second_gift_amount, f"{pop.upper()} ONLY", shares=(0.001, 0.01, 0.10))
        print(f"\nconfig.STAKEHOLDER_POPULATION = {pop!r}: {len(sub):,} donors, "
              f"{sub.gave_again.mean():.1%} repeat, ${sub.second_gift_amount.sum():,.0f} subsequent giving")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "holdout")
