# data/ — gitignored

Raw data never gets committed. This file is the reproducible fetch recipe.

## Dataset: DonorsChoose Open Data, United States, 2002–2019 (ICPSR 37898)

- DOI: https://doi.org/10.3886/ICPSR37898.v1 → ICPSR study 37898, version V1.0
- Depositor: DonorsChoose. Distributed by ICPSR (University of Michigan).
- Access: public-use files. Downloading from ICPSR requires a **free ICPSR account** (no institutional
  membership). Create one at icpsr.umich.edu, sign in, open the study page, and download the files
  below. The study page could not be read automatically (bot check), so confirm the file list on the page.
- Verified against the DOI's DataCite registration on Sep 7, 2026: coverage is projects posted
  September 2002 through June 30, 2019, with activity through December 31, 2019.

### ⚠️ The data never goes into GitHub

Two hard reasons: GitHub rejects files over 100 MB (the donations table is 1.46 GB), and a repo
carrying gigabytes of undiffable data is unusable for everyone who clones it. `data/` is gitignored.
If a `.tsv` or the zip ever shows up in `git status`, stop and ask.

For the record: the `TermsOfUse.html` in the zip says *"You agree not to redistribute data or other
materials without the written agreement of ICPSR."* A copy passed around inside the team on the
school's Teams is the team's call; anything beyond the five of us is not.

### What actually arrived (Sep 11) — read this, it corrects the estimates above

The "Download" button on the study page gives one zip, `ICPSR_37898-V1.zip`, **1.2 GB** (not the
9 + 4 GB the page shows per dataset — those figures bundle every statistical-package format). It
unpacks to 3.1 GB and holds all four datasets plus codebooks:

```
data/raw/ICPSR_37898/
├── DS0001/37898-0001-Data.tsv    Donations   1.46 GB   11,377,479 rows   ← the one that matters
├── DS0002/37898-0002-Data.tsv    Resources   0.97 GB   not used yet
├── DS0003/37898-0003-Data.tsv    Projects    0.62 GB   2,149,817 rows    ← Reid's join target
├── DS0004/                       restricted-use README only (no data)
└── */37898-000N-Codebook-ICPSR.pdf            copied to docs/codebook/
```

**Facts that changed the code:**
- Files are **tab-separated**, not comma. Both loaders now sniff the separator.
- Column names are exactly `DONOR_ID, PROJECT_ID, AMOUNT, CREATED_MONTH, DONOR_TYPE,
  PAYMENT_WAS_MATCHED, IS_TEACHER_REFERRED, THANK_YOU_PACKET_MAILED, PAYMENT_INCLUDED_CAMPAIGN_GIFT_1`.
  Flags are inconsistently encoded within one file (`Yes/No` for some, `t/f` for others) — normalised.
- `AMOUNT` has a minimum of **−15.00**: refunds exist. 151 rows; excluded from label construction.
- Every row has a valid `DONOR_ID` and `PROJECT_ID`. No nulls to handle.
- `CREATED_MONTH` runs from 2000-03; the 2000–2002 tail is a few hundred rows and is dropped as
  pre-coverage.
- Text fields in Projects (`SHORT_DESCRIPTION`, `NEED_STATEMENT`, `ESSAY_TEXT`) are **`MASKED BY
  ICPSR`** — no essay text is available. Feature work is structured fields only.
- `DONOR_TYPE` has three values, and they are three populations — see the scoping note in
  `src/config.py`. **Organizations are 0.1% of donors and 62.5% of subsequent dollars.**

### Files we use (original estimates, kept for the record)

| File | Records (from the DOI record) | Approx. size (from Malorie's schema check) |
|---|---|---|
| Donations | 11,377,479 · 11 variables | ~9 GB |
| Projects (public-use) | 2,149,817 · 28 variables | ~4 GB |
| Resources (not needed for v1) | 13,291,370 · 5 variables | — |

Key Donations columns: `DONOR_ID`, `AMOUNT`, `CREATED_MONTH`, `DONOR_TYPE`, `PAYMENT_WAS_MATCHED`,
`IS_TEACHER_REFERRED`, `THANK_YOU_PACKET_MAILED`. Projects supplies subject category, grade level,
cost, and school state, joined on the project id.

### Fetch

```bash
mkdir -p data/raw
# 1. Sign in to ICPSR (free account), open https://www.icpsr.umich.edu/web/ICPSR/studies/37898
# 2. Download the Donations and Projects public-use files (choose CSV or the delimited option)
# 3. Move them into data/raw/ without renaming, then record the exact filenames and sizes here:
#    data/raw/<donations file>   <size>  <sha256>
#    data/raw/<projects file>    <size>  <sha256>
```

Record the checksums in this file on first download so every teammate can confirm they have the
same bytes. Do not commit the files.

### ⚠️ Read before building the label or features

- **Dates are month-level** (`CREATED_MONTH`). "Within 12 months" must be defined in months and
  written down once in `src/`; every notebook imports that definition.
- **The label is ours.** First recorded donation per `DONOR_ID` defines the cohort; a second donation
  within the 12-month window defines the positive class. Only cohorts whose window closes before
  December 2019 are labeled. Train on cohorts through 2016, hold out 2017 and 2018.
- **Possible leakage to check, not assume:** whether `THANK_YOU_PACKET_MAILED` can be recorded after
  a second gift. Verify the timing from the codebook before using it as a feature.
- **Size.** ~13 GB does not fit comfortably on JupyterHub or a laptop in pandas. Plan: stream the
  donations file once to build per-donor cohort tables (`data/processed/`), then work from those.
  If Albert approves, a stratified sample of cohorts is acceptable — say so in the notebook.

### Layout

```
data/
├── raw/         exactly as downloaded, never edited
├── processed/   produced by src/ scripts from raw/ (cohorts, labels, features), reproducible
└── README.md    this file (the only thing in data/ that is committed)
```

Small derived artifacts the evaluation depends on (the held-out cohort labels, the RFM baseline
table) live in `evals/` and **are** committed.

---

### Fallback dataset (not in use): Amazon Reviews 2023

If Albert rejects the direction, the Amazon fallback's fetch recipe is in the git history of this file
(commit `2f90ab1`): per-category files under `raw/` on
https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023, no login; exclude `rating_number`
and `average_rating` from features (2023 outcome snapshots).
