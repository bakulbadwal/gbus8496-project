# GBUS 8496 — Final Project Proposal

**Team:** Bakul Badwal · Thadeus Knospe · Malorie Black · [names] — Group [#]
**Working title:** *Who reads this one? Screening triage for a nonprofit's volunteer reviewers*

## 1. Problem and business application

DonorsChoose.org is a nonprofit through which public-school teachers post classroom project requests that donors fund. Before a request goes live, a volunteer screener reads it against the organization's approval criteria. Volume runs to hundreds of thousands of proposals a year, and volunteer reviewers are the scarce resource: they set how fast a request reaches donors. Today every proposal gets a full human read.

**User:** the operations lead for project screening. **Decision:** which incoming proposals can be approved with no human read, which go to a reviewer as routine, and which are flagged for a closer read. The costs are explicit and asymmetric: a reviewer-hour; approving a proposal that should have been rejected (donor money misdirected, trust damaged); and rejecting or delaying a good classroom request. The output turns a flat queue into a triage policy with a stated reviewer-hours saving and error budget.

## 2. Dataset and source

*DonorsChoose.org Application Screening* — released by DonorsChoose for the 2018 Kaggle competition of the same name: about 182,000 real proposals submitted in 2016–2017, each with the teacher's essays, title, resource summary, subject categories, grade band, state, and count of prior projects; a linked resources table (requested items and prices); and the human screener's actual decision, `project_is_approved` (roughly 85% approved). Ground truth is a real human judgment. Source: kaggle.com/competitions/donorschoose-application-screening; login-free mirror on Hugging Face (`udayl/donors_choose_data`, 200 MB + 127 MB).

## 3. What we will build

A screening-triage system built as three tiers of increasing cost, compared honestly: **(a)** a tabular-only gradient-boosting model on categories, prices, and teacher history; **(b)** the same model plus sentence-transformer embeddings of the essays (the Session 7 pipeline); **(c)** a frontier LLM asked to screen each proposal with DonorsChoose's published criteria in the prompt (Session 8). On top of whichever tier wins, a **decision layer**: approve / route / flag thresholds derived from the stated payoffs rather than tuned, plus the cost per 1,000 proposals of each tier at production volume.

## 4. Evaluation

**Ground truth:** the human screener's decision on a **time-based held-out split** (train on earlier submissions, test on the final months), untouched during development. **Model metrics:** AUC and calibration per tier. **Decision metric:** reviewer-hours saved and expected error cost under our policy versus two honest baselines, *review everything* and *approve everything* (the 85% majority rule). **Error analysis:** where each tier fails, cut by subject, grade, state, essay length, and request price, including whether errors fall unevenly across teacher groups. **Ceiling:** because the label is itself a human judgment, we hand-read a stratified sample of about 100 model–human disagreements to estimate how noisy the human decision is, which sets the ceiling for any model. The LLM tier is scored on a cost-bounded subset of about 2,000 test proposals. **A negative result is reportable:** if essay text adds nothing over tabular features, or the LLM screener agrees with humans no better than the cheap model, we report it, with the cost implications.

## 5. What we need from you

(1) Confirmation that scoring the LLM tier on a ~2,000-proposal subset of the test split is an acceptable evaluation scope. (2) Whether the JupyterHub API tokens may be used for those calls, or we should bring our own keys. (3) Any objection to grounding a 2026 recommendation in 2016–17 data; we will state the limitation either way.
