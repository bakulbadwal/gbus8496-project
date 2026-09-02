# GBUS 8496 Final Group Project — the assignment, decoded (v2)

**Team-shareable.** Source of truth: Albert's *Final Group Project* page (7pp, Canvas → PDF) plus
his Canvas announcement of **Tue Sep 1, 3:19 PM**. v2 corrects v1's count of worked examples (nine,
not seven — the intent-routing one was missing), adds the announcement facts, adds a build timeline
and a workstream split for a five-person team, and turns the five proposal elements into a
fill-in template. Direction options are in a separate memo, `Project_DIRECTION-MEMO.md`.

---

## 1. Two deadlines

| | Due | Where | Graded? |
|---|---|---|---|
| **Proposal** | **Tue Sep 8, midnight** | Canvas → *Final Project Proposal - per team* | No — but approval is mandatory before you may present |
| **Final project** | **Fri Oct 2, 11:59 PM** | Box link on the Canvas assignment, one file `Group_#.zip` | **Yes — 40% of the course grade** |

From the Sep 1 announcement:
- Teams already exist on Canvas, so the proposal is **team-scoped**: **one person uploads, it counts for everyone.**
- Final teams are on the **read-only Google sheet** linked in the announcement. One student was moved by
  random draw from the two six-person groups; the draw is documented at the bottom of the sheet.
- No way to reach teammates → email Albert, he will facilitate an email chain.
- *"This is a hard deadline so that I can return timely feedback to all groups."* Feedback comes back
  **Thursday Sep 10.**
- Want a read before the deadline? Office hours or email (albertm@darden.virginia.edu, FOB 269).

---

## 2. The proposal: one page, five elements

Verbatim: *"one page, submitted on Canvas. It should contain: the problem and the business
application; the dataset and its source; what you will build or analyze; what your evaluation will
be — what you will measure, and against what ground truth; and anything you need from me."*

Fill-in template — each element is one short paragraph:

| # | Element | What a strong answer contains |
|---|---|---|
| 1 | **Problem + business application** | A **named user** (a role at a real or realistic company), the **decision** they make today, why the output would **change what they do** |
| 2 | **Dataset + source** | Named, linked, size stated, licence checked, **actually downloadable today** |
| 3 | **What we will build or analyze** | The artifact: model / RAG system / agent / fine-tune / evaluation study. One sentence on the honest baseline it is compared against |
| 4 | **Evaluation** | **What we measure, against what ground truth.** Where the ground truth comes from, what the baselines are, and what a *negative* result would look like. This is the element most teams under-specify, and it is 25% of the instructor score |
| 5 | **What we need from Albert** | Compute, API credits, data access, a ruling on scope, a read on a risk |

---

## 3. The two hard requirements

**1. A technical contribution.** *"You must build, train, or analyze something, and you must
evaluate it."* Every project needs an answer to *"how well does this work?"* — a held-out test set,
a hand-labeled sample, a set of verified test questions, a comparison against human performance,
or a backtest. Explicitly **not** enough: a presentation about what AI could do for a company with
no working artifact; a demo that is just prompting Claude or ChatGPT with no data, no system, no
evaluation.

**2. A concrete, business-relevant problem.** Who is the user of the output, and why would they
derive value from it. *"It is not enough to have a theoretically interesting problem."*

And the line to take literally: *"A rigorous project that concludes an approach does not work, and
shows why, can earn a high grade. I am grading the quality of the investigation and the strength
of the evidence, not whether the results came out positive."*

---

## 4. Grading — where the points are

```
Project Score      = 0.5 × Instructor Score + 0.5 × Class Score
Instructor         = Technical contribution 30 · Evaluation 25 · Communication 20
                     · Business framing 15 · Ambition & novelty 10
Class (per group)  = every non-presenting student rates 1–5 on three questions;
                     each rater's scores are z-scored (own mean/sd) before averaging
Final Individual   = 0.5 × Project + 0.5 × (n − 1) × (your average rated effort share) × Project
```

