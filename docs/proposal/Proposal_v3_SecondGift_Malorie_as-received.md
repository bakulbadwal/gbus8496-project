**Project Proposal: Predicting the Second Gift**

\[Course number and name\] \| \[Professor name\] \| Group \[#\] \| September 8, 2026

------------------------------------------------------------------------

Team: \[Name\], \[Name\], \[Name\], \[Name\]

**Problem and business application**

Most nonprofits acquire a donor once and never hear from them again. The highest-leverage moment in the donor lifecycle is the second gift, and the organizations least equipped to work it are small ones. Our stakeholder is the development lead at a nonprofit with roughly a \$500K annual budget and no dedicated data staff. Each month she can personally follow up with only a fraction of the people who gave for the first time, and today she builds that list by hand from recency and gift size.

The decision we support is specific: given a fixed outreach budget measured in staff hours, which first-time donors should receive follow-up, and where should the cutoff sit? Our output is a ranked, scored follow-up list with a recommended threshold and the expected dollars behind it. One of our team members founded GoGood Technologies, a volunteer and donor engagement platform serving exactly this customer, so we can validate the output against real practitioners.

**Dataset and source**

DonorsChoose Open Data, United States, 2002-2019 (ICPSR 37898), https://doi.org/10.3886/ICPSR37898.v1. Free; the public-use files do not require ICPSR membership.

We use two files: Donations (11,377,479 records, 9 GB) and Projects Public-use Data (2,149,817 records, 4 GB), covering projects posted September 2002 through June 2019 with activity through December 2019. We confirmed the schema before committing. Donations carries DONOR_ID, so we can reconstruct each donor’s giving history and build our own outcome label rather than inheriting someone else’s. It also carries AMOUNT, CREATED_MONTH, DONOR_TYPE, PAYMENT_WAS_MATCHED, IS_TEACHER_REFERRED, and THANK_YOU_PACKET_MAILED. Two constraints we accept up front: dates are month-level, and there is no donor demographics file, so DONOR_TYPE is our only donor attribute.

**What we will build**

A second-gift model plus a decision layer on top of it.

- **Label.** For each donor whose first recorded donation falls in the observation window, did they give again within 12 months?

- **Features.** Donation-side (amount, month and seasonality, matched, campaign gift card, teacher-referred, donor type, thank-you packet mailed) and project-side (subject category, grade level, cost, school state).

- **Split.** Time-based, not random. Train on first-gift cohorts through 2016, hold out the 2017 and 2018 cohorts, and observe outcomes through December 2019. A random split would leak future information.

- **Decision layer.** Convert predicted probability and predicted second-gift amount into expected value per contact, subtract an explicit cost per contact in staff time, and recommend a threshold.

**Evaluation**

Our ground truth is observed donor behavior in the held-out period, not hand labels. Four measurements:

- **Discrimination and calibration** on the held-out cohorts. PR-AUC because the class is imbalanced, plus a calibration curve, since an uncalibrated score cannot support a threshold recommendation.

- **Against honest baselines.** The baseline that matters is RFM, the recency-and-amount heuristic small nonprofits actually use, alongside random targeting and contact-everyone. The business metric is net value retained per hour of outreach at a fixed budget. If the model does not beat RFM, we will report that as the finding.

- **Does stewardship predict retention?** THANK_YOU_PACKET_MAILED records a real post-gift action. We will estimate its association with a second gift while controlling for gift size, and state plainly that packets were not randomly assigned, so this is association and not a causal effect.

- **Error analysis by cohort.** We expect the model to be weakest on donors with the thinnest history, which is precisely the case our stakeholder cares about most.

**Limitation we will address head-on**

DonorsChoose donors are marketplace donors who often fund classrooms they have no prior relationship with. Small nonprofit donors are relational. Rather than assume the model transfers, we will test which signal survives: behavioral features (likely to transfer) versus platform-specific ones (likely not).

**What we need from you**

- Confirmation that a well-supported negative finding against the RFM baseline is an acceptable result.

- Guidance on working with 13 GB on JupyterHub, or approval to use a stratified sample of donor cohorts.

- Any concern about anchoring the framing to a company a team member founded.
