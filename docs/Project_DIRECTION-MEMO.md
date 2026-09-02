# GBUS 8496 Final Project — direction options and a recommendation

**Team-shareable.** Written Sep 2 against Albert's spec (`Final_Project_SPEC.md`) and the
grading rubric. The point of this memo is to pick *one* direction by the weekend so the one-page
proposal can be uploaded before **Tue Sep 8 midnight**.

---

## What the rubric rewards, in one line

A **named decision-maker**, a **real dataset**, an artifact we built, an evaluation against
**ground truth we can defend**, **honest baselines**, an **error analysis**, a **cost-at-scale**
number, and a talk the room can take an insight from. Model sophistication is explicitly not scored.
A well-evidenced *negative* result is explicitly rewarded.

## What this team already has on hand (from the quarter's coursework)

- **A working RAG pipeline** (Exercise III): MiniLM sentence embeddings, cosine retrieval, precision@k
  scoring, and measured latency and storage numbers — plus a finding that 3.9% of long texts silently
  truncate at the encoder's 256-token limit. That is a head start on any retrieval project.
- **Cost-weighted decision analysis** (Sessions 4–5, UVA Hospital): thresholds derived from payoffs
  rather than `argmax`, and a leaderboard result showing that *tuning* the threshold lost money.
  Directly reusable for any "act / don't act" layer.
- **Split-half and out-of-fold validation** discipline that killed two ideas which looked best
  in-sample — the habit Albert's "honest baselines, correct interpretation" line is asking for.
- **Evaluation-study experience** (Session 6, Kibet Capital): a 22-point representation gap that
  survived the classifier's own error bars; two prep claims corrected when the data contradicted them.
- **Domain credibility in M&A / private equity** — a real diligence workflow to name a stakeholder in.

---

## The shortlist, scored against the rubric

Scores are 1–5 on how well each option can hit the line, given 3½ weeks and five people.

