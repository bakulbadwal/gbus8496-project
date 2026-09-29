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
| 2 | Annotated pipeline | [`notebooks/`](notebooks/) 01 labels & baseline · 02 feature join & effects · 03 model · 04 evaluation; code in [`src/`](src/) |
| 3 | Evaluation: test data, ground truth, code that reproduces the numbers | `python evals/run_all.py` rebuilds every number from the raw files; outputs in [`evals/results/`](evals/results/); label tests in [`tests/`](tests/) |
| 4 | Dataset access | [`data/README.md`](data/README.md): ICPSR study 37898 download recipe (the data itself is not redistributed) |
| 5 | One-page executive summary | [`docs/EXEC-SUMMARY.md`](docs/EXEC-SUMMARY.md) / [`.pdf`](docs/EXEC-SUMMARY.pdf) |
| 6 | AI-use note | [`AI-USE-NOTE.md`](AI-USE-NOTE.md) |

Build the zip from a clean, committed tree: `python evals/check_submission.py --zip` → `../Group_11.zip` (no data inside).

## The team

All five of us have push access to this repo. GitHub's **Contributors** sidebar only lists people
who have already pushed a commit, so it will fill in as we each start working — it is not the
membership list. This table is.

| Member | GitHub | Workstream | Status |
|---|---|---|---|
| Malorie Black | [@blackm33](https://github.com/blackm33) | Outreach economics and recommendations | plain-language talk in progress; cost number owed |
| Reid Jacobson | [@Reido938](https://github.com/Reido938) | Exploratory analysis and feature engineering | ✅ feature exploration pushed |
| Thadeus Knospe | [@thadeusk](https://github.com/thadeusk) | Evaluation and error analysis | ✅ evaluation verified; slides 7 + 9 drafted with speaker notes; review and present |
| Rodolfo Perez-Cortes Manrique | [@rodolfopiem33](https://github.com/rodolfopiem33) | Baseline and model development | ✅ model pushed Sep 17, holdout scored Sep 22 |
| Bakul Badwal | [@bakulbadwal](https://github.com/bakulbadwal) | Data and label construction | ✅ done Sep 11; integration + deck + exec summary Sep 22 |

## Status by workstream — what is done, what is pending, what is left

| Workstream | Owner | Status | What is left |
|---|---|---|---|
| **Data + label construction** | Bakul | ✅ **DONE Sep 11**, on the real file, **13 tests passing** (`tests/`) | One decision for the team to confirm (below) |
| **Exploratory analysis + features** | Reid | ✅ **JOIN + EXPLORATION PUSHED** | Validate selected interactions against the gift-size baseline on the untouched holdout |
| **Baseline + model** | Rodolfo | ✅ **Parser corrected and rerun Sep 27** (`evals/results/10_model_holdout.txt`): $119.71/contact vs $116.26, paired +$3.51 ± 0.51. See `docs/PROJECT-PARSER-FIX.md` | Present slide 6 |
| **Evaluation + error analysis** | Thadeus | ✅ **verified and corrected Sep 24**: full reproduction, calibration, dollar-ranked cohort/size analysis, regression tests, executed [notebook 04](notebooks/04_evaluation_and_error_analysis.ipynb); slides 7 + 9 and speaker notes drafted | Review the findings and speaking notes; share branch for teammate review; rehearse and present. Carry the corrected findings into Malorie’s final deck |
| **Outreach economics + recommendation** | Malorie | ✅ **decision layer run on the model Sep 22** (`evals/results/11_decision_model.txt`); slides 8 + 10 filled; building a plain-language version of the talk | **One number still owed: real cost per contact** (placeholder $25 in `src/config.py`). Post it in the chat; re-run `src/decision.py` |
| **Slides · exec summary · AI-use note · zip** | all | ✅ **Presented Tue Sep 29** | [`docs/slides/Group11_FINAL_presented.pptx`](docs/slides/Group11_FINAL_presented.pptx) is the deck as presented (20 slides + 13 hidden appendix slides). The Sep 11 template and outline are in `docs/slides/superseded/`. Zip due to the Box link on Canvas by **Fri Oct 2, midnight**: `python evals/check_submission.py --zip` |

### What Bakul's workstream delivered

- **The blocking check, passed.** `src/check_donor_id.py` on the real file: 3,466,570 donors, 25.4% give to more than one project. The ID follows the person. Bonus finding: **71.1% of donors gave exactly once, ever.**
- **The label**, `src/labels.py` → `data/processed/cohorts.parquet`: **3,277,153 donors**, one row each, with cohort month, first-gift amount and attributes (donor type, matched, teacher-referred, thank-you packet, gift card), the 12-month second-gift label, the subsequent amount, and the train/holdout split. Four judgment calls documented in notebook 01: same-month repeats excluded, twelve whole months, unclosed windows dropped, refunds excluded.
- **The baseline ladder and the scorer** for Albert's measurement 1 (`src/baselines.py`, `evals/score.py`), with a built-in consistency check that holds on real data.
- **The population finding.** Pooled, gift-size ranking "found" 80% of subsequent value — an artefact of 708 organizations holding 62.5% of the dollars. `evals/profile_cohorts.py` reproduces it in one command.
- **Notebook 01**, executed on the real data with outputs saved, 0 errors. Read it first.

### What the reference model and the decision layer found — read before you build

Both ran on the real holdout on Sep 12 (`evals/results/06_*.txt`, `07_*.txt`). Four things:

1. **There is very little signal in the donations file alone.** A logistic regression on every
   first-gift attribute gets ROC-AUC **0.578** on a 12.6% base rate. It edges gift size at capacity
   ($119 vs $116 per contact, precision 22% vs 20%), but barely. **Rodolfo:** the model that matters
   needs Reid's projects join — subject, cost, school, whether the project funded. **Reid:** that
   join is where the whole result lives now.
2. **Two attributes carry real sign.** Campaign gift-card donors are *less* likely to return
   (coefficient −0.21: someone gifted the money is not a self-motivated donor). And the repeat rate
   **falls by cohort year** (−0.21): behaviour is drifting. **Thadeus:** that drift is your error
   analysis by cohort.
3. **The policy arithmetic is illustrative.** At a $25 placeholder contact cost, historical
   giving less hypothetical contact costs is **−$3.6M** for selecting everyone and **+$7.7M**
   for the reference model’s 10% list. Neither is outreach profit: the data does not establish
   how much giving contact causes. The train returner median of $50 is also not a mean-dollar forecast.
4. **The illustrative threshold is sensitive to the cost assumption.** p* = cost / amount proxy. At $5 per
   contact you call 61% of donors; at $10, 1.5%; at $25, 0.1%. **Malorie:** your cost per contact is
   the single most consequential input in the project. The sensitivity table in
   `evals/results/07_decision_layer.txt` shows exactly what each value implies.

The reference amount proxy is the train-set cohort-year median, $50 in every year. A median is
not an expected mean; the later log-amount regressor also supplies a ranking score rather than a
calibrated forecast of dollar returns.

### 🔴 One decision the team must confirm

`src/config.py` sets `STAKEHOLDER_POPULATION = "citizen donor"`. Organizations (0.1% of donors, 62.5% of subsequent dollars, one made 66,348 donations in a year) and teachers (seeding their own classrooms, 38% repeat rate) are not who a development lead stewards. The label is built for everyone; the filter is applied at scoring, so it is one line to reverse. **If anyone disagrees, say so in the chat before building on it.**

Robustness note, already checked: 17 citizen-donor accounts made 200+ repeat gifts in their window and hold 8% of citizen subsequent value. Excluding them moves the 10%-capacity headline from 56.4% to 53.2% of value, $116 to $101 per contact. The result does not depend on them; they are left in.

### The headline so far — citizen donors, 10% capacity, holdout

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

### 🔴 THE RESULT — holdout, corrected parser rerun Sep 27 (`evals/results/10–12_*.txt`)

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

### Thank-you packet — corrected parser rerun Sep 27, the Sep 24 meeting's action item (`evals/results/14_*`, `15_*`)

Run under the team's assumption that the packet is mailed before any second gift (no mailing
dates exist; this is an assumption, not a fact).

- **It does not improve dollar ranking in this sensitivity run.** Dev-val with the packet: $119.45/contact, ROC-AUC 0.590;
  without it: $119.62, 0.586 (`src/model.py --with-packet`). No packet-augmented model was
  scored on the holdout; the main model still excludes the flag.
- **Descriptively, packet recipients return more:** citizens 20.3% vs 12.8% (+12.5 pp holding
  gift size fixed). Organizations +5 pp; teachers −2 pp.
- **But the packet is mostly a "your project got funded" signal:** 12.3% of donors to funded
  projects got one vs 0.6% for expired projects. Funding happens after the first gift, so the raw
  gap mixes "thanked" with "saw the project succeed."
- **The $50 cutoff exists but is fuzzy.** Among non-round whole amounts, packets go 5.5% → 20.8%
  across $50 while repeat goes 16.0% → 17.9%: an implied packet effect of **+12% (95% CI +1% to
  +23%)** — suggestive, small sample, and repeat rates rise with gift size anyway. Honest slide line:
  *"There's a hint the packet helps, but our data can't separate it from the project succeeding.
  That's exactly what the Darden pilot should randomize."*
- **Project-level note and impact letter** (the meeting's second thank-you type; text is masked, only
  presence is known): 99.9% of funded projects have a thank-you note, so it can't be tested; donors
  whose project sent an impact letter return 13.2% vs 10.7% without (funded projects only). Also undated.
- Side finding: donors whose first project **expired** return more (19% vs 13%), likely because
  DonorsChoose credits get redirected to other classrooms — a caveat on what counts as a "second gift."

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
   still undertrained or the learning rate is too low. Worth one more pass before the holdout run.

### Historical reference-model review — Sep 19

These dated notes retain the original review. The latest rerun is in `evals/results/09_calibration.txt`; the final boosted model is evaluated above.

`evals/calibration.py` answers Albert's "how do you know it works, and where does it not?" for
any scores file. Run on the reference logistic's holdout predictions (it will be re-run on
`model_scores.parquet` after the holdout run). Figure for slide 7: `docs/slides/assets/slide7_calibration.png`.

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

**No VM required.** All of the above ran on a laptop. The Very Large VM on JupyterHub is available
if your machine is slow or you would rather not hold 3 GB locally, but nothing here needs it.

**Rules that keep our numbers comparable.** The label window, the split boundary, the capacity and
the population all live in [`src/config.py`](src/config.py) and nowhere else — change one only after
saying so in the chat, because it invalidates every number anyone has already produced. Nobody
looks at the holdout until a result is final; Rodolfo scores it once.

## Two deadlines

| | Due | Where | Counts |
|---|---|---|---|
| **Proposal** | **Tue Sep 8, 2026 · midnight** | Canvas → *Final Project Proposal - per team* (one uploader for the team) | Not graded; **approval is mandatory** |
| **Final project** | **Fri Oct 2, 2026 · 11:59 PM** | Box link on Canvas, one file `Group_11.zip` | **40% of the course grade** |

Albert returns proposal feedback **Thu Sep 10**. Presentations are 10 minutes in Sessions 13–14, order drawn at random, all members present.

## Where we are

| Step | Status |
|---|---|
| Team formed (Canvas / Google sheet) | ✅ done |
| Team chat (Teams) | ✅ open |
| Everyone on this repo | ✅ all five invited with push access; four accepted, Malorie's invite pending (checked Sep 8 AM) |
| Direction chosen | ✅ **Predicting the Second Gift** (Malorie) — team poll Sep 7, 4 of 4. Amazon traction (Rodolfo) is the fallback. Reasoning: [docs/Project_DIRECTION-MEMO.md](docs/Project_DIRECTION-MEMO.md) |
| Proposal submitted → **APPROVED** | ✅ submitted Sep 8; **Albert approved it Sep 9** ("a well-designed proposal"). His guidance changes the build order — read [docs/ALBERT-FEEDBACK.md](docs/ALBERT-FEEDBACK.md) before doing anything |
| ✅ **Donor-ID link check** | **PASSED Sep 11** on the real file: 11,377,479 donations, 3,466,570 distinct donors, **25.4% give to more than one project**, so the ID follows the person. Also: **71.1% of all donors gave exactly once, ever** — the problem statement with a number on it |
| Data on disk + labels built | ✅ **Sep 11** — ICPSR files in `data/raw/` (gitignored), codebooks in `docs/codebook/`. `cohorts.parquet`: **3,277,153 labelled donors, 15.8% gave again within 12 months**; train 2.33M / holdout 943K; 189K unlabelable 2019 cohorts dropped; 151 refund rows excluded |
| Measurement 1 — first real number | ✅ **Sep 11, citizen donors, 10% capacity:** ranking by first-gift size identifies **56% of subsequent giving at $116 per contact** vs $21 contacting everyone. Precision 19.7%, so four in five contacts don't return. Full table: `python evals/score.py data/processed/cohorts.parquet` |
| 🔴 **Scoping decision — team must confirm** | The file holds three populations. **708 organizations (0.1% of donors) hold 62.5% of subsequent dollars**; the largest made 66,348 donations in a year. Pooled, any ranker "wins" by finding corporations. `src/config.py` defaults to **citizen donors only**; the pooled number (80% at 10%) is kept for contrast. Evidence: `python evals/profile_cohorts.py data/processed/cohorts.parquet`. **Say in the chat if you disagree** |
| Projects parser correction | ✅ Sep 27: all 3,277,153 project joins match; frozen model and dependent results rebuilt. $119.71 vs $116.26/contact. Branch pending teammate review; [audit and deliverable impact](docs/PROJECT-PARSER-FIX.md) |
| Measurements 2–3 (Albert's order) | ✅ calibration + dollar-ranked error analysis verified Sep 24 (Thadeus), notebook 04 and slides 7 + 9 ready for review; thank-you-packet flag excluded because timing is unknown |
| Slides, exec summary, AI-use note, zip | Evaluation slides 7 + 9 and exec-summary correction prepared Sep 24 in existing files. Team review, final deck integration, rehearsal/delivery and final zip remain; recorded backup needed if using a live demo |

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
├── docs/                ← spec, direction memo, Albert's original PDF; later: exec summary, slides
├── data/                ← GITIGNORED. Raw data never gets committed; data/README.md says how to fetch it
├── notebooks/           ← COMMITTED. Annotated in the style of the course starter code
├── src/                 ← shared Python (loading, chunking, models, scoring) imported by notebooks
├── evals/               ← gold set, ground-truth provenance, and the one-command scorer
└── assets/              ← images for docs and slides
```

## Working here

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
