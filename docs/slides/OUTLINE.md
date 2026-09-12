# Presentation outline — ten minutes, ten slides, five voices

**Sessions 13–14, Sep 28–29. Order drawn at random, so we are ready on the 28th.** All five present.
Live demo welcome, recorded backup required. Aim the talk at the class, not at Albert: they grade half
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
| 7 | **How we know it works, and where it does not** | Thadeus | "It is calibrated here, it is not calibrated there, and it is weakest on exactly the donors she cares about most." | Albert Q1 · Q3 evidence |
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
Calibration curve on the holdout. Error analysis by cohort year: does 2018 behave like 2015? Cut
by first-gift size band: the model is probably weakest on small first gifts, which is where most
of her donors are. That sentence is the honest one and the room will respect it. Answers Albert's
"how do you know it works" directly.

### 8 · What she does on Monday — Malorie, 60 seconds
The decision layer (`src/decision.py`). Her capacity in hours → contacts per month. Cost per
contact from real practice (a number GoGood can defend) — **this number decides the
recommendation**: break-even p* = cost / $50, and the sensitivity table in
`evals/results/07_decision_layer.txt` shows it swings from "call 61%" at $5 to "call 0.1%" at $25.
The line to land: **contacting everyone loses money** (−$3.6M on the holdout at $25) while the
ranked 10% nets +$7.7M. Production cost: a batch job on one laptop, no API, once a month —
effectively zero. Answers Albert's "cost at scale" in one line and turns the model into a
Monday-morning list (a real one for Dec 2018 is in `evals/results/`).

### 9 · What we did not find, and what we are not claiming — Thadeus, 50 seconds
Three things, plainly. (1) No causal claim: nobody was randomly assigned to be contacted, so we
rank by predicted future value and say "identified", never "caused". (2) The thank-you-packet
question is dropped: the codebook gives no timing, so the flag might record something that
happened *after* the second gift. Albert pre-approved dropping it. (3) Transfer: DonorsChoose
donors are marketplace donors; small-nonprofit donors are relational. Which features are
behavioural (likely transfer) and which are platform-specific (likely not).

### 10 · The recommendation, in one line — Malorie, 20 seconds
One sentence, then stop. Something like: "Rank this month's first-time donors by [model / gift
size], call the top [N], and expect to reach [X]% of next year's repeat giving with [Y] hours."
The exact words come from slides 6 and 8.

---

## Gaps with no owner yet — someone claim these in the chat

- ~~Second-gift amount model~~ — **done as the default** (`src/decision.py`): cohort-year median
  from train, $50 every year. Upgrade to a regression on log amount if someone wants it.
- **Recorded backup of the talk.** Albert requires it. Record on the 26th or 27th once slides exist.
- **The deck file itself.** This outline is markdown so five agents can read it. The actual deck
  gets built once, in the final week, from the sections each owner writes. Google Slides or
  PowerPoint, whichever the team uses.
