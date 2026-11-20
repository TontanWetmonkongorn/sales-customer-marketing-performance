# Methods and findings

## Findings

1. The Regular segment had the highest reported order value (2.89 million in unspecified currency units) and 400 repeat purchasers among 574 purchasing customers. Inspect frequency and average order value separately before choosing a segment for a retention campaign.
2. The Inactive segment still included 518 customers who purchased during the observation period, including 350 repeat purchasers. Check when the segment label was assigned before using it to target a win-back campaign.
3. Email Referral Program had the highest recalculated ROAS among the observed channel and campaign combinations (2.207×). Check the attribution method and compare test groups before reallocating spending.

## Terms to explain in an interview

| Term | What it means here | How to check it |
| --- | --- | --- |
| Grain | What one row represents. An order row describes an order, while an item row describes a supplied product entry. | Check that order IDs are unique in Orders and count rows per order in Order Items before combining them. |
| JOIN | Combines records that share a key, such as a customer ID. | Check unique keys and unmatched records. Summarize orders by customer before joining to the customer list. |
| LEFT JOIN | Keeps every customer, including those without a recorded purchase. | Compare registered customers with purchasing customers. |
| CTE | A named intermediate SQL result. The customer query first calculates observed purchases per customer, then summarizes by segment. | Compare the intermediate order counts with the raw Orders table. |
| Reconciliation | An independent comparison of two totals expected to agree under the same definition. | Compare reported order totals with summed quantity × unit price per order. The disagreement is documented in the audit. |
| ROAS | Return on ad spend. Divide total reported campaign revenue by total spend for the same rows. | Compare the ratio with a manual calculation for one campaign. A simple average of row ratios gives every row equal weight regardless of spending. |
| PivotTable | An Excel summary that groups rows and aggregates values. | Build a PivotTable from the local order data with month as rows and sum of order_total as values, then compare it to the monthly SQL export. |
| Power Query | Imports and reshapes tables. | Import the four aggregate CSVs, set types explicitly, and check the imported row count against the exports. |
| DAX measure | A calculation evaluated for the filters applied to a Power BI visual. | Check that campaign ROAS changes to the ratio of the selected campaign's totals when filtered. |

For a Power BI report based on the aggregate tables, keep each export at its documented grain. Use `DIVIDE(SUM(Campaign[reported_campaign_revenue]), SUM(Campaign[spend]))` for campaign ROAS and validate it against the SQL result. Keep reported order value and item-derived category value in separate visuals. The original class PBIX was located locally. A refreshed native Power BI version has not been verified.
