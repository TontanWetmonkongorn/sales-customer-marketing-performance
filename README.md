# Sales, Customer & Marketing Performance Analysis

An academic analytics project being rebuilt from six professor-provided CSV files. The original classroom Power BI report was located locally. This repository contains the reproducible source-data audit, SQLite analysis, and an aggregate browser report.

## Open the Connected Sales dashboard

Download the repository and open [Connected Sales.pbip](power-bi/connected/Connected%20Sales.pbip) in Power BI Desktop. Select **Refresh now** if prompted. The public dashboard uses **synthetic demonstration data** so anyone can explore the four pages without the classroom CSVs. The audit and findings below describe the classroom analysis and will differ from the demo KPIs.

The model connects Customers to Orders, Orders to Order Items and Feedback, Products to Order Items, and Calendar to Orders and Marketing. Six one-to-many relationships support segment and period filtering. A shared date supports period comparisons across sales and marketing. Campaign-to-order attribution requires an additional key.

## What the dashboard answers

These answers use the **synthetic data in Connected Sales**, with the month filter set to **All** unless specified. The classroom findings below use the original dataset.

| Business question | Where to look | What the dashboard shows | What to do with it |
| --- | --- | --- | --- |
| Did sales soften because fewer orders came in or because orders were smaller? | **Sales Overview** → Monthly results and Orders by month | Reported order value fell **3.57%** from September to October 2024, from **62,320 to 60,093**. Orders fell from **85 to 82**, while average order value stayed near **733**. | Investigate order volume first. Compare those two full months and exclude partial November. |
| Which customer segment deserves a closer look? | **Customer Insights** → Reported order value by segment and Average feedback rating by customer segment | **Premium** led reported order value at **302,318** and had the lowest average rating at **3.60 out of 5**. | Review Premium feedback before planning a retention campaign. |
| What should the team investigate for Premium customers? | **Sales and Customer Feedback** → select **Premium**, then read the rating and feedback-category charts | The filter returns **385 responses**. **App Experience** was the most frequent category (**102 responses**), followed by **Product Quality** (**96**). | Review the App Experience responses first. Category counts indicate discussion volume, so check ratings before calling them complaints. |
| Which channel merits a follow-up campaign test? | **Marketing Performance** → Reported ROAS by channel and Cost per conversion by channel | **Social Media** had the lowest cost per recorded conversion (**16.30**) and the highest calculated ROAS (**4.473×**), very close to **Email (4.470×)**. Both display as **4.47×** at two decimals. | Test Social Media against Email before shifting budget. Reported ROAS does not establish incremental impact. |

## Data

| File | Records | Grain |
| --- | ---: | --- |
| customers.csv | 2,500 | Customer |
| products.csv | 268 | Product |
| orders.csv | 5,000 | Order |
| order_items.csv | 5,000 | Supplied item record |
| customer_feedback.csv | 5,000 | Feedback record |
| marketing_performance.csv | 5,400 | Campaign observation |

Source: professor-provided classroom materials. Original publisher, license, currency, and whether records are synthetic have not been confirmed. Raw CSVs are retained locally and excluded from this repository. The published demonstration rows are generated. Original classroom records are excluded.

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

- Completed: source inventory, reproducible checks, SQL analysis, aggregate browser report, and business recommendations.
- The native Power BI project and Excel PivotTable have been verified. Source definitions such as currency and campaign attribution remain unspecified.



## Reproduce the portfolio report

Run `python src/analyze.py` to execute the four SQLite queries and write aggregate CSVs to `data/processed/`. Then run `python src/report.py` and open `reports/portfolio.html` in a browser. See [methods and findings](docs/methods-and-findings.md) for interpretation and interview explanations. The original classroom Power BI report was located and retained locally. The native Excel PivotTable has been verified against SQLite for all 21 observed months. Generate it on Windows with Excel installed by running `powershell -File src/build_excel.ps1` after the SQL export. See [Power BI rebuild files](power-bi/README.md) for typed imports, DAX measures, and page checks. Open the [previous aggregate Power BI project](power-bi/Sales%20Performance.pbip) in Desktop. On first open, use Refresh now to load the embedded aggregate tables.
