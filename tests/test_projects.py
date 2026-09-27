"""Protect project joins against literal quotes swallowing unrelated donor projects."""
import sys
from io import StringIO
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from projects import read_projects

TSV = 'PROJECT_ID\tTITLE\tSCHOOL_STATE\nA\t"Books for everyone\tVA\nB\tMath\tNY\nC\tClosing quote"\tCA\n'


@pytest.mark.parametrize('chunksize', [None, 1, 2])
def test_literal_quotes_preserve_rows_even_when_title_not_selected(chunksize):
    result = read_projects(StringIO(TSV), usecols=['PROJECT_ID', 'SCHOOL_STATE'],
                           dtype='string', chunksize=chunksize)
    if chunksize:
        result = pd.concat(result, ignore_index=True)
    assert result.PROJECT_ID.tolist() == ['A', 'B', 'C']
    assert result.SCHOOL_STATE.tolist() == ['VA', 'NY', 'CA']


def test_literal_quotes_and_missing_values_are_preserved():
    result = read_projects(StringIO(TSV + 'D\t\t\n'), dtype='string')
    assert result.TITLE.iloc[0] == '"Books for everyone'
    assert result.TITLE.iloc[2] == 'Closing quote"'
    assert pd.isna(result.SCHOOL_STATE.iloc[3])