**What each instructor line actually asks for** (paraphrasing his rubric):
- *Technical 30* — something real, sound methods, sensible choices, **honest treatment of limitations**. Expectations scale with difficulty attempted.
- *Evaluation 25* — suitable ground truth, **honest baselines**, correct interpretation. **An error analysis (where it fails and why) is expected in strong projects.**
- *Communication 20* — clear talk; notebook annotated so he can follow **every decision without asking**. *"Err on the side of more explanation."*
- *Business framing 15* — named stakeholder, real decision, actionable recommendation, sound economics, **no hidden assumptions that would block real use**.
- *Ambition 10* — goes somewhere the starter code does not: unusual problem, creative evaluation, or a well-defended negative finding.

**Half the grade is the room.** The class is told exactly three things, published so we build the talk around them:
1. *"This team convinced me their problem is real and worth solving."*
2. *"I took away a genuine insight about what works, what does not, or why."*
3. *"The team supported its conclusions with evidence."*

Nothing about model sophistication. His own words: *"neither I nor your class really care what the
exact tuning parameters were for your CatBoost model, for example, but I do care if you found text
embeddings to be an important component of your data pipeline."*

**Effort shares are real.** Each member privately allocates 100% across teammates excluding
themselves. Everyone floors at half the project score; an equal share (1/(n−1)) puts you at par.

---

## 5. Deliverables — one `Group_#.zip` to Box by Oct 2

1. **Slides** used in the presentation.
2. **Annotated notebook or small repo** — *"in the style of the course starter code"*: what you tried, what you kept, why. If not a notebook, a detailed `README.md`. *"If you think something is clear, someone else reading your code will still find it confusing."*
3. **The evaluation** — test data or task set, the ground truth and where it came from, and **the code that produces the reported numbers.** *"I should be able to re-run your evaluation."*
4. **The dataset**, or clear access instructions.
5. **One-page executive summary** — problem, approach, findings, recommendation — for an executive who missed the talk.
6. **A short AI-use note** in the notebook: which tools, for what, how the output was verified.

Re-uploads: mark the newer file clearly and email him which one counts.

**Presentation:** 10 minutes, Sessions 13–14, order drawn at random after proposals are in, brief
Q&A. **All members participate.** Live demo welcome — **bring a recorded backup.** Aim the ten
minutes at the class, not at him; technical detail goes in the notebook unless it explains *why*
something works or fails. He also requires every project to answer two questions: **how do you know
your system works**, and **what would it cost at production scale**.

---

## 6. AI policy for the project — the opposite of the Kaggle rule

*"You may use the course provided tools (JupyterHub and OpenCode), but you are not restricted to
those tools. You can use any AI tool for assisting in your project, but you have to document how you
built it in such a way that others could reproduce your work. It is not enough that 'Claude told me
the answer was x'. You need to have clear code that can be run on anyone's computer that shows every
step of the process. The judgment must be your own."*

So: any tool, any model, any machine — **the requirement is reproducible, documented code** plus the
AI-use note. The graded judgment calls are the choice of problem, the design of the evaluation, the
interpretation, and the recommendations, and we answer questions live.

---

## 7. The nine worked examples (calibration for scope)

Each names a real dataset and the evaluation he would expect. We may take one as-is; he *"strongly
encourages"* exploring others.

| # | Direction | Dataset | Evaluation he describes |
|---|---|---|---|
| 1 | Cancellation model → overbooking policy | Hotel Booking Demand (Kaggle) — 119,390 bookings, 32 features | Held-out performance **+ policy backtest**: revenue vs "never overbook" and "always overbook x%", with explicit walked-guest vs empty-room costs |
| 2 | Demand forecasting, asymmetric costs | M5 (Kaggle) — 30,490 item-stores, 10 Walmart stores | Rolling-origin backtest vs naive and seasonal baselines, **in dollars**; which items are unforecastable |
| 3 | Credit decisioning, relational data | Home Credit Default Risk (Kaggle) — 307,511 apps + 6 linked tables | Held-out discrimination **+ profit curve + threshold recommendation**; which features survive regulatory scrutiny |
| 4 | Pricing from tabular + text | Inside Airbnb — one city | Held-out pricing error vs a **tabular-only baseline**, plus actionable mispriced listings |
| 5 | Contract review with expert ground truth | CUAD — 510 contracts, 13,000+ lawyer clause annotations | Retrieval hit rate + citation accuracy vs the expert annotations, **by clause type** |
| 6 | Agent over a live public API | NYC 311 — ~40M requests, public query API | Task set with answers verified by hand-written queries, success by task type, **auditable transcripts** |
| 7 | Fine-tuned specialist | LEDGAR (HF `lex_glue`) — 80,000 provisions, 100 clause types | Base vs fine-tuned vs frontier few-shot on held-out; **cost per 1,000 clauses**; what the specialist lost on general tasks |
| 8 | Intent routing, own vs rent | Bitext (27,000 utterances, 27 intents) or Banking77 (13,000 queries, 77 intents) | Held-out accuracy + **confusion structure** — which intents are genuinely confusable and what that means for queue design |
| 9 | Machine labels vs human labels | GoEmotions (211,000 rater-level annotations w/ rater IDs) or CFPB complaints | Agreement stats **with chance baselines**; accuracy broken out by level of human agreement — humans-vs-humans sets the ceiling |

