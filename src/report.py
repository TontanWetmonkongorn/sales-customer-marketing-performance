"""Generate a browser-ready report from the aggregate query results."""
import csv
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def section(title, table, label_fields, value_field, caption, decimals=0):
    with (ROOT / "data" / "processed" / (table + ".csv")).open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    highest = max(float(row[value_field]) for row in rows) or 1
    bars = []
    for row in rows:
        label = escape(" · ".join(row[key] for key in label_fields))
        value = float(row[value_field])
        bars.append(f'<li><span>{label}</span><meter min="0" max="{highest}" value="{value}"></meter>'
                    f'<strong>{value:,.{decimals}f}</strong></li>')
    return f'<section><h2>{title}</h2><p>{caption}</p><ul>{"".join(bars)}</ul></section>'


def main():
    sections = [
        section("Monthly reported order value", "monthly_sales", ("month", "coverage"),
                "reported_order_value", "March 2023 and November 2024 are partial months. Currency is unspecified."),
        section("Repeat purchasers by customer segment", "customer_segments", ("customer_segment",),
                "repeat_pct_of_purchasers", "Percent of purchasing customers who placed at least two orders during the observed period.", 2),
        section("Supplied item value by category", "product_categories", ("category",),
                "supplied_item_value", "Quantity × unit price, summed by category. The supplied items do not reconcile to order totals."),
        section("Campaign return on ad spend", "campaign_performance", ("channel", "campaign_name"),
                "recalculated_roas", "Total reported campaign revenue divided by total spend for each campaign and channel.", 3),
    ]
    output = ROOT / "reports" / "portfolio.html"
    output.write_text("""<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sales, Customer &amp; Marketing Performance</title>
<style>
body{font:16px system-ui;margin:0;background:#edf4f2;color:#172e31}
main{max-width:900px;margin:auto;padding:clamp(16px,4vw,48px)}
header{padding:30px;background:#173d41;color:white;border-radius:18px}h1{margin:0}
section{background:white;padding:24px;margin:20px 0;border-radius:16px}h2{margin-top:0}
ul{list-style:none;padding:0}li{display:grid;grid-template-columns:minmax(0,2fr) minmax(30px,2fr) 6em;gap:12px;align-items:center;margin:8px 0}
meter{width:100%;accent-color:#137e73}strong{text-align:right;font-variant-numeric:tabular-nums}
</style><main><header><h1>Sales, Customer &amp; Marketing Performance</h1>
<p>Academic portfolio analysis · 5,000 orders · March 2023 to November 2024</p></header>"""
                      + "\n".join(sections) + "</main></html>\n", encoding="utf-8")


if __name__ == "__main__":
    main()
