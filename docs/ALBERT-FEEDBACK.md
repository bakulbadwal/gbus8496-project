# Albert's approval and guidance — received Sep 9, 2026

**The project is approved.** He called it a well-designed proposal. This file is his guidance,
recorded because it changes the build order. Where this file and our proposal disagree, **this wins.**

Relayed through Bakul from Albert's reply to our proposal questions; he was answering the three
"what we need from you" asks. Paraphrased closely, not a verbatim transcript.

---

## 1. The blocking check — do this before anything else

> "As soon as possible, confirm that the donor ID in the public-use file actually links gifts across
> projects, because the whole project depends on it."

He is right, and it is the single point of failure. If `DONOR_ID` is scoped per project rather than
per person, there is no donor history, no second-gift label, and no project.

**Run `src/check_donor_id.py` first.** It answers exactly this and nothing else. Post the numbers in
the team chat before any other work starts. If the answer is bad, we switch to the Amazon fallback
(`docs/proposal/superseded/Proposal_v2.docx`) the same day, with three weeks still on the clock.

## 2. Compute and data

> "You can use the 'Very Large Virtual Machine' and it will work fine."

So no sampling is required. Use the Very Large VM on JupyterHub and work on the full files.

**If we do sample anyway:**

> "Sample whole first-gift cohorts by month rather than random rows, so that the change in donor
> behavior over time that you want to report survives the sampling."

Sampling random donation rows would destroy each donor's history and flatten the time trend that is
half our story. Whole monthly cohorts, in or out.

## 3. Order of the four measurements — his order, not ours

Two weeks is not long, and he ranked them:

| Order | Measurement | Note |
|---|---|---|
| **1** | **The ranking result at the stewardship capacity, against the ladder of baselines** | This is the decision. Everything else is support. |
| **2** | Calibration, and the error analysis by cohort | |
| **3** | The thank-you-packet question | **Drop it without regret** if the timing of that flag is ambiguous — which we already flagged as a risk |

This supersedes the ordering in our proposal and in Thadeus's five-area list. The headline number is
"at our stakeholder's capacity, how much better is the model's ranked list than the baselines" — not
PR-AUC, and not calibration.

## 4. The amount model — keep it cheap

> "For the amount model, a simple approach such as a regression on the log of the amount, or even the
> cohort median, is fine to start, and it should not delay the main result."

Start with the cohort median. Do not let a second-gift-amount model block measurement 1.

## 5. Negative findings

> "Yes, a well-supported negative finding against the simple baselines is an acceptable result,
> provided the baselines are fair and the comparison is careful."

Confirmed, with a condition attached: the baselines have to be **fair**. A strawman RFM rule that we
beat easily is worse than no baseline. Tune the baseline honestly before comparing.

## 6. Disclosure

> "Please keep disclosing the team member's commercial connection in the presentation, as you did in
> the proposal."

The GoGood Technologies connection goes on a slide, not just in the proposal. Not optional.

## 7. Scope

> "It is fine to work on a project relevant to your broader interests as long as the group is okay
> with it. It sounds like they are."

Settled — the poll was 4 of 4.
