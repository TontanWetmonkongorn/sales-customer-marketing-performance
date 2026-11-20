"""Create an editable Power BI project from the four aggregate SQL exports."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "power-bi"
REPORT = PROJECT / "Sales Performance.Report"
MODEL = PROJECT / "Sales Performance.SemanticModel"
SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition"
TABLES = {
    "MonthlySales": ("monthly_sales", {"month", "coverage"}),
    "CustomerSegments": ("customer_segments", {"customer_segment"}),
    "ProductCategories": ("product_categories", {"category"}),
    "CampaignPerformance": ("campaign_performance", {"channel", "campaign_name"}),
}
MEASURES = {
    "MonthlySales": {"Reported Order Value": "SUM(MonthlySales[reported_order_value])",
                     "Order Count": "SUM(MonthlySales[orders])",
                     "Average Order Value": "DIVIDE([Reported Order Value], [Order Count])"},
    "CustomerSegments": {"Repeat Purchaser Rate": "DIVIDE(SUM(CustomerSegments[repeat_purchasers]), SUM(CustomerSegments[purchasing_customers]))",
                         "Purchasing Customers": "SUM(CustomerSegments[purchasing_customers])",
                         "Repeat Purchasers": "SUM(CustomerSegments[repeat_purchasers])",
                         "Segment Order Value": "SUM(CustomerSegments[reported_order_value])"},
    "ProductCategories": {"Supplied Item Value": "SUM(ProductCategories[supplied_item_value])"},
    "CampaignPerformance": {"Campaign Spend": "SUM(CampaignPerformance[spend])",
                            "Campaign Revenue": "SUM(CampaignPerformance[reported_campaign_revenue])",
                            "Campaign ROAS": "DIVIDE([Campaign Revenue], [Campaign Spend])",
                            "Click-Through Rate": "DIVIDE(SUM(CampaignPerformance[clicks]), SUM(CampaignPerformance[impressions]))",
                            "Click-to-Conversion Rate": "DIVIDE(SUM(CampaignPerformance[conversions]), SUM(CampaignPerformance[clicks]))"},
}
PERCENT = {"Repeat Purchaser Rate", "Click-Through Rate", "Click-to-Conversion Rate"}
INTEGER = {"Order Count", "Purchasing Customers", "Repeat Purchasers"}


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def model_table(name, export, text_fields):
    with (ROOT / "data" / "processed" / f"{export}.csv").open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)
    columns = [{"name": f, "sourceColumn": f, "dataType": "string" if f in text_fields else "double",
                "summarizeBy": "none"} for f in fields]
    table_type = ", ".join(f'{f} = {"text" if f in text_fields else "number"}' for f in fields)
    lines = [f"#table(type table [{table_type}], {{"]
    for i, row in enumerate(rows):
        values = [json.dumps(row[f], ensure_ascii=False) if f in text_fields else row[f] or "null" for f in fields]
        lines.append("    {" + ", ".join(values) + "}" + ("," if i < len(rows) - 1 else ""))
    lines.append("})")
    measures = [{"name": key, "expression": expr,
                 "formatString": "0.00%" if key in PERCENT else "#,##0" if key in INTEGER
                 else "0.000" if key == "Campaign ROAS" else "#,##0.00"} for key, expr in MEASURES[name].items()]
    return {"name": name, "columns": columns, "measures": measures, "partitions": [
        {"name": name, "mode": "import", "source": {"type": "m", "expression": lines}}]}


def projection(table, name, kind):
    return {"field": {kind: {"Expression": {"SourceRef": {"Entity": table}}, "Property": name}},
            "queryRef": f"{table}.{name}", "nativeQueryRef": name, "active": True}


def visual(page, name, visual_type, table, rectangle, groups=(), measures=(), title=None):
    x, y, width, height = rectangle
    query = {}
    if visual_type == "tableEx":
        query["Values"] = {"projections": [projection(table, g, "Column") for g in groups]
                           + [projection(table, m, "Measure") for m in measures]}
    else:
        if groups:
            query["Category"] = {"projections": [projection(table, g, "Column") for g in groups]}
        query["Y" if visual_type != "card" else "Values"] = {
            "projections": [projection(table, m, "Measure") for m in measures]}
    definition = {"visualType": visual_type, "query": {"queryState": query}, "drillFilterOtherVisuals": True}
    if title:
        definition["visualContainerObjects"] = {"title": [{"properties": {
            "show": {"expr": {"Literal": {"Value": "true"}}},
            "text": {"expr": {"Literal": {"Value": "'" + title + "'"}}}}}]}
    save(REPORT / "definition" / "pages" / page / "visuals" / name / "visual.json",
         {"$schema": f"{SCHEMA}/visualContainer/2.0.0/schema.json", "name": name,
          "position": {"x": x, "y": y, "z": 0, "width": width, "height": height},
          "visual": definition})


def main():
    save(PROJECT / "Sales Performance.pbip", {"version": "1.0", "artifacts": [
        {"report": {"path": "Sales Performance.Report"}}], "settings": {"enableAutoRecovery": True}})
    save(MODEL / "definition.pbism", {"version": "1.0", "settings": {}})
    save(MODEL / "model.bim", {"name": "Sales Performance", "compatibilityLevel": 1600,
                              "model": {"culture": "en-US", "defaultPowerBIDataSourceVersion": "powerBI_V3",
                                        "tables": [model_table(name, *source) for name, source in TABLES.items()]}})
    save(REPORT / "definition.pbir", {"version": "4.0", "datasetReference": {
        "byPath": {"path": "../Sales Performance.SemanticModel"}}})
    save(REPORT / "definition" / "version.json", {"$schema": f"{SCHEMA}/versionMetadata/1.0.0/schema.json", "version": "2.0.0"})
    save(REPORT / "definition" / "report.json", {"$schema": f"{SCHEMA}/report/2.0.0/schema.json",
                                                 "themeCollection": {}})
    pages = {"SalesOverview": "Sales Overview", "CustomerInsights": "Customer Insights", "MarketingPerformance": "Marketing Performance"}
    save(REPORT / "definition" / "pages" / "pages.json", {
        "$schema": f"{SCHEMA}/pagesMetadata/1.0.0/schema.json", "pageOrder": list(pages), "activePageName": next(iter(pages))})
    for key, label in pages.items():
        save(REPORT / "definition" / "pages" / key / "page.json", {
            "$schema": f"{SCHEMA}/page/2.0.0/schema.json", "name": key, "displayName": label,
            "displayOption": "FitToPage", "width": 1360, "height": 760})
    visual("SalesOverview", "MonthlyTrend", "lineChart", "MonthlySales", (30, 25, 1300, 360),
           ("month",), ("Reported Order Value",), "Monthly order value | Mar 2023 and Nov 2024 partial")
    visual("SalesOverview", "MonthlyDetail", "tableEx", "MonthlySales", (30, 410, 665, 320),
           ("month", "coverage"), ("Order Count", "Average Order Value"), "Order counts and average value")
    visual("SalesOverview", "ProductMix", "barChart", "ProductCategories", (720, 410, 610, 320),
           ("category",), ("Supplied Item Value",), "Supplied item value by category")
    visual("CustomerInsights", "SegmentSales", "barChart", "CustomerSegments", (30, 25, 1300, 340),
           ("customer_segment",), ("Segment Order Value",), "Reported order value by segment")
    visual("CustomerInsights", "RepeatPurchasing", "tableEx", "CustomerSegments", (30, 390, 1300, 340),
           ("customer_segment",), ("Purchasing Customers", "Repeat Purchasers", "Repeat Purchaser Rate"),
           "Repeat purchasing within the observed period")
    visual("MarketingPerformance", "CampaignMetrics", "tableEx", "CampaignPerformance", (30, 25, 1300, 700),
           ("channel", "campaign_name"), ("Campaign Spend", "Campaign Revenue", "Campaign ROAS",
           "Click-Through Rate", "Click-to-Conversion Rate"), "Campaign results by channel")


if __name__ == "__main__":
    main()
