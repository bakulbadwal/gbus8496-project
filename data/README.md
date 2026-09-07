# data/ — gitignored

Raw data never gets committed. This file is the reproducible fetch recipe.

## Dataset: Amazon Reviews 2023 (McAuley Lab, UC San Diego)

- Hub page: https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023
- Public, **not gated, no login needed**. Verified Sep 6, 2026.
- Two files per category under `raw/`: `meta_categories/meta_<Category>.jsonl` (one item per line)
  and `review_categories/<Category>.jsonl` (one review per line).
- Whole dataset is hundreds of GB. **We use two to three categories.** Start with the pilot below;
  add a second category only after the pilot pipeline runs end to end.

### Pilot category: All_Beauty

| File | Size (bytes, from HTTP headers Sep 6) |
|---|---|
| `raw/meta_categories/meta_All_Beauty.jsonl` | 212,990,142 |
| `raw/review_categories/All_Beauty.jsonl` | 326,611,506 |

Candidate second categories (check sizes before pulling; `Video_Games` reviews alone are 2.7 GB):
`Musical_Instruments`, `Software`, `Magazine_Subscriptions`, `Gift_Cards`.

### Fetch

```bash
mkdir -p data/raw
B=https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/resolve/main/raw
curl -L -o data/raw/meta_All_Beauty.jsonl "$B/meta_categories/meta_All_Beauty.jsonl"
curl -L -o data/raw/All_Beauty.jsonl      "$B/review_categories/All_Beauty.jsonl"
ls -l data/raw   # sizes must match the table above
```

### Fields (verified from the first record of each file)

**meta:** `main_category, title, average_rating, rating_number, features, description, price, images,
videos, store, categories, details, parent_asin, bought_together`
**reviews:** `rating, title, text, images, asin, parent_asin, user_id, timestamp (ms since epoch),
helpful_vote, verified_purchase`

### ⚠️ Leakage — read before building features

`rating_number` and `average_rating` in **meta** are **September 2023 snapshots of the outcome**
(total reviews to date, mean rating to date). They are not observable at launch. **Never use them as
features.** The label is built from the **reviews** file: first review timestamp per `parent_asin`,
then the count of reviews in the following 365 days. Only products whose 12-month window closes before
the dataset cutoff are labeled. `price` is also a 2023 snapshot — keep it as a feature but report the
model with price removed as a robustness check.

### Layout

```
data/
├── raw/         exactly as downloaded, never edited
├── processed/   produced by src/ scripts from raw/ (labels, features), reproducible
└── README.md    this file (the only thing in data/ that is committed)
```

Small derived artifacts the evaluation depends on (the labeled test cohort, N-sensitivity table)
live in `evals/` and **are** committed.
