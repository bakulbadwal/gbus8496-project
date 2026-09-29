<div align="center">

<img src="assets/hero.png?v=2" alt="GBUS 8496 Final Group Project — Darden, Fall 2026" width="100%">

# GBUS 8496 · Final Group Project

**Machine Learning and AI for Business · Prof. Michael Albert · UVA Darden · Q1 2026–27**

Problem → data → system → evaluation → judgment → communication.
One business problem, one artifact we built, one evaluation we can defend.

</div>

---

## Submission — `Group_11.zip` (Albert's six deliverables)

| # | Deliverable | Where it is in this repo |
|---|---|---|
| 1 | Slides used in the presentation | [`docs/slides/Group11_FINAL_presented.pptx`](docs/slides/Group11_FINAL_presented.pptx) (presented Tue Sep 29; hidden slides are the appendix) |
| 2 | Annotated pipeline | [`notebooks/`](notebooks/) 01 labels & baseline · 02 feature join & effects · 03 model · 04 evaluation · 05 thank-you research; code in [`src/`](src/) |
| 3 | Evaluation: test data, ground truth, code that reproduces the numbers | `python evals/run_all.py` rebuilds every number from the raw files; outputs in [`evals/results/`](evals/results/); label tests in [`tests/`](tests/) |
| 4 | Dataset access | [`data/README.md`](data/README.md): ICPSR study 37898 download recipe (the data itself is not redistributed) |
| 5 | One-page executive summary | [`docs/EXEC-SUMMARY.md`](docs/EXEC-SUMMARY.md) / [`.pdf`](docs/EXEC-SUMMARY.pdf) |
| 6 | AI-use note | [`AI-USE-NOTE.md`](AI-USE-NOTE.md) |

Build the zip from a clean, committed tree: `python evals/check_submission.py --zip` → `../Group_11.zip` (no data inside).

## The team — Group 11

