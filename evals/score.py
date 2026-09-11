"""
score.py — measurement 1, the headline. Run this to produce the number the project turns on.

Albert, approving the proposal, on what to do first:

    "the ranking result at the stewardship capacity against your ladder of baselines,
     since that is the decision"

So this file answers exactly one question, and does not compute anything else:

    Our stakeholder can personally follow up with the top X% of each month's new donors.
    If she works OUR ranked list instead of her current one, how much more of next year's
    giving does she reach — and how much per hour of her time?

WHAT WE ARE AND ARE NOT CLAIMING
--------------------------------
There is no randomised contact in this data. Nobody was assigned to be stewarded or not, so we
cannot measure the *uplift from being contacted*. We rank by predicted future value and report the
value **identified**, never "retained" or "caused". Every metric name in this file is chosen to keep
that honest, and the presentation must say it out loud.

RANKING IS WITHIN COHORT MONTH
------------------------------
Capacity is a monthly staffing budget. She is choosing among this month's new donors, not against
donors from three years ago, so the top-X% is taken per cohort month and then pooled.

    python evals/score.py data/processed/cohorts.parquet
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import config          # noqa: E402
import baselines       # noqa: E402


def _top_k_mask(frame, scores, capacity):
    """Boolean mask: the top `capacity` fraction of each cohort month, by score.

    Ties are broken by a stable index order rather than randomly, so the number is reproducible.
    A month with 7 donors at 10% capacity contacts 1 (ceil), never 0 — she does not skip a month.
    """
    work = pd.DataFrame({"cohort_month": frame["cohort_month"].values, "score": scores})
    mask = np.zeros(len(work), dtype=bool)
    for _, idx in work.groupby("cohort_month").groups.items():
        positions = work.index.get_indexer(idx)
        k = int(np.ceil(len(positions) * capacity))
        if k == 0:
            continue
        order = np.argsort(-work["score"].values[positions], kind="stable")
        mask[positions[order[:k]]] = True
    return mask


def evaluate_at_capacity(frame, scores, capacity):
    """Metrics for one ranking at one capacity. `frame` must be a single split (e.g. holdout)."""
    contacted = _top_k_mask(frame, scores, capacity)
    gave_again = frame["gave_again"].values.astype(bool)
    value = frame["second_gift_amount"].values.astype(float)

    n_contacted = int(contacted.sum())
    total_value = float(value.sum())
    found_value = float(value[contacted].sum())

    return {
        "capacity": capacity,
        "donors_contacted": n_contacted,
        "repeat_donors_found": int((contacted & gave_again).sum()),
        # Of the people she calls, what share come back? Drives whether the list feels worth working.
        "precision": float((contacted & gave_again).sum() / n_contacted) if n_contacted else 0.0,
        # Of everyone who came back, what share did she reach? The coverage side of the trade.
        "recall": float((contacted & gave_again).sum() / gave_again.sum()) if gave_again.sum() else 0.0,
        "value_identified": found_value,
        # The headline ratio: share of next year's repeat giving sitting inside the contacted list.
        "value_capture_rate": found_value / total_value if total_value else 0.0,
        # The business unit: dollars of subsequent giving per contact she makes.
        "value_per_contact": found_value / n_contacted if n_contacted else 0.0,
    }


def compare(frame, score_dict, capacities=None):
    """Every ranking against every capacity → one tidy table. This is the deliverable."""
    capacities = capacities or config.CAPACITY_SWEEP
    rows = []
    for name, scores in score_dict.items():
        for capacity in capacities:
            row = evaluate_at_capacity(frame, scores, capacity)
            row["ranking"] = name
            rows.append(row)
    out = pd.DataFrame(rows)[
        ["ranking", "capacity", "donors_contacted", "repeat_donors_found",
         "precision", "recall", "value_identified", "value_capture_rate", "value_per_contact"]
    ]
    return out.sort_values(["capacity", "value_per_contact"], ascending=[True, False])


def contact_everyone_reference(frame):
    """What working the whole list would cost and yield. Not a ranking — the policy we replace."""
    value = frame["second_gift_amount"].values.astype(float)
    return {
        "donors_contacted": len(frame),
        "repeat_donors_found": int(frame["gave_again"].sum()),
        "value_identified": float(value.sum()),
        "value_capture_rate": 1.0,
        "value_per_contact": float(value.sum() / len(frame)) if len(frame) else 0.0,
    }


def select_population(cohorts, population=config.STAKEHOLDER_POPULATION):
    """Apply the population scoping decision from config. See the comment there for why."""
    if population is None or "donor_type" not in cohorts.columns:
        return cohorts, "all donor types"
    return cohorts[cohorts["donor_type"] == population], population


def main(cohorts_path, split="holdout", model_scores=None, population=config.STAKEHOLDER_POPULATION):
    cohorts = pd.read_parquet(cohorts_path)
    cohorts, pop_label = select_population(cohorts, population)
    frame = cohorts[cohorts["split"] == split].reset_index(drop=True)
    print(f"Scoring split '{split}', population = {pop_label}: {len(frame):,} donors, "
          f"{frame['gave_again'].mean():.1%} gave again, "
          f"${frame['second_gift_amount'].sum():,.0f} of subsequent giving in total\n")

    scores = baselines.score_all_baselines(frame)
    if model_scores is not None:
        scores["model"] = model_scores  # populated by the modelling workstream

    table = compare(frame, scores)
    print(table.to_string(index=False, float_format=lambda v: f"{v:,.4f}"))

    ref = contact_everyone_reference(frame)
    print(f"\nReference — contact everyone: {ref['donors_contacted']:,} contacts, "
          f"${ref['value_identified']:,.0f} identified, "
          f"${ref['value_per_contact']:,.2f} per contact")

    at = config.STEWARDSHIP_CAPACITY
    headline = table[table["capacity"] == at].sort_values("value_per_contact", ascending=False)
    if not headline.empty:
        best = headline.iloc[0]
        print(f"\nAt the stewardship capacity ({at:.0%}), best ranking is '{best['ranking']}': "
              f"${best['value_per_contact']:,.2f} identified per contact, "
              f"{best['value_capture_rate']:.1%} of all subsequent giving reached.")
    return table


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        print("Usage: python evals/score.py <cohorts parquet> [split] [--all-donors]")
        sys.exit(1)
    pop = None if "--all-donors" in sys.argv else config.STAKEHOLDER_POPULATION
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(args[0], args[1] if len(args) > 1 else "holdout", population=pop)
