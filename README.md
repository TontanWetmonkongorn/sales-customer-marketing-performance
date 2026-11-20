# Sales, Customer & Marketing Performance Analysis

An academic analytics project being rebuilt from six professor-provided CSV files. The original Power BI file is unavailable. This repository currently contains the reproducible source-data audit and a dashboard rebuild specification; the rebuilt dashboard is pending.

## Business questions

- How do reported order value and order volume change over time?
- Which customer segments account for the most purchases?
- Which campaigns have the strongest revenue-to-spend ratios?
- Which data inconsistencies affect interpretation?

## Data

| File | Records | Grain |
| --- | ---: | --- |
| customers.csv | 2,500 | Customer |
| products.csv | 268 | Product |
| orders.csv | 5,000 | Order |
| order_items.csv | 5,000 | Supplied item record |
| customer_feedback.csv | 5,000 | Feedback record |
| marketing_performance.csv | 5,400 | Campaign observation |

Source: professor-provided classroom materials. Original publisher, license, currency, and whether records are synthetic have not been confirmed. Raw CSVs are retained locally and excluded from this repository. No customer names, contact details, addresses, or record-level data are published here.

## Reproduce the audit

Requires Python 3.11+; no third-party packages.

Place the six original CSVs in `data/raw/`, then run from the repository root:

```sh
python src/audit.py
```

Alternatively, pass their directory with `python src/audit.py --data-dir PATH`.
The audit writes aggregate results to `reports/data_audit.json`. It does not modify source files. A successful run means the audit executed, not that all data passed validation.

## Initial findings

- 4,999 of 5,000 reported order totals differ from supplied item extensions by more than 0.02 currency units.
- 5,348 marketing observations have supplied ROAS differing from revenue divided by spend by more than 0.02 ratio units.
- 1,568 delivery classifications disagree with an exact comparison of actual and promised timestamps. A business grace period has not been documented.
- Primary customer, product, order and feedback IDs are unique in the supplied snapshots. Checked order/customer and item/order/product links have no unmatched references.

These are reconciliation questions, not proof that a particular source field is wrong. Order value and item value must remain separate; recalculated ROAS must be labeled explicitly. See [audit results](reports/data_audit.json) and [dashboard specification](docs/dashboard_specification.md).

## Status

- Completed: source inventory, reproducible structural and reconciliation checks.
- Pending: source-definition clarification, SQL analysis, Power Query transformations, Power BI measures and three report pages, screenshots, and business recommendations.

The repository does not claim implemented revenue improvements or a completed Power BI dashboard.
