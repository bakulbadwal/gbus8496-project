"""
model.py — Rodolfo's workstream: the model that has to earn its place against $116/contact.

WHAT THIS IS
------------
Two gradient-boosted models on features knowable the day of the first gift:

  1. P(return)  — HistGradientBoostingClassifier on the 12-month second-gift label.
  2. E[amount | return] — HistGradientBoostingRegressor on log(second gift amount), fit on
     returners only. Albert pre-approved the cohort median as a start and named "a regression on
     the log of the amount" as the upgrade; this is that upgrade.

Two rankings go through the shared scorer (evals/score.py), against the shared baseline ladder:

  model_p_return        rank by P(return)              — finds *people* who come back
  model_expected_value  rank by P(return) × E[amount]  — finds *dollars* that come back

The distinction matters because the headline metric is dollars per contact, and the reference
logistic showed a pure-probability ranking barely moves that number: gift size predicts the SIZE
of the second gift more than the FACT of it (Reid's finding). Ranking by expected value is the
honest way to compete with "rank by first gift size" on its own turf.

WHY GRADIENT BOOSTING AND NOT MORE LOGISTIC REGRESSION
------------------------------------------------------
Reid's exploration found the signal in *interactions*: state × gift decile, subject × gift decile,
grade × gift decile. A linear model needs those crosses hand-built (thousands of columns, chosen by
us, a tuning surface we could overfit); trees learn them from the marginal columns directly. It is
also the cheapest credible step up from the reference logistic — no new dependency, scikit-learn
only, per the repo rule about not adding tooling nobody asked for.

THE HOLDOUT IS NOT TOUCHED HERE — read this before running
----------------------------------------------------------
Development happens entirely inside the TRAIN split, re-split by time exactly the way the real
split was made (per AGENTS.md: "validation that transfers"):

  dev-train    cohorts ..2015-12      fit models here
  dev-val      cohorts 2016-01..12    the last pre-holdout year; every development number
                                      comes from here, through the same scorer as everything else

`python src/model.py <cohorts_with_projects.parquet>` runs ONLY that loop. Scoring the real
holdout requires `--holdout`, is meant to be run ONCE after the team agrees the model is final,
refits on the full train split, and writes model_scores.parquet for Malorie's decision layer and
Thadeus's calibration work. That gate is the whole reason this file exists as a script and not a
notebook cell.

LEAKAGE RULES (same as the reference model, plus Reid's)
--------------------------------------------------------
  • THANK_YOU_PACKET_MAILED excluded — codebook gives no timing; Albert pre-approved dropping it.
  • TEACHER_ID excluded — memorization, not generalization (Reid's call, kept).
  • No post-outcome project fields — only what is visible when the first gift lands.
  • The amount model is fit on dev-train returners only; dev-val amounts are never seen in fitting.

    python src/model.py data/processed/cohorts_with_projects.parquet             # development
    python src/model.py data/processed/cohorts_with_projects.parquet --holdout   # ONCE, at the end
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.preprocessing import OrdinalEncoder

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "evals"))
import score as scorer  # noqa: E402
import baselines        # noqa: E402

# ── Features ─────────────────────────────────────────────────────────────────────────────────────
# Donations-file features: identical to the reference model, so any gain over it is attributable
# to (a) the model class and (b) the projects join, not to a quietly different feature set.
FLAGS = ["first_matched", "first_teacher_referred", "first_gift_card"]  # thank-you packet excluded

# Projects-join features (Reid's columns, notebook 02). Present only in cohorts_with_projects.parquet;
# the code degrades gracefully to donations-only if they are absent, and says so.
PROJECT_NUMERIC = [
    "COST_OF_REQUESTED_RESOURCES", "TOTAL_PRICE_EXCLUDING_OPTIONAL_1",
    "SCHOOL_PERCENTAGE_FREE_AND_RED_1", "STUDENTS_REACHED",
]
PROJECT_CATEGORICAL = [
    "GRADE_LEVEL", "SUBJECT_CATEGORY", "SUBJECT_SUBCATEGORY", "CATEGORY", "SCHOOL_STATE",
]
MAX_CARDINALITY = 200   # HistGB native-categorical bin limit is 255; anything wilder becomes NaN

RANDOM_STATE = 8496     # the course number, same convention as Reid's sample seed


def month_str_to_index(s):
    """'2016-12' → months since 2000-01, the unit cohort_month is stored in (labels.py)."""
    y, m = s.split("-")
    return (int(y) - 2000) * 12 + int(m) - 1


def design_matrix(df):
    """Feature frame + boolean mask of which columns are categorical. Knowable-at-first-gift only."""
    X = pd.DataFrame(index=df.index)
    cat = []

    # ── donations file ──
    X["log_amount"] = np.log1p(df["first_gift_amount"].clip(lower=0))
    X["first_month_gifts"] = df["first_month_gifts"].astype(float)
    for f in FLAGS:
        X[f] = df[f].astype(float) if f in df.columns else 0.0
    X["month_of_year"] = (df["cohort_month"] % 12).astype(float)        # seasonality
    X["cohort_year"] = (df["cohort_month"] // 12).astype(float)         # drift (reference found −0.21)
    cat += [False] * len(X.columns)

    # ── projects join ──
    have_projects = all(c in df.columns for c in PROJECT_CATEGORICAL)
    if have_projects:
        for c in PROJECT_NUMERIC:
            if c in df.columns:
                X[c] = pd.to_numeric(df[c], errors="coerce")
                cat.append(False)
        X["log_project_cost"] = np.log1p(
            pd.to_numeric(df.get("COST_OF_REQUESTED_RESOURCES"), errors="coerce").clip(lower=0))
        cat.append(False)
        if "POSTED_MONTH" in df.columns:
            posted = pd.to_datetime(df["POSTED_MONTH"], errors="coerce")
            posted_idx = (posted.dt.year - 2000) * 12 + posted.dt.month - 1
            X["project_age_months"] = (df["cohort_month"] - posted_idx).clip(lower=0, upper=60)
            cat.append(False)
        for c in PROJECT_CATEGORICAL:
            col = df[c].astype("string")
            if col.nunique(dropna=True) > MAX_CARDINALITY:               # safety, not expected
                col = pd.Series(pd.NA, index=df.index, dtype="string")
            X[c] = col
            cat.append(True)
        if "project_record_missing" in df.columns:
            X["project_record_missing"] = df["project_record_missing"].astype(float)
            cat.append(False)
    return X, np.array(cat, dtype=bool), have_projects


def _encode(X_train, cat_mask, *others):
    """Ordinal-encode categoricals fit on TRAIN only; unseen categories at predict time → NaN,
    which HistGB treats as missing. Version-portable (no reliance on from_dtype)."""
    cat_cols = list(X_train.columns[cat_mask])
    if not cat_cols:
        return [X_train.astype(float).values] + [o.astype(float).values for o in others]
    enc = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=np.nan,
                         encoded_missing_value=np.nan)
    out = []
    for frame in (X_train, *others):
        f = frame.copy()
        vals = enc.fit_transform(f[cat_cols]) if frame is X_train else enc.transform(f[cat_cols])
        f[cat_cols] = vals
        out.append(f.astype(float).values)
    return out


def fit_models(train, cat_mask_from=None):
    """Fit classifier + amount regressor on `train`. Returns (clf, reg, encoder-closure)."""
    X, cat_mask, have_projects = design_matrix(train)
    y = train["gave_again"].astype(int).values

    cat_cols = list(X.columns[cat_mask])
    enc = None
    Xv = X.copy()
    if cat_cols:
        enc = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=np.nan,
                             encoded_missing_value=np.nan)
        Xv[cat_cols] = enc.fit_transform(Xv[cat_cols])
    Xv = Xv.astype(float).values

    # Defaults deliberately conservative; the one knob raised is max_iter with early stopping on an
    # internal 10% validation slice, so "tuning" is bounded and reproducible.
    clf = HistGradientBoostingClassifier(
        max_iter=500, learning_rate=0.06, max_leaf_nodes=63, min_samples_leaf=200,
        l2_regularization=1.0, early_stopping=True, validation_fraction=0.10,
        categorical_features=cat_mask if cat_cols else None, random_state=RANDOM_STATE)
    clf.fit(Xv, y)

    ret = train["gave_again"].astype(bool).values
    reg = HistGradientBoostingRegressor(
        max_iter=400, learning_rate=0.06, max_leaf_nodes=63, min_samples_leaf=200,
        l2_regularization=1.0, early_stopping=True, validation_fraction=0.10,
        categorical_features=cat_mask if cat_cols else None, random_state=RANDOM_STATE)
    reg.fit(Xv[ret], np.log1p(train.loc[ret, "second_gift_amount"].clip(lower=0).values))

    def predict(frame):
        Xp, _, _ = design_matrix(frame)
        Xp = Xp.reindex(columns=X.columns)
        if cat_cols:
            Xp[cat_cols] = enc.transform(Xp[cat_cols].astype("string"))
        Xp = Xp.astype(float).values
        p = clf.predict_proba(Xp)[:, 1]
        ev = p * np.expm1(reg.predict(Xp))          # rank score, monotone in expected dollars
        return p, ev

    return clf, reg, predict, have_projects, X.columns


def bootstrap_noise_floor(frame, score_dict, capacity, n_boot=30, seed=RANDOM_STATE):
    """Std. error of value_per_contact per ranking, by resampling donors (AGENTS: report the
    noise floor next to any leaderboard-style number)."""
    rng = np.random.default_rng(seed)
    n = len(frame)
    stats = {name: [] for name in score_dict}
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        boot = frame.iloc[idx].reset_index(drop=True)
        for name, s in score_dict.items():
            r = scorer.evaluate_at_capacity(boot, np.asarray(s)[idx], capacity)
            stats[name].append(r["value_per_contact"])
    return {name: (float(np.mean(v)), float(np.std(v, ddof=1))) for name, v in stats.items()}


def run(cohorts_path, holdout=False, out_path=None):
    cohorts = pd.read_parquet(cohorts_path)
    pop = config.STAKEHOLDER_POPULATION
    if pop and "donor_type" in cohorts.columns:
        cohorts = cohorts[cohorts["donor_type"] == pop]
    train = cohorts[cohorts["split"] == "train"].reset_index(drop=True)

    if not holdout:
        # ── development loop: train split only, re-split by time ──
        dev_val_start = month_str_to_index(config.TRAIN_COHORT_END) - 11     # last 12 train months
        dev_train = train[train["cohort_month"] < dev_val_start].reset_index(drop=True)
        dev_val = train[train["cohort_month"] >= dev_val_start].reset_index(drop=True)
        eval_name, fit_frame, eval_frame = "dev-val (last pre-holdout year)", dev_train, dev_val
    else:
        print("🔴 HOLDOUT RUN. This is meant to happen once, after the team signed off in chat.")
        fit_frame = train
        eval_frame = cohorts[cohorts["split"] == "holdout"].reset_index(drop=True)
        eval_name = "HOLDOUT"

    print(f"Population: {pop or 'all'} · fit {len(fit_frame):,} · evaluate on {eval_name} "
          f"{len(eval_frame):,} · base rate {eval_frame['gave_again'].mean():.4f}")

    clf, reg, predict, have_projects, feat_cols = fit_models(fit_frame)
    if not have_projects:
        print("⚠️  Projects columns not found — running on donations-only features. For the real "
              "result this must be cohorts_with_projects.parquet (Reid's notebook 02 output).")
    print(f"Features ({len(feat_cols)}): {', '.join(feat_cols)}")
    print(f"Boosting iterations used: clf {clf.n_iter_}, amount-reg {reg.n_iter_} (early stopping)")

    p, ev = predict(eval_frame)
    y = eval_frame["gave_again"].values
    print(f"\n{eval_name} ROC-AUC {roc_auc_score(y, p):.4f} · PR-AUC "
          f"{average_precision_score(y, p):.4f}   (reference logistic on holdout was 0.578)")

    rankings = baselines.score_all_baselines(eval_frame)
    rankings["model_p_return"] = p
    rankings["model_expected_value"] = ev
    table = scorer.compare(eval_frame, rankings)

    at = table[table["capacity"] == config.STEWARDSHIP_CAPACITY].sort_values(
        "value_per_contact", ascending=False)
    print(f"\nAt {config.STEWARDSHIP_CAPACITY:.0%} capacity, on {eval_name}:")
    print(at[["ranking", "precision", "recall", "value_capture_rate", "value_per_contact"]]
          .to_string(index=False, float_format=lambda v: f"{v:,.4f}"))

    floor = bootstrap_noise_floor(
        eval_frame, {k: rankings[k] for k in ("model_expected_value", "model_p_return", "gift_amount")},
        config.STEWARDSHIP_CAPACITY)
    print("\nNoise floor (bootstrap over donors, value per contact ± 1 SE):")
    for name, (m, se) in floor.items():
        print(f"  {name:22s} ${m:8,.2f} ± {se:,.2f}")

    best = at.iloc[0]
    amt = at[at.ranking == "gift_amount"].iloc[0]
    mev = at[at.ranking == "model_expected_value"].iloc[0]
    diff = mev["value_per_contact"] - amt["value_per_contact"]
    se = float(np.hypot(floor["model_expected_value"][1], floor["gift_amount"][1]))
    print(f"\nVerdict on {eval_name}: model_expected_value vs gift_amount = "
          f"${mev['value_per_contact']:,.0f} vs ${amt['value_per_contact']:,.0f} "
          f"(Δ ${diff:+,.0f}, ~{abs(diff)/se:.1f}× the combined SE). Best ranking: {best['ranking']}.")
    if not holdout:
        print("Nothing here touched the holdout. When the team signs off, run once with --holdout.")

    if holdout:
        out = Path(out_path or Path(cohorts_path).parent / "model_scores.parquet")
        pd.DataFrame({"donor_id": eval_frame["donor_id"], "p_return": p,
                      "expected_value": ev}).to_parquet(out, index=False)
        print(f"\nHoldout scores written to {out} — replaces reference_scores.parquet for "
              f"src/decision.py (Malorie) and calibration (Thadeus).")
    return table


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cohorts", help="data/processed/cohorts_with_projects.parquet")
    ap.add_argument("--holdout", action="store_true",
                    help="score the real holdout ONCE, after team sign-off, and write model_scores.parquet")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    run(a.cohorts, holdout=a.holdout, out_path=a.out)
