# Power BI rebuild

Run `python src/analyze.py` to generate the four inputs in `data/processed`. In a new Power BI Desktop file, add a text parameter named `ExportFolder` pointing to that folder. Create a blank Power Query named `LoadAggregate` and paste the contents of [LoadAggregate.pq](LoadAggregate.pq) into its Advanced Editor. Create four more blank queries using these expressions.

```powerquery
// MonthlySales
LoadAggregate(ExportFolder, "monthly_sales.csv",
    {{"month", type text}, {"orders", Int64.Type},
     {"reported_order_value", Currency.Type}, {"average_order_value", Currency.Type},
     {"coverage", type text}})

// CustomerSegments
LoadAggregate(ExportFolder, "customer_segments.csv",
    {{"customer_segment", type text}, {"registered_customers", Int64.Type},
     {"purchasing_customers", Int64.Type}, {"repeat_purchasers", Int64.Type},
     {"repeat_pct_of_purchasers", type number}, {"reported_order_value", Currency.Type}})

// ProductCategories
LoadAggregate(ExportFolder, "product_categories.csv",
    {{"category", type text}, {"supplied_units", Int64.Type}, {"supplied_item_value", Currency.Type}})

// CampaignPerformance
LoadAggregate(ExportFolder, "campaign_performance.csv",
    {{"channel", type text}, {"campaign_name", type text}, {"impressions", Int64.Type},
     {"clicks", Int64.Type}, {"conversions", Int64.Type}, {"spend", Currency.Type},
     {"reported_campaign_revenue", Currency.Type}, {"ctr_pct", type number},
     {"click_conversion_pct", type number}, {"recalculated_roas", type number}})
```

Each input has its own **grain**, or what a row represents. Keep these aggregate tables disconnected. For example, a row in MonthlySales describes a month, while a row in CustomerSegments describes a segment over the full analysis period. Use filters from the same table as the visual. The [transaction-level specification](../docs/dashboard_specification.md) describes a separate model for future cross-filtering.

Add the [DAX measures](measures.dax) individually. A **measure** recalculates for the current selection. When several campaigns are selected, ROAS divides their combined revenue by their combined spend. Configure amounts as decimal numbers with no currency symbol because the source currency is unspecified.

| Page | Visuals | Check |
| --- | --- | --- |
| Sales Overview | Order value, orders and average order value cards. Monthly line chart with coverage in the tooltip. Separate bar chart for supplied item value by category. | 5,000 orders. Flag March 2023 and November 2024 as partial. |
| Customer Insights | Segment bars for reported value and a matrix with purchasing customers, repeat purchasers and repeat purchaser rate. | Regular has 574 purchasing customers and 400 repeat purchasers. |
| Marketing Performance | Spend and ROAS cards. Campaign and channel matrix with clicks, conversions, CTR, and ROAS. | Email / Referral Program is approximately 2.207×. |

The original classroom PBIX is local. These files are build inputs for a new report and have not been executed in Power BI Desktop.
