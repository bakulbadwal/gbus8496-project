"""
calibration.py — Albert's measurement 2: "how do you know it works, and where does it not?"

Thadeus's lane. It runs on scores files with columns (donor_id, p_return),
so it works today on the reference logistic (data/processed/reference_scores.parquet) and, after
the team signs off and Rodolfo runs `src/model.py --holdout`, on model_scores.parquet with no
change. Extend it, don't fork it.

    python evals/calibration.py data/processed/cohorts.parquet data/processed/reference_scores.parquet
    python evals/calibration.py ... --out docs/slides/assets/slide7_calibration     # also writes the figure

Three questions, in Albert's order:

  1. CALIBRATION — when the model says 20%, do 20% return? Ten quantile bins of predicted
     probability, mean predicted vs observed, plus Brier score and expected calibration error.
     The decision layer (src/decision.py) thresholds on p*, so calibration is not cosmetic: a
     model that ranks well but says 0.30 when it means 0.15 calls three times too many people.

  2. ERROR ANALYSIS BY COHORT YEAR — does 2018 behave like 2017? The reference model found
     repeat rates falling by cohort (coefficient −0.21). Precision at capacity and AUC per year
     show whether the ranking degrades on the most recent donors — the ones she will actually call.

  3. BY FIRST-GIFT SIZE BAND — where is the model weakest? Most citizen donors give $25 or less.
     If precision collapses there, the model is good at the donors she already knew about and
     weak on the ones she needs help with. That sentence, if true, goes on slide 7.

Calibration always checks p_return. List error analysis uses expected_value when supplied,
matching the headline policy, or p_return for the reference model. --ranking makes this explicit.
The score comparison keeps both lists visible. Nothing here refits or tunes the model.
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, roc_auc_score

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "evals"))
import config          # noqa: E402
import score as scorer  # noqa: E402

BANDS = [(0, 10, "<$10"), (10, 25, "$10–24"), (25, 50, "$25–49"), (50, 100, "$50–99"),
         (100, 250, "$100–249"), (250, np.inf, "$250+")]


def load(cohorts_path, scores_path, population=config.STAKEHOLDER_POPULATION):
    c = pd.read_parquet(cohorts_path)
    c = c[c["split"] == "holdout"]
    if population and "donor_type" in c.columns:
        c = c[c["donor_type"] == population]
    s = pd.read_parquet(scores_path)
    columns = ["donor_id", "p_return"] + (["expected_value"] if "expected_value" in s else [])
    df = c.merge(s[columns], on="donor_id", how="left", validate="one_to_one").reset_index(drop=True)
    if df.empty or not np.isfinite(df[columns[1:]].to_numpy(dtype=float)).all():
        raise ValueError("Every holdout donor must have finite scores; missing predictions cannot be dropped.")
    if not df["p_return"].between(0, 1).all():
        raise ValueError("p_return must be between 0 and 1.")
    print(f"Holdout {population or 'all'}: {len(c):,} donors · scored {len(df):,}")
    df["cohort_year"] = df["cohort"].str[:4]
    df["y"] = df["gave_again"].astype(int)
    return df


def calibration_table(df, bins=10):
    df = df.copy()
    df["bin"] = pd.qcut(df["p_return"], q=bins, labels=False, duplicates="drop")
    t = df.groupby("bin").agg(donors=("y", "size"), predicted=("p_return", "mean"),
                              observed=("y", "mean"), p_low=("p_return", "min"),
                              p_high=("p_return", "max"))
    t["gap_pp"] = 100 * (t["observed"] - t["predicted"])
    ece = float((t["donors"] / len(df) * (t["observed"] - t["predicted"]).abs()).sum())
    brier = float(brier_score_loss(df["y"], df["p_return"]))
    base = float(df["y"].mean())
    brier_base = float(((df["y"] - base) ** 2).mean())   # predict the base rate for everyone
    return t, {"ece": ece, "brier": brier, "brier_base_rate": brier_base, "base_rate": base}


def ranking_column(df, ranking="auto"):
    """Use the headline dollar ranking when available; the reference model has probability only."""
    column = ("expected_value" if "expected_value" in df else "p_return") if ranking == "auto" else ranking
    if column not in df:
        raise ValueError(f"Ranking column {column!r} is missing from the scores file.")
    return column


def by_group(df, key, capacity=config.STEWARDSHIP_CAPACITY, ranking="auto"):
    """Per group: size, base rate, AUC, and precision / $ per contact when the capacity ranking
    is applied to the WHOLE holdout (so the group rows show where the list's hits come from)."""
    df = df.reset_index(drop=True)
    top = scorer._top_k_mask(df, df[ranking_column(df, ranking)].values, capacity)
    rows = []
    for g, part in df.groupby(key, observed=True):
        sel = top[part.index.values]
        contacted = part[sel]
        auc = roc_auc_score(part["y"], part["p_return"]) if part["y"].nunique() == 2 else np.nan
        rows.append({
            key: g, "donors": len(part), "share_of_donors": len(part) / len(df),
            "base_rate": part["y"].mean(), "mean_p": part["p_return"].mean(), "auc": auc,
            "contacted": int(sel.sum()), "share_of_list": sel.sum() / top.sum(),
            "repeat_donors_found": int(contacted["y"].sum()),
            "precision": contacted["y"].mean() if len(contacted) else np.nan,
            "value_per_contact": (contacted["second_gift_amount"].sum() / len(contacted)
                                  if len(contacted) else np.nan),
        })
    return pd.DataFrame(rows).set_index(key)


def by_size_band(df, capacity=config.STEWARDSHIP_CAPACITY, ranking="auto"):
    df = df.copy()
    labels = [b[2] for b in BANDS]
    edges = [b[0] for b in BANDS] + [np.inf]
    df["band"] = pd.cut(df["first_gift_amount"], bins=edges, labels=labels, right=False)
    return by_group(df, "band", capacity, ranking)


def pooled_precision(groups):
    """Returners / selected donors across bands; do not give tiny bands equal weight."""
    n = groups["contacted"].sum()
    return float(groups["repeat_donors_found"].sum() / n) if n else np.nan


def compare_rankings(df, capacity=config.STEWARDSHIP_CAPACITY):
    """Keep dollar, probability and gift-size lists explicitly separate, using the shared scorer."""
    rows = []
    for column in ["expected_value", "p_return", "first_gift_amount"]:
        if column not in df:
            continue
        selected = scorer._top_k_mask(df, df[column].values, capacity)
        row = scorer.evaluate_at_capacity(df, df[column].values, capacity)
        row["ranking"] = column
        row["under_50_share_of_list"] = float((selected & (df["first_gift_amount"] < 50)).sum() / selected.sum())
        rows.append(row)
    return pd.DataFrame(rows).set_index("ranking")


def figure(cal, years, out_prefix, dark=False, ranking="p_return"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if dark:   # deck surface; palette validated on the dark surface (see make_charts.py)
        blue, ink, muted, grid, surface = "#3987E5", "#F2EFE6", "#B9B4A6", "#3a4a66", "#14213D"
    else:
        blue, ink, muted, grid, surface = "#2a78d6", "#0b0b0b", "#52514e", "#e1e0d9", "white"
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12, "axes.edgecolor": grid,
                         "axes.labelcolor": muted, "xtick.color": muted, "ytick.color": muted,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "text.color": ink, "axes.facecolor": surface, "figure.facecolor": surface})

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), dpi=200)

    ax = axes[0]
    lim = max(cal["observed"].max(), cal["predicted"].max()) * 1.15
    ax.plot([0, lim], [0, lim], color=grid, lw=1.5, ls="--", zorder=1)
    ax.plot(cal["predicted"], cal["observed"], color=blue, lw=2, marker="o", ms=7,
            markeredgecolor=surface, markeredgewidth=2, zorder=3)
    r = cal.iloc[-1]
    ax.annotate(f"top bin: says {r['predicted']:.0%}, gets {r['observed']:.0%}",
                (r["predicted"], r["observed"]), textcoords="offset points", xytext=(-8, 10),
                ha="right", fontsize=10, color=ink)
    ax.set_xlim(0, lim); ax.set_ylim(0, lim)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.set_xlabel("Predicted probability of a second gift")
    ax.set_ylabel("Observed share who gave again")
    ax.set_title("Calibration — dashed line is perfect", loc="left", color=ink, fontsize=12)
    ax.grid(axis="y", color=grid, lw=0.6); ax.set_axisbelow(True)

    ax = axes[1]
    x = np.arange(len(years))
    bars = ax.bar(x, years["precision"], color=blue, width=0.55, zorder=3)
    ax.plot(x, years["base_rate"], color=muted, lw=1.5, ls="--", marker="o", ms=5, zorder=4)
    for b, v in zip(bars, years["precision"]):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.004, f"{v:.1%}",
                ha="center", va="bottom", fontsize=11, color=ink)
    ax.text(x[-1] + 0.35, years["base_rate"].iloc[-1], "base rate", va="center", fontsize=10, color=muted)
    ax.set_xticks(x, years.index.tolist())
    ax.set_ylim(0, max(years["precision"].max(), years["base_rate"].max()) * 1.25)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.set_ylabel("Precision of the 10% list")
    label = "Dollar-ranked" if ranking == "expected_value" else "Probability-ranked"
    ax.set_title(f"{label} list, by cohort year", loc="left", color=ink, fontsize=12)
    ax.grid(axis="y", color=grid, lw=0.6); ax.set_axisbelow(True)

    fig.tight_layout()
    path = Path(f"{out_prefix}{'_dark' if dark else ''}.png")
    fig.savefig(path, bbox_inches="tight", facecolor=surface)
    plt.close(fig)
    return path


