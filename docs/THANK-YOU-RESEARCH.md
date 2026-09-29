# Thank-you packets and digital notes: what this project can establish

Research for Thadeus, September 26, 2026; integration updated September 29.
Proposed interpretation for team review.
Original research base: `0778343`. Integrated with GitHub `main` at `25fbeee` on September 29,
including the merged parser fix and rebuilt evaluation. Work on `thadeus/thank-you-research`.

## Recommendation

**Keep a short descriptive analysis and a documented negative finding about identification.**
We can describe who has a packet recorded, compare subsequent giving, and demonstrate why the
public release cannot establish that thanking caused another gift. Do not present the existing
“+12% packet effect” as an estimated causal uplift, and keep these snapshot fields out of the
first-gift prediction model. This is not evidence that thanking has no effect.

An especially useful contribution is that the timing objection is now measurable: **653 donors
with a packet recorded made their first repeat gift definitely before their first project was
funded.** Under the documented post-funding workflow, that project's packet could not have caused
the first repeat gift in those cases. The rest remain timing-ambiguous.

## Research history and what Teams adds

On September 26, the local checkout was clean. `main` was updated from `03fdd60` to `0778343`, which includes
Thadeus's evaluation review, the Q&A follow-ups, and Bakul's packet exploration. The previous
evaluation branch is preserved. The main model already excludes thank-you fields; a separate
development-only run adds the packet flag. Its saved metrics show no improvement, but those model
runs were not retrained during the original September 26 research. Prediction gains do not estimate intervention effects.

