"""
calibration.py — Albert's measurement 2: "how do you know it works, and where does it not?"

Thadeus's lane. This is the floor: it runs on ANY scores file with columns (donor_id, p_return),
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

The scores file is holdout predictions that already exist; nothing here refits anything, so the
holdout is read, not re-touched.
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
    df = c.merge(s[["donor_id", "p_return"]], on="donor_id", how="inner").reset_index(drop=True)
    missing = len(c) - len(df)
    print(f"Holdout {population or 'all'}: {len(c):,} donors · scored {len(df):,}"
          + (f" · ⚠️ {missing:,} unscored (dropped)" if missing else ""))
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


def by_group(df, key, capacity=config.STEWARDSHIP_CAPACITY):
    """Per group: size, base rate, AUC, and precision / $ per contact when the capacity ranking
    is applied to the WHOLE holdout (so the group rows show where the list's hits come from)."""
    top = scorer._top_k_mask(df, df["p_return"].values, capacity)
    rows = []
    for g, part in df.groupby(key, observed=True):
        sel = top[part.index.values]
        contacted = part[sel]
        auc = roc_auc_score(part["y"], part["p_return"]) if part["y"].nunique() == 2 else np.nan
        rows.append({
            key: g, "donors": len(part), "share_of_donors": len(part) / len(df),
            "base_rate": part["y"].mean(), "mean_p": part["p_return"].mean(), "auc": auc,
            "contacted": int(sel.sum()), "share_of_list": sel.sum() / top.sum(),
            "precision": contacted["y"].mean() if len(contacted) else np.nan,
            "value_per_contact": (contacted["second_gift_amount"].sum() / len(contacted)
                                  if len(contacted) else np.nan),
        })
    return pd.DataFrame(rows).set_index(key)


def by_size_band(df, capacity=config.STEWARDSHIP_CAPACITY):
    df = df.copy()
    labels = [b[2] for b in BANDS]
    edges = [b[0] for b in BANDS] + [np.inf]
    df["band"] = pd.cut(df["first_gift_amount"], bins=edges, labels=labels, right=False)
    return by_group(df, "band", capacity)


def figure(cal, years, out_prefix, dark=False):
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
    ax.set_title("Precision at capacity, by cohort year", loc="left", color=ink, fontsize=12)
    ax.grid(axis="y", color=grid, lw=0.6); ax.set_axisbelow(True)

    fig.tight_layout()
    path = Path(f"{out_prefix}{'_dark' if dark else ''}.png")
    fig.savefig(path, bbox_inches="tight", facecolor=surface)
    plt.close(fig)
    return path


def main(cohorts_path, scores_path, out_prefix=None):
    df = load(cohorts_path, scores_path)
    fmt = lambda v: f"{v:,.4f}"

    cal, m = calibration_table(df)
    print(f"\n1 · CALIBRATION (holdout, {len(df):,} donors, base rate {m['base_rate']:.4f})")
    print(cal.to_string(float_format=fmt))
    print(f"\nExpected calibration error (ECE): {m['ece']:.4f}   "
          f"Brier: {m['brier']:.4f} vs {m['brier_base_rate']:.4f} predicting the base rate for everyone "
          f"({100 * (1 - m['brier'] / m['brier_base_rate']):+.2f}% skill)")
    top, bottom = cal.iloc[-1], cal.iloc[0]
    print(f"Top decile says {top['predicted']:.1%}, gets {top['observed']:.1%}; "
          f"bottom decile says {bottom['predicted']:.1%}, gets {bottom['observed']:.1%}.")

    years = by_group(df, "cohort_year")
    print(f"\n2 · ERROR ANALYSIS BY COHORT YEAR (10% list built within cohort month)")
    print(years.to_string(float_format=fmt))
    if len(years) > 1:
        d = years["precision"].iloc[-1] - years["precision"].iloc[0]
        print(f"Precision {years.index[0]} → {years.index[-1]}: {d * 100:+.2f} pp; "
              f"base rate moved {(years['base_rate'].iloc[-1] - years['base_rate'].iloc[0]) * 100:+.2f} pp.")

    bands = by_size_band(df)
    print(f"\n3 · BY FIRST-GIFT SIZE BAND — share of donors vs share of the list, and how each does")
    print(bands.to_string(float_format=fmt))
    small = bands.loc[["<$10", "$10–24", "$25–49"]]
    print(f"Donors giving under $50 are {small['share_of_donors'].sum():.1%} of the holdout and "
          f"{small['share_of_list'].sum():.1%} of the list; their precision on the list is "
          f"{np.nanmean(small['precision']):.1%} vs {np.nanmean(bands.loc[['$100–249', '$250+'], 'precision']):.1%} "
          f"for $100+.")

    if out_prefix:
        for dark in (False, True):
            print(f"figure → {figure(cal, years, out_prefix, dark=dark)}")
    return cal, years, bands


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cohorts")
    ap.add_argument("scores", help="parquet with donor_id, p_return (reference_scores or model_scores)")
    ap.add_argument("--out", default=None, help="figure path prefix, e.g. docs/slides/assets/slide7_calibration")
    a = ap.parse_args()
    main(a.cohorts, a.scores, a.out)