def main(cohorts_path, scores_path, out_prefix=None, ranking="auto"):
    df = load(cohorts_path, scores_path)
    rank_col = ranking_column(df, ranking)
    fmt = lambda v: f"{v:,.4f}"
    print(f"List ranking: {rank_col}. Calibration and AUC always use p_return.")
    print("First-gift size = total first-month giving; outcome dollars = all giving in months M+1..M+12.")

    cal, m = calibration_table(df)
    print(f"\n1 · CALIBRATION (holdout, {len(df):,} donors, base rate {m['base_rate']:.4f})")
    print(cal.to_string(float_format=fmt))
    print(f"\nExpected calibration error (ECE): {m['ece']:.4f}   "
          f"Brier: {m['brier']:.4f} vs {m['brier_base_rate']:.4f} predicting the base rate for everyone "
          f"({100 * (1 - m['brier'] / m['brier_base_rate']):+.2f}% skill)")
    top, bottom = cal.iloc[-1], cal.iloc[0]
    print(f"Top decile says {top['predicted']:.1%}, gets {top['observed']:.1%}; "
          f"bottom decile says {bottom['predicted']:.1%}, gets {bottom['observed']:.1%}.")

    years = by_group(df, "cohort_year", ranking=rank_col)
    print(f"\n2 · ERROR ANALYSIS BY COHORT YEAR (10% list within cohort month; ranking = {rank_col})")
    print(years.to_string(float_format=fmt))
    if len(years) > 1:
        d = years["precision"].iloc[-1] - years["precision"].iloc[0]
        print(f"Precision {years.index[0]} → {years.index[-1]}: {d * 100:+.2f} pp; "
              f"base rate moved {(years['base_rate'].iloc[-1] - years['base_rate'].iloc[0]) * 100:+.2f} pp.")

    bands = by_size_band(df, ranking=rank_col)
    print(f"\n3 · BY FIRST-GIFT SIZE BAND — share of donors vs share of the list, and how each does")
    print(bands.to_string(float_format=fmt))
    small = bands.loc[["<$10", "$10–24", "$25–49"]]
    print(f"Donors giving under $50 are {small['share_of_donors'].sum():.1%} of the holdout and "
          f"{small['share_of_list'].sum():.2%} of the list; their precision on the list is "
          f"{pooled_precision(small):.1%} vs {pooled_precision(bands.loc[['$100–249', '$250+']]):.1%} "
          f"for $100+.")

    print("\n4 · SAME CAPACITY, DIFFERENT LISTS (value identified, not caused)")
    print(compare_rankings(df).to_string(float_format=fmt))
    print("\nGift-size baseline by year:")
    print(by_group(df, "cohort_year", ranking="first_gift_amount").to_string(float_format=fmt))

    if "expected_value" in df:
        keep = df["second_gift_count"] < 200
        print(f"\n5 · ROBUSTNESS: excluding {(~keep).sum():,} accounts with 200+ subsequent gifts")
        print(compare_rankings(df.loc[keep].reset_index(drop=True)).to_string(float_format=fmt))
        print(f"\nDollar-score check: mean predicted ${df['expected_value'].mean():.2f} vs "
              f"observed ${df['second_gift_amount'].mean():.2f} per donor.")
        print("The log-amount model gives a ranking score, not a calibrated mean-dollar forecast. "
              "Cost thresholds are illustrative; no outreach profit or causal uplift is established.")

    if out_prefix:
        for dark in (False, True):
            print(f"figure → {figure(cal, years, out_prefix, dark=dark, ranking=rank_col)}")
    return cal, years, bands


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cohorts")
    ap.add_argument("scores", help="parquet with donor_id, p_return (reference_scores or model_scores)")
    ap.add_argument("--out", default=None, help="figure path prefix, e.g. docs/slides/assets/slide7_calibration")
    ap.add_argument("--ranking", choices=["auto", "expected_value", "p_return"], default="auto",
                    help="list for error analysis; auto uses expected_value if present, otherwise p_return")
    a = ap.parse_args()
    main(a.cohorts, a.scores, a.out, a.ranking)
