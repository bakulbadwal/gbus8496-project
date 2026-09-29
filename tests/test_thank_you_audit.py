"""Pin descriptive standardization against independently worked small examples."""
import importlib.util
from pathlib import Path

import pandas as pd
import pytest

spec = importlib.util.spec_from_file_location(
    'thank_you_audit', Path(__file__).resolve().parents[1] / 'evals/thank_you_audit.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def group(cell, packet, size, repeats):
    return pd.DataFrame({'cell': cell, 'packet': packet,
                         'gave_again': [1] * repeats + [0] * (size - repeats)})


def test_standardization_uses_same_pooled_weights_and_reports_excluded_donors():
    frame = pd.concat([
        group('a', False, 100, 10), group('a', True, 300, 90),
        group('b', False, 300, 60), group('b', True, 100, 40),
        group('unsupported', False, 100, 0), group('unsupported', True, 99, 99),
    ], ignore_index=True)
    result = audit.standardized(frame, 'packet', ['cell'], 'hand-worked')
    # Both supported cells have 400 donors, hence weight 1/2 each:
    # no = (.10 + .20)/2; yes = (.30 + .40)/2. The 99-recipient cell is excluded.
    assert result['repeat_no'] == pytest.approx(.15)
    assert result['repeat_yes'] == pytest.approx(.35)
    assert result['gap_pp'] == pytest.approx(20)
    assert result['supported_donors'] == 800
    assert result['source_donors'] == 999
    assert result['coverage'] == pytest.approx(800 / 999)
    assert result['cells'] == 2


def test_one_sided_exposure_does_not_create_a_comparison():
    frame = group('a', True, 200, 100)
    result = audit.standardized(frame, 'packet', ['cell'], 'no control group')
    assert result['supported_donors'] == 0
    assert result['coverage'] == 0
    assert pd.isna(result['gap_pp'])
