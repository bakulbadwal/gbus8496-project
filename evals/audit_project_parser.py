"""Verify the official Projects file and quantify old versus corrected parsing.

No raw records are exported. Run from a clean clone with downloaded raw data:
    python evals/audit_project_parser.py
"""
import csv
import hashlib
import json
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from features import PROJECT_KEEP
from projects import read_projects


def main():
    path=ROOT/'data/raw/ICPSR_37898/DS0003/37898-0003-Data.tsv'
    digest=hashlib.md5()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):
            digest.update(block)
    assert digest.hexdigest()=='37e7bd5ac4af5b71545fc6538c5be3dd'
    widths={}
    with path.open(newline='') as f:
        reader=csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE)
        header=next(reader)
        for row in reader:
            widths[len(row)]=widths.get(len(row),0)+1
    assert len(header)==28 and widths=={28:2_149_817}
    old=pd.read_csv(path,sep='\t',usecols=PROJECT_KEEP,dtype='string').set_index('PROJECT_ID')
    new=read_projects(path,usecols=PROJECT_KEEP,dtype='string').set_index('PROJECT_ID')
    assert old.index.is_unique and new.index.is_unique
    common=old.index.intersection(new.index)
    changed=old.loc[common].fillna('<MISSING>').ne(new.loc[common].fillna('<MISSING>'))
    c=pd.read_parquet(ROOT/'data/processed/cohorts.parquet')
    old_missing=~c.first_project_id.isin(old.index)
    new_missing=~c.first_project_id.isin(new.index)
    affected_ids=changed.index[changed.any(axis=1)]
    result=dict(project_file_md5=digest.hexdigest(),physical_row_width_counts=widths,
                old_project_rows=len(old),corrected_project_rows=len(new),
                recovered_project_ids=len(new.index.difference(old.index)),
                common_project_ids_with_changed_fields=len(affected_ids),
                changed_project_fields=changed.sum().astype(int).to_dict(),
                old_missing_cohort_rows=int(old_missing.sum()),new_missing_cohort_rows=int(new_missing.sum()),
                old_missing_citizen_rows=int((old_missing&c.donor_type.eq('citizen donor')).sum()),
                new_missing_citizen_rows=int((new_missing&c.donor_type.eq('citizen donor')).sum()),
                cohort_rows_with_changed_existing_project_fields=int(c.first_project_id.isin(affected_ids).sum()))
    print(json.dumps(result,indent=2))
    (ROOT/'evals/results/project_parser_audit.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':
    main()
