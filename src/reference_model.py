"""
reference_model.py — the deliberately simple model that any real model has to beat.

This is NOT the modelling workstream. Rodolfo owns the model. This file exists for two reasons:

  1. The skeleton promised "a deliberately dumb logistic regression so the pipeline runs end to
     end", and until now the scorer had only rule-based baselines to compare. Now the model path
     through evals/score.py is exercised and the numbers it produces are on record.
  2. It answers a question Rodolfo should know the answer to before spending a week: is there any
     signal in the first-gift attributes BEYOND gift size? If a logistic regression on five flags
     cannot beat "rank by amount", the feature work has to come from the projects join, not from
     the donations file.

What it uses — only what is knowable the day of the first gift:
  log first-gift amount · number of gifts in the first checkout · matched · teacher-referred ·
  campaign gift card · month of year of the first gift (seasonality) · cohort year (drift).

What it deliberately leaves out: THANK_YOU_PACKET_MAILED. The codebook gives no timing for that
flag, so it may record something that happened after the second gift. Albert pre-approved dropping
it; it is excluded here so the reference number cannot be inflated by leakage.

The holdout is scored exactly once, here, to produce a fixed reference. Nothing is tuned.

    python src/reference_model.py data/processed/cohorts.parquet
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

FLAGS = ["first_matched", "first_teacher_referred", "first_gift_card"]   # thank-you packet excluded on purpose


def design_matrix(df):
    """Features knowable at first gift. Returns (X, column names)."""
    X = pd.DataFrame(index=df.index)
    X["log_amount"] = np.log1p(df["first_gift_amount"].clip(lower=0))
    X["first_month_gifts"] = df["first_month_gifts"].astype(float)
    for f in FLAGS:
        X[f] = df[f].astype(float) if f in df.columns else 0.0
    moy = (df["cohort_month"] % 12).astype(int)
    for m in range(1, 12):                                   # 11 dummies, January is the base
        X[f"moy_{m:02d}"] = (moy == m).astype(float)
    X["cohort_year"] = (df["cohort_month"] // 12 + 2000 - 2010).astype(float)   # centred on 2010
    return X, list(X.columns)


def fit_reference(train):
    X, cols = design_matrix(train)
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, C=1.0))
    model.fit(X.values, train["gave_again"].values)
    return model, cols


def main(cohorts_path, out_path=None):
    cohorts = pd.read_parquet(cohorts_path)
    pop = config.STAKEHOLDER_POPULATION
    if pop and "donor_type" in cohorts.columns:
        cohorts = cohorts[cohorts["donor_type"] == pop]
    train = cohorts[cohorts["split"] == "train"].reset_index(drop=True)
    hold = cohorts[cohorts["split"] == "holdout"].reset_index(drop=True)
    print(f"Population: {pop or 'all'} · train {len(train):,} · holdout {len(hold):,}")

    model, cols = fit_reference(train)
    Xh, _ = design_matrix(hold)
    p = model.predict_proba(Xh.values)[:, 1]

    # Coefficients, standardised, so the direction and rough size of each effect is readable.
    coefs = pd.Series(model.named_steps["logisticregression"].coef_[0], index=cols)
    print("\nStandardised coefficients (holdout untouched during fitting):")
    print(coefs.reindex(coefs.abs().sort_values(ascending=False).index).head(8).to_string(float_format=lambda v: f"{v:+.3f}"))

    y = hold["gave_again"].values
    print(f"\nHoldout ROC-AUC {roc_auc_score(y, p):.4f} · PR-AUC {average_precision_score(y, p):.4f} · "
          f"base rate {y.mean():.4f}")

    # The comparison that matters: through the same scorer as everything else.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "evals"))
    import baselines, score  # noqa: E402
    scores = baselines.score_all_baselines(hold)
    scores["reference_logistic"] = p
    table = score.compare(hold, scores)
    at = table[table["capacity"] == config.STEWARDSHIP_CAPACITY].sort_values("value_per_contact", ascending=False)
    print(f"\nAt {config.STEWARDSHIP_CAPACITY:.0%} capacity:")
    print(at[["ranking", "precision", "recall", "value_capture_rate", "value_per_contact"]]
          .to_string(index=False, float_format=lambda v: f"{v:,.4f}"))

    ref = at[at.ranking == "reference_logistic"].iloc[0]
    amt = at[at.ranking == "gift_amount"].iloc[0]
    verdict = ("beats" if ref["value_per_contact"] > amt["value_per_contact"] else "does NOT beat")
    print(f"\nVerdict: the reference logistic {verdict} rank-by-gift-size on dollars per contact "
          f"(${ref['value_per_contact']:,.0f} vs ${amt['value_per_contact']:,.0f}); "
          f"precision {ref['precision']:.1%} vs {amt['precision']:.1%}.")

    out = Path(out_path or Path(cohorts_path).parent / "reference_scores.parquet")
    pd.DataFrame({"donor_id": hold["donor_id"], "p_return": p}).to_parquet(out, index=False)
    print(f"Holdout scores written to {out} — the decision layer reads these until a real model replaces them.")
    return table


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