| Member | GitHub | Workstream | What they delivered |
|---|---|---|---|
| Malorie Black | [@blackm33](https://github.com/blackm33) | Problem framing, stakeholder, recommendation | Proposed the topic; stakeholder and GoGood/Darden framing; decision-layer framing; built and led the final presentation deck |
| Reid Jacobson | [@Reido938](https://github.com/Reido938) | Exploratory analysis and features | Projects join and feature exploration ([notebook 02](notebooks/02_feature_joining_and_effects.ipynb), [write-up](docs/REID-FEATURE-EXPLORATION.md)) |
| Thadeus Knospe | [@thadeusk](https://github.com/thadeusk) | Evaluation and error analysis | Calibration and dollar-ranked error analysis ([notebook 04](notebooks/04_evaluation_and_error_analysis.ipynb)), regression tests, the Projects parser fix ([audit](docs/PROJECT-PARSER-FIX.md)), and thank-you timing/cutoff research ([notebook 05](notebooks/05_thank_you_research.ipynb)) |
| Rodolfo Perez-Cortes Manrique | [@rodolfopiem33](https://github.com/rodolfopiem33) | Model development | Gradient-boosted return and amount models ([`src/model.py`](src/model.py), [notebook 03](notebooks/03_model_development.ipynb)), team model explainer |
| Bakul Badwal | [@bakulbadwal](https://github.com/bakulbadwal) | Data, labels, integration | Donor-ID check, label construction and tests ([notebook 01](notebooks/01_labels_and_baseline.ipynb)), baseline ladder and scorer, decision layer, one-command reproduction, holdout scoring, exec summary, submission packaging |

**Result in one line:** on 2017–18 donors the model never saw, ranking the top 10% of each month's new
individual donors by expected value identifies **about $120 of next-year giving per contact vs $116**
for the "biggest gift first" rule (paired edge about $3.50, roughly 7 standard errors). It predicts
who gives, not who a contact would persuade.

### What Bakul's workstream delivered

- **The blocking check, passed.** `src/check_donor_id.py` on the real file: 3,466,570 donors, 25.4% give to more than one project. The ID follows the person. Bonus finding: **71.1% of donors gave exactly once, ever.**
- **The label**, `src/labels.py` → `data/processed/cohorts.parquet`: **3,277,153 donors**, one row each, with cohort month, first-gift amount and attributes (donor type, matched, teacher-referred, thank-you packet, gift card), the 12-month second-gift label, the subsequent amount, and the train/holdout split. Four judgment calls documented in notebook 01: same-month repeats excluded, twelve whole months, unclosed windows dropped, refunds excluded.
- **The baseline ladder and the scorer** for Albert's measurement 1 (`src/baselines.py`, `evals/score.py`), with a built-in consistency check that holds on real data.
- **The population finding.** Pooled, gift-size ranking "found" 80% of subsequent value — an artefact of 708 organizations holding 62.5% of the dollars. `evals/profile_cohorts.py` reproduces it in one command.
- **Notebook 01**, executed on the real data with outputs saved, 0 errors. Read it first.

### What the reference model and the decision layer found (Sep 12)

Both ran on the real holdout on Sep 12 (`evals/results/06_*.txt`, `07_*.txt`). Four things:

1. **There is very little signal in the donations file alone.** A logistic regression on every
   first-gift attribute gets ROC-AUC **0.578** on a 12.6% base rate. It edges gift size at capacity
   ($119 vs $116 per contact, precision 22% vs 20%), but barely. That pointed the final model at the
   projects join (subject, cost, school) for extra signal.
2. **Two attributes carry real sign.** Campaign gift-card donors are *less* likely to return
   (coefficient −0.21: someone gifted the money is not a self-motivated donor). And the repeat rate
   **falls by cohort year** (−0.21): behaviour is drifting, which is why the evaluation checks each
   cohort year separately.
3. **The policy arithmetic is illustrative.** At a $25 placeholder contact cost, historical
   giving less hypothetical contact costs is **−$3.6M** for selecting everyone and **+$7.7M**
   for the reference model’s 10% list. Neither is outreach profit: the data does not establish
   how much giving contact causes. The train returner median of $50 is also not a mean-dollar forecast.
4. **The illustrative threshold is sensitive to the cost assumption.** p* = cost / amount proxy. At $5 per
   contact you call 61% of donors; at $10, 1.5%; at $25, 0.1%. The cost per contact is the single
   most consequential input, and $25 remains a placeholder. The sensitivity table in
   `evals/results/07_decision_layer.txt` shows what each value implies.

The reference amount proxy is the train-set cohort-year median, $50 in every year. A median is
not an expected mean; the later log-amount regressor also supplies a ranking score rather than a
calibrated forecast of dollar returns.

### Scoping decision: individual donors only

`src/config.py` sets `STAKEHOLDER_POPULATION = "citizen donor"`. Organizations (0.1% of donors, 62.5% of subsequent dollars, one made 66,348 donations in a year) and teachers (seeding their own classrooms, 38% repeat rate) are not who a development lead stewards. The label is built for everyone and the filter is applied at scoring, so it is one line to reverse. The team adopted it; the pooled number is kept for contrast.

Robustness note, already checked: 17 citizen-donor accounts made 200+ repeat gifts in their window and hold 8% of citizen subsequent value. Excluding them moves the 10%-capacity headline from 56.4% to 53.2% of value, $116 to $101 per contact. The result does not depend on them; they are left in.

### The baseline ladder — individual donors, 10% capacity, holdout

| Ranking | Precision | Recall | Value identified | $ per contact |
|---|---|---|---|---|
| **First gift size** (the honest baseline) | 19.7% | 15.7% | **56.4%** | **$116** |
| First-month gift count | 20.4% | 16.2% | 41.4% | $85 |
| Random | 12.7% | 10.1% | 9.1% | $19 |
| Contact everyone | 12.6% | 100% | 100% | $21 |

That is the bar. Gift size finds dollars but not people: four in five contacts on its list do not return. A model earns its place by beating **$116 per contact** at 10% capacity, or by finding people the size rule misses.

### What Reid's exploratory workstream delivered

The reproducible notebook is [`notebooks/02_feature_joining_and_effects.ipynb`](notebooks/02_feature_joining_and_effects.ipynb). The detailed narrative is [`docs/REID-FEATURE-EXPLORATION.md`](docs/REID-FEATURE-EXPLORATION.md).

- **Projects join:** `first_project_id` now matches all 3,277,153 cohort rows (100%). The old CSV quote handling swallowed Projects records; this was a parsing bug, not a public-use coverage gap. `project_record_missing` is retained as a safeguard for future unmatched inputs. [Audit and impact](docs/PROJECT-PARSER-FIX.md).
- **Features constructed:** grade, subject, optional subject, project category, state, resource and charge fields, school free/reduced-price lunch percentage, students reached, posted month, and missing-project status. Post-outcome fields and raw teacher IDs are excluded to avoid leakage or memorization.
- **Two outcomes separated:** repeat likelihood, `P(gave_again)`, and conditional future size, `E(second_gift_amount | gave_again)`. First-gift size is weak-to-moderate for return likelihood but substantially stronger for the amount a returning donor gives.
- **Interaction exploration:** project-only candidates include state × category, subject × category, and subject × grade. Gift-size interactions show that category, subject, grade, and state modify the relationship between first-gift size and repeat behavior.
- **Expected value:** the full citizen-training analysis covers 2,156,784 donors. The strongest families are state × gift decile, subject × gift decile, category × gift decile, and grade × gift decile. These are training associations, not causal effects or proof of holdout improvement.
- **Significance and value tables:** full outputs are in [`docs/term_effects_table_full.csv`](docs/term_effects_table_full.csv), [`docs/term_value_effects_full.csv`](docs/term_value_effects_full.csv), and the de-duplicated family summary [`docs/term_value_effects_unique_families.csv`](docs/term_value_effects_unique_families.csv).

**Key takeaway:** project context appears more useful for explaining who returns and for modifying expected value than for replacing first-gift size as the strongest predictor of conditional donation amount. The next test is a regularized model evaluated at 10% capacity on the untouched holdout; exploratory percentage-point differences do not, by themselves, beat the `$116/contact` baseline.

#### Reid's analysis callouts

**Expected future value:** expected value is the average subsequent 12-month donation across all donors, so it combines repeat probability and the amount given after returning.

| Term | Repeat rate | Expected-value difference |
|---|---:|---:|
| Mississippi × gift decile 8 | 30.2% vs 14.0% | **+$199/donor** |
| Music × gift decile 8 | 26.9% vs 13.9% | **+$187/donor** |
| Books × gift decile 8 | 28.5% vs 13.8% | **+$158/donor** |
| Grades 6–8 × gift decile 8 | 25.6% vs 13.8% | **+$144/donor** |
| Top first-gift-size decile | 25.9% vs 13.0% | **+$142/donor** |

Contrasting cells for the five highlighted effects were:

| Term family | Repeat rate | Expected value: term | Expected value: comparison | Differential |
|---|---:|---:|---:|---:|
| Mississippi × gift decile 1 | 9.0% vs 14.0% | $4.37 | $20.27 | **−$15.90/donor** |
| Music × gift decile 1 | 6.5% vs 14.0% | $2.58 | $20.32 | **−$17.74/donor** |
| Technology × gift decile 8 | 23.3% vs 13.7% | $129.25 | $17.51 | **+$111.73/donor** |
| Grades 9–12 × gift decile 8 | 24.5% vs 13.8% | $152.41 | $18.79 | **+$133.62/donor** |
| Gift decile 1 | 5.5% vs 14.8% | $2.53 | $22.03 | **−$19.50/donor** |

These contrast cells are descriptive comparisons, not causal effects. They show how the same broad gift-size pattern can look different across project context, state, subject, or grade.

**Interaction exploration:** project-only combinations showed meaningful spread before gift size was added. The largest observed project-only contrast was `Other subject × Trips` at **29.2%** repeat versus a **14.0%** comparison rate (**+15.2 percentage points**). State × category also varied from `Connecticut × Trips` at **7.9%** to `Indiana × Trips` at **20.6%**. When gift size was added, `Books × gift decile 8` reached **28.5%** repeat versus **13.8%** outside the cell, with approximately **+$158 per donor** in expected value.

These are full citizen-training associations with a minimum cell size of 500 donors. They identify candidate terms for the model; they are not causal effects and have not replaced the untouched holdout evaluation.

### The result — holdout, corrected parser rerun Sep 27 (`evals/results/10–12_*.txt`)

Model frozen on dev-val first (iteration cap raised 1,200 → 3,000 with learning rate 0.06 → 0.10 so
early stopping actually fires; dev-val moved $119.82 → $119.51, i.e. the cap was not binding), then
the 2017–18 holdout was first scored. The Sep 27 rerun corrects the input parser; features, hyperparameters, splits and seeds are unchanged. See [the parser-fix audit](docs/PROJECT-PARSER-FIX.md).

| Citizen donors, holdout, 10% capacity | Precision | Recall | Value identified | $ per contact |
|---|---|---|---|---|
| **Model, probability × amount score** | **22.3%** | 17.7% | **58.1%** | **$120** |
| First gift size (her rule) | 19.7% | 15.7% | 56.4% | $116 |
| Model, P(return) only | 24.3% | 19.2% | 52.3% | $108 |
| Random | 12.7% | 10.1% | 9.1% | $19 |

- **Reproducibility across machines (checked Sep 27):** re-running the identical code and data on a
  second machine (Python 3.14 / scikit-learn 1.9.1 vs 3.11 / 1.8.0) gives $120.14 and **+$3.89 ± 0.53**;
  before the parser fix the two machines gave +$3.80 and +$3.62. The edge is **+$3.5 to +$3.9 per contact,
  ~7 SE, in every run** — robust in direction and size, not identical to the cent
  (`evals/results/parser_fix_independent_check.txt`).
- **Paired bootstrap: +$3.51 ± 0.51 per contact** (~7 SE) — stronger than on dev-val (+$1.90 ± 0.78). ROC-AUC 0.604.
- **Decision layer** (`src/decision.py`, now using the model's own per-donor E[amount]): capacity-10%
  by the model identifies **$9.76M**; subtracting hypothetical $25/contact costs leaves **$7.72M**
  vs **$7.44M** for her rule (+$282K). These balances are not outreach profit estimates. Threshold "EV > cost": 53.7% of donors at $5, 23.4% at $10, 6.7% at $25.
- **Calibration and error analysis, rerun Sep 27** (`evals/results/12_calibration_model.txt`):
  ECE 0.0080; Brier skill 2.3%. The highest probability tenth predicts 27.2% returning and observes
  24.5%. Calibration uses probabilities; the contact-list analysis uses the headline dollar score.
  On that list, precision is **23.7% in 2017 → 21.1% in 2018**, and value/contact is **$139 → $103**;
  gift-size ranking is lower in both years ($137 → $99).
- **Correction to the small-donor claim:** under-$50 first-month donors are 52.4% of the holdout
  but only **0.51% of the dollar-ranked list** (416 of 81,509 selected). For comparison, **14.1%**
  belongs to the **probability-only list**, which identifies $108/contact. The dollar policy
  still concentrates on large gifts; the small donors it does select have 42.8% repeat precision.
- **Robustness:** excluding 17 accounts with 200+ subsequent gifts leaves **$104.11 vs $100.81**
  per selected donor, a $3.30 advantage. The main full-sample gain is $3.45 (3.0%); the bootstrap
  mean is $3.51 ± $0.51, with ± denoting one standard error from 30 paired donor resamples.
- **Economic limits:** the mean dollar score is $11.17 against $20.61 observed per donor. The
  log-amount prediction is a ranking score, not a calibrated mean-dollar forecast. Cost thresholds
  remain illustrative, and historical future giving does not identify the extra giving caused by a call.

- **Who the model adds** (`evals/results/13_qa_analyses.txt`, B): versus the gift-size list it drops
  20,606 donors who are 81% teacher-referred and return 13% of the time, and adds 20,606 who are 32%
  multi-classroom first-month givers and return 23%. **Thadeus** owns slide 7; figure
  `docs/slides/assets/slide7_calibration_model_dark.png`.

**Reproduce this review:** `python evals/run_all.py` rebuilds the model and all reported evaluations.
Then open [notebook 04](notebooks/04_evaluation_and_error_analysis.ipynb) for the annotated evaluation;
it reads frozen scores without refitting. For measurement 2 alone:

```bash
python evals/calibration.py data/processed/cohorts.parquet data/processed/model_scores.parquet --ranking expected_value --out docs/slides/assets/slide7_calibration_model
python -m pytest tests/ -q
```

### Thank-you research — descriptive evidence and identification limits

The [research memo](docs/THANK-YOU-RESEARCH.md), [notebook 05](notebooks/05_thank_you_research.ipynb),
and `python evals/thank_you_audit.py` extend the packet exploration to digital notes,
single-donation cutoff checks and conservative timing bounds. All comparisons are descriptive.
The audit runs as step 18 of the full evaluation, after the existing parser and feature-table checks.

- **It does not improve dollar ranking in this sensitivity run.** Dev-val with the packet: $119.45/contact, ROC-AUC 0.590;
  without it: $119.62, 0.586 (`src/model.py --with-packet`). No packet-augmented model was
  scored on the holdout; the main model still excludes the flag.
- **Packets are positively associated with return:** citizens 20.3% vs 12.8%. Within single-row,
  funded, $50+ first-gift donors, standardization by year, gift band, referral, matching and gift
  card gives 17.52% vs 13.86% (+3.65 pp), covering 98.0% of that narrower population. Selection
  and timing remain unresolved. The earlier +12.5-point reweighted estimate has weak overlap
  among very small gifts; it is not an intervention effect.
- **Digital-note presence is nearly universal after funding:** 99.90% of single-first-month-row
  citizen donors to funded projects have a note recorded. There is little comparable no-note
  data; content is masked and send/receipt dates are unavailable.
- **The cutoff result is unstable.** With a single first-month donation, the observed repeat-rate
  difference above versus below $50 is −2.45 pp including exactly $50, −0.91 pp excluding it, and
  +1.97 pp selecting non-round whole-dollar amounts. The earlier +12% ratio is **not an identified
  causal effect**; its bootstrap interval cannot repair sample selection or missing timing.
- **Timing ambiguity is demonstrated:** 653 packet-recorded repeaters definitely gave again
  before their associated project was funded. This is a conservative lower bound, not the total
  share returning before receipt. Keep snapshot flags out of the baseline prediction model.
- **Projects parsing is fixed:** PR #2 corrected the shared loader and rebuilt the frozen
  evaluation on Sep 27. This audit uses that same loader. See [the parser-fix audit](docs/PROJECT-PARSER-FIX.md).

### Q&A analyses — rerun Sep 27, from Malorie's list (`evals/qa_analyses.py` → `evals/results/13_qa_analyses.txt`)

- **Same classroom?** Of citizen donors who gave again, **61% gave only to different teachers**;
  32% gave only to the same teacher; 24% of repeat dollars went back to the first classroom. Most
  "loyalty" here is to the platform, not the classroom — the honest answer to "DonorsChoose ≠ a small
  nonprofit." (No school id exists in the Projects file, so "same school" cannot be tested.)
- **Who the model adds** (holdout, 10%): swaps 20,606 gift-size picks (81% teacher-referred, return
  13%, $25 next-year giving) for 20,606 donors who are 32% multi-classroom first-month givers, 21%
  teacher-referred, higher-poverty schools (72% free lunch), return 23%, $39 next-year giving.
- **Capacity 5%–30%:** the model beats gift size at every capacity — biggest at 5% (+$7/contact,
  $200 vs $193), shrinking to about +$1 at 20–30%. Precision edge 1.4–3.7 points throughout.
- **Second → third gift:** 13.6% of first-time citizen donors give again within a year; **36% of
  second-time donors give a third time** — 2.7× — our own data's version of the FEP 19%-vs-59% slide.
- Not run, with the one-line answer: *thank-you packet* — no mailing dates exist, Albert pre-approved
  dropping it; *more model types* — two model classes against four baselines already, and gift size
  carries most of the signal.

### Historical development notes — first real-data run, Sep 17

These dated notes describe the earlier model. Current corrected results are in `evals/results/08_model_dev.txt` and the headline section above.

`src/model.py`: a gradient-boosted classifier for P(return) and a gradient-boosted regressor for
log(second-gift amount) on returners, ranked by P × E[amount]. Features are the reference model's
plus Reid's projects join. Developed entirely inside the train split (fit ≤2015, evaluate on 2016
cohorts); **the holdout has not been touched.** The join is reproduced by `src/features.py`.

| Ranking, 2016 dev-val, 10% capacity | Precision | Value identified | $ per contact |
|---|---|---|---|
| **Model, expected value** | 22.4% | 56.6% | **$120** |
| First gift size | 20.6% | 55.3% | $117 |
| Model, P(return) only | 23.3% | 47.7% | $101 |
| Random | 12.9% | 10.9% | $23 |

Paired bootstrap: the model beats gift size by **$2.05 ± 0.67 per contact** — real (3× its standard
error) and small (under 2%). ROC-AUC 0.590 against the reference logistic's 0.578. Three readings:

1. **The projects join adds a little, not a lot.** Reid's interactions are real, but gift size
   already carries most of what predicts *dollars*. That is a finding, not a failure — Albert wrote
   that a well-supported negative result earns a high grade.
2. **Probability and dollars pull apart.** Ranking by P(return) alone finds the most *people*
   (precision 23.3%) and the fewest *dollars* ($101). Which list she works depends on whether her
   goal is retained donors or retained revenue. That is a slide.
3. **The classifier used 1,196 of 1,200 boosting iterations without early stopping firing** — it is
   still undertrained or the learning rate is too low. Resolved Sep 22: the cap was raised, early stopping now fires, and the dev-val result was unchanged.

### Historical reference-model review — Sep 19

These dated notes retain the original review. The latest rerun is in `evals/results/09_calibration.txt`; the final boosted model is evaluated above.

`evals/calibration.py` answers Albert's "how do you know it works, and where does it not?" for
any scores file. Run on the reference logistic's holdout predictions; the final model's version is
`evals/results/12_calibration_model.txt`. Figure for slide 7: `docs/slides/assets/slide7_calibration.png`.

1. **It under-promises.** Every decile returns *more* than predicted: the top decile says 18%
   and gets 22%; bottom says 6.5%, gets 8.2%. Expected calibration error 0.016, Brier 0.109 vs
   0.110 for predicting the base rate (1.2% skill — the ranking works, the probabilities barely
   beat a constant). The direction matters for `src/decision.py`: a threshold rule built on these
   probabilities calls *too few* people. The likely cause is the cohort-year drift term
   extrapolating 2017–18 lower than they turned out. This explanation was not tested; the final boosted model is evaluated separately in notebook 04.
2. **It holds up across years, but the dollars don't.** Precision 23.6% in 2017 → 21.3% in 2018,
   almost exactly tracking the base rate (14.0% → 11.5%), so lift over base is stable at ~1.8×.
   Value per contact falls $139 → $102: the 2018 list finds returners as well, but they give less.
3. **The list is the big-gift list.** Donors giving under $50 are 52% of the holdout and **1.9%
   of the 10% list**; $100+ donors are 15% of the holdout and 82% of the list. Precision on the few
   small donors it does pick is high (38%), which says the model can find small returners — it just
   almost never has room for them at capacity. That is the honest sentence for slide 7: *this
   ranks the donors she already knew about; it does not yet find the small donors she needs help
   with.* Reid's features and Rodolfo's model are where that would change.

## Setup — takes about five minutes, most of it the download

```bash
git clone https://github.com/bakulbadwal/gbus8496-project.git && cd gbus8496-project
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

**Data.** Download `ICPSR_37898-V1.zip` (Delimited) from icpsr.umich.edu/web/ICPSR/studies/37898 —
free account, no institutional login needed — and unzip it into `data/raw/`. It is 1.2 GB and
never goes into git. Then, in order:

```bash
python src/check_donor_id.py  data/raw/ICPSR_37898/DS0001/37898-0001-Data.tsv     # ~35 s, prints PASS
python src/labels.py          data/raw/ICPSR_37898/DS0001/37898-0001-Data.tsv data/processed/cohorts.parquet   # ~30 s
python evals/profile_cohorts.py data/processed/cohorts.parquet                    # who is in it
python evals/score.py         data/processed/cohorts.parquet holdout              # measurement 1
```

**No VM required.** Everything, including `python evals/run_all.py`, ran on a laptop.

**Rules that keep our numbers comparable.** The label window, the split boundary, the capacity and
the population all live in [`src/config.py`](src/config.py) and nowhere else; changing one
invalidates every reported number. The holdout was scored once, after the model was frozen on 2016.

## Timeline

| Step | Date |
|---|---|
| Direction chosen by team poll (Second Gift, 4 of 4) | Sep 7 |
| Proposal submitted / approved by Albert | Sep 8 / Sep 9 |
| Real data landed; donor-ID check passed; labels built | Sep 11 |
| Reference model and decision layer | Sep 12 |
| Projects join and feature exploration | Sep 15 |
| Model built; first real-data run | Sep 17 |
| Holdout scored once; calibration on the final model | Sep 22 |
| Evaluation review merged; thank-you-packet analysis | Sep 26 |
| Projects parser fix (PR #2) merged and verified independently | Sep 27 |
| Presented (Session 14) | Tue Sep 29 |
| `Group_11.zip` to the Box link on Canvas | due Fri Oct 2, 11:59 PM |

## Read these first

1. [docs/Final_Project_SPEC.md](docs/Final_Project_SPEC.md) — Albert's assignment decoded: the five proposal elements, the two hard requirements, the grading formula, the six deliverables, the nine worked examples, a week-by-week timeline, and a five-person workstream split.
2. [docs/Project_DIRECTION-MEMO.md](docs/Project_DIRECTION-MEMO.md) — every candidate direction scored against the rubric, newest first. Top section = current recommendation.
3. [docs/proposal/](docs/proposal/) — **`Proposal_v4_FINAL.docx` is the submitted version** (Second Gift, Group 11). `Proposal_v4_house-style.pdf` is the same content in the house look for sharing. Earlier drafts and the two fallback proposals (Amazon traction, DonorsChoose screening) are in `docs/proposal/superseded/`. `Proposal_v2` (Amazon) and `Proposal_v1` (DonorsChoose screening) are the fallbacks, kept for the record. [data/README.md](data/README.md) has the ICPSR fetch recipe and the label/leakage notes.
4. [docs/albert/Final_Group_Project_Albert.pdf](docs/albert/Final_Group_Project_Albert.pdf) — the original assignment, verbatim. When in doubt, this wins.

His nine examples are *suggestions*. Any business problem qualifies as long as there is a named user, a real dataset, an artifact we built, and an evaluation against ground truth.

## What the grade rewards

```
Project        = 0.5 × Instructor + 0.5 × Class
Instructor     = Technical 30 · Evaluation 25 · Communication 20 · Business framing 15 · Ambition 10
Class          = every other student rates us 1–5 on: problem is real · I took away an insight ·
                 conclusions were supported by evidence   (z-scored per rater)
Individual     = 0.5 × Project + 0.5 × (n−1) × (your rated effort share) × Project
```

Two questions every presentation must answer: **how do you know it works**, and **what would it cost at production scale**. A well-evidenced negative result is explicitly rewarded.

## Repo layout

```
gbus8496-project/
├── README.md            ← you are here
├── AGENTS.md            ← the contract every coding agent reads (Codex, OpenCode, Cursor, …)
├── CLAUDE.md            ← Claude Code reads this; it points at AGENTS.md
├── AI-USE-NOTE.md       ← deliverable #6, kept as we go, not written at the end
├── requirements.txt
├── docs/                ← exec summary, final slides, spec, proposal, codebooks, Albert's original PDF
├── data/                ← GITIGNORED. Raw data never gets committed; data/README.md says how to fetch it
├── notebooks/           ← COMMITTED. Annotated in the style of the course starter code
├── src/                 ← shared Python: labels, projects join, baselines, model, decision layer
├── tests/               ← label-rule, calibration and parser tests (pytest)
├── evals/               ← scorer, run_all.py (one-command reproduction), analyses, results/
└── assets/              ← images for docs and slides
```

## Working on this repo

**Setup**

```bash
git clone https://github.com/bakulbadwal/gbus8496-project.git
cd gbus8496-project
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

**Coding agents.** Use whatever you like — Claude Code, Codex, OpenCode on JupyterHub, Cursor. Albert's project policy is explicit: *any AI tool is allowed*, the requirement is reproducible, documented code plus an AI-use note. Every agent here reads `AGENTS.md` (and Claude Code also reads `CLAUDE.md`) at the repo root, so start your agent inside this folder and it picks the project up cold. Log what you used and how you checked it in `AI-USE-NOTE.md` as you go.

**GitHub from an agent.** Have `gh` authenticated on your machine (`gh auth login`) so your agent can commit, push, and open PRs under *your* name — commit history is part of how we document "how we built it".

**Rules that protect the grade** (full list in `AGENTS.md`):

- Build the evaluation harness and gold set **before** the system. Never tune on the test set.
- Every reported number is produced by code in this repo that anyone can re-run in one command.
- Raw data and API keys never get committed. `data/README.md` says how to fetch data; keys live in `.env` (ignored).
- Notebooks are read aloud in class: annotate every decision, no unexplained cells.
- A discrepancy between our number and someone else's is a finding, not a bug to hide.

---

<sub>UVA Darden School of Business, GBUS 8496 A, 2027 MBA Q1.</sub>
