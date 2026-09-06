"""
compute_metrics.py — Reproducible metric computation for the quick-commerce FMCG capstone.

Reads data/raw_sourced_table.csv (verified consolidated line items, FY2019-FY2025),
computes all derived metrics per the data dictionary (average-balance basis), and writes:
  outputs/metrics_full_series.csv        — FY2020-FY2025 metric values per company
  outputs/pre_post_comparison.csv        — FY20-22 vs FY24-25 averages + FY23-25 sensitivity
Run: python src/compute_metrics.py
"""
import pandas as pd
import numpy as np

YEARS = ['FY19','FY20','FY21','FY22','FY23','FY24','FY25']
STUDY = YEARS[1:]
PRE, TRANS, POST = ['FY20','FY21','FY22'], 'FY23', ['FY24','FY25']

raw = pd.read_csv('data/raw_sourced_table.csv')
key = {'Revenue from operations':'rev','Other income':'oi','Cost of materials consumed':'com',
 'Purchases of stock-in-trade':'psit','Changes in inventories of FG/WIP/stock-in-trade':'chg',
 'Finance costs':'fc','Depreciation and amortisation expense':'da',
 'Profit before exceptional items and tax (PBEIT)':'pbeit',
 'Net profit attributable to Owners of the Company':'np','Inventories':'inv',
 'Trade receivables':'tr','Trade payables (MSME dues + other dues)':'tp',
 'Total assets':'ta','Total current liabilities':'tcl'}
raw['k'] = raw['line_item'].map(key)
raw = raw.dropna(subset=['k'])
wide = raw.pivot_table(index=['company','fiscal_year'], columns='k', values='value_inr_crore').reset_index()

rows = []
for co, d in wide.groupby('company'):
    d = d.set_index('fiscal_year').reindex(YEARS)
    cogs = d.com + d.psit + d.chg
    ebitda = d.pbeit + d.fc + d.da - d.oi
    ebit = ebitda - d.da
    ce = d.ta - d.tcl
    avg = lambda s: (s.shift(1) + s) / 2
    m = pd.DataFrame({
        'DIO': avg(d.inv)/cogs*365, 'DSO': avg(d.tr)/d.rev*365, 'DPO': avg(d.tp)/cogs*365,
        'GrossMargin': (d.rev-cogs)/d.rev, 'EBITDAMargin': ebitda/d.rev, 'NetMargin': d.np/d.rev,
        'ROCE': ebit/avg(ce), 'ROA': d.np/avg(d.ta), 'RevGrowth': d.rev.pct_change()})
    m['CCC'] = m.DIO + m.DSO - m.DPO
    m['company'] = co
    rows.append(m.loc[STUDY].reset_index())
full = pd.concat(rows)
full.to_csv('outputs/metrics_full_series.csv', index=False)

comp = []
for co, d in full.groupby('company'):
    d = d.set_index('fiscal_year')
    for metric in ['DIO','DSO','DPO','CCC','GrossMargin','EBITDAMargin','NetMargin','ROCE','ROA','RevGrowth']:
        pre = d.loc[PRE, metric].mean(); post = d.loc[POST, metric].mean()
        sens = d.loc[[TRANS]+POST, metric].mean()
        comp.append({'company':co,'metric':metric,'pre_FY20_22':pre,'FY23_transition':d.loc[TRANS,metric],
                     'post_FY24_25':post,'abs_change':post-pre,
                     'pct_change':(post-pre)/abs(pre) if pre else np.nan,
                     'sens_post_FY23_25':sens,'sens_abs_change':sens-pre})
pd.DataFrame(comp).to_csv('outputs/pre_post_comparison.csv', index=False)

# Sensitivity: geometric (CAGR) revenue growth vs the arithmetic period-average used above.
# Pre = FY19->FY22 CAGR (3y), Post = FY23->FY25 CAGR (2y), FY23-25 sensitivity = FY22->FY25 CAGR (3y).
cag = []
for co, d in wide.groupby('company'):
    r = d.set_index('fiscal_year')['rev']
    g_ = lambda a, b, n: (r[b] / r[a]) ** (1 / n) - 1
    cag.append({'company': co,
                'pre_FY20_22_arith': full[full.company == co].set_index('fiscal_year').loc[PRE, 'RevGrowth'].mean(),
                'pre_FY20_22_cagr': g_('FY19', 'FY22', 3),
                'post_FY24_25_arith': full[full.company == co].set_index('fiscal_year').loc[POST, 'RevGrowth'].mean(),
                'post_FY24_25_cagr': g_('FY23', 'FY25', 2),
                'sens_FY23_25_cagr': g_('FY22', 'FY25', 3)})
pd.DataFrame(cag).to_csv('outputs/revenue_growth_cagr_check.csv', index=False)
print('Wrote outputs/metrics_full_series.csv, outputs/pre_post_comparison.csv and outputs/revenue_growth_cagr_check.csv')
