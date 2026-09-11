"""
config.py — every decision that must be identical across all five workstreams.

The point of this file: five people are working in parallel, each in their own notebook. If the
label window or the split boundary is written down in five places it will silently drift in one of
them, and every number we report afterwards is incomparable. So it is written down ONCE, here, and
everything imports it.

If you want to change a value in this file, say so in the team chat first. Changing it invalidates
every number anyone has already produced.
"""

# ── The label ────────────────────────────────────────────────────────────────────────────────────
# "Did this first-time donor give again within 12 months of their first gift?"
# Dates in the public-use file are month-level (no day), so the window is counted in whole calendar
# months: a donor whose first gift is in month M is labelled 1 if they give again in M+1 .. M+12.
SECOND_GIFT_WINDOW_MONTHS = 12

# ── Observation boundaries ───────────────────────────────────────────────────────────────────────
# The release covers projects posted Sep 2002 – Jun 2019, with activity observed through Dec 2019.
# A donor is only labelable if their full 12-month window closes on or before the activity cutoff,
# otherwise a 0 might just mean "we stopped looking". Last labelable first-gift month is therefore
# Dec 2018 (window closes Dec 2019).
DATA_ACTIVITY_END = "2019-12"
LAST_LABELABLE_COHORT = "2018-12"

# Left-censoring: a donor whose first *recorded* gift is early in the file may have given before
# coverage began. DonorsChoose data starts near platform inception so this is mild, but cohorts in
# the first year are the least trustworthy. Reported as a limitation; not dropped.
FIRST_TRUSTED_COHORT = "2003-01"

# ── The split — time-based, never random ─────────────────────────────────────────────────────────
# Train on early first-gift cohorts, hold out the late ones. A random split would let the model see
# the future, and the whole point of the project is behaviour changing over time.
TRAIN_COHORT_END = "2016-12"      # cohorts up to and including this month → train
HOLDOUT_COHORT_START = "2017-01"  # 2017 and 2018 cohorts → held out, untouched during development

# ── The decision ─────────────────────────────────────────────────────────────────────────────────
# Our stakeholder is a development lead who can personally steward only a fraction of first-time
# donors each month. That fraction is the capacity, and the headline result is measured AT it.
# Albert, approving the proposal: report "the ranking result at the stewardship capacity against
# your ladder of baselines, since that is the decision."
STEWARDSHIP_CAPACITY = 0.10                       # default: she can reach the top 10%
CAPACITY_SWEEP = [0.01, 0.05, 0.10, 0.20, 0.50]   # reported as a curve, so the result is not one
                                                  # cherry-picked operating point

# ── The population — a scoping decision the team must confirm ────────────────────────────────────
# The file holds three donor types, and they are not one population (holdout cohorts, Sep 11):
#
#     type            share of donors   repeat rate   share of subsequent $   median first gift
#     citizen donor        86.4%           12.6%             23.1%                 $40
#     organization          0.1%           69.8%             62.5%             $11,988
#     teacher              13.5%           38.2%             14.4%                 $65
#
# 708 organizations hold 62.5% of every dollar that came back; the largest made 66,348 donations in
# its window. Those are corporate matching programs and foundations, not people a development lead
# steward. Teachers are seeding their own classrooms. Pooling all three makes any ranker look
# brilliant by finding the corporations, which is not the decision our stakeholder faces.
#
# Default: score citizen donors only. Set to None to score everyone (the pooled number is reported
# in the notebook for contrast). Labels are built for ALL donors regardless — this filters at
# scoring time, so the choice is reversible and both numbers stay reproducible.
STAKEHOLDER_POPULATION = "citizen donor"

# ── Column names ─────────────────────────────────────────────────────────────────────────────────
# The ICPSR release may not use the same names as the older Kaggle release. Rather than hardcode,
# every loader resolves names through these candidate lists (case- and underscore-insensitive).
# Add to a list rather than editing code elsewhere.
COLUMN_CANDIDATES = {
    # required — label construction cannot proceed without these four
    "donor_id":   ["donor_id", "donorid", "donor", "donoracctid"],
    "project_id": ["projectid", "project_id", "proj_id", "projid"],
    "month":      ["created_month", "donation_created_month", "donation_month", "month",
                   "donation_received_date", "created_date", "donation_timestamp"],
    "amount":     ["amount", "donation_amount", "donation_total", "dollar_amount"],
    # optional first-gift attributes — carried onto the cohort row when present, skipped when not.
    # Verified against the ICPSR 37898 DS1 codebook (docs/codebook/DS1_Donations_Codebook.pdf).
    "donor_type":       ["donor_type", "donortype"],
    "matched":          ["payment_was_matched", "matched"],
    "teacher_referred": ["is_teacher_referred", "teacher_referred"],
    "thank_you_packet": ["thank_you_packet_mailed", "thankyou_packet_mailed", "thank_you_packet"],
    "gift_card":        ["payment_included_campaign_gift_1", "payment_included_campaign_gift_card"],
}
REQUIRED_COLUMNS = ("donor_id", "project_id", "month", "amount")
OPTIONAL_FLAGS = ("matched", "teacher_referred", "thank_you_packet", "gift_card")   # yes/no style
OPTIONAL_CATEGORICAL = ("donor_type",)
