# Reid: Feature Exploration and Expected Value

## Workstream

The analysis starts from the reconstructed `cohorts.parquet` label table and joins each
donor's `first_project_id` to the ICPSR Projects file. The join is many-to-one and matches
3,268,721 of 3,277,153 cohort rows (99.74%). The remaining rows are retained with a
`project_record_missing` indicator.

Raw and processed data are intentionally not committed. Reproducible code is in
`notebooks/02_feature_joining_and_effects.ipynb`.

## Variables Constructed

Donor-side features:

- `first_gift_amount`: positive first-month donation total.
- `first_month_gifts`: number of donation records in the first month.
- First-month flags for matching, teacher referral, gift card, and thank-you packet.
- `donor_type`, cohort month, and the time-based train/holdout split.

Project-side features:

- Grade, subject, optional subject, category, and state.
- Resource cost, shipping, processing, tax, fulfillment/labor/materials, optional support,
  and total project price.
- Free/reduced-price lunch percentage, students reached, and posted month.

Leakage controls:

- Teacher ID is not used as a raw predictor.
- Post-outcome status, completion timing, thank-you notes, and impact letters are excluded.
- Thank-you packet timing is ambiguous and should remain descriptive unless timing is verified.

## Exploratory Findings

There are two different prediction questions:

1. Whether a donor gives again within the twelve-month label window.
2. How much a returning donor gives during that window.

First-gift size has a weak-to-moderate relationship with returning (`r` approximately 0.127)
but a stronger relationship with subsequent amount among returners (`r` approximately 0.554
on log amounts). This supports separate retention and conditional-value analyses.

Project-only exploratory differences were generally modest. The most promising combinations
were state by category, subject by category, and subject by grade. Project features became more
informative when interacted with gift-size deciles, especially category, subject, grade, and
state by gift size.

## Expected Value Analysis

The full citizen-training analysis uses 2,156,784 donors and a 13.97% repeat rate. It reports
both:

- `P(gave_again)`, the repeat-rate outcome.
- `E(second_gift_amount)`, expected subsequent dollars across all donors.
- `E(log(second_gift_amount) | gave_again)`, conditional gift size among returners.

The full term-level outputs are generated locally and are not committed with the raw data.
The compact family-level table is committed at `docs/term_value_effects_unique_families.csv`.

The strongest family-level patterns were:

- State by gift decile for expected value, with the strongest observed cell around +$381 per donor.
- Subject by gift decile and category by gift decile for expected value.
- Category by gift decile, especially Supplies in a high gift-size decile, for conditional amount.
- First-gift size remained the strongest single relationship with conditional donation size.

These are training-data associations, not causal effects or final model performance. Small cells
and multiple comparisons require regularization, false-discovery-rate control, and time-based
validation.

## Baseline

On the citizen-donor holdout at 10% stewardship capacity, ranking by first-gift amount alone
produced approximately:

- 19.8% precision
- 15.7% recall
- 56.5% of subsequent value identified
- $116.44 subsequent value per contact

This is the benchmark a project-feature model must beat. An exploratory differential effect is
not evidence that a feature beats this ranking policy. The final comparison must use the same
capacity and untouched holdout, reporting precision, recall, value captured, calibration, and
dollars per contact.
