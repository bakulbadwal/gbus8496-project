# Presentation outline — ten minutes, ten slides, five voices

**Sessions 13–14, Sep 28–29. Order drawn at random, so we are ready on the 28th.** All five present.
If the team uses a live demo, bring a recorded backup of that demo. Aim the talk at the class, not at Albert: they grade half
of it, and they are told exactly three questions to grade on. Every slide below names which of
those questions it serves. Technical detail goes in the notebook unless it explains *why* something
works or fails.

The three class-vote questions, verbatim:
1. **Problem** — *"This team convinced me their problem is real and worth solving."*
2. **Insight** — *"I took away a genuine insight about what works, what does not, or why."*
3. **Evidence** — *"The team supported its conclusions with evidence."*

Plus Albert's two required answers: **how do you know it works**, and **what would it cost at
production scale.** And his one required disclosure: the GoGood Technologies connection.

Budget: about 55 seconds a slide. If you are over, cut words, not slides.

---

| # | Slide | Owner | The one sentence it has to land | Serves |
|---|---|---|---|---|
| 1 | **Title, team, disclosure** | Malorie | "One of us founded a company that sells to exactly this customer; that is why we chose it, and you should weigh what we say accordingly." | required disclosure |
| 2 | **71% never come back** | Malorie | "Across seventeen years, 71% of DonorsChoose donors gave once and were never heard from again. A development lead with no data staff has hours for a fraction of them. Which fraction?" | Q1 problem |
| 3 | **What a "second gift" is** | Bakul | "Four decisions turn eleven million rows into one label, and each could have gone the other way. Here is why they went this way." | Q3 evidence |
| 4 | **The finding that almost fooled us** | Bakul | "Our first result found 80% of all repeat dollars with the dumbest possible rule. It was measuring corporate matching programs. Three populations, not one." | Q2 insight |
| 5 | **What predicts a return** | Reid | "Gift size finds dollars; [feature] finds people. Here is what moved and what did not." | Q2 insight |
| 6 | **The model against the honest baseline** | Rodolfo | "At her capacity, the model identifies $[X] per contact against $116 for ranking by gift size and $21 for calling everyone." | Q3 evidence · headline |
| 7 | **How we know it works, and where it does not** | Thadeus | "The modest gain reproduces, but the dollar-ranked list still concentrates on large first gifts." | Albert Q1 · Q3 evidence |
| 8 | **What she does on Monday** | Malorie | "Given [N] hours a month, work this list, expect roughly $[Y] in subsequent giving that the old list would have missed. It costs nothing to run." | Albert Q2 cost at scale · recommendation |
| 9 | **What we did not find, and what we are not claiming** | Thadeus | "We cannot say outreach causes the second gift, we dropped the thank-you-packet question because the data cannot answer it, and here is the honest case that this does not transfer." | Q2 insight · limitations |
| 10 | **The recommendation, in one line** | Malorie | The sentence a development lead repeats to her board. | Q1 · Q3 |

---

## Slide-by-slide notes

### 1 · Title, team, disclosure — Malorie, 30 seconds
Title: *Predicting the Second Gift.* Five names. Then the disclosure, spoken not buried: Malorie
founded GoGood Technologies, whose customers are the stakeholder in this talk. Albert asked for it
explicitly. Saying it first makes it a strength — we picked a problem one of us has watched people
have — instead of something the room discovers.

### 2 · 71% never come back — Malorie, 60 seconds
The chart: donations per donor, 17 years, one bar per bucket. 71.1% at "1". Then the stakeholder:
a $500K nonprofit, no data staff, a development lead who builds her follow-up list by hand from
recency and gift size. Her decision is which fraction of this month's new donors to call. Land the
number and the person, and stop. **Asset:** `docs/slides/assets/donations_per_donor.png`.

### 3 · What a "second gift" is — Bakul, 55 seconds
DonorsChoose Open Data, 11.4M donations, 3.5M donors, 2002–2019. The label: first gift in month M,
any gift in M+1..M+12. Four decisions, one line each: same-month repeats excluded (one checkout,
many classrooms); twelve whole months (no day precision exists); unclosed windows dropped, not
zeroed; refunds out. Time-based split — train through 2016, hold out 2017–18 — because her
question is about next year's donors and a random split would let the model see the future.
Result: 3.28M labelled donors, 15.8% give again. **No chart; one clean table of the four calls.**

### 4 · The finding that almost fooled us — Bakul, 60 seconds
Tell it as it happened. First run: rank by first-gift size, 10% capacity, 80% of all subsequent
dollars found. Looked like a triumph. Then the donor-type breakdown: 708 organizations, one tenth
of one percent of donors, 62% of every repeat dollar; the largest made 66,348 donations in a year.
Corporate matching programs. Any ranker wins the pooled contest by finding them, and she already
knows who they are. Teachers are a third population, seeding their own classrooms. So: citizen
donors only, 86% of donors, 23% of dollars, the people she actually calls. **Asset:**
`docs/slides/assets/donor_type_shares.png` — donor share vs dollar share, three bars each.
This is the slide the "genuine insight" vote is won on.

