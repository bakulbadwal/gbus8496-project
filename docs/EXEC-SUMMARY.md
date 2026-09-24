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
selecting everyone. The paired bootstrap gap is +$3.80 ± 0.51 (one standard error, 30 resamples). One call
in ten reaches 58% of all subsequent giving. The model is two gradient-boosted estimators, for the
chance of a second gift and its size, using first-gift attributes plus the project and school
first funded. Gift size carries much of the signal; the full model adds a modest gain.

**Calibration and coverage limit the result.** The highest probability tenth predicts 26.6%
returning and observes 24.2%. The dollar-ranked list identifies $140 per donor in 2017 and $103
in 2018, beating gift size in both years. Under-$50 donors are 52.4% of the population but only
**0.55% of this list**. The 14.4% figure applies to probability-only ranking, which identifies
fewer dollars ($107/contact). The two lists serve different objectives.

## Recommendation

Pilot the model-ranked list against gift-size ranking, measuring additional donations caused
by outreach before scaling. The historical model list contains $9.79M of subsequent giving;
subtracting contact costs at an assumed $25 leaves $7.75M, versus $7.44M for the gift-size list.
These are **values identified less hypothetical costs, not profit estimates**. The log-amount
model is a useful ranking score but is not calibrated as a mean-dollar forecast, so cost
thresholds remain illustrative. Scoring runs locally without model API fees; outreach, setup
and maintenance still require resources.

**What we are not claiming.** No causal effect: nobody was randomly assigned a call, so these are
dollars *identified*, not *caused*; outreach impact remains unknown. The thank-you-packet
question was dropped because the data gives no timing. Transfer from a marketplace to a relational
small nonprofit is a hypothesis. The $25 cost is a placeholder for a figure from real practice.

*Every number reproduces with `python evals/run_all.py`; sources in `evals/results/`.*
