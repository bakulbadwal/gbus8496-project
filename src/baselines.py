"""
baselines.py — the ladder our model has to beat.

Albert's condition on accepting a negative finding: *"provided the baselines are fair and the
comparison is careful."* A strawman we beat easily is worth less than no baseline at all, so each
rule here is implemented as the strongest honest version of itself.

WHY "RFM" COLLAPSES TO "M" IN THIS SETTING — the one thing to say out loud in the presentation
------------------------------------------------------------------------------------------------
Small nonprofits rank donors by RFM: Recency, Frequency, Monetary value. Applied to a cohort of
*first-time* donors it degenerates, and it is worth being precise about why:

  • Frequency is 1 for everyone. By construction — they have given exactly once.
  • Recency is identical for everyone in a cohort. Dates are month-level and a cohort *is* a month,
    so every donor in it last gave in the same month.
  • Monetary value is the only surviving signal.

So the honest, strongest simple baseline is "rank by first gift size", and that is genuinely what a
development lead does when she builds the list by hand. Calling it RFM would overstate it; calling
it a strawman would understate it. It is the real practice, correctly named.

Every ranker takes the cohort frame and returns a score, higher = contact sooner. Ranking happens
*within cohort month*, because the stakeholder's capacity is a monthly budget — she is choosing
among this month's new donors, not against donors from three years ago.
"""

import numpy as np
import pandas as pd


def rank_by_gift_amount(cohorts):
    """The real practice: bigger first gift, higher priority. The baseline that matters."""
    return cohorts["first_gift_amount"].astype(float).values


def rank_random(cohorts, seed=201):
    """Random ordering. The floor — shows what the capacity constraint alone buys you."""
    rng = np.random.default_rng(seed)
    return rng.random(len(cohorts))


def rank_contact_everyone(cohorts):
    """No ranking at all. Not a ranker so much as the policy the model is meant to replace.

    Scored separately in `evals/score.py`, because at full capacity it captures 100% of the value
    by definition — the interesting question is what it costs in staff hours to do that.
    """
    return np.ones(len(cohorts))


def rank_first_month_gift_count(cohorts):
    """Tiebreak-flavoured alternative: donors who funded several classrooms in their first checkout.

    Included because it is cheap and it tests whether 'breadth of first gift' carries signal that
    amount alone misses. If it beats amount, that is a finding worth a sentence.
    """
    return cohorts["first_month_gifts"].astype(float).values


BASELINES = {
    "gift_amount": rank_by_gift_amount,
    "first_month_gift_count": rank_first_month_gift_count,
    "random": rank_random,
}


def score_all_baselines(cohorts):
    """Return {name: score array} for every baseline, aligned to `cohorts` row order."""
    return {name: fn(cohorts) for name, fn in BASELINES.items()}