In [Malorie's September 24 message](https://teams.microsoft.com/l/message/19%3A057b2a3c0192468f9a132c09b2c28378%40thread.v2/1790268747537),
the explicit question is whether a gift cutoff could test thanking. The September 25 discussion
about Rodolfo's donation distinguishes an immediate email from a possible personalized teacher
message. That is useful context, not a verified mapping from today's emails to historical variables.
I read the chat text and attachment listings; the attached screenshots and presentation were not inspected.
No messages were sent. Albert's guidance still places this after ranking and error analysis, and
explicitly allows dropping the causal packet question when timing is ambiguous.

## Three different forms of thanks

| Field | What it records | What it does not establish |
|---|---|---|
| `THANK_YOU_PACKET_MAILED` in Donations | A student packet was mailed for a donation requiring it | Mailing/receipt date, opt-in, eligibility reason, receipt by the donor, or availability at the first gift |
| `THANKYOU_NOTE` in Projects | A digital teacher note after project funding | Donor-specific receipt, content, personalization, send time or whether it preceded repeat giving |
| `IMPACT_LETTER` in Projects | A digital teacher account of implementation and student benefit | Delivery/reading, timing or content |

The dictionary explicitly places the digital note **after funding**. Public-use note and impact
text is either blank or `MASKED BY ICPSR`. That supports a **recorded-presence proxy**, not sentiment,
quality, personalization, or proof that a particular donor was thanked. Blank is “no note recorded,”
not proof that no communication occurred. Project-level fields are shared across donors.

DonorsChoose's [November 2015 description](https://blog.donorschoose.org/articles/power-of-student-thank-you-notes)
documents a $50 minimum plus providing a mailing address/choosing student thanks. Thus receipt is
not automatic above the cutoff. Its internal opt-in comparison is external observational evidence;
we have not reproduced it and should not import its dollar claim into our business case.
The [current help page](https://help.donorschoose.org/hc/en-us/articles/201937136-Donors-waiting-for-Student-Thank-Yous)
describes an average wait of three to four months **after funding**. This is context, not a historical
mailing-date imputation or a guarantee about any donor in our dataset.

## Recomputed findings

The primary population is the project's 2,971,755 citizen donors with first observed gifts in
2003–2018 and complete 12-month windows. “Repeat” means at least one positive donation in calendar
months M+1 through M+12; same-month repeats are excluded. “Future dollars” is the sum over that
window, not just the second transaction. These are retrospective exploratory analyses, including
separate train/holdout descriptions; they do not tune or re-score the headline model.

### Packets: a positive association survives descriptive adjustment

| First-month packet flag | Donors | Repeat rate | Mean subsequent 12-month giving |
|---|---:|---:|---:|
| No packet recorded | 2,643,712 | 12.77% | $14.51 |
| Packet recorded | 328,043 | 20.28% | $67.52 |

The raw gap is **7.52 percentage points**. In the 2017–2018 holdout cohorts it is 18.59% versus
11.71%. This describes selected groups; it is not the additional giving a packet generated.
The association is not universal across populations or time: teachers show the opposite pooled
direction, and citizens in 2007–2008 also show a negative raw association.

I standardized within cohort year × gift-size band × teacher referral × matched gift × campaign
gift-card cells, requiring at least 100 donors in each packet group. For donors with one
first-month donation, a funded project, and an amount of at least $50, the standardized rates are
**17.52% versus 13.86% (+3.65 points)**. Supported cells contain 919,340 of 938,049 donors (98.0%).
This is a pooled-population descriptive comparison. Opt-in, engagement, exact gift size within
bands, teacher behavior and exposure timing are still unresolved. Restricting to final funded
status selects on a post-gift outcome; it does not create random assignment.

The older +12.5-point gift-band-adjusted figure is arithmetically reproducible but has weak overlap:
only 226 packet donors occur below $10 and 1,411 at $10–24.99, versus 868,778 no-packet donors across
those bands. Reweighting those unusual recipients to the no-packet population magnifies their
influence. The new estimate uses different controls, weights and a narrower population, so the
difference between the two numbers is not itself a measured confounding effect.

### Digital notes: the comparison is largely about project funding

To align each donor with one unambiguous project, this analysis uses the **2,743,076 citizens with
exactly one donation row in their first month**. All now join to Projects.

Of the 2,451,846 donors to ultimately funded projects, **2,449,289 (99.90%)** have a digital note
recorded; only 2,557 do not. No digital note is recorded for the 278,330 donors to expired projects.
The funded no-note minority returns at 15.80% versus 11.80% for the note group; this is neither
evidence that notes hurt nor a credible untreated comparison. After requiring reasonable cell
sizes, only **3.0%** of funded donors remain in supported note-versus-no-note strata.

Impact letters retain more variation: use the generated status-specific table as supplementary
description. Their completion is also a later teacher/project outcome, not a baseline treatment.
We cannot compare the efficacy of physical packets and digital notes directly: eligibility,
measurement level and timing differ, and most packet recipients also have a digital note recorded.

### The $50 idea does not support a causal headline

The existing `first_gift_amount` is a **sum across the first month** and the packet flag means
“any row in that month.” There are 228,679 multi-row citizen donors. I therefore repeated cutoff
checks on donors with exactly one first-month donation and verified their raw amount, project and
packet flag against the cohort file, with zero discrepancies.

| Single-donation comparison | Packet-rate jump | Repeat-rate jump | Ratio of jumps, NOT an effect |
|---|---:|---:|---:|
| $45–49.99 vs $50–54.99 | +12.76 pp | −2.45 pp | −0.192 |
| Same, excluding exactly $50 | +20.04 pp | −0.91 pp | −0.045 |
| Non-multiples-of-five, whole dollars $41–49 vs $51–59 | +17.17 pp | +1.97 pp | +0.115 |

**538,562 of 557,355 donors in the $45–54.99 window gave exactly $50 (96.6%).** The groups also
differ in observed composition: teacher-referral rates are 33.9% below versus 55.9% at/above $50;
matched-gift rates are 25.2% versus 35.7%. Dropping common amounts changes the population, and
removing $50 alone does not give the same sign as selecting non-round whole-dollar amounts.

These are finite-window comparisons, not a fitted regression-discontinuity design. A threshold
study would need a historically verified assignment rule, a correctly measured running variable,
adequate support near the threshold, continuity/balance diagnostics, bandwidth robustness and
credible exclusion/monotonicity assumptions for a receipt-effect interpretation. Here we have
self-chosen/heaped amounts, optional receipt, changes over years, and a sample-sensitive sign.
Missing mail dates alone would not rule out every possible **eligibility** effect design; the
present comparisons simply do not establish its required assumptions. A bootstrap interval
around the selected ratio only quantifies resampling uncertainty, not these identification failures.

### The timing problem is partly observable

For funded projects, the dictionary defines days to completion as days from posting to funding.
Let the project posting month begin on day S and its completion lag be D. Its earliest possible
funding day is S+D. If the entire first-repeat month ends before that day, repeat giving definitely
preceded funding, even though the precise posting day is withheld.

Using this conservative bound, among single-first-month-row citizens:

- **653 of 50,622 packet-recorded repeaters (1.29%)** gave again definitely before funding.
- **4,834 of 289,041 repeaters with a digital note recorded (1.67%)** did so.

These are lower bounds under the dictionary's date semantics and documented post-funding workflow.
They are **not** the total shares who returned before their packet/note: funding is only an earliest
possible starting point for thanks, and month-level comparisons leave many cases unresolved.
They do not establish that the other donors were thanked before returning. Likewise, moving the
outcome to M+4..M+12 preserves a positive raw packet association but cannot establish exposure order.
Snapshot flags may have become positive even after a donor's 12-month outcome window.

## An additional project issue: the missing joins were a parsing bug

At the original research base, `src/features.py` and earlier exploratory loaders used ordinary CSV quote handling on
the TSV. Literal quotation marks in project titles cause the parser to consume subsequent rows:
it yields **2,144,304 projects**, 5,513 short of the documented count. Reading with
`quoting=csv.QUOTE_NONE` yields **2,149,817 unique projects**, each physical row has 28 fields, and
the file MD5 equals the ICPSR manifest: `37e7bd5ac4af5b71545fc6538c5be3dd`.

The previous missing-project count was 7,651 citizen donors; with the corrected parser it is **zero**.
The existing packet report was first reproduced exactly using its original parser, then the new
audit was run with the corrected loader. This explains differences in project-based counts.
**Resolved on main:** PR #2 merged on September 27 and corrected the shared Projects loader,
rebuilt project features and reran the frozen evaluation. See [PROJECT-PARSER-FIX.md](PROJECT-PARSER-FIX.md)
for the headline changes and independent check. The September 29 integration routes this audit
through `src/projects.py` too. The research adds descriptive evidence without changing the model,
its features, hyperparameters or splits.

## What to present and what to do next

**Suggested slide wording:** “Donors with a thank-you packet recorded were more likely to return
(20.3% vs 12.8%). But this is not an estimate of the packet's effect: recipients were selected,
dates are missing, and some repeat gifts definitely preceded project funding. The $50 comparison
changes sign with the sample. We recommend a randomized test of additional stewardship.”

Use the raw comparison and the cutoff sensitivity figure on one appendix slide; give the digital
note and timing audit a short explanation in the notebook. Do not let this replace the project's
ranking result. The negative finding is that **this release does not identify the intervention
effect**, not that gratitude is ineffective.

For better observational data, request donor/project-linked opt-in and eligibility records;
amount used by the historical eligibility rule; project funding, note creation/send, packet
mail/receipt and exact gift timestamps; and flags distinguishing new cash from reallocated credits.
Then define exposure at a specified decision time and count only later outcomes. A funding or
mailing landmark changes the target population and requires equal follow-up; it is not a fix for
unmeasured selection by itself. Restricted note text would enable content analysis but does not
necessarily supply delivery dates—the access documentation must be checked first.

For a pilot, randomize **additional** personalized digital thanks and/or a physical packet against
standard stewardship, leaving required acknowledgments in every arm. If the team wants separate
and combined effects, use a 2×2 design when sample size allows; otherwise test one intervention.
Set the assignment time and outcome window in advance, log send/receipt dates, and report
intention-to-treat differences in repeat rate and average subsequent giving per assigned donor.
Net incremental value is the between-arm difference in average giving minus the difference in
per-donor costs. The project-level fulfillment/labor cost field includes other work and is not
an identified marginal cost per packet.

Althoff and Leskovec's [2015 DonorsChoose study](https://arxiv.org/html/1503.02729), particularly
sections 2 and 5.2–5.3 and Table 2, used response-time information to study digital confirmation
notes and impact letters. That supports the relevance of **timeliness** and clarifies the richer
data needed; it is not a replicated result from our public-use release or a randomized proof.

## Reproduction and evidence

From the repository root, with the raw files in place:

```bash
python src/check_donor_id.py data/raw/ICPSR_37898/DS0001/37898-0001-Data.tsv
python src/labels.py data/raw/ICPSR_37898/DS0001/37898-0001-Data.tsv data/processed/cohorts.parquet
python evals/thank_you_audit.py
```

`python evals/run_all.py` also includes this as step 18. The annotated reader is
[`notebooks/05_thank_you_research.ipynb`](../notebooks/05_thank_you_research.ipynb).
All numeric results above come from [`evals/results/thank_you_audit/`](../evals/results/thank_you_audit/);
tables 01–04 cover packets, 05–09 cover notes/status, 10 standardization, 11–13 cutoff diagnostics,
14 return timing and 15 the before-funding lower bound. `checks.json` records source integrity and
full-label agreement. [`thank_you_audit.png`](thank_you_audit.png) is regenerated by the same script.

Original September 26 validation: cross-project donor-ID gate passed on all 11,377,479 donation rows;
all 2,971,755 citizen repeat labels independently matched the raw donation stream;
single-first-month-row amount/packet/project comparisons had zero mismatches; project checksum,
unique IDs, join cardinality, permitted note encodings and record counts passed; existing suite
passed 23 tests. No independence-based p-values are reported: donors share projects/teachers and
the dataset is historical. Any future uncertainty analysis should respect those clusters.

September 29 integration validation: the full raw-data pipeline through step 18 passed, all
15 aggregate CSV tables and `checks.json` reproduced byte-for-byte, 29 tests passed, and notebook 05
executed six code cells without errors. The audit now uses the shared Projects loader. See
[`thank_you_integration_validation.txt`](../evals/results/thank_you_integration_validation.txt).

Local source definitions: `docs/codebook/37898-Documentation-dictionary.xlsx`, worksheet
`DonorsChoose ICPSR Data Diction`, rows 8, 28, 35–37; DS1 codebook pages 7–8; DS3 codebook pages
3 and 18–20; `data/raw/ICPSR_37898/37898-manifest.txt`. External sources above were checked
September 26, 2026. Costs and final methodological judgments require team ownership.
