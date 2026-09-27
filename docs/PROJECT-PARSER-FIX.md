# Projects parser correction — September 27, 2026

## What went wrong

The Projects export is a tab-separated file. Quotation marks in project titles are literal
text, but our reader used pandas' default CSV quotation rules. An opening quote could make
the reader treat following lines as part of the same field until another quote appeared.
Rows then disappeared or fields were attached to the wrong project. Asking pandas to read
only selected columns did not help: it still parsed the title while finding column boundaries.

The source data were intact. The shared `src/projects.py` reader explicitly uses
`quoting=csv.QUOTE_NONE`. The feature join, same-teacher analysis, packet exploration and
feature notebook now use it. The missing-project indicator remains as a future safeguard.

## Verified scope

The source file matches the ICPSR manifest MD5 `37e7bd5ac4af5b71545fc6538c5be3dd`.
An independent physical-line check finds exactly 2,149,817 data rows, each with 28 fields.
See `evals/results/project_parser_audit.json` and `evals/audit_project_parser.py`.

| Check | Old reader | Correct reader |
|---|---:|---:|
| Projects read | 2,144,304 | 2,149,817 |
| Donor-cohort rows without a matching project | 8,432 | 0 |
| Citizen-donor rows without a matching project | 7,651 | 0 |
| Existing project IDs with wrongly read feature fields | 121 | 0 |

The 121 incorrectly read existing records affected another 214 donor rows. Thus this was
more than a cosmetic missing-data flag. All 3,277,153 donor rows now match. A direct equality
check of the rebuilt and previous donation-label tables passed: cohort membership, outcomes,
splits and gift-size baseline inputs did not change.

## Effect on the headline

Model features, hyperparameters, seeds, train/validation dates and monthly capacity are unchanged.
The model was retrained because its inputs changed; this is not another round of model selection
on the holdout. Different data can change tree splits and the iteration chosen by existing early
stopping, and therefore predictions for many donors, including those whose own fields did not change.

| Holdout, 10% monthly capacity | Previous saved result | Old inputs, current environment | Corrected inputs, current environment |
|---|---:|---:|---:|
| Model value identified per contact | $120.09 | $119.98 | **$119.71** |
| Gift-size baseline per contact | $116.26 | $116.26 | **$116.26** |
| Model advantage per contact | $3.83 | $3.72 | **$3.45** |
| Paired bootstrap advantage, mean ± 1 SE | $3.80 ± $0.51 | $3.62 ± $0.47 | **$3.51 ± $0.51** |

The controlled comparison attributes a $0.27/contact reduction to the changed inputs in this
environment. The additional $0.11 difference from the saved result was already present when
rerunning the old inputs; its precise runtime cause has not been established. The repository's
requirements were unpinned, so we retain the environment versions and the old-input rerun rather
than claiming the entire $0.38 saved-to-current change comes from the parser.

The corrected model still identifies about 58% of subsequent giving while selecting 10% of
donors, and still beats gift size in both holdout years. The paired donor bootstrap supports
a modest historical advantage; it does not measure training uncertainty or future drift.
7,162 of the 81,509 contact-list members change in the controlled before/after comparison.
The list must therefore be regenerated even though the rounded $120-versus-$116 headline survives.

At the assumed $25/contact cost, historical giving identified less contact costs changes from
$7.75M to $7.72M, versus the unchanged $7.44M gift-size comparison. This is not outreach profit:
we still do not know how much additional giving a call causes. The recommendation remains a
randomized outreach pilot, with no change to the limits on causal claims or thank-you timing.

Sources: `10_model_holdout.txt`, `11_decision_model.txt`, `12_calibration_model.txt`,
`parser_before_model_same_environment.txt`, `parser_fix_comparison.json`, and
`parser_fix_environment.json`, all in `evals/results/`.

## Main deliverables

- **Notebooks 02–04:** corrected join and feature exploration; rerun model development,
  permutation importance and holdout evaluation outputs. Notebook 01's label logic is unchanged;
  the full pipeline reruns it through the shared label builder.
- **Presentation:** refresh slides 6–8, the calibration images, presenter notes, editable deck,
  deck preview and maintained slide source. Existing unfinished slides remain team work.
- **Executive summary:** refresh model, calibration, coverage and illustrative cost figures in
  both Markdown and PDF. The main recommendation is unchanged.
- **Supporting evidence:** refresh feature tables, model/packet sensitivity logs, teacher and
  capacity analyses, and the example Monday contact list. Remove the false claim that unmatched
  projects are an ICPSR coverage gap.

The existing final feature tables lacked a complete rebuild path. `refresh_feature_tables.py`
now recomputes their fixed comparison inventory, recorded from main at `0778343`. It reproduces
all 1,291 old rate comparisons and 1,228 old amount comparisons on old inputs (counts and rates
exact; floating statistics within 1e-7). With corrected inputs, 1,264 and 1,204 nonempty comparisons
remain. Empty missing-project groups disappear. Ambiguous gift-decile True/False labels in the
amount table are resolved to their original bins using unchanged group counts. No new feature
screening or model selection is introduced by this table rebuild.

## Reproduce

With the ICPSR files installed per `data/README.md`:

```bash
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4
python -m pytest tests/ -q
python evals/run_all.py
```

The full command includes the raw-file audit and feature-table rebuild. Execute notebooks
02, 03 and 04 in order afterward to refresh their saved outputs; notebook 04 reads the frozen
holdout predictions. The table CSVs in `docs/` are regenerated, not manually edited.

For an optional controlled old/new comparison, keep the same Python environment and labels:

```bash
git show 0778343:src/features.py > /tmp/group11-features-before.py
PYTHONPATH=src python /tmp/group11-features-before.py data/processed/cohorts.parquet data/raw/ICPSR_37898/DS0003/37898-0003-Data.tsv /tmp/group11-features-before.parquet
python src/model.py /tmp/group11-features-before.parquet --holdout --out /tmp/group11-scores-before.parquet
python evals/compare_parser_runs.py /tmp/group11-scores-before.parquet data/processed/model_scores.parquet
```

`--published path/to/saved/model_scores.parquet` optionally adds the previously published scores.
This comparison reports changes; it must not be used to select new model settings.

## Cost and review

The correction adds no external API calls or per-donor scoring charge. It requires one rebuild
and retraining using the existing local pipeline; the source checksum/physical-row audit also
reads the Projects file. Staff contact cost assumptions remain unchanged. Four regression cases
cover literal quotes, ignored title columns, chunk boundaries and missing values. A teammate
should review the shared reader, audit counts and headline comparison before merging.
