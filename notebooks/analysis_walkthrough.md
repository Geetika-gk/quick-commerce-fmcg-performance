# Analysis Walkthrough

Reproducible pipeline (run from repo root):

1. `python src/compute_metrics.py` — reads `data/raw_sourced_table.csv` (verified, per-observation-sourced consolidated line items), computes all metrics on the average-balance basis defined in `data/data_dictionary.csv`, writes `outputs/metrics_full_series.csv`, `outputs/pre_post_comparison.csv`, and `outputs/revenue_growth_cagr_check.csv` (a CAGR-based robustness check on revenue growth, alongside the arithmetic-average figures used as primary).
2. `python src/make_charts.py` — regenerates the six charts in `outputs/charts/`.

The Excel workbook in `data/` contains the same computations as live formulas and serves as the manually-auditable twin of the Python pipeline; the two were diff-checked to zero mismatches during verification (294 derived values: 98 computed metric/intermediate cells per company across the workbook's three company sheets). This is distinct from the 315 raw line-item observations in data/raw_sourced_table.csv, each of which was separately verified against scanned statement pages.
