"""
decision.py — from a probability to a Monday-morning list. The part nobody owned.

The proposal's decision layer, in one line: contact a donor when the expected value of contacting
them exceeds the cost of doing so.

    expected value per contact  =  P(return) × E[second-gift amount | return]
    contact if                     expected value  >  cost per contact
    break-even probability  p*  =  cost per contact / E[amount]

That is the same arithmetic as the Session 4–5 hospital case: act when p exceeds cost over benefit,
and never tune the threshold — derive it. Two policies fall out, and both are reported:

  • THRESHOLD policy — contact everyone with p > p*. The number of contacts is whatever it is.
  • CAPACITY policy  — rank by expected value, contact the top share she has hours for.

On the holdout we know what actually happened, so each policy is scored on what it identified
(realised subsequent giving among the contacted) net of what it cost. No causal claim: this is value
*identified*, not value *caused* — nobody in the data was randomly assigned to be called.

INPUTS THAT ARE PLACEHOLDERS — Malorie's workstream owns the real ones (see src/config.py):
  cost per contact, minutes per contact, monthly outreach hours. Every printed line that depends on
  them says PLACEHOLDER. E[amount] is the cohort-year median second gift among returners in TRAIN,
  which Albert said is fine to start.

    python src/decision.py data/processed/cohorts.parquet data/processed/reference_scores.parquet
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402


def expected_amount_by_cohort_year(train):
    """E[second gift | returned], per cohort year, from TRAIN only. Median, per Albert's guidance."""
    r = train[train["gave_again"] == 1]
    med = r.groupby(r["cohort_month"] // 12)["second_gift_amount"].median()
    return med, float(r["second_gift_amount"].median())


def score_policy(frame, contacted, cost):
    contacted = np.asarray(contacted, dtype=bool)
    n = int(contacted.sum())
    found = float(frame.loc[contacted, "second_gift_amount"].sum())
    total = float(frame["second_gift_amount"].sum())
    return {
        "contacts": n,
        "repeat_donors_found": int(frame.loc[contacted, "gave_again"].sum()),
        "value_identified": found,
        "share_of_value": found / total if total else 0.0,
        "cost": n * cost,
        "net": found - n * cost,
        "net_per_contact": (found - n * cost) / n if n else 0.0,
    }


def main(cohorts_path, scores_path):
    cost = config.COST_PER_CONTACT_USD
    cohorts = pd.read_parquet(cohorts_path)
    if config.STAKEHOLDER_POPULATION and "donor_type" in cohorts.columns:
        cohorts = cohorts[cohorts["donor_type"] == config.STAKEHOLDER_POPULATION]
    train = cohorts[cohorts["split"] == "train"]
    hold = cohorts[cohorts["split"] == "holdout"].merge(pd.read_parquet(scores_path), on="donor_id", how="inner")
    hold = hold.reset_index(drop=True)
    print(f"Holdout scored: {len(hold):,} donors · cost per contact ${cost:.2f} (PLACEHOLDER)\n")

    # ── 1. Expected amount and the break-even probability ──
    med_by_year, med_all = expected_amount_by_cohort_year(train)
    hold["exp_amount"] = (hold["cohort_month"] // 12).map(med_by_year).fillna(med_all)
    hold["ev_contact"] = hold["p_return"] * hold["exp_amount"]
    p_star = cost / med_all
    print(f"E[second gift | return], train median: ${med_all:,.2f}  (by cohort year: "
          + ", ".join(f"{int(y)+2000}: ${v:,.0f}" for y, v in med_by_year.tail(4).items()) + ")")
    print(f"Break-even probability p* = cost / E[amount] = {cost:.2f} / {med_all:.2f} = {p_star:.3f}  (PLACEHOLDER cost)")
    print(f"Holdout donors with p > p*: {(hold['p_return'] > p_star).mean():.1%}\n")

    # ── 2. Policies ──
    capacity = config.STEWARDSHIP_CAPACITY
    if config.MONTHLY_OUTREACH_HOURS:
        contacts_per_month = config.MONTHLY_OUTREACH_HOURS * 60 / config.CONTACT_MINUTES
        avg_cohort = hold.groupby("cohort_month").size().mean()
        capacity = min(1.0, contacts_per_month / avg_cohort)
        print(f"Capacity from hours: {config.MONTHLY_OUTREACH_HOURS} h/mo ÷ {config.CONTACT_MINUTES} min → "
              f"{contacts_per_month:.0f} contacts/mo ≈ {capacity:.1%} of an average cohort (PLACEHOLDER)\n")

    def top_share_within_month(col, share):
        mask = np.zeros(len(hold), dtype=bool)
        for _, idx in hold.groupby("cohort_month").indices.items():
            k = int(np.ceil(len(idx) * share))
            order = np.argsort(-hold[col].values[idx], kind="stable")
            mask[idx[order[:k]]] = True
        return mask

    policies = {
        f"threshold  p > p* ({p_star:.3f})":        hold["p_return"].values > p_star,
        f"capacity {capacity:.0%} by expected value": top_share_within_month("ev_contact", capacity),
        f"capacity {capacity:.0%} by gift size (her rule)": top_share_within_month("first_gift_amount", capacity),
        "contact everyone":                          np.ones(len(hold), dtype=bool),
    }
    rows = [{"policy": k, **score_policy(hold, v, cost)} for k, v in policies.items()]
    table = pd.DataFrame(rows)
    print("Policies on the holdout (value identified, not caused; cost is a PLACEHOLDER):")
    print(table.to_string(index=False, float_format=lambda v: f"{v:,.2f}"))

    # ── 3. Sensitivity to the placeholder cost — so Malorie can see what her number changes ──
    print("\nBreak-even p* and threshold-policy net, as cost per contact varies:")
    for c in [5, 10, 25, 50, 100]:
        ps = c / med_all
        m = hold["p_return"].values > ps
        r = score_policy(hold, m, c)
        print(f"  cost ${c:>3}: p* = {ps:.3f} · contacts {r['contacts']:>8,} ({m.mean():5.1%}) · "
              f"net ${r['net']:>12,.0f} · net/contact ${r['net_per_contact']:>7,.2f}")

    # ── 4. The Monday list: one real month, ranked, top of the list only ──
    last = hold["cohort_month"].max()
    month = hold[hold["cohort_month"] == last].sort_values("ev_contact", ascending=False)
    k = int(np.ceil(len(month) * capacity))
    out_dir = Path(__file__).resolve().parent.parent / "evals" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    from labels import month_index_to_str  # noqa: E402
    label = month_index_to_str(last)
    lst = month.head(min(k, 200))[["donor_id", "first_gift_amount", "first_month_gifts", "p_return", "exp_amount", "ev_contact"]]
    path = out_dir / f"monday_list_{label}_top{len(lst)}.csv"
    lst.to_csv(path, index=False, float_format="%.2f")
    print(f"\nMonday list for cohort {label}: {len(month):,} new donors, capacity → {k:,} contacts; "
          f"top {len(lst)} written to {path.name} (donor ids only, no PII in this file).")
    return table


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    main(sys.argv[1], sys.argv[2])
