# data/ — gitignored

Raw data never gets committed. This file is the reproducible fetch recipe; update it the moment the
direction is decided.

## Fetch steps (fill in once the dataset is chosen)

```
# example shape — replace with the real commands
# 1. source URL and licence
# 2. exact download command (curl / huggingface-cli / kaggle CLI)
# 3. expected files, sizes, row counts, and a checksum
# 4. any preprocessing script in src/ that turns raw → data/processed/
```

## Layout

```
data/
├── raw/         exactly as downloaded, never edited
├── processed/   produced by src/ scripts from raw/, reproducible
└── README.md    this file (the only thing in data/ that is committed)
```

Small derived artifacts that the evaluation depends on (a gold set, a task list) live in `evals/`
and **are** committed, so the evaluation can be re-run without re-fetching everything.