**The pattern:** every evaluation is stated in business units against an honest baseline, and most
carry a decision (threshold, policy, own-vs-rent, trust-vs-don't). That is what the 25% buys.

---

## 8. Timeline — 3½ weeks from approval to submission

| Week | Dates | Milestone |
|---|---|---|
| 0 | Sep 2–8 | Team found, direction agreed, **proposal uploaded by Tue Sep 8 midnight** |
| 1 | Sep 10–13 | Albert's feedback (Thu 9/10) → adjust · dataset downloaded and profiled · **evaluation harness and gold set built first**, before any modelling |
| 2 | Sep 14–20 | Baselines run and locked · main system v1 · first numbers on the held-out set |
| 3 | Sep 21–27 | Error analysis · cost-at-scale model · negative results written up honestly · exec summary draft |
| 4 | Sep 28–Oct 2 | Slides · recorded demo backup · notebook annotation pass · re-run evaluation from clean clone · **zip to Box by Fri Oct 2 11:59 PM** |
| — | Sessions 13–14 | 10-minute presentation, order random |

Week 1's order is deliberate: build the test before the system, so the system cannot quietly be
tuned to the test.

---

## 9. Suggested workstreams for a five-person team

| Stream | Owns | Produces |
|---|---|---|
| A · Data + pipeline | download, cleaning, chunking/feature build, reproducible `make data` step | dataset access instructions, data notebook |
| B · System | the model / RAG / agent itself | the artifact, annotated |
| C · Evaluation | gold set, ground truth provenance, baselines, the scoring code | the numbers everyone quotes, re-runnable in one command |
| D · Economics + framing | stakeholder, decision, cost-at-scale, threshold/policy analysis | exec summary, the "so what" slides |
| E · Communication | slides, demo recording, AI-use note, final annotation pass | the deck, the zip |

Everyone reads everyone's code once before Oct 2; Albert grades whether *he* can follow it.

---

## 10. Open items before the proposal can be written

1. **Who is on the team?** Read the Google sheet in the Sep 1 announcement (not on disk).
2. **Has anyone already claimed a direction?** One person uploads — coordinate first.
3. **Which direction?** See `Project_DIRECTION-MEMO.md` for a ranked shortlist and a recommendation.
4. **Who uploads the proposal**, and by when internally (suggest **Mon Sep 7 evening**, a day of slack).
5. Screenshot the *Final Project Proposal - per team* Canvas page to the course root as
   `ASSIGNMENT_FinalProjectProposal.png` when next on Canvas.

---

## 11. What Albert has said in class (Granola transcripts, checked Sep 2)

- **Class 1, Aug 17** — the only substantive in-class discussion so far. Framing: *"identify — this
  pretty loosely because I do want there to be a lot of freedom — some business problem and build
  either an ML or AI solution."* Datasets: *"I'm going to push you guys to look for example datasets
  that might be helpful either through a website called Hugging Face or Kaggle … but pretty broadly
  open if you guys have other ideas here."* Deliverable: *"a 10-minute presentation … Your goal is
  to kind of show that your prototype works and estimate what it might cost implemented at scale."*
  Plus a peer-evaluation component and ~5-person teams once add/drop settled.
- **Class 5, Aug 31** — no project discussion (all binary-classification metrics).
- **Class 6, Sep 1** — only the team-balancing note: any group at six members by noon gets rebalanced
  by random draw. (Recording started mid-session; anything earlier was not captured.)
- Nothing in any recording about forking existing work versus building new. The written spec's
  requirement stands: *"the project itself must be something you built and measured."*
