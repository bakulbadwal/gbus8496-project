"""
labels.py — turn the raw donations file into the labelled first-gift cohort table.

This is the foundation every other workstream builds on. One row per donor, and it answers the
question the project is about: this person gave for the first time in month M — did they give again
within twelve months?

    donations.csv  ──►  build_cohorts()  ──►  one row per donor:
                                              donor_id, cohort_month, first_gift_amount,
                                              first_project_id, gave_again (0/1),
                                              second_gift_amount, split

THREE DECISIONS ARE BAKED IN HERE, AND EACH ONE COULD HAVE GONE THE OTHER WAY
-----------------------------------------------------------------------------
1. **Same-month repeats do not count as a second gift** (default). DonorsChoose lets a donor fund
   several projects in one checkout, and dates in this release are month-level, so two donations in
   the first month are more plausibly one giving event split across classrooms than a genuine
   return. Counting them would inflate the positive class with something the stakeholder cannot act
   on — she cannot "steward someone back" who never left. `build_cohorts()` reports the count both
   ways so the sensitivity is visible, and `same_month_counts=True` flips it.

2. **The window is twelve whole calendar months after the first-gift month**, M+1 .. M+12. No day
   precision exists, so no finer definition is available.

3. **Only cohorts whose window closes inside the observed period are labelled.** A donor whose first
   gift is in mid-2019 would look like a non-repeater purely because the data stops. Those rows are
   dropped, not labelled 0.

Everything tunable lives in `src/config.py`. Do not re-define any of it here.
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

CHUNK = 1_000_000


# ── column and date handling ─────────────────────────────────────────────────────────────────────

def resolve_columns(header, needed=config.REQUIRED_COLUMNS,
                    optional=config.OPTIONAL_FLAGS + config.OPTIONAL_CATEGORICAL):
    """Map our logical names onto whatever the file actually calls them.

    The ICPSR release may differ from the Kaggle one, so nothing is hardcoded. Required columns
    raise with the real header printed, rather than guessing and producing a silently wrong table.
    Optional ones are included when found and silently skipped when not.
    """
    normalized = {c.lower().replace("_", ""): c for c in header}

    def find(logical):
        for candidate in config.COLUMN_CANDIDATES[logical]:
            key = candidate.lower().replace("_", "")
            if key in normalized:
                return normalized[key]
        return None

    resolved = {}
    for logical in needed:
        found = find(logical)
        if found is None:
            raise KeyError(
                f"No column found for '{logical}'. Columns present: {list(header)}\n"
                f"Add the right name to COLUMN_CANDIDATES['{logical}'] in src/config.py."
            )
        resolved[logical] = found
    for logical in optional:
        found = find(logical)
        if found is not None:
            resolved[logical] = found
    return resolved


def _to_bool(series):
    """ICPSR encodes flags inconsistently within one file: Yes/No for some, t/f for others."""
    return series.astype(str).str.strip().str.lower().isin(["yes", "y", "t", "true", "1"])


def to_month_index(values):
    """Any date-ish column → integer months since 2000-01. NaT becomes NaN.

    Working in integer months keeps window arithmetic exact and avoids every calendar edge case that
    day-level date maths introduces. 2016-11 → (2016-2000)*12 + 10 → 202.
    """
    parsed = pd.to_datetime(values, errors="coerce", format="mixed")
    return (parsed.dt.year - 2000) * 12 + (parsed.dt.month - 1)


def month_index_to_str(idx):
    """202 → '2016-11'. For readable output and for comparing against config's month strings."""
    idx = int(idx)
    return f"{2000 + idx // 12:04d}-{idx % 12 + 1:02d}"


def month_str_to_index(s):
    """'2016-11' → 202."""
    year, month = str(s).split("-")[:2]
    return (int(year) - 2000) * 12 + (int(month) - 1)


# ── loading ──────────────────────────────────────────────────────────────────────────────────────

