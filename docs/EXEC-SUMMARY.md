# Predicting the Second Gift — executive summary

*Deliverable 5 of 6. One page, for an executive who missed the presentation. Problem, approach,
findings, recommendation. The first two sections are written; the last two fill in when the
numbers exist. Keep it to one page when rendered.*

**Group 11 · GBUS 8496 · Malorie Black, Reid Jacobson, Thadeus Knospe, Rodolfo Perez-Cortes
Manrique, Bakul Badwal · [date]**

## Problem

Most nonprofits acquire a donor once and never hear from them again. On DonorsChoose, the
classroom crowdfunding platform, 71% of all donors across seventeen years gave exactly once. The
second gift is where retention is won or lost, and the organizations least equipped to work it are
small ones: a development lead at a nonprofit with a $500K budget and no data staff can personally
follow up with only a fraction of the people who gave for the first time last month. Today she
builds that list by hand from recency and gift size.

The decision this project supports: given a fixed monthly outreach capacity, which first-time
donors should receive a personal follow-up, and where should the cutoff sit?

One of us founded GoGood Technologies, a donor-engagement platform whose customers are this
stakeholder. That is why we chose the problem, and the reader should weigh our conclusions with
that in mind.

## Approach

We used DonorsChoose Open Data 2002–2019 (ICPSR 37898): 11.4 million donations from 3.5 million
donors, with a donor identifier that we confirmed links gifts across projects. For each donor we
built one label — did they give again within twelve months of their first gift — and held out the
2017 and 2018 first-gift cohorts as a test set the model never saw, because the stakeholder's
question is about next year's donors and a random split would let the model see the future.

We scored every ranking rule at her capacity, the top 10% of each month's new donors, and measured
dollars of subsequent giving identified per contact. The baseline is the rule she uses by hand:
rank by first-gift size. On a cohort of first-time donors that is the strongest simple rule
available, since frequency and recency are identical for everyone in it.

One finding shaped everything after it. The file holds three populations, not one: citizen donors
(86% of people, 23% of repeat dollars), organizations (0.1% of people, 62% of dollars, the largest a
corporate matching program making tens of thousands of gifts a year), and teachers seeding their
own classrooms. Pooled, any ranking rule looks brilliant by finding the corporations. We scored
citizen donors only, the people a development lead actually calls.

## Findings

*[Fill in from slides 6 and 7. The headline: model vs gift-size rule vs contact-everyone at 10%
capacity, in dollars per contact. Then calibration, and where the model is weakest. If the model
does not beat the gift-size rule, say so here in the first sentence; Albert grades the rigor, not
the direction of the result.]*

Baseline established: ranking by first-gift size identifies 56% of subsequent citizen giving at
10% capacity, $116 per contact against $21 for contacting everyone, but with 20% precision — it
finds dollars, not people.

## Recommendation

*[Fill in from slide 8 and 10. Her capacity in hours, the list she works, what it costs to run
(nothing — a monthly batch job), and what it is expected to reach. One paragraph. Then the three
things we are not claiming: no causal effect of outreach, thank-you-packet question dropped, and
the transfer caveat to relational small-nonprofit donors.]*