| Option | Tech 30 | Eval 25 | Business 15 | Ambition 10 | Room (insight) | Crowding risk | Total feel |
|---|---|---|---|---|---|---|---|
| **1. Contract-diligence assistant on CUAD, with a "what still needs a lawyer" triage layer** | 4 | **5** | **5** | 4 | 4 | medium (on his list) | **best** |
| 2. Hotel overbooking policy (his example #1) | 3 | 4 | 4 | 2 | 3 | **high** — the canonical pick | safe, low ceiling |
| 3. Intent router: own a fine-tuned model vs rent an API (Banking77) | 4 | 4 | 3 | 3 | 4 | medium | clean, generic |
| 4. Evaluation study: LLM labels vs human labels (CFPB, data already on hand) | 3 | 5 | 3 | 3 | 4 | low | rigorous, thin artifact |
| 5. Clinical-trial success screener for a biotech investor (ClinicalTrials.gov + published base rates) | 4 | 3 | 4 | **5** | 4 | none | ambitious, label risk |

### Option 1 — recommended: *"Which clauses can the machine be trusted on?"*

**User and decision.** An M&A associate (or a PE deal team) reviewing a target's contracts in a data
room. Today they read every material contract for ~40 standard clause types — change of control,
exclusivity, non-compete, MFN, uncapped liability, termination for convenience, and so on — at
lawyer or associate hourly rates. The decision: **for which clause types can a retrieval system be
trusted to find the clause, and for which must a human still read the contract?**

**Dataset.** CUAD (Atticus Project): 510 real commercial contracts, 41 clause categories, 13,000+
clause spans annotated by lawyers. Public, CC-BY-4.0, downloadable today; also on Hugging Face.
This is the best ground truth on Albert's whole list — expert labels at the span level.

**Build.** A page-cited clause finder: chunk → embed → retrieve → LLM extracts the clause span with a
citation. Against **three honest baselines**: keyword/BM25 search (what a paralegal's Ctrl-F does),
the LLM with the whole contract in context and no retrieval (long-context, the "just stuff it in"
option), and *no system* (human reads everything). Then the **triage layer**: for each clause type,
a payoff-derived rule — trust the system if its measured recall clears the threshold implied by the
cost of a missed clause vs the cost of an hour of review. That is the Session 5 threshold logic
transplanted into a GenAI system, and it turns a retrieval benchmark into a decision.

**Evaluation.** Held-out contracts never touched during development. Per clause type: retrieval hit
rate (did the gold span land in the top-k), citation accuracy (does the cited page/passage contain
the gold span), and extraction exactness. **Failure decomposition:** when it is wrong, was the
right passage never retrieved, or retrieved and then mis-read? Cost per contract for each option
at production volume. Expected honest findings: some clause types are near-perfect, some (the ones
written in many different ways, e.g. MFN, uncapped liability) fail badly — and long-context may beat
RAG at a price. A negative finding on a clause type *is* the recommendation.

**Why it wins on the rubric.** Expert ground truth (Eval 25). A real user with a real hourly cost
(Business 15). A decision layer the starter code never had (Ambition 10). Reuses the Exercise III
pipeline, so week 1 is spent on the gold set, not on plumbing (Tech 30, on time). The room's insight
question answers itself: *"here is the list of clauses you can stop reading, and here is the list you
can't, and here is why."*

**Risks.** CUAD contracts are long (many exceed 50 pages), so chunking strategy is a real design
variable — treat it as a finding, not a nuisance. Frontier-API cost: bound the LLM-scored subset to
~100 held-out contracts × 41 clause types; retrieval-only metrics can run on all 510 for free.
Crowding: CUAD is on his list, so another team may pick it — the triage layer and the
long-context-vs-RAG comparison are the differentiators, and are worth stating in the proposal.

**Ask Albert.** Whether JupyterHub's coding-agent API tokens can be used for the extraction calls
(or whether we bring our own key), and whether a 100-contract LLM-scored held-out set is an
acceptable scope for the evaluation.

### Option 2 — Hotel overbooking (the safe fallback)

Exactly the cost-weighted decision analysis the team has already done once. Held-out cancellation
model, then a policy backtest in revenue against "never overbook" and "always overbook x%". Strong
evaluation, easy business story, and the tabular skills are all in hand. The problem is the room:
it is his first example, it will be picked by more than one team, and the class score is z-scored
*relative* to the other groups. The ceiling on "genuine insight" is low unless the finding is
surprising. Keep as the fallback if the team wants a low-variance quarter.

### Option 3 — Own vs rent an intent router (Banking77)

Fine-tune a small open model on 77 banking intents and compare against a frontier model with
few-shot prompting: accuracy, confusion structure, and cost per 1,000 queries. Fits Session 11
(fine-tuning) and gives a crisp own-vs-rent economics story a support-operations lead cares about.
Generic, though — a lot of teams in a lot of schools have built this — and the "insight" is
predictable (the specialist wins on cost, the frontier model wins on rare intents).

### Option 4 — LLM labeler vs human labels (CFPB)

The study is the contribution: agreement with chance baselines, accuracy by level of human
agreement. The CFPB narratives are already on disk from Exercise III. Rigorous, cheap, and it plays
to the team's Kibet-style evaluation discipline. Weaker on "artifact" and on business framing (who
acts on the label, and what does it cost them to be wrong), and CFPB carries one human label per
complaint, so the human-vs-human ceiling needs GoEmotions instead.

### Option 5 — Clinical-trial success screener (from a prior side project)

A transparent base-rate model over live ClinicalTrials.gov data for a biotech investor already
exists as a screening tool with cited base rates. Upgrading it to a real predictive model with a
temporal held-out split and a decision layer is the most ambitious option here and the one no other
team will have. The risk is the label: "trial succeeded" has to be engineered from phase
transitions and termination reasons, and that label engineering could eat two of the three weeks.
Worth proposing only if the team is excited by biotech and accepts the schedule risk.

### What *not* to do with the prior GitHub builds

Several earlier builds (a fraud-victim intake agent, a grounded background-briefing agent, an
on-chain tracer) share a pattern worth borrowing — **deterministic code owns every fact, the model
only narrates, and an executable gate with negative controls proves it** — but none of them is the
project. They were built solo, before the course, with tiny golden sets; reusing one would score
poorly on "something the *team* built and measured" and would leave four people with nothing to
own. Borrow the pattern for the evaluation harness (gold set, negative controls, one-command
re-run); don't submit the repo.

---

## Recommendation

**Propose Option 1**, with Option 2 as the stated fallback if Albert's Thursday feedback pushes back
on scope. Decide by **Sat Sep 5**, draft the page Sun Sep 6, upload **Mon Sep 7** evening with a day
of slack against the hard deadline.

## Decision needed from the team (reply in the chat)

1. Option 1, or one of the others — and any strong objection.
2. Who uploads the proposal.
3. Anyone with a licence or domain reason to prefer a different dataset (e.g. someone with real
   contract-review or revenue-management experience changes the business-framing calculus).