### 5 · What predicts a return — Reid, 55 seconds
Owner fills in. Structure to keep: one chart of feature importance or a lift table; one sentence per
feature that mattered; one sentence on what did not (text is masked by ICPSR, so no embeddings).
Tie back to slide 4: gift size finds dollars, what finds *people*?

### 6 · The model against the honest baseline — Rodolfo, 60 seconds
The capacity table from `evals/score.py`, three rows: model, gift-size rule, random. At 10%.
Headline metric is **dollars identified per contact**, not AUC — Albert said the ranking at
capacity is the decision. State the baseline is fair: RFM collapses to gift size on a first-gift
cohort, and gift size is literally what she does by hand. **The reference logistic on donation-file
attributes only reaches $119 (ROC-AUC 0.58)** — so the story of this slide is whether the projects
join moved it. If the model does not beat $116, say so and go to slide 9; Albert wrote that a
well-supported negative finding earns a high grade.

### 7 · How we know it works, and where it does not — Thadeus, 60 seconds
**Completed Sep 24:** `evals/calibration.py`, notebook `04_evaluation_and_error_analysis.ipynb`,
and slide 7 in the existing deck. Asset: `assets/slide7_calibration_model_dark.png`.
Calibration always uses return probabilities; the year and size-band analysis now uses
`expected_value`, the same ranking as the $120 headline. Probability-only results remain a
separate comparison. Small-group precision is pooled by donor count.

**Speaker notes (about 60 seconds):** “We reproduced the headline from the raw data. On the
left, the highest probability tenth says 26.6% will return, and 24.2% do. On the right, the
actual dollar-ranked list has 23.6% returning in 2017 and 20.9% in 2018, alongside a falling
base rate. Giving per selected donor falls from $140 to $103; the model still beats gift size
in both years. The limitation is coverage: under-$50 donors are 52.4% of the population, but
only 0.55% of this list. The earlier 14.4% figure belongs to probability-only ranking, which
finds more returners but fewer dollars.”

**For Q&A:** 81,509 donors selected across 24 months; exact gain $3.83/contact (3.3%). The paired
bootstrap mean is $3.80 ± $0.51 (one standard error, 30 samples, each the full test-set size
with replacement). This quantifies donor resampling uncertainty, not future drift. Excluding
the 17 accounts with 200+ repeat gifts leaves a $3.71/contact gain. Small-donor precision is
42.3% among just 449 selected donors: the issue is low coverage, not evidence they cannot be ranked.

### 8 · What she does on Monday — Malorie, 60 seconds
The decision layer (`src/decision.py`) applies the model's dollar score at monthly capacity.
The selected list contains $9.79M of historical subsequent giving; subtracting $2.04M of
hypothetical contact costs leaves $7.75M, compared with $7.44M for gift-size ranking. This is
**value identified less assumed cost, not outreach profit**. Additional giving caused by contact
is unknown. Malorie still supplies the real contact-cost figure; $25 is a placeholder.
The threshold sensitivity table is illustrative because the log-amount score is not calibrated
as mean dollars. Batch scoring needs no model API, but staff, setup and maintenance have costs.

### 9 · What we did not find, and what we are not claiming — Thadeus, 50 seconds
**Completed Sep 24:** slide 9 and its speaking notes are in the existing deck.

**Speaker notes (about 50 seconds):** “Three limits matter. First, we identify future giving,
but cannot say a call created it; donors might have given anyway. Subtracting hypothetical
contact costs does not establish profit. Second, we dropped the thank-you-packet flag because
its timing is unknown, so it could contain information from after the outcome. Third, this
is a test of 2017–18 DonorsChoose donors; performance today or at another nonprofit is untested.
Before scaling, measure actual staff costs and run a randomized outreach pilot to estimate
additional giving caused by contact.”

The dollar score also requires mean-dollar calibration before using it as a literal cost
threshold. No model refitting or tuning was done on the holdout during this evaluation review.

### 10 · The recommendation, in one line — Malorie, 20 seconds
One sentence, then stop. Something like: "Rank this month's first-time donors by [model / gift
size], call the top [N], and expect to reach [X]% of next year's repeat giving with [Y] hours."
The recommendation is a randomized pilot of the model-ranked list against gift-size ranking, with incremental donations measured before scaling.

---

## Gaps with no owner yet — someone claim these in the chat

- ~~Second-gift amount model~~ — **done as the default** (`src/decision.py`): cohort-year median
  from train, $50 every year. Upgrade to a regression on log amount if someone wants it.
- **Recorded backup if using a live demo.** Albert asks for a backup in case the demo has technical problems; he does not separately require a recording of the entire talk. The team still needs to choose a demo and owner.
- **Final deck integration.** `Group11_deck.pptx` and its existing builder contain slides 7 and 9. Malorie is also preparing a plain-language deck; carry these findings into that final version. Rehearsal, live delivery, and teammate review remain human tasks.
