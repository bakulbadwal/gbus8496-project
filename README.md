<div align="center">

<img src="assets/hero.png?v=2" alt="GBUS 8496 Final Group Project — Darden, Fall 2026" width="100%">

# GBUS 8496 · Final Group Project

**Machine Learning and AI for Business · Prof. Michael Albert · UVA Darden · Q1 2026–27**

Problem → data → system → evaluation → judgment → communication.
One business problem, one artifact we built, one evaluation we can defend.

</div>

---

## The team

All five of us have push access to this repo. GitHub's **Contributors** sidebar only lists people
who have already pushed a commit, so it will fill in as we each start working — it is not the
membership list. This table is.

| Member | GitHub | Workstream | Status |
|---|---|---|---|
| Malorie Black | [@blackm33](https://github.com/blackm33) | Outreach economics and recommendations | ready to start |
| Reid Jacobson | [@Reido938](https://github.com/Reido938) | Exploratory analysis and feature engineering | ready to start |
| Thadeus Knospe | [@thadeusk](https://github.com/thadeusk) | Evaluation and error analysis | ready to start |
| Rodolfo Perez-Cortes Manrique | [@rodolfopiem33](https://github.com/rodolfopiem33) | Baseline and model development | ready to start |
| Bakul Badwal | [@bakulbadwal](https://github.com/bakulbadwal) | Data and label construction | ✅ skeleton pushed Sep 9 |

## Status by workstream — what is done, what is pending, what is left

| Workstream | Owner | Status | What is left |
|---|---|---|---|
| **Data + label construction** | Bakul | ✅ **DONE Sep 11**, on the real file | Nothing blocking. One decision for the team to confirm (below) |
| Exploratory analysis + features | Reid | ⏳ not started | Join `cohorts.parquet` to the Projects file on `first_project_id`; find features that beat gift size alone |
| Baseline + model | Rodolfo | ⏳ not started | Train on `split == "train"`, citizen donors; score the holdout through `evals/score.py` **once** |
| Evaluation + error analysis | Thadeus | ⏳ not started | Albert's measurement 2: calibration curve + error analysis by cohort year. Measurement 1 already runs |
| Outreach economics + recommendation | Malorie | ⏳ not started | A real cost per contact, a defensible capacity, and the recommendation slide |
| Slides · exec summary · AI-use note · zip | all | ⏳ **spine done Sep 11** | [`docs/slides/OUTLINE.md`](docs/slides/OUTLINE.md): 10 slides, owner per slide, class-vote question per slide; Bakul's two slides drafted with figures in `docs/slides/assets/`. [`docs/EXEC-SUMMARY.md`](docs/EXEC-SUMMARY.md): problem + approach written, findings + recommendation blank. Deck assembled in the final week. Presentations **Sep 28–29**; zip Oct 2 |

### What Bakul's workstream delivered

- **The blocking check, passed.** `src/check_donor_id.py` on the real file: 3,466,570 donors, 25.4% give to more than one project. The ID follows the person. Bonus finding: **71.1% of donors gave exactly once, ever.**
- **The label**, `src/labels.py` → `data/processed/cohorts.parquet`: **3,277,153 donors**, one row each, with cohort month, first-gift amount and attributes (donor type, matched, teacher-referred, thank-you packet, gift card), the 12-month second-gift label, the subsequent amount, and the train/holdout split. Four judgment calls documented in notebook 01: same-month repeats excluded, twelve whole months, unclosed windows dropped, refunds excluded.
- **The baseline ladder and the scorer** for Albert's measurement 1 (`src/baselines.py`, `evals/score.py`), with a built-in consistency check that holds on real data.
- **The population finding.** Pooled, gift-size ranking "found" 80% of subsequent value — an artefact of 708 organizations holding 62.5% of the dollars. `evals/profile_cohorts.py` reproduces it in one command.
- **Notebook 01**, executed on the real data with outputs saved, 0 errors. Read it first.

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

## Setup — takes ten minutes

```bash
git clone https://github.com/bakulbadwal/gbus8496-project.git && cd gbus8496-project
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

**Data.** Download `ICPSR_37898-V1.zip` (Delimited) from icpsr.umich.edu/web/ICPSR/studies/37898 —
free account, no institutional login needed — and unzip it into `data/raw/`. It is 1.2 GB and
never goes into git. Then, in order:

```bash
python src/check_donor_id.py  data/raw/ICPSR_37898/DS0001/37898-0001-Data.tsv     # ~3 min, prints PASS
python src/labels.py          data/raw/ICPSR_37898/DS0001/37898-0001-Data.tsv data/processed/cohorts.parquet   # ~5 min
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
| Measurements 2–3 (Albert's order) | ⏳ calibration + error analysis by cohort (Thadeus); thank-you-packet question — codebook has no timing, **recommend dropping as a feature** (Albert pre-approved) |
| Slides, exec summary, AI-use note, zip | spine done — outline with owners, two slides drafted, summary half-written; deck built in the final week |

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
