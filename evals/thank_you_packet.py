"""
thank_you_packet.py — the thank-you packet question, as far as this data can take it (Sep 24 meeting).

    python evals/thank_you_packet.py

The team asked two things on Sep 24: does the packet go to donors above a gift cutoff (which would
allow a cutoff-based comparison), and does it matter differently for individuals and organizations.
The codebook gives no mailing date, so every result here is descriptive. The model-side test is
`python src/model.py <cohorts_with_projects.parquet> --with-packet`, which assumes the packet was
mailed before any second gift.

  A. Who gets a packet: rate and repeat rate by donor type.
  B. Citizen donors: repeat rate with vs without a packet, within first-gift size bands.
  C. The $50 cutoff: packet and repeat rates in $1 steps around $50, and a fuzzy cutoff estimate.
  D. When is a packet sent: packet rate by the first project's final status (funded or not), and
     alongside the project-level thank-you note and impact letter.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
PROC = REPO / "data" / "processed"
PROJECTS = REPO / "data" / "raw" / "ICPSR_37898" / "DS0003" / "37898-0003-Data.tsv"
pct = lambda v: f"{v:.1%}"


def section(t):
    print(f"\n{'=' * 90}\n{t}\n{'=' * 90}")


def main():
    c = pd.read_parquet(PROC / "cohorts.parquet",
                        columns=["donor_id", "donor_type", "first_project_id", "first_gift_amount",
                                 "first_thank_you_packet", "gave_again", "second_gift_amount", "split"])
    c["packet"] = c["first_thank_you_packet"].astype(bool)
    c["y"] = c["gave_again"].astype(int)

    section("A · Packet rate and repeat rate by donor type (all labelled donors)")
    a = c.groupby("donor_type").agg(donors=("y", "size"), packet_rate=("packet", "mean"),
                                    repeat_with=("y", lambda s: s[c.loc[s.index, "packet"]].mean()),
                                    repeat_without=("y", lambda s: s[~c.loc[s.index, "packet"]].mean()))
    a["gap_pp"] = 100 * (a["repeat_with"] - a["repeat_without"])
    print(a.to_string(float_format=lambda v: f"{v:,.3f}"))

    cit = c[c["donor_type"] == "citizen donor"].copy()
    section("B · Citizen donors: repeat rate with vs without a packet, within first-gift bands")
    cit["band"] = pd.cut(cit["first_gift_amount"], [0, 10, 25, 50, 100, 250, np.inf], right=False,
                         labels=["<$10", "$10–24", "$25–49", "$50–99", "$100–249", "$250+"])
    b = cit.groupby(["band", "packet"], observed=True)["y"].agg(["size", "mean"]).unstack("packet")
    b.columns = [f"{m}_{'packet' if p else 'none'}" for m, p in b.columns]
    b["packet_rate"] = b["size_packet"] / (b["size_packet"] + b["size_none"])
    b["gap_pp"] = 100 * (b["mean_packet"] - b["mean_none"])
    print(b.to_string(float_format=lambda v: f"{v:,.3f}"))
    # size-band-adjusted gap: reweight packet-group rates to the no-packet group's band mix
    w = b["size_none"] / b["size_none"].sum()
    print(f"Raw gap: {pct(cit[cit.packet].y.mean())} vs {pct(cit[~cit.packet].y.mean())}. "
          f"Gap after holding the gift-size mix fixed: {100 * ((b['mean_packet'] - b['mean_none']) * w).sum():+.1f} pp.")

    section("C · Around $50: is there a cutoff?")
    near = cit[(cit["first_gift_amount"] >= 40) & (cit["first_gift_amount"] < 61)].copy()
    near["dollar"] = np.floor(near["first_gift_amount"]).astype(int)
    t = near.groupby("dollar").agg(donors=("y", "size"), packet_rate=("packet", "mean"), repeat=("y", "mean"))
    print(t.to_string(float_format=lambda v: f"{v:,.3f}"))
    lo = cit[(cit["first_gift_amount"] >= 45) & (cit["first_gift_amount"] < 50)]
    hi = cit[(cit["first_gift_amount"] >= 50) & (cit["first_gift_amount"] < 55)]
    hi_x = hi[hi["first_gift_amount"] != 50]
    for name, h in [("$50–54.99 (incl. exactly $50)", hi), ("$50.01–54.99 (excl. exactly $50)", hi_x)]:
        dp = h["packet"].mean() - lo["packet"].mean()
        dy = h["y"].mean() - lo["y"].mean()
        print(f"$45–49.99 vs {name}: packet {pct(lo.packet.mean())} → {pct(h.packet.mean())}; "
              f"repeat {pct(lo.y.mean())} → {pct(h.y.mean())}; "
              f"implied effect of a packet = Δrepeat/Δpacket = {dy / dp:+.1%}" if dp > 0.02 else
              f"$45–49.99 vs {name}: packet jump too small ({dp * 100:+.1f} pp) to estimate an effect")

    # Round amounts ($40, $45, $50, $55, $60) are preset buttons with their own packet rates, so the
    # cleaner comparison uses whole-dollar amounts that are NOT multiples of 5, just either side of $50.
    a = cit["first_gift_amount"]
    nonround = (np.abs(a - np.round(a)) < 1e-9) & (np.floor(a) % 5 != 0)
    L = cit[nonround & (a >= 41) & (a < 50)][["packet", "y"]].astype(float).values
    H = cit[nonround & (a > 50) & (a <= 59)][["packet", "y"]].astype(float).values
    dp, dy = H[:, 0].mean() - L[:, 0].mean(), H[:, 1].mean() - L[:, 1].mean()
    rng = np.random.default_rng(8496)
    boots = []
    for _ in range(500):
        l, h = L[rng.integers(0, len(L), len(L))], H[rng.integers(0, len(H), len(H))]
        boots.append((h[:, 1].mean() - l[:, 1].mean()) / (h[:, 0].mean() - l[:, 0].mean()))
    print(f"\nNon-round whole amounts, $41–49 (n={len(L):,}) vs $51–59 (n={len(H):,}): packet "
          f"{pct(L[:, 0].mean())} → {pct(H[:, 0].mean())} ({dp * 100:+.1f} pp), repeat {pct(L[:, 1].mean())} → "
          f"{pct(H[:, 1].mean())} ({dy * 100:+.1f} pp). Implied packet effect {dy / dp:+.1%} "
          f"(bootstrap 95% CI {np.percentile(boots, 2.5):+.1%} to {np.percentile(boots, 97.5):+.1%}). "
          "Suggestive only: small n, and repeat rates also rise with gift size across the window.")

    section("D · When is a packet sent? Packet rate by the first project's final status")
    proj = pd.read_csv(PROJECTS, sep="\t", dtype=str,
                       usecols=["PROJECT_ID", "PROJECT_STATUS_AS_OF_12_31_2019", "THANKYOU_NOTE", "IMPACT_LETTER"])
    proj = proj.drop_duplicates("PROJECT_ID").rename(columns={"PROJECT_ID": "first_project_id"})
    m = cit.merge(proj, on="first_project_id", how="left")
    d = m.groupby("PROJECT_STATUS_AS_OF_12_31_2019", dropna=False).agg(
        donors=("y", "size"), packet_rate=("packet", "mean"), repeat=("y", "mean"))
    print(d.sort_values("donors", ascending=False).to_string(float_format=lambda v: f"{v:,.3f}"))
    for col in ["THANKYOU_NOTE", "IMPACT_LETTER"]:
        x = m.groupby(m[col].fillna("missing"))["packet"].agg(["size", "mean"]).sort_values("size", ascending=False).head(4)
        print(f"\nPacket rate by project-level {col}:\n{x.to_string(float_format=lambda v: f'{v:,.3f}')}")


if __name__ == "__main__":
    main()
