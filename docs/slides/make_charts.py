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


# ── Dark variants for the deck (navy background matches the slide) ──────────────────────────────
NAVY, INK_D, MUTED_D, SUBTLE_D, TERT_D, GRID_D = "#081321", "#F2EDE3", "#D9D3C6", "#B4AE9F", "#8A8474", "#13253A"
BLUE_D, ORANGE_D = "#3987E5", "#D95926"   # dark-surface categorical slots 1 and 2, validated


def _dark_axes(fig, ax):
    fig.patch.set_facecolor(NAVY); ax.set_facecolor(NAVY)
    for sp in ("top", "right", "left"): ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(GRID_D)
    ax.tick_params(colors=MUTED_D, labelsize=11, length=0)
    ax.set_yticks([])


def chart_donations_per_donor_dark(counts_shares=None):
    """Slide 2. Same data as the light chart; recomputed unless shares are passed in."""
    if counts_shares is None:
        sep = labels.detect_sep(DONATIONS); counts = Counter()
        for chunk in pd.read_csv(DONATIONS, sep=sep, usecols=["DONOR_ID"], chunksize=1_000_000, dtype=str):
            counts.update(chunk["DONOR_ID"].dropna().values)
        n = len(counts); b = Counter()
        for v in counts.values():
            b["1" if v == 1 else "2" if v == 2 else "3–5" if v <= 5 else "6–20" if v <= 20 else "21+"] += 1
        order = ["1", "2", "3–5", "6–20", "21+"]; shares = [b[k] / n for k in order]
    else:
        order, shares = counts_shares
    fig, ax = plt.subplots(figsize=(4.9, 4.25), dpi=220); _dark_axes(fig, ax)
    bars = ax.bar(order, shares, color=BLUE_D, width=0.6)
    for bar, sh in zip(bars, shares):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.015, f"{sh:.1%}", ha="center", va="bottom",
                color=INK_D, fontsize=12, fontweight="bold" if sh == max(shares) else "normal")
    ax.set_ylim(0, max(shares) * 1.2)
    ax.set_xlabel("LIFETIME GIFTS PER DONOR", color=TERT_D, fontsize=8, labelpad=10, family="monospace")
    fig.tight_layout(pad=0.6)
    fig.savefig(OUT / "slide2_donations_per_donor_dark.png", facecolor=NAVY)
    print("slide2_donations_per_donor_dark.png")


def chart_donor_type_shares_dark():
    """Slide 4. Donor share vs repeat-dollar share by type, holdout cohorts."""
    c = pd.read_parquet(COHORTS); h = c[c["split"] == "holdout"]
    g = h.groupby("donor_type").agg(donors=("donor_id", "size"), value=("second_gift_amount", "sum"))
    g["donor_share"] = g["donors"] / g["donors"].sum(); g["value_share"] = g["value"] / g["value"].sum()
    g = g.loc[["citizen donor", "teacher", "organization"]]
    fig, ax = plt.subplots(figsize=(5.05, 4.15), dpi=220); _dark_axes(fig, ax)
    x = range(3); w = 0.36
    b1 = ax.bar([i - w / 2 - 0.01 for i in x], g["donor_share"], w, color=BLUE_D, label="Share of donors")
    b2 = ax.bar([i + w / 2 + 0.01 for i in x], g["value_share"], w, color=ORANGE_D, label="Share of repeat dollars")
    for bars in (b1, b2):
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.015, f"{bar.get_height():.1%}",
                    ha="center", va="bottom", color=INK_D, fontsize=11)
    ax.set_xticks(list(x)); ax.set_xticklabels(["Citizen donors", "Teachers", "Organizations"], color=MUTED_D, fontsize=11)
    ax.set_ylim(0, 1.0)
    leg = ax.legend(frameon=False, loc="upper right", fontsize=10, labelcolor=MUTED_D)
    fig.tight_layout(pad=0.6)
    fig.savefig(OUT / "slide4_donor_type_shares_dark.png", facecolor=NAVY)
    print("slide4_donor_type_shares_dark.png")


if __name__ == "__main__":
    chart_donor_type_shares()
    chart_donations_per_donor()
    chart_donor_type_shares_dark()
    chart_donations_per_donor_dark()
