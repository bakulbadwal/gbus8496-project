"""
qa_analyses.py — the four follow-up analyses Malorie flagged for Q&A (Sep 24).

    python evals/qa_analyses.py

  A. Same teacher: when a citizen donor gives a second time, is it to the same classroom
     (same teacher) as the first gift? Closest proxy in this data to "gave again to the same
     nonprofit." The Projects file carries TEACHER_ID and SCHOOL_STATE but no school id, so
     "same school" cannot be tested.
  B. Who the model added: on the holdout, donors on the model's 10% list but not on the
     gift-size list, compared with the ones gift size picked that the model dropped.
  C. Capacity 5%–30%: the model vs gift size vs random at every capacity from 5% to 30%.
  D. Second → third gift: of citizen donors who gave a second time, how many gave a third time
     within twelve months of the second? Our own analogue of the FEP 19%-vs-59% slide.

Citizen donors only (config.STAKEHOLDER_POPULATION). Reads data/processed/*.parquet plus the raw
donations and projects files. Descriptive; nothing here is fit, and the holdout scores already exist.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "evals"))
import config           # noqa: E402
import labels           # noqa: E402
import score as scorer  # noqa: E402

DONATIONS = REPO / "data" / "raw" / "ICPSR_37898" / "DS0001" / "37898-0001-Data.tsv"
PROJECTS = REPO / "data" / "raw" / "ICPSR_37898" / "DS0003" / "37898-0003-Data.tsv"
PROC = REPO / "data" / "processed"
POP = config.STAKEHOLDER_POPULATION
pct = lambda v: f"{v:.1%}"


def section(t):
    print(f"\n{'=' * 90}\n{t}\n{'=' * 90}")


def main():
    cohorts = pd.read_parquet(PROC / "cohorts.parquet")
    cit = cohorts[cohorts["donor_type"] == POP][["donor_id", "cohort_month", "first_project_id",
                                                 "gave_again", "split"]].copy()

    # ── raw donations, citizens only, positive amounts ──
    d = labels.load_donations(DONATIONS, verbose=False)
    d = d[d["amount"] > 0]
    d = d[d["donor_id"].isin(set(cit["donor_id"]))]
    last_month = int(d["month_index"].max())

    # ── A. same teacher ──
    section("A · Did the second gift go to the same classroom (same teacher) as the first?")
    teacher = pd.read_csv(PROJECTS, sep="\t", usecols=["PROJECT_ID", "TEACHER_ID"], dtype=str)
    teacher = teacher.drop_duplicates("PROJECT_ID").set_index("PROJECT_ID")["TEACHER_ID"]
    ret = cit[cit["gave_again"].astype(bool)].copy()
    ret["first_teacher"] = ret["first_project_id"].map(teacher)
    w = d.merge(ret[["donor_id", "cohort_month", "first_teacher"]], on="donor_id")
    w = w[(w["month_index"] > w["cohort_month"]) & (w["month_index"] <= w["cohort_month"] + 12)]
    w["teacher"] = w["project_id"].map(teacher)
    w = w[w["first_teacher"].notna() & w["teacher"].notna()]
    w["same"] = w["teacher"] == w["first_teacher"]
    w["same_amount"] = w["amount"].where(w["same"], 0.0)
    per = w.groupby("donor_id").agg(any_same=("same", "any"), all_same=("same", "all"),
                                    dollars=("amount", "sum"), same_dollars=("same_amount", "sum"))
    print(f"Citizen donors who gave again (teacher known): {len(per):,}")
    print(f"  any repeat gift to the SAME teacher:        {pct(per['any_same'].mean())}")
    print(f"  ONLY to the same teacher (a loyal donor):   {pct(per['all_same'].mean())}")
    print(f"  ONLY to different teachers (the platform):  {pct((~per['any_same']).mean())}")
    print(f"  share of repeat dollars to the same teacher: {pct(per['same_dollars'].sum() / per['dollars'].sum())}")

    # ── B. who the model added ──
    section("B · Holdout, 10% capacity: who the model added vs who gift size would have called")
    hp = pd.read_parquet(PROC / "cohorts_with_projects.parquet")
    hp = hp[(hp["split"] == "holdout") & (hp["donor_type"] == POP)]
    hp = hp.merge(pd.read_parquet(PROC / "model_scores.parquet"), on="donor_id").reset_index(drop=True)
    cap = config.STEWARDSHIP_CAPACITY
    m_model = scorer._top_k_mask(hp, hp["expected_value"].values, cap)
    m_gift = scorer._top_k_mask(hp, hp["first_gift_amount"].values, cap)
    groups = {"added by model": m_model & ~m_gift, "dropped by model": ~m_model & m_gift,
              "on both lists": m_model & m_gift, "all holdout donors": np.ones(len(hp), bool)}
    num = lambda col: pd.to_numeric(hp[col], errors="coerce")
    rows = []
    for name, m in groups.items():
        g = hp[m]
        rows.append({
            "group": name, "donors": len(g),
            "gave_again": g["gave_again"].mean(),
            "$ next 12 mo / donor": g["second_gift_amount"].mean(),
            "median first gift": g["first_gift_amount"].median(),
            "first gift < $50": (g["first_gift_amount"] < 50).mean(),
            "2+ classrooms 1st month": (g["first_month_gifts"] >= 2).mean(),
            "gift card": g["first_gift_card"].astype(float).mean(),
            "matched": g["first_matched"].astype(float).mean(),
            "teacher-referred": g["first_teacher_referred"].astype(float).mean(),
            "median project price": num("TOTAL_PRICE_EXCLUDING_OPTIONAL_1")[m].median(),
            "free-lunch %": num("SCHOOL_PERCENTAGE_FREE_AND_RED_1")[m].mean(),
        })
    t = pd.DataFrame(rows).set_index("group").T
    print(t.to_string(float_format=lambda v: f"{v:,.3f}"))
    added = hp[groups["added by model"]]
    for col in ["SCHOOL_STATE", "CATEGORY", "SUBJECT_CATEGORY", "GRADE_LEVEL"]:
        lift = (added[col].value_counts(normalize=True) / hp[col].value_counts(normalize=True)).dropna()
        common = added[col].value_counts(normalize=True).head(8).index
        top = lift.loc[lift.index.isin(common)].sort_values(ascending=False).head(3)
        print(f"  {col}: over-represented among added donors → " +
              ", ".join(f"{k} ({v:.1f}× their share)" for k, v in top.items()))

    # ── C. capacity sweep ──
    section("C · Capacity 5%–30%, holdout: $ per contact, share of repeat dollars, precision")
    rng = np.random.default_rng(201)
    table = scorer.compare(hp, {"model": hp["expected_value"].values,
                                "gift size": hp["first_gift_amount"].values,
                                "random": rng.random(len(hp))},
                           capacities=[0.05, 0.10, 0.15, 0.20, 0.25, 0.30])
    for metric in ["value_per_contact", "value_capture_rate", "precision"]:
        pv = table.pivot_table(index="capacity", columns="ranking", values=metric)[["model", "gift size", "random"]]
        pv["model − gift"] = pv["model"] - pv["gift size"]
        print(f"\n{metric}")
        print(pv.to_string(float_format=lambda v: f"{v:,.3f}"))

    # ── D. second → third gift ──
    section("D · Second gift → third gift, citizen donors (months, 12-month windows)")
    months = d[["donor_id", "month_index"]].drop_duplicates().sort_values(["donor_id", "month_index"])
    months["k"] = months.groupby("donor_id").cumcount()
    wide = months[months["k"] <= 2].pivot(index="donor_id", columns="k", values="month_index")
    wide.columns = ["m1", "m2", "m3"][: len(wide.columns)]
    base = cit.set_index("donor_id")[["cohort_month", "gave_again"]].join(wide, how="inner")
    base = base[base["m1"] == base["cohort_month"]]
    first_rate = base["gave_again"].mean()
    sec = base[base["gave_again"].astype(bool) & (base["m2"] <= base["m1"] + 12)]
    sec = sec[sec["m2"] + 12 <= last_month]            # third-gift window must be closed
    third = (sec["m3"].notna() & (sec["m3"] <= sec["m2"] + 12)).mean()
    print(f"First gift → second within 12 months:  {pct(first_rate)}  (n = {len(base):,})")
    print(f"Second gift → third within 12 months:  {pct(third)}  (n = {len(sec):,} with a closed window)")
    print(f"A second-time donor is {third / first_rate:.1f}× as likely to give again as a first-time donor.")


if __name__ == "__main__":
    main()
