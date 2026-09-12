"""
test_labels.py — the label is the foundation of the project, so its rules are pinned down here.

Every rule in src/labels.py gets one hand-built donor whose correct answer is known before the code
runs. If a teammate changes the window, the same-month rule, or the refund handling, a test fails
and says which rule moved. Run from the repo root:

    .venv/bin/python -m pytest tests/ -q

The fixture is nine donors. Amounts and months are chosen so every branch is exercised exactly once.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import config   # noqa: E402
import labels   # noqa: E402

M = labels.month_str_to_index


def donations():
    """Nine donors, each testing one rule. Columns match what load_donations() produces."""
    rows = [
        # donor, project, month,       amount   — what it tests
        ("A", "p1", M("2016-03"), 10.0),   # A: returns in-window (M+6)            → gave_again 1
        ("A", "p2", M("2016-09"), 20.0),
        ("B", "p1", M("2016-03"), 10.0),   # B: two gifts in the FIRST month only  → 0 (one event), first_amount 15
        ("B", "p2", M("2016-03"),  5.0),
        ("C", "p1", M("2016-03"), 10.0),   # C: returns at exactly M+12            → 1 (window is inclusive)
        ("C", "p2", M("2017-03"),  5.0),
        ("D", "p1", M("2016-03"), 10.0),   # D: returns at M+13                    → 0 (outside window)
        ("D", "p2", M("2017-04"),  5.0),
        ("E", "p1", M("2019-06"), 10.0),   # E: first gift after LAST_LABELABLE   → dropped (unclosed window)
        ("F", "p1", M("2016-03"), -15.0),  # F: only a refund                      → no cohort at all
        ("G", "p1", M("2016-03"), 10.0),   # G: refund inside the window           → 0 (a reversal is not a gift)
        ("G", "p2", M("2016-05"), -10.0),
        ("H", "p1", M("2002-01"), 10.0),   # H: before FIRST_TRUSTED_COHORT        → dropped (pre-coverage)
        ("I", "p1", M("2017-01"), 10.0),   # I: 2017 cohort                        → split == holdout
        ("I", "p2", M("2017-08"), 30.0),
    ]
    df = pd.DataFrame(rows, columns=["donor_id", "project_id", "month_index", "amount"])
    df["donor_type"] = "citizen donor"
    return df


@pytest.fixture(scope="module")
def cohorts():
    c, diag = labels.build_cohorts(donations(), verbose=False)
    return c.set_index("donor_id"), diag


def test_month_index_roundtrip():
    assert labels.month_str_to_index("2016-11") == 202
    assert labels.month_index_to_str(202) == "2016-11"
    assert labels.to_month_index(pd.Series(["2016-11", "2000-01"])).tolist() == [202, 0]


def test_returner_is_positive(cohorts):
    c, _ = cohorts
    assert c.loc["A", "gave_again"] == 1
    assert c.loc["A", "second_gift_amount"] == 20.0
    assert c.loc["A", "cohort"] == "2016-03"


def test_same_month_repeat_is_one_event_not_a_return(cohorts):
    c, _ = cohorts
    assert c.loc["B", "gave_again"] == 0
    assert c.loc["B", "first_gift_amount"] == 15.0        # the whole first checkout
    assert c.loc["B", "first_month_gifts"] == 2


def test_window_edge_is_inclusive_at_twelve_months(cohorts):
    c, _ = cohorts
    assert c.loc["C", "gave_again"] == 1                  # M+12 counts
    assert c.loc["D", "gave_again"] == 0                  # M+13 does not


def test_unclosed_window_is_dropped_not_zeroed(cohorts):
    c, diag = cohorts
    assert "E" not in c.index
    assert diag["donors_dropped_unclosed_window"] == 1


def test_refund_only_donor_has_no_cohort(cohorts):
    c, _ = cohorts
    assert "F" not in c.index


def test_refund_in_window_is_not_a_second_gift(cohorts):
    c, _ = cohorts
    assert c.loc["G", "gave_again"] == 0
    assert c.loc["G", "second_gift_amount"] == 0.0


def test_pre_coverage_cohort_is_dropped(cohorts):
    c, diag = cohorts
    assert "H" not in c.index
    assert diag["donors_dropped_pre_coverage"] == 1


def test_split_is_time_based(cohorts):
    c, _ = cohorts
    assert c.loc["A", "split"] == "train"                 # 2016 cohort
    assert c.loc["I", "split"] == "holdout"               # 2017 cohort
    assert c.loc["I", "gave_again"] == 1


def test_same_month_flag_flips_only_b():
    loose, _ = labels.build_cohorts(donations(), same_month_counts=True, verbose=False)
    loose = loose.set_index("donor_id")
    assert loose.loc["B", "gave_again"] == 1              # the extra same-month gift now counts
    assert loose.loc["A", "gave_again"] == 1              # everyone else unchanged
    assert loose.loc["D", "gave_again"] == 0


def test_positive_rate_matches_hand_count(cohorts):
    c, diag = cohorts
    # Labelled: A B C D G I → positives A C I → 3/6
    assert len(c) == 6
    assert diag["positive_rate"] == pytest.approx(0.5)


def test_detect_sep(tmp_path):
    tsv = tmp_path / "x.tsv"; tsv.write_text("DONOR_ID\tAMOUNT\n1\t2\n")
    csv = tmp_path / "x.csv"; csv.write_text("DONOR_ID,AMOUNT\n1,2\n")
    assert labels.detect_sep(tsv) == "\t"
    assert labels.detect_sep(csv) == ","


def test_column_resolution_is_case_and_underscore_insensitive():
    got = labels.resolve_columns(["Donor_ID", "PROJECTID", "created_month", "Amount", "DONOR_TYPE"])
    assert got["donor_id"] == "Donor_ID" and got["project_id"] == "PROJECTID"
    assert got["donor_type"] == "DONOR_TYPE"
    with pytest.raises(KeyError):
        labels.resolve_columns(["something", "else"])
