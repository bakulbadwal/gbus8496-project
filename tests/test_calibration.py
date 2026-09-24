"""Regression checks for the list used in error analysis and its denominators."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "evals"))
import calibration as C


@pytest.fixture
def donors():
    # In each month the best return probability and best dollar score belong to different people.
    return pd.DataFrame({
        "donor_id": ["a", "b", "c", "d"], "cohort_month": [204, 204, 216, 216],
        "cohort": ["2017-01", "2017-01", "2018-01", "2018-01"],
        "cohort_year": ["2017", "2017", "2018", "2018"],
        "split": ["holdout"] * 4, "donor_type": ["citizen donor"] * 4,
        "first_gift_amount": [10., 100., 10., 100.], "gave_again": [1, 0, 0, 1],
        "y": [1, 0, 0, 1], "second_gift_amount": [10., 0., 0., 200.],
        "p_return": [.9, .2, .8, .1], "expected_value": [9., 100., 8., 80.],
    })


def test_dollar_ranking_selects_the_headline_list_within_each_month(donors):
    bands = C.by_size_band(donors, capacity=.5)
    assert bands.loc["$100–249", "contacted"] == 2
    assert bands.loc["$10–24", "contacted"] == 0
    assert bands.loc["$100–249", "precision"] == .5
    assert bands.loc["$100–249", "value_per_contact"] == 100
    years = C.by_group(donors, "cohort_year", capacity=.5)
    assert years["contacted"].tolist() == [1, 1]
    assert years["precision"].tolist() == [0, 1]


def test_probability_comparison_does_not_change_calibration(donors):
    before = C.calibration_table(donors, bins=2)
    bands = C.by_size_band(donors, capacity=.5, ranking="p_return")
    assert bands.loc["$10–24", "contacted"] == 2
    pd.testing.assert_frame_equal(before[0], C.calibration_table(donors, bins=2)[0])
    comparison = C.compare_rankings(donors, capacity=.5)
    assert comparison.loc["expected_value", "under_50_share_of_list"] == 0
    assert comparison.loc["p_return", "under_50_share_of_list"] == 1


def test_reference_model_fallback_and_explicit_missing_ranking(donors):
    reference = donors.drop(columns="expected_value")
    assert C.ranking_column(reference) == "p_return"
    with pytest.raises(ValueError, match="missing"):
        C.by_group(reference, "cohort_year", ranking="expected_value")


def test_precision_pools_donors_instead_of_averaging_band_percentages():
    groups = pd.DataFrame({"contacted": [1, 9, 0], "repeat_donors_found": [1, 0, 0]})
    assert C.pooled_precision(groups) == .1  # not (100% + 0%) / 2
    assert np.isnan(C.pooled_precision(groups.iloc[[2]]))


def test_filtered_frame_indices_do_not_change_the_selected_people(donors):
    expected = C.by_group(donors, "cohort_year", capacity=.5)
    donors.index = [3, 8, 20, 42]
    pd.testing.assert_frame_equal(C.by_group(donors, "cohort_year", capacity=.5), expected)


@pytest.mark.parametrize("problem", ["missing", "duplicate", "infinite", "probability"])
def test_incomplete_or_invalid_predictions_fail_instead_of_changing_population(tmp_path, donors, problem):
    cohorts = tmp_path / "cohorts.parquet"
    scores = tmp_path / "scores.parquet"
    donors.drop(columns=["p_return", "expected_value"]).to_parquet(cohorts)
    s = donors[["donor_id", "p_return", "expected_value"]].copy()
    if problem == "missing":
        s = s.iloc[:-1]
    elif problem == "duplicate":
        s = pd.concat([s, s.iloc[[0]]])
    elif problem == "infinite":
        s.loc[0, "expected_value"] = np.inf
    else:
        s.loc[0, "p_return"] = 1.1
    s.to_parquet(scores)
    with pytest.raises(ValueError):
        C.load(cohorts, scores)


def test_loading_preserves_dollar_scores(tmp_path, donors):
    c, s = tmp_path / "cohorts.parquet", tmp_path / "scores.parquet"
    donors.drop(columns=["p_return", "expected_value"]).to_parquet(c)
    donors[["donor_id", "p_return", "expected_value"]].to_parquet(s)
    loaded = C.load(c, s)
    assert loaded["expected_value"].tolist() == [9, 100, 8, 80]
