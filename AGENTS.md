# AGENTS.md — the contract for every coding agent working in this repo

You are working on a graded group project for **GBUS 8496, Machine Learning and AI for Business**
(Prof. Michael Albert, UVA Darden, Fall 2026). Five MBA students share this repo; each may drive a
different agent (Claude Code, Codex, OpenCode on JupyterHub, Cursor). This file is what all of them
read. **Read it fully before doing anything.** `CLAUDE.md` is a pointer to this file.

## 1. What the project is

Read, in order: `README.md` → `docs/Final_Project_SPEC.md` → `docs/Project_DIRECTION-MEMO.md`.
Albert's original assignment is `docs/albert/Final_Group_Project_Albert.pdf` and wins any conflict.

Two deadlines: **proposal Tue Sep 8 2026 midnight** (Canvas, one page, five elements, one uploader)
and **final Fri Oct 2 2026 11:59 PM** (Box, `Group_11.zip` — we are Group 11, 40% of the grade).

**Direction is decided (Sep 7 poll, 4 of 4) and APPROVED by Albert on Sep 9: Predicting the Second
Gift** — donor retention on DonorsChoose Open Data 2002–2019 (ICPSR 37898). The submitted proposal is
`docs/proposal/Proposal_v4_FINAL.docx`.

🔴 **Read `docs/ALBERT-FEEDBACK.md` before writing any code.** It carries his guidance and it
overrides the proposal where they differ. The three things that change what you do:

1. **One check gates everything.** `src/check_donor_id.py` must pass before any other work — it
   confirms `DONOR_ID` links gifts across projects. If it fails, the project is dead and we move to
   the Amazon fallback. Do not build around it, do not assume it passes.
2. **His measurement order, not ours.** (1) the ranking result at stewardship capacity against the
   baseline ladder — this is the decision and the headline; (2) calibration and error analysis by
   cohort; (3) the thank-you-packet question, dropped without regret if the flag's timing is
   ambiguous. Do not start (2) before (1) produces a number.
3. **Compute.** Use the JupyterHub **Very Large Virtual Machine**; the full files fit. If you sample
   anyway, sample **whole first-gift cohorts by month**, never random rows — random rows destroy
   donor histories and flatten the time trend.

`data/README.md` has the fetch recipe and the label rules. The evaluation harness still comes before
the model.

## 2. The standard: every number is rebuilt, every result is re-runnable

- **Build the test before the system.** The gold set, its provenance, and the scoring code in
  `evals/` exist before any model or pipeline is tuned. The held-out split is never looked at during
  development. Tuning on the test set is the one unforgivable error here.
- **Every reported number is produced by code in this repo**, from raw data to figure, runnable on a
  clean clone in one documented command. Albert: *"I should be able to re-run your evaluation."*
- **Rebuild before you restate.** Never quote a number from a paper, a dataset card, a notebook's
  markdown, or another teammate's message as if you verified it. Recompute it. Where your number and
  theirs disagree, say so and say which is right — a reproducible discrepancy is a finding.
- **Honest baselines are mandatory.** A naive/majority baseline, the simplest credible method, and
  where relevant a frontier-model-with-no-system baseline. A result without a baseline is not a result.
- **Validation that transfers.** Use out-of-fold or split-half checks before believing a tuning gain.
  Report the noise floor (standard error) next to any leaderboard-style number.
- **Negative findings are kept, not deleted.** *"A rigorous project that concludes an approach does
  not work, and shows why, can earn a high grade."*
- **Decisions, not just metrics.** Wherever the output feeds a decision, derive the threshold or
  policy from the payoffs and state the costs explicitly. Report the business-unit number (dollars,
  hours, contracts) next to the ML metric.
- **Cost at production scale** is a required answer. Keep a running cost model (API calls, tokens,
  compute, human review hours) in `docs/` and update it when the pipeline changes.

## 3. Repo rules

- `data/` is gitignored. Never commit raw data. `data/README.md` documents exact fetch steps and
  checksums or row counts so anyone can reproduce the dataset. Small derived files (< 5 MB, e.g. a
  gold set) may live in `evals/` and must be committed.
- **Secrets never enter the repo.** API keys go in `.env` (ignored). If you see a key in a diff, stop
  and remove it before committing.
- **Notebooks are committed** and are the primary deliverable. Annotate them in the style of the
  course starter code: a markdown cell before every code cell saying what it does and why, what was
  tried and rejected, and what the output means. They will be read aloud in class; *"if you think
  something is clear, someone else reading your code will still find it confusing."*
- Shared logic lives in `src/` and is imported by notebooks; do not copy-paste functions between
  notebooks. Keep `src/` plain Python with docstrings.
- Names: `notebooks/NN_short-name.ipynb` numbered in run order; `evals/run_evals.py` (or equivalent)
  is the single command that produces every reported number.
- Keep `README.md`'s "Where we are" table current. It is the team's shared state; chat threads are not.
- Do not restructure the repo, rename folders, or add tooling nobody asked for. Ask in the team chat.

## 4. Git

- Work on a branch per task (`<name>/<short-task>`), open a pull request, get one teammate to read
  it. Small, frequent commits with messages that say *why*.
- Commit under your own GitHub identity so the history shows who built what (this also feeds the
  peer effort-share ratings).
- Never force-push `main`. Never rewrite shared history.
- Before pushing, run the eval command and make sure it still passes or still reproduces.

## 5. AI use — allowed, documented

Albert's project policy (verbatim): *"You can use any AI tool for assisting in your project, but you
have to document how you built it in such a way that others could reproduce your work. It is not
enough that 'Claude told me the answer was x'."* And: *"The judgment must be your own."*

So, for every agent session that changes something:
- Append a line to `AI-USE-NOTE.md`: date, who, which tool/model, what it did, **how the output was
  verified** (test run, recomputed number, manual check).
- Do not paste code you cannot explain; the team answers questions live.
- The judgment calls — choice of problem, design of the evaluation, interpretation, recommendation —
  are written by humans and discussed in the team chat, then recorded in `docs/`.

## 6. When you are unsure

Ask in the team chat rather than guessing. If you must proceed, state the assumption in the
notebook or PR description and flag it in `README.md` under "Where we are".
