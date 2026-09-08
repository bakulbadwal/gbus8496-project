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

### Files we use

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
