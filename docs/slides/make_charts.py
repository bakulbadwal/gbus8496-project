"""
make_charts.py — the two figures on Bakul's slides, produced from the data, not typed in.

    python docs/slides/make_charts.py

Writes docs/slides/assets/donations_per_donor.png   (slide 2: 71% never come back)
       docs/slides/assets/donor_type_shares.png     (slide 4: three populations, not one)

Both recompute from the files on disk so the numbers on the slide are traceable. The first needs
one streaming pass over the donations file (~3 min); the second reads the cohort table.

Style follows the repo's chart rules: one hue for magnitude, two fixed hues for the two-series
comparison, thin bars, direct labels, no gridlines fighting the marks, text in ink not in color.
"""

import sys
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "src"))
import labels  # noqa: E402

DONATIONS = REPO / "data" / "raw" / "ICPSR_37898" / "DS0001" / "37898-0001-Data.tsv"
COHORTS = REPO / "data" / "processed" / "cohorts.parquet"
OUT = REPO / "docs" / "slides" / "assets"
OUT.mkdir(parents=True, exist_ok=True)

BLUE, ORANGE = "#2a78d6", "#eb6834"     # categorical slots 1 and 2, fixed order
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e1e0d9"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12, "axes.edgecolor": GRID,
                     "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.spines.top": False, "axes.spines.right": False})


def chart_donations_per_donor():
    """How many times each donor ever gave. Streams the raw file; counts per donor id."""
    sep = labels.detect_sep(DONATIONS)
    counts = Counter()
    for chunk in pd.read_csv(DONATIONS, sep=sep, usecols=["DONOR_ID"], chunksize=1_000_000, dtype=str):
        counts.update(chunk["DONOR_ID"].dropna().values)
    n = len(counts)
    buckets = Counter()
    for v in counts.values():
        buckets["1" if v == 1 else "2" if v == 2 else "3–5" if v <= 5 else "6–20" if v <= 20 else "21+"] += 1
    order = ["1", "2", "3–5", "6–20", "21+"]
    shares = [buckets[k] / n for k in order]

    fig, ax = plt.subplots(figsize=(9, 4.6), dpi=200)
    bars = ax.bar(order, shares, color=BLUE, width=0.58)
    for b, s in zip(bars, shares):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.012, f"{s:.1%}",
                ha="center", va="bottom", color=INK, fontsize=13, fontweight="bold" if s == max(shares) else "normal")
    ax.set_ylim(0, max(shares) * 1.18)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Lifetime gifts per donor", labelpad=8)
    ax.set_title(f"{shares[0]:.0%} of DonorsChoose donors gave once and never again",
                 loc="left", color=INK, fontsize=15, fontweight="bold", pad=14)
    ax.text(0, 1.0, f"{n:,} donors · 2002–2019 · ICPSR 37898", transform=ax.transAxes,
            color=MUTED, fontsize=10, va="bottom")
    fig.tight_layout()
    fig.savefig(OUT / "donations_per_donor.png", bbox_inches="tight", facecolor="white")
    print(f"donations_per_donor.png  ({n:,} donors; once-only = {shares[0]:.1%})")


def chart_donor_type_shares():
    """Share of donors vs share of subsequent dollars, by donor type. Holdout cohorts."""
    c = pd.read_parquet(COHORTS)
    h = c[c["split"] == "holdout"]
    g = h.groupby("donor_type").agg(donors=("donor_id", "size"), value=("second_gift_amount", "sum"))
    g["donor_share"] = g["donors"] / g["donors"].sum()
    g["value_share"] = g["value"] / g["value"].sum()
    order = ["citizen donor", "teacher", "organization"]
    g = g.loc[order]
    labels_x = ["Citizen donors", "Teachers", "Organizations"]

    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=200)
    x = range(len(order)); w = 0.36
    b1 = ax.bar([i - w / 2 - 0.01 for i in x], g["donor_share"], w, color=BLUE, label="Share of donors")
    b2 = ax.bar([i + w / 2 + 0.01 for i in x], g["value_share"], w, color=ORANGE, label="Share of repeat dollars")
    for bars in (b1, b2):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.012, f"{b.get_height():.1%}",
                    ha="center", va="bottom", color=INK, fontsize=12)
    ax.set_xticks(list(x)); ax.set_xticklabels(labels_x, color=INK, fontsize=12)
    ax.set_ylim(0, 1.0); ax.set_yticks([]); ax.spines["left"].set_visible(False)
    ax.legend(frameon=False, loc="upper right", fontsize=11, labelcolor=MUTED)
    org = g.loc["organization"]
    ax.set_title(f"{int(org['donors']):,} organizations — {org['donor_share']:.1%} of donors — hold "
                 f"{org['value_share']:.0%} of every repeat dollar",
                 loc="left", color=INK, fontsize=15, fontweight="bold", pad=14)
    ax.text(0, 1.0, f"Holdout cohorts 2017–18 · {len(h):,} donors · ${h['second_gift_amount'].sum():,.0f} subsequent giving",
            transform=ax.transAxes, color=MUTED, fontsize=10, va="bottom")
    fig.tight_layout()
    fig.savefig(OUT / "donor_type_shares.png", bbox_inches="tight", facecolor="white")
    print(f"donor_type_shares.png    (organizations: {org['donor_share']:.2%} of donors, {org['value_share']:.1%} of value)")


if __name__ == "__main__":
    chart_donor_type_shares()
    chart_donations_per_donor()
