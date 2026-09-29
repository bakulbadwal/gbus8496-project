"""Audit packet/note associations without treating snapshot flags as interventions.

Run `python evals/thank_you_audit.py` after label construction. Results are small
aggregate tables only; no raw donor records are exported. No model is trained.
"""
from pathlib import Path
import sys
import hashlib
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from projects import read_projects
OUT = ROOT / 'evals/results/thank_you_audit'
RAW = ROOT / 'data/raw/ICPSR_37898'
BANDS = [0, 10, 25, 50, 100, 250, 1000, np.inf]
LABELS = ['<10', '10–24.99', '25–49.99', '50–99.99', '100–249.99', '250–999.99', '1000+']


def save(name, table):
    """Write and display a compact, reproducible aggregate table."""
    table.to_csv(OUT / f'{name}.csv', index=False)
    print(f'\n{name}\n{table.to_string(index=False, float_format=lambda x: f"{x:,.5f}")}')


def describe(frame, keys):
    """Every row is a donor, outcome is giving in months M+1 through M+12."""
    return frame.groupby(keys, observed=True, dropna=False).agg(
        donors=('gave_again', 'size'), repeat_rate=('gave_again', 'mean'),
        mean_future_dollars=('second_gift_amount', 'mean'),
        packet_rate=('packet', 'mean')).reset_index()


def standardized(frame, exposure, strata, label, minimum=100):
    """Pooled-population standardization on cells with >=100 in BOTH groups.

    Reports overlap explicitly; no extrapolation to unsupported cells and no
    causal interpretation. Funding restrictions are descriptive, post-gift
    selections, not pre-treatment adjustment. No independence-based p-values.
    """
    a = frame.groupby(strata + [exposure], observed=True).gave_again.agg(['size', 'mean'])
    n = a['size'].unstack(exposure).reindex(columns=[False, True]).fillna(0)
    rate = a['mean'].unstack(exposure).reindex(columns=[False, True])
    valid = n.min(axis=1) >= minimum
    if not valid.any():
        return dict(analysis=label, source_donors=len(frame), supported_donors=0,
                    coverage=0.0, cells=0, repeat_no=np.nan, repeat_yes=np.nan, gap_pp=np.nan)
    weights = n.loc[valid].sum(axis=1)
    weights = weights / weights.sum()
    rates = rate.loc[valid].mul(weights, axis=0).sum()
    return dict(analysis=label, source_donors=len(frame), supported_donors=int(n.loc[valid].sum().sum()),
                coverage=float(n.loc[valid].sum().sum()/len(frame)), cells=int(valid.sum()),
                repeat_no=float(rates[False]), repeat_yes=float(rates[True]),
                gap_pp=float(100*(rates[True]-rates[False])))


