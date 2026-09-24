# Predicting the Second Gift — executive summary

**Group 11 · GBUS 8496 · Malorie Black, Reid Jacobson, Thadeus Knospe, Rodolfo Perez-Cortes
Manrique, Bakul Badwal · October 2026**

## Problem

On DonorsChoose, the classroom crowdfunding platform, 71% of donors across seventeen years gave
exactly once. The second gift is where retention is won or lost. A development lead at a $500K
nonprofit with no data staff can personally follow up with only a fraction of last month's
first-time donors, and today she picks them by hand from gift size. Our question: at a fixed
monthly capacity, which first-time donors should get the call? One of us founded GoGood
Technologies, whose customers are this stakeholder; weigh our conclusions with that in mind.

## Approach

We used DonorsChoose Open Data 2002–2019 (ICPSR 37898): 11.4 million donations from 3.5 million
donors. Each donor gets one label, whether they gave again within twelve months of their first
gift. The 2017–18 cohorts were held out and scored once, because her question is about next year's
donors. Every rule is scored at her capacity, the top 10% of each month's new donors, in dollars of
subsequent giving identified per contact. The baseline is her own rule, rank by first-gift size.

One finding shaped everything after it: the file holds three populations. Organizations are 0.1%
of donors but 62% of repeat dollars, mostly corporate matching programs. Teachers seed their own
classrooms. Pooled, any rule looks brilliant by finding the corporations. We scored citizen donors,
86% of people, the ones she actually calls.

## Findings

**A model beats her rule by a small, reliable margin.** On the holdout, ranking by predicted
second-gift value identifies **$120 per contact**, against **$116** for gift size and **$21** for
calling everyone. On the same donors the gap is +$3.80 ± 0.51, about seven standard errors. One call
in ten reaches 58% of all subsequent giving. The model is two gradient-boosted estimators, for the
chance of a second gift and its size, using first-gift attributes plus the project and school
first funded. Gift size already carries most of the signal; project context adds modest lift.

**The probabilities can be trusted.** Predicted and observed return rates agree within about a point
across most of the range; the top decile predicts 27% and observes 24%. Lift is stable from 2017
to 2018 as the base rate falls. The gain comes from a swap: her rule is crowded with
teacher-referred donors, friends and family recruited for one classroom, who return 13% of the
time. The model replaces them with donors who funded several classrooms at once, who return 23%.

## Recommendation

Each month, rank new first-time donors by predicted second-gift value and call the top one in ten.
On the holdout that nets **$7.75M** over two years at $25 per contact, **$312K more** than her rule
on the same number of calls; calling everyone **loses $3.6M**. Cost per contact sets how deep to go:
at $5 about half of new donors clear break-even, at $25 only 6.5%. It runs as one monthly batch job
on a laptop, about ten minutes, no API calls.

**What we are not claiming.** No causal effect: nobody was randomly assigned a call, so these are
dollars *identified*, not *caused*; a small randomized pilot is the next step. The thank-you-packet
question was dropped because the data gives no timing. Transfer from a marketplace to a relational
small nonprofit is a hypothesis. The $25 cost is a placeholder for a figure from real practice.

*Every number reproduces with `python evals/run_all.py`; sources in `evals/results/`.*
