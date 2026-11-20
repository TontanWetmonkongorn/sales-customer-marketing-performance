# Dashboard rebuild specification

## Planned pages

1. Sales overview: reported order value, distinct order count, reported average order value, monthly movement, and separate item-value breakdown by category.
2. Customer insights: purchasing customers, observed repeat purchasers, segment-level reported order value, and purchasing recency within the observed dataset.
3. Marketing performance: spend, impressions, clicks, conversions, reported campaign revenue, and recalculated revenue-to-spend ratio.

## Metric definitions

| Metric | Definition | Limitation |
| --- | --- | --- |
| Reported order value | Sum of orders.order_total | Unreconciled with items; currency, tax and refund treatment unknown |
| Orders | Distinct orders.order_id | Do not interpret delivery statuses as cancellation flags |
| Reported average order value | Reported order value / distinct orders | Same order-value limitations |
| Supplied item value | Sum of quantity multiplied by unit_price | Separate basis from reported order totals; completeness unresolved |
| Observed repeat purchasers | Customers with at least two supplied orders | Does not establish lifetime retention |
| Click-through rate | Sum of clicks / sum of impressions | Return blank for zero denominator |
| Click-to-conversion rate | Sum of conversions / sum of clicks | Conversion definition and attribution window unknown |
| Recalculated ROAS | Sum of revenue_generated / sum of spend | Do not average supplied row ratios; attribution unverified |

## Model

Customers filter Orders through customer_id. Orders filter Order Items through order_id; Products filter Order Items through product_id. Verify cardinalities before configuring relationships. Connect Feedback to Orders through order_id after checking multiplicity and customer agreement; avoid a second active customer path that introduces ambiguity.

Add a Date dimension and derive date-only order dates. Keep Marketing as a separate fact connected to Date; it has no order/customer attribution key. Do not join marketing directly to orders by date, audience label, or campaign name. Check campaign_id uniqueness rather than assuming a campaign dimension key.

Customer total_orders and avg_order_value are supplied attributes. Recompute purchase behavior from Orders for the observed period and compare before using supplied summaries. Do not infer profit from product margin_percentage until its meaning and cost basis are confirmed.

## Data decisions to resolve

- Determine why almost all order totals disagree with supplied item value.
- Clarify supplied ROAS, currency and campaign revenue attribution.
- Determine whether the delivery classifications use a grace period.
- Confirm data publisher, redistribution permission and synthetic status.
- Do not invent pipeline stages, sales targets, or customer acquisition attribution.

## Completion checks

Reconcile dashboard totals to independent SQL results, validate filter behavior and weighted ratios, label incomplete edge months, and export readable screenshots. Include three supported findings with recommendations once interpretation is defensible.