def return_months(cit):
    """Stream all donations to verify single-row flags and build timing sensitivity.

    Use the same positive-amount, M+1..M+12 rules as src/labels.py. M+4..M+12
    is a sensitivity outcome, NOT a post-mailing outcome or landmark design.
    """
    lookup = cit[['donor_id', 'cohort_month', 'first_month_gifts', 'packet', 'first_gift_amount',
                  'first_project_id']].copy()
    lookup['row'] = np.arange(len(cit))
    lookup = lookup.set_index('donor_id')
    earliest = np.full(len(cit), 999, dtype=np.int16)
    late = np.zeros(len(cit), dtype=bool)
    first_single_rows = flag_mismatch = amount_mismatch = project_mismatch = 0
    cols = ['DONOR_ID', 'PROJECT_ID', 'AMOUNT', 'CREATED_MONTH', 'THANK_YOU_PACKET_MAILED']
    for number, chunk in enumerate(pd.read_csv(RAW/'DS0001/37898-0001-Data.tsv', sep='\t', usecols=cols,
                             dtype={'DONOR_ID':str, 'PROJECT_ID':str}, chunksize=500_000), start=1):
        chunk = chunk[chunk.AMOUNT > 0].join(lookup, on='DONOR_ID', how='inner')
        dates = pd.to_datetime(chunk.CREATED_MONTH, format='%Y-%m', errors='raise')
        delta = ((dates.dt.year-2000)*12 + dates.dt.month-1 - chunk.cohort_month).to_numpy()
        idx = chunk.row.to_numpy(dtype=int)
        inside = (delta >= 1) & (delta <= 12)
        np.minimum.at(earliest, idx[inside], delta[inside].astype(np.int16))
        late[idx[(delta >= 4) & (delta <= 12)]] = True
        single = chunk[(delta == 0) & (chunk.first_month_gifts == 1)]
        flags = single.THANK_YOU_PACKET_MAILED.astype(str).str.lower().str.strip()
        assert flags.isin(['yes', 'no', 't', 'f', 'true', 'false', '1', '0']).all()
        first_single_rows += len(single)
        flag_mismatch += int((flags.isin(['yes', 't', 'true', '1']) != single.packet).sum())
        amount_mismatch += int((~np.isclose(single.AMOUNT, single.first_gift_amount)).sum())
        project_mismatch += int((single.PROJECT_ID != single.first_project_id).sum())
        if number % 5 == 0:
            print(f'  donation chunks checked: {number}', flush=True)
    assert first_single_rows == int((cit.first_month_gifts == 1).sum())
    assert flag_mismatch == amount_mismatch == project_mismatch == 0
    assert np.array_equal(earliest <= 12, cit.gave_again.astype(bool))
    cit['earliest_repeat_offset'] = earliest
    cit['repeat_4_12'] = late
    return dict(verified_single_first_month_rows=first_single_rows, flag_mismatches=flag_mismatch,
                amount_mismatches=amount_mismatch, project_mismatches=project_mismatch,
                all_citizen_repeat_labels_match=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    c = pd.read_parquet(ROOT/'data/processed/cohorts.parquet')
    assert c.donor_id.is_unique
    assert c.first_thank_you_packet.notna().all()
    c['packet'] = c.first_thank_you_packet.astype(bool)
    save('01_packet_by_population', describe(c, ['donor_type', 'packet']))
    cit = c[c.donor_type == 'citizen donor'].copy().reset_index(drop=True)
    checks = return_months(cit)
    cit['year'] = cit.cohort.str[:4].astype(int)
    cit['band'] = pd.cut(cit.first_gift_amount, BANDS, right=False, labels=LABELS)
    save('02_packet_by_split', describe(cit, ['split', 'packet']))
    save('03_packet_by_year', describe(cit, ['year', 'packet']))
    save('04_packet_by_band', describe(cit, ['band', 'packet']))

    fields = ['PROJECT_ID', 'THANKYOU_NOTE', 'IMPACT_LETTER', 'PROJECT_STATUS_AS_OF_12_31_2019',
              'POSTED_MONTH', 'DAYS_BETWEEN_POSTED_AND_COMPLE_1']
    project_path = RAW/'DS0003/37898-0003-Data.tsv'
    # ICPSR TSV has literal quotes in TITLE; default CSV quoting swallows 5,513
    # records. All 2,149,817 physical data lines have exactly 28 tab fields.
    p = read_projects(project_path, usecols=fields, dtype=str, keep_default_na=False)
    assert len(p) == 2_149_817
    h = hashlib.md5()
    with project_path.open('rb') as source:
        for block in iter(lambda: source.read(8*1024*1024), b''):
            h.update(block)
    checks['projects_md5'] = h.hexdigest()
    assert h.hexdigest() == '37e7bd5ac4af5b71545fc6538c5be3dd'
    assert p.PROJECT_ID.is_unique
    for col in ['THANKYOU_NOTE', 'IMPACT_LETTER']:
        p[col] = p[col].str.strip()
        assert p[col].isin(['', 'MASKED BY ICPSR']).all()
    save('05_project_note_coverage', p.groupby(['PROJECT_STATUS_AS_OF_12_31_2019', 'THANKYOU_NOTE',
                                              'IMPACT_LETTER']).size().reset_index(name='projects'))
    cit = cit.merge(p.rename(columns={'PROJECT_ID':'first_project_id'}), on='first_project_id',
                    how='left', validate='many_to_one', indicator=True)
    checks.update(project_rows=len(p), citizen_donors=len(cit),
                  multirow_first_month_donors=int((cit.first_month_gifts > 1).sum()),
                  unmatched_citizen_donors=int((cit._merge == 'left_only').sum()))
    # For notes and project timing, one donation in the first month gives an
    # unambiguous project. Multi-row donors are retained only in packet summaries.
    one = cit[(cit.first_month_gifts == 1) & (cit._merge == 'both')].copy()
    one['note'] = one.THANKYOU_NOTE.eq('MASKED BY ICPSR')
    one['impact'] = one.IMPACT_LETTER.eq('MASKED BY ICPSR')
    one['status'] = one.PROJECT_STATUS_AS_OF_12_31_2019
    save('06_note_and_funding', describe(one, ['status', 'note']))
    save('07_packet_note_combinations', describe(one, ['packet', 'note']))
    funded = one[one.status == 'funded'].copy()
    save('08_funded_packet_note_combinations', describe(funded, ['packet', 'note']))
    save('09_impact_and_funding', describe(one, ['status', 'impact']))

    strata = ['year', 'band', 'first_teacher_referred', 'first_matched', 'first_gift_card']
    adjusted = [standardized(cit, 'packet', strata, 'All citizens: packet'),
                standardized(one, 'packet', strata, 'Single first-month row, matched project: packet'),
                standardized(funded, 'packet', strata, 'Single row, funded: packet'),
                standardized(funded[funded.first_gift_amount >= 50], 'packet', strata,
                             'Single row, funded, amount >=50: packet'),
                standardized(one, 'note', strata, 'Single row, matched project: note'),
                standardized(funded, 'note', strata, 'Single row, funded: note')]
    save('10_standardized_associations', pd.DataFrame(adjusted))

    # Cutoff diagnostics using all single-row donors (including project nonmatches).
    single = cit[cit.first_month_gifts == 1].copy()
    a = single.first_gift_amount
    cents = np.rint(a*100).astype(np.int64)
    masks = [('45–<50 vs 50–<55', (a>=45)&(a<50), (a>=50)&(a<55)),
             ('45–<50 vs >50–<55', (a>=45)&(a<50), (a>50)&(a<55)),
             ('Non-multiple-of-5 whole dollars 41–49 vs 51–59',
              (a>=41)&(a<50)&(cents%100==0)&(cents%500!=0),
              (a>50)&(a<=59)&(cents%100==0)&(cents%500!=0))]
    cuts = []
    for split in ['all', 'train', 'holdout']:
        scope = np.ones(len(single), bool) if split == 'all' else single.split.eq(split)
        for name, lm, hm in masks:
            lo, hi = single[lm & scope], single[hm & scope]
            dp = hi.packet.mean()-lo.packet.mean()
            dy = hi.gave_again.mean()-lo.gave_again.mean()
            cuts.append(dict(split=split, comparison=name, n_below=len(lo), n_above=len(hi),
                             packet_below=lo.packet.mean(), packet_above=hi.packet.mean(),
                             repeat_below=lo.gave_again.mean(), repeat_above=hi.gave_again.mean(),
                             packet_gap_pp=100*dp, repeat_gap_pp=100*dy,
                             descriptive_ratio=dy/dp if abs(dp)>1e-8 else np.nan))
    save('11_cutoff_sensitivity_NOT_CAUSAL', pd.DataFrame(cuts))
    near = single[(a>=40)&(a<61)].copy()
    near['dollar_bin'] = np.floor(near.first_gift_amount).astype(int)
    save('12_cutoff_dollar_bins', describe(near, ['dollar_bin']))
    checks['exactly_50_single_donors'] = int((cents == 5000).sum())
    checks['single_donors_45_to_under55'] = int(((a>=45)&(a<55)).sum())
    save('13_cutoff_composition', single[(a>=45)&(a<55)].assign(
        side=np.where(a[(a>=45)&(a<55)]<50, 'below', 'at_or_above')).groupby('side').agg(
            donors=('gave_again','size'), teacher_referred=('first_teacher_referred','mean'),
            matched=('first_matched','mean'), gift_card=('first_gift_card','mean'),
            mean_year=('year','mean')).reset_index())

    save('14_return_timing', cit.groupby('packet').agg(
        donors=('gave_again','size'), repeats=('gave_again','sum'),
        repeat_month_1=('earliest_repeat_offset', lambda x: (x==1).sum()),
        repeat_by_month_3=('earliest_repeat_offset', lambda x: (x<=3).sum()),
        any_repeat_months_4_12=('repeat_4_12','mean')).reset_index())
    # Completion is funded/expired/reallocated per the dictionary. Restrict to
    # funded, nonnegative valid durations. Unknown posted day gives an INTERVAL.
    posted = pd.to_datetime(funded.POSTED_MONTH, format='%Y-%m', errors='coerce')
    days = pd.to_numeric(funded.DAYS_BETWEEN_POSTED_AND_COMPLE_1, errors='coerce')
    valid = posted.notna() & days.notna() & days.ge(0)
    earliest_completion = posted + pd.to_timedelta(days.where(valid), unit='D')
    end = (pd.PeriodIndex(funded.cohort, freq='M') + funded.earliest_repeat_offset.to_numpy() + 1).to_timestamp()
    before = valid & funded.gave_again.eq(1) & (end <= earliest_completion)
    timing = []
    for label, mask in [('All funded single-row donors', np.ones(len(funded), bool)),
                        ('Packet recorded yes', funded.packet), ('Digital note recorded', funded.note)]:
        positive = mask & valid & funded.gave_again.eq(1)
        timing.append(dict(group=label, donors=int(np.sum(mask)), valid_duration=int((mask&valid).sum()),
                           repeaters_with_valid_duration=int(positive.sum()),
                           definitely_repeated_before_funding=int((mask&before).sum()),
                           share_of_repeaters=float((mask&before).sum()/positive.sum())))
    save('15_before_funding_lower_bound', pd.DataFrame(timing))
    checks['funded_single_row_donors'] = len(funded)
    checks['funded_invalid_or_negative_duration'] = int((~valid).sum())
    checks['single_row_matched_donors'] = len(one)
    (OUT/'checks.json').write_text(json.dumps(checks, indent=2)+'\n')
    print('\nChecks:', json.dumps(checks, indent=2))
    print('\nAll comparisons are retrospective associations; no treatment effect identified.')
    make_figure()


def make_figure():
    """Plot raw return rates and cutoff instability, without implying causation."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':11,
                         'axes.spines.top':False, 'axes.spines.right':False})
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5), gridspec_kw={'width_ratios':[1, 1.35]})
    tab = pd.read_csv(OUT/'01_packet_by_population.csv')
    tab = tab[tab.donor_type == 'citizen donor'].sort_values('packet')
    bars = axes[0].bar(['No packet recorded', 'Packet recorded'], 100*tab.repeat_rate,
                      color=['#a0acb8', '#227a86'], width=.55)
    axes[0].bar_label(bars, labels=[f'{v:.1%}\nn = {n:,}' for v,n in zip(tab.repeat_rate,tab.donors)], padding=8)
    axes[0].set_ylim(0,27)
    axes[0].set_ylabel('Gave again within 12 months (%)')
    axes[0].set_title('A positive association', loc='left', fontweight='bold')
    cuts = pd.read_csv(OUT/'11_cutoff_sensitivity_NOT_CAUSAL.csv')
    cuts = cuts[cuts.split=='all']
    labels = ['Include exactly $50', 'Exclude exactly $50', 'Selected non-round\nwhole-dollar gifts']
    colors = ['#a0acb8', '#a0acb8', '#227a86']
    bars = axes[1].barh(labels, cuts.repeat_gap_pp, color=colors, height=.5)
    for i, v in enumerate(cuts.repeat_gap_pp):
        axes[1].text(v/2, i, f'{v:+.2f} pp', ha='center', va='center',
                     color='white' if v>0 else '#1f2c37', fontsize=10)
    axes[1].axvline(0,color='#344352',lw=.8)
    axes[1].invert_yaxis()
    axes[1].set_xlim(-3.4,3.0)
    axes[1].set_xlabel('Repeat-rate gap above versus below $50\n(percentage points)')
    axes[1].set_title('The cutoff conclusion changes with the sample', loc='left', fontweight='bold')
    fig.suptitle('Thank-you packets: association is measurable; causal impact is not identified',
                 x=.06, ha='left', fontsize=15, fontweight='bold')
    fig.text(.06,.035,'ICPSR 37898; first observed citizen-donor cohorts 2003–2018. Right: one donation in first month.\n'
             'Retrospective snapshot flags; no mailing dates. Comparisons are not treatment-effect estimates.',
             color='#475462',fontsize=10)
    fig.tight_layout(rect=[.03,.12,.98,.91],w_pad=3)
    fig.savefig(ROOT/'docs/thank_you_audit.png',dpi=180)
    plt.close(fig)


if __name__ == '__main__':
    main()