def detect_sep(path):
    """ICPSR ships delimited files as tab-separated .tsv; the older Kaggle release was .csv.
    Sniff the header line rather than trust the extension."""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        header = f.readline()
    return "\t" if header.count("\t") > header.count(",") else ","


def load_donations(path, chunk=CHUNK, verbose=True):
    """Read only the four columns we need, in chunks, and return one tidy frame.

    Only four columns of ~11.4M rows are held, which fits comfortably on the Very Large VM. Reading
    the whole file would not.
    """
    sep = detect_sep(path)
    header = list(pd.read_csv(path, nrows=0, sep=sep).columns)
    cols = resolve_columns(header)
    if verbose:
        print(f"Separator: {'TAB' if sep == chr(9) else 'comma'}")
        print("Resolved columns:")
        for logical, actual in cols.items():
            print(f"  {logical:<11} → {actual}")

    frames = []
    reader = pd.read_csv(path, sep=sep, usecols=list(cols.values()), chunksize=chunk,
                         dtype={cols["donor_id"]: str, cols["project_id"]: str},
                         on_bad_lines="warn")
    keep = ["donor_id", "project_id", "month_index", "amount"]
    flags = [f for f in config.OPTIONAL_FLAGS if f in cols]
    cats = [c for c in config.OPTIONAL_CATEGORICAL if c in cols]
    for i, chunk_df in enumerate(reader, start=1):
        chunk_df = chunk_df.rename(columns={v: k for k, v in cols.items()})
        chunk_df["month_index"] = to_month_index(chunk_df["month"])
        chunk_df["amount"] = pd.to_numeric(chunk_df["amount"], errors="coerce")
        for f in flags:
            chunk_df[f] = _to_bool(chunk_df[f])
        for c in cats:
            chunk_df[c] = chunk_df[c].astype(str).str.strip()
        frames.append(chunk_df[keep + flags + cats])
        if verbose:
            print(f"  chunk {i}: {sum(len(f) for f in frames):,} rows")

    donations = pd.concat(frames, ignore_index=True)
    before = len(donations)
    donations = donations.dropna(subset=["donor_id", "month_index", "amount"])
    donations["month_index"] = donations["month_index"].astype(int)
    if verbose and before != len(donations):
        print(f"  dropped {before - len(donations):,} rows missing donor, month or amount "
              f"({100 * (before - len(donations)) / before:.2f}%)")
    return donations


# ── the label ────────────────────────────────────────────────────────────────────────────────────

