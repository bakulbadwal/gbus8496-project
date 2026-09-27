"""Read ICPSR Projects TSV without interpreting literal title quotes as CSV syntax."""
import csv

import pandas as pd


def read_projects(path_or_buffer, **kwargs):
    """Read a frame, or yield chunks when chunksize is supplied.

    ICPSR 37898 DS3 has tab-delimited fields and literal quotes in TITLE.
    Default CSV quoting can swallow subsequent records even if TITLE is excluded
    with usecols. Preserve pandas' existing missing-value and dtype behavior.
    """
    return pd.read_csv(path_or_buffer, sep="\t", quoting=csv.QUOTE_NONE, **kwargs)
