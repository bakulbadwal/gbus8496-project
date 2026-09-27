"""Recompute the existing exploratory table comparisons after rebuilding project features.

The fixed comparison inventory comes from main at 0778343, not from new outcome
screening. Old ambiguous True/False gift-decile labels are resolved by their
unchanged group sizes. No model selection or holdout tuning takes place here.
"""
from pathlib import Path
import json
import sys

import numpy as np
import pandas as pd
from scipy.stats import norm
from statsmodels.stats.multitest import multipletests

ROOT = Path(__file__).resolve().parents[1]


def rebuild(cohorts_path=None, output_dir=None):
    """Rebuild fixed group-versus-complement tables from sums and counts."""
    out = Path(output_dir or ROOT/'docs')
    out.mkdir(parents=True, exist_ok=True)
    d = pd.read_parquet(cohorts_path or ROOT/'data/processed/cohorts_with_projects.parquet')
    d = d[(d.split=='train') & (d.donor_type=='citizen donor')].copy()
    d['gift_decile'] = pd.qcut(d.first_gift_amount, 10, labels=False, duplicates='drop').astype(str)
    inventory = json.loads((ROOT/'evals/fixtures/feature_table_terms.json').read_text())
    columns = {col for rows in inventory.values() for r in rows for col in r['columns']}
    for col in columns:
        if col.endswith('>0'):
            raw = pd.to_numeric(d[col[:-2]], errors='coerce')
            d[col] = pd.Series(np.where(raw.isna(), 'Missing', np.where((raw>0).fillna(False), 'True', 'False')), index=d.index)
        else:
            d[col] = d[col].fillna('Missing').astype(str)
    d['_n'] = 1
    d['_y'] = d.gave_again.astype(int)
    d['_dollars'] = d.second_gift_amount.astype(float)
    d['_log'] = np.log1p(d._dollars).where(d._y.eq(1), 0)
    sums = ['_n', '_y', '_dollars', '_log']
    total = d[sums].sum()
    sd_y = d._y.std(ddof=0)
    sd_dollars = d._dollars.std(ddof=0)
    sd_log = d.loc[d._y.eq(1), '_log'].std(ddof=0)
    cache = {}
    def means(v):
        return v._y/v._n, v._dollars/v._n, v._log/v._y if v._y else np.nan
    def corr(n, nt, diff, sd):
        return np.sqrt(n/nt*(1-n/nt))*diff/sd if sd and n and n<nt else np.nan
    for name, specs in inventory.items():
        rows=[]
        for spec in specs:
            cols=tuple(spec['columns'])
            if cols not in cache:
                cache[cols] = d.groupby(list(cols), observed=True)[sums].sum()
            key=tuple(spec['values']) if len(cols)>1 else spec['values'][0]
            group=cache[cols]
            yes=group.loc[key] if key in group.index else total*0
            if spec['complement']:
                yes=total-yes
            no=total-yes
            if not yes._n or not no._n:
                continue
            py,vy,ly=means(yes); pn,vn,ln=means(no)
            row=dict(term_type=spec['term_type'],term=spec['term'],n_yes=int(yes._n),
                     repeat_rate_yes=py,repeat_rate_no=pn)
            if name=='term_effects_table_full':
                se=np.sqrt(py*(1-py)/yes._n+pn*(1-pn)/no._n)
                row.update(share_yes=yes._n/total._n,difference_pp=100*(py-pn),
                    corr_with_return=corr(yes._n,total._n,py-pn,sd_y),
                    p_value=2*norm.sf(abs(py-pn)/se) if se else np.nan,
                    ci_low_pp=100*(py-pn-1.96*se),ci_high_pp=100*(py-pn+1.96*se))
            else:
                row.update(expected_value_yes=vy,expected_value_no=vn,expected_value_difference=vy-vn,
                    corr_with_expected_value=corr(yes._n,total._n,vy-vn,sd_dollars),
                    n_returners_yes=int(yes._y),mean_log_amount_yes=ly,mean_log_amount_no=ln,
                    log_amount_difference=ly-ln,
                    corr_with_log_amount_returners=corr(yes._y,total._y,ly-ln,sd_log))
            rows.append(row)
        table=pd.DataFrame(rows)
        if name=='term_effects_table_full':
            table['q_value']=multipletests(table.p_value,method='fdr_bh')[1]
            table['significant_fdr_05']=table.q_value<.05
            table=table.sort_values('difference_pp',key=abs,ascending=False)
        else:
            table=table.sort_values('expected_value_difference',key=abs,ascending=False)
        table.to_csv(out/f'{name}.csv',index=False)
        print(f'{name}: {len(table):,} fixed comparisons recomputed')
        if name=='term_value_effects_full':
            table['effect_family']=table.term.str.split('=').str[0]
            table.loc[table.term_type=='gift-size decile','effect_family']='first_gift_size'
            picks=[]
            for metric,col in [('expected_value','expected_value_difference'),('conditional_amount','log_amount_difference')]:
                top=table.sort_values(col,key=abs,ascending=False).drop_duplicates('effect_family').head(10).copy()
                top['ranking_metric']=metric
                picks.append(top)
            pd.concat(picks).to_csv(out/'term_value_effects_unique_families.csv',index=False)


if __name__=='__main__':
    rebuild(*sys.argv[1:])
