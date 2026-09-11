"""
check_donor_id.py — the one check that has to pass before we build anything else.

WHY THIS EXISTS
---------------
Albert, approving the proposal on Sep 9: "As soon as possible, confirm that the donor ID in the
public-use file actually links gifts across projects, because the whole project depends on it."

He is right. Our entire project is "did this first-time donor give again within 12 months?" That
question only exists if DONOR_ID identifies a *person across their whole giving history*. If the
public-use file instead assigns a fresh id per project (a common privacy measure in released data),
then every donor looks like a one-time donor by construction, the label is all zeros, and there is
no project. We would switch to the Amazon fallback the same day.

WHAT IT MEASURES
----------------
Three numbers, in increasing order of importance:

  1. How many distinct donor ids are there, against how many donation rows?
  2. What share of donors appear more than once at all?
  3. What share of donors appear against MORE THAN ONE DISTINCT PROJECT?   <-- the answer

(3) is the real test. If ids were minted per project, (3) is exactly zero and (2) only reflects
donors who gave to the same project twice. If (3) is a healthy share, ids follow the person and
we are in business.

HOW TO RUN IT
-------------
On the JupyterHub "Very Large Virtual Machine", from the repo root:

    python src/check_donor_id.py data/raw/<donations file>.csv

It streams the file in chunks, so it does not need the whole 9 GB in memory. Expect a few minutes.
Paste the output into the team chat.

NOTE ON COLUMN NAMES: this script does not hardcode them. The ICPSR release may not use the same
names as the older Kaggle release, so it detects the donor and project columns and prints what it
found. If detection fails it lists every column and exits, rather than guessing.
"""

import sys
from collections import Counter

import pandas as pd

CHUNK = 1_000_000  # rows per chunk; tune down if memory is tight

# Candidate column names, most likely first. Matched case-insensitively against the real header.
DONOR_CANDIDATES = ["donor_id", "donorid", "donor", "donoracctid"]
PROJECT_CANDIDATES = ["projectid", "project_id", "proj_id", "projid"]


def detect_sep(path):
    """ICPSR ships delimited files as tab-separated .tsv; Kaggle's older release was .csv.
    Sniff the header line rather than trust the extension, so a renamed file cannot fool us."""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        header = f.readline()
    return "\t" if header.count("\t") > header.count(",") else ","


def pick_column(header, candidates, role):
    """Find one column in `header` matching any of `candidates`, case- and underscore-insensitively."""
    normalized = {c.lower().replace("_", ""): c for c in header}
    for want in candidates:
        key = want.lower().replace("_", "")
        if key in normalized:
            return normalized[key]
    print(f"\nCould not find a {role} column. Columns actually present:\n")
    for c in header:
        print(f"    {c}")
    print(f"\nEdit {role.upper()}_CANDIDATES in this script and re-run.")
    sys.exit(1)


def main(path):
    # Read only the header first, so we can pick columns before committing to a big read.
    sep = detect_sep(path)
    header = list(pd.read_csv(path, nrows=0, sep=sep).columns)
    donor_col = pick_column(header, DONOR_CANDIDATES, "donor")
    project_col = pick_column(header, PROJECT_CANDIDATES, "project")
    print(f"Separator            : {'TAB' if sep == chr(9) else 'comma'}")
    print(f"Using donor column   : {donor_col}")
    print(f"Using project column : {project_col}")
    print(f"Streaming {path} in chunks of {CHUNK:,} rows...\n")

    # donations_per_donor: how many rows each donor appears in.
    # projects_per_donor:  how many DISTINCT projects each donor gave to. This is the one that matters,
    #                      so we keep a set per donor. Memory scales with distinct donors, not rows.
    donations_per_donor = Counter()
    projects_per_donor = {}
    rows = 0

    reader = pd.read_csv(path, sep=sep, usecols=[donor_col, project_col], chunksize=CHUNK,
                         dtype=str, on_bad_lines="warn")
    for i, chunk in enumerate(reader, start=1):
        chunk = chunk.dropna(subset=[donor_col])
        rows += len(chunk)
        donations_per_donor.update(chunk[donor_col].values)
        for donor, project in zip(chunk[donor_col].values, chunk[project_col].values):
            projects_per_donor.setdefault(donor, set()).add(project)
        print(f"  chunk {i}: {rows:,} rows so far, {len(donations_per_donor):,} distinct donors")

    donors = len(donations_per_donor)
    repeat_donors = sum(1 for n in donations_per_donor.values() if n > 1)
    multi_project = sum(1 for s in projects_per_donor.values() if len(s) > 1)

    print("\n" + "=" * 72)
    print("RESULT")
    print("=" * 72)
    print(f"Donation rows                          : {rows:,}")
    print(f"Distinct donor ids                     : {donors:,}")
    print(f"Donations per donor (mean)             : {rows / donors:.2f}")
    print(f"Donors appearing more than once        : {repeat_donors:,}  ({100 * repeat_donors / donors:.1f}%)")
    print(f"Donors giving to >1 DISTINCT project   : {multi_project:,}  ({100 * multi_project / donors:.1f}%)   <-- THE ANSWER")

    # Distribution, so we can see whether repeat giving is a long tail or a handful of whales.
    print("\nDonations per donor, distribution:")
    buckets = Counter()
    for n in donations_per_donor.values():
        buckets["1" if n == 1 else "2" if n == 2 else "3-5" if n <= 5 else "6-20" if n <= 20 else "21+"] += 1
    for label in ["1", "2", "3-5", "6-20", "21+"]:
        count = buckets.get(label, 0)
        print(f"  {label:>5} donation(s): {count:>12,}  ({100 * count / donors:5.1f}%)")

    print("\n" + "=" * 72)
    if multi_project == 0:
        print("STOP. Donor ids do NOT link across projects — every donor is confined to one project.")
        print("The second-gift label cannot be built. Switch to the Amazon fallback and tell the team today.")
    elif 100 * multi_project / donors < 5:
        print("CAUTION. Cross-project linking exists but is rare. The label is buildable but the")
        print("positive class will be very small. Report this share in the presentation, and check")
        print("the base rate of the label before committing.")
    else:
        print("PASS. Donor ids link gifts across projects. The second-gift label is buildable.")
    print("=" * 72)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        print("Usage: python src/check_donor_id.py <path to donations csv>")
        sys.exit(1)
    main(sys.argv[1])