def build_cohorts(donations, same_month_counts=False, verbose=True):
    """One row per donor: their first gift, and whether a second one followed within the window.

    Returns (cohorts, diagnostics). `diagnostics` carries the counts we have to report — how many
    donors were dropped for an unclosed window, and how the positive rate moves under the
    same-month rule — so the choices in this file are auditable rather than assumed.
    """
    # Refunds and reversals appear as negative or zero amounts (codebook: AMOUNT min = -15.00).
    # A reversal is not a gift, and must not create a first-gift cohort or count as a second gift.
    n_nonpositive = int((donations["amount"] <= 0).sum())
    d = donations[donations["amount"] > 0]

    first_month = d.groupby("donor_id")["month_index"].min().rename("cohort_month")

    # The first giving *event*: everything the donor gave in their first month, summed. If they
    # funded three classrooms in one checkout, that is one event worth the total.
    first = d.join(first_month, on="donor_id")
    is_first_month = first["month_index"] == first["cohort_month"]
    # First-gift attributes ride along. For flags, "any" across the first-month event: if any part
    # of that first checkout was matched / teacher-referred / got a thank-you packet, the event was.
    aggs = dict(first_gift_amount=("amount", "sum"),
                first_month_gifts=("amount", "size"),
                first_project_id=("project_id", "first"))
    for f in config.OPTIONAL_FLAGS:
        if f in d.columns:
            aggs[f"first_{f}"] = (f, "any")
    for c in config.OPTIONAL_CATEGORICAL:
        if c in d.columns:
            aggs[c] = (c, "first")
    first_event = first[is_first_month].groupby("donor_id").agg(**aggs)

    cohorts = pd.concat([first_month, first_event], axis=1).reset_index()

    # Window: M+1 .. M+12 by default; M .. M+12 (extra same-month gifts) if same_month_counts.
    later = d.join(first_month, on="donor_id")
    window_end = later["cohort_month"] + config.SECOND_GIFT_WINDOW_MONTHS
    if same_month_counts:
        in_window = (later["month_index"] >= later["cohort_month"]) & (later["month_index"] <= window_end)
        # a same-month gift only counts if it is not the single first gift itself
        in_window &= ~((later["month_index"] == later["cohort_month"]) & (later.groupby("donor_id").cumcount() == 0))
    else:
        in_window = (later["month_index"] > later["cohort_month"]) & (later["month_index"] <= window_end)

    second = (later[in_window]
              .groupby("donor_id")
              .agg(second_gift_amount=("amount", "sum"),
                   second_gift_count=("amount", "size")))
    cohorts = cohorts.merge(second, on="donor_id", how="left")
    cohorts["second_gift_amount"] = cohorts["second_gift_amount"].fillna(0.0)
    cohorts["second_gift_count"] = cohorts["second_gift_count"].fillna(0).astype(int)
    cohorts["gave_again"] = (cohorts["second_gift_count"] > 0).astype(int)

    # Sensitivity: what the positive rate would have been under the other same-month rule.
    strict = (later[(later["month_index"] > later["cohort_month"]) & (later["month_index"] <= window_end)]
              .groupby("donor_id").size())
    loose_extra = cohorts["first_month_gifts"] > 1
    diagnostics = {
        "rows_dropped_nonpositive_amount": n_nonpositive,
        "donors_before_window_filter": len(cohorts),
        "positive_rate_strict": float((cohorts["donor_id"].isin(strict.index)).mean()),
        "share_with_multiple_first_month_gifts": float(loose_extra.mean()),
    }

    # Drop cohorts whose 12-month window has not closed, and the least trustworthy earliest months.
    last_ok = month_str_to_index(config.LAST_LABELABLE_COHORT)
    first_ok = month_str_to_index(config.FIRST_TRUSTED_COHORT)
    keep = (cohorts["cohort_month"] >= first_ok) & (cohorts["cohort_month"] <= last_ok)
    diagnostics["donors_dropped_unclosed_window"] = int((cohorts["cohort_month"] > last_ok).sum())
    diagnostics["donors_dropped_pre_coverage"] = int((cohorts["cohort_month"] < first_ok).sum())
    cohorts = cohorts[keep].copy()

    cohorts["cohort"] = cohorts["cohort_month"].map(month_index_to_str)
    cohorts["split"] = assign_split(cohorts["cohort_month"])
    diagnostics["donors_labelled"] = len(cohorts)
    diagnostics["positive_rate"] = float(cohorts["gave_again"].mean())

    if verbose:
        print("\nLabel construction:")
        for k, v in diagnostics.items():
            print(f"  {k:<40} {v:,.4f}" if isinstance(v, float) else f"  {k:<40} {v:,}")
        print("\nBy split:")
        print(cohorts.groupby("split").agg(donors=("donor_id", "size"),
                                           positive_rate=("gave_again", "mean")).to_string())
    return cohorts, diagnostics


def assign_split(cohort_month):
    """Time-based split. Cohorts through 2016 train; 2017–2018 are held out and not looked at."""
    train_end = month_str_to_index(config.TRAIN_COHORT_END)
    return pd.Series(["train" if m <= train_end else "holdout" for m in cohort_month],
                     index=cohort_month.index)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        print("Usage: python src/labels.py <donations csv> [output parquet]")
        sys.exit(1)
    donations = load_donations(sys.argv[1])
    cohorts, _ = build_cohorts(donations)
    out = sys.argv[2] if len(sys.argv) > 2 else "data/processed/cohorts.parquet"
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    cohorts.to_parquet(out, index=False)
    print(f"\nWrote {len(cohorts):,} labelled donors to {out}")
