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
                     "Average Order Value": "DIVIDE([Reported Order Value], [Order Count])",
                     "Full Month Order Value": 'CALCULATE([Reported Order Value], KEEPFILTERS(MonthlySales[coverage] = "Within coverage"))',
                     "Latest Full Month Growth": '''
VAR FullMonths = FILTER(ALL(MonthlySales), MonthlySales[coverage] = "Within coverage")
VAR Latest = MAXX(FullMonths, MonthlySales[month])
VAR Prior = MAXX(FILTER(FullMonths, MonthlySales[month] < Latest), MonthlySales[month])
VAR CurrentValue = SUMX(FILTER(FullMonths, MonthlySales[month] = Latest), MonthlySales[reported_order_value])
VAR PriorValue = SUMX(FILTER(FullMonths, MonthlySales[month] = Prior), MonthlySales[reported_order_value])
RETURN DIVIDE(CurrentValue - PriorValue, PriorValue)'''},
    "CustomerSegments": {"Repeat Purchaser Rate": "DIVIDE(SUM(CustomerSegments[repeat_purchasers]), SUM(CustomerSegments[purchasing_customers]))",
                         "Purchasing Customers": "SUM(CustomerSegments[purchasing_customers])",
                         "Repeat Purchasers": "SUM(CustomerSegments[repeat_purchasers])",
                         "Segment Order Value": "SUM(CustomerSegments[reported_order_value])",
                         "Purchase Participation": "DIVIDE([Purchasing Customers], SUM(CustomerSegments[registered_customers]))"},
    "ProductCategories": {"Supplied Item Value": "SUM(ProductCategories[supplied_item_value])"},
    "CampaignPerformance": {"Campaign Spend": "SUM(CampaignPerformance[spend])",
                            "Campaign Revenue": "SUM(CampaignPerformance[reported_campaign_revenue])",
                            "Campaign ROAS": "DIVIDE([Campaign Revenue], [Campaign Spend])",
                            "Cost per Conversion": "DIVIDE([Campaign Spend], SUM(CampaignPerformance[conversions]))",
                            "Campaign Conversions": "SUM(CampaignPerformance[conversions])",
                            "Click-Through Rate": "DIVIDE(SUM(CampaignPerformance[clicks]), SUM(CampaignPerformance[impressions]))",
                            "Click-to-Conversion Rate": "DIVIDE(SUM(CampaignPerformance[conversions]), SUM(CampaignPerformance[clicks]))"},
}
PERCENT = {"Repeat Purchaser Rate", "Click-Through Rate", "Click-to-Conversion Rate",
           "Purchase Participation", "Latest Full Month Growth"}
INTEGER = {"Order Count", "Purchasing Customers", "Repeat Purchasers", "Campaign Conversions"}
INK = "#14283E"
TEAL = "#007F78"
CANVAS = "#F0F5F7"


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
                 else '0.00"×"' if key == "Campaign ROAS" else "#,##0.00"} for key, expr in MEASURES[name].items()]
    return {"name": name, "columns": columns, "measures": measures, "partitions": [
        {"name": name, "mode": "import", "source": {"type": "m", "expression": lines}}]}


def projection(table, name, kind):
    return {"field": {kind: {"Expression": {"SourceRef": {"Entity": table}}, "Property": name}},
            "queryRef": f"{table}.{name}", "nativeQueryRef": name, "active": True}


def literal(value):
    return {"expr": {"Literal": {"Value": value}}}


def color(value):
    return {"solid": {"color": literal(f"'{value}'")}}


def container(fill="#FFFFFF"):
    return {"background": [{"properties": {"show": literal("true"), "color": color(fill),
                                            "transparency": literal("0D")}}]}


def emit_visual(page, name, rectangle, definition):
    x, y, width, height = rectangle
    save(REPORT / "definition" / "pages" / page / "visuals" / name / "visual.json",
         {"$schema": f"{SCHEMA}/visualContainer/2.0.0/schema.json", "name": name,
          "position": {"x": x, "y": y, "z": 0, "width": width, "height": height},
          "visual": definition})


def textbox(page, name, rectangle, lines, fill):
    paragraphs = [{"textRuns": [{"value": value, "textStyle": {
        "fontFamily": "Segoe UI", "fontSize": f"{size}pt", "color": foreground,
        "fontWeight": weight}}]} for value, size, foreground, weight in lines]
    emit_visual(page, name, rectangle, {"visualType": "textbox",
        "objects": {"general": [{"properties": {"paragraphs": paragraphs}}]},
        "visualContainerObjects": container(fill)})


def visual(page, name, visual_type, table, rectangle, groups=(), measures=(), title=None):
    query = {}
    if visual_type == "tableEx":
        query["Values"] = {"projections": [projection(table, g, "Column") for g in groups]
                           + [projection(table, m, "Measure") for m in measures]}
    else:
        if groups:
            query["Category"] = {"projections": [projection(table, g, "Column") for g in groups]}
        query["Y" if visual_type != "card" else "Values"] = {
            "projections": [projection(table, m, "Measure") for m in measures]}
    if visual_type in {"lineChart", "barChart", "columnChart"}:
        sort = projection(table, groups[0], "Column") if visual_type == "lineChart" else projection(table, measures[0], "Measure")
        sort_definition = {"sort": [{"field": sort["field"], "direction": "Ascending" if visual_type == "lineChart" else "Descending"}]}
    else:
        sort_definition = None
    definition = {"visualType": visual_type, "query": {"queryState": query}, "drillFilterOtherVisuals": True}
    if sort_definition:
        definition["query"]["sortDefinition"] = sort_definition
    definition["visualContainerObjects"] = container()
    if title:
        definition["visualContainerObjects"]["title"] = [{"properties": {
            "show": literal("true"), "text": literal("'" + title + "'"), "fontColor": color(INK),
            "fontSize": literal("13D"), "bold": literal("true")}}]
    if visual_type == "card":
        definition["objects"] = {
            "labels": [{"properties": {"color": color(TEAL), "fontSize": literal("27D"),
                                       "labelDisplayUnits": literal("0D")}}],
            "categoryLabels": [{"properties": {"show": literal("false")}}],
        }
    emit_visual(page, name, rectangle, definition)


def cards(page, table, items):
    for index, (measure, title) in enumerate(items):
        visual(page, f"Kpi{index + 1}", "card", table, (28 + 330 * index, 128, 314, 102),
               measures=(measure,), title=title)


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
    subtitles = {
        "SalesOverview": "Track order value, volume and recent sales momentum",
        "CustomerInsights": "Compare customer segments and identify repeat purchase opportunities",
        "MarketingPerformance": "Compare reported return and conversion costs by channel",
    }
    notes = {
        "SalesOverview": "March 2023 and November 2024 are partial. Item values use quantity times unit price and do not reconcile to reported order totals. Currency unspecified.",
        "CustomerInsights": "Repeat rate counts purchasers with at least two orders. Participation compares purchasing customers with all registered customers in each segment.",
        "MarketingPerformance": "ROAS uses total reported campaign revenue divided by spend. Cost per conversion uses spend divided by recorded conversions. Attribution and currency unspecified.",
    }
    for index, (key, label) in enumerate(pages.items(), 1):
        save(REPORT / "definition" / "pages" / key / "page.json", {
            "$schema": f"{SCHEMA}/page/2.0.0/schema.json", "name": key, "displayName": label,
            "displayOption": "FitToPage", "width": 1360, "height": 760,
            "objects": {"background": [{"properties": {"color": color(CANVAS), "transparency": literal("0D")}}]}})
        textbox(key, "PageHeader", (28, 20, 1304, 100), [
            (f"0{index}  /  SALES PERFORMANCE", 9, "#8BF0E3", "bold"),
            (label, 25, "#FFFFFF", "bold"),
            (subtitles[key], 11, "#DCE9F1", "normal")], INK)
        textbox(key, "PageNote", (28, 700, 1304, 38),
                [(notes[key], 11, INK, "normal")], "#E2EEF1")

    cards("SalesOverview", "MonthlySales", [
        ("Reported Order Value", "Reported order value"), ("Order Count", "Orders"),
        ("Average Order Value", "Avg. order value"), ("Latest Full Month Growth", "Latest full month vs prior")])
    visual("SalesOverview", "MonthlyTrend", "lineChart", "MonthlySales", (28, 248, 808, 258),
           ("month",), ("Full Month Order Value",), "Reported order value | Full months only")
    visual("SalesOverview", "MonthlyDetail", "tableEx", "MonthlySales", (28, 522, 808, 162),
           ("month", "coverage"), ("Reported Order Value", "Order Count", "Average Order Value"), "Monthly results")
    visual("SalesOverview", "ProductMix", "barChart", "ProductCategories", (852, 248, 480, 436),
           ("category",), ("Supplied Item Value",), "Supplied item value by category")

    cards("CustomerInsights", "CustomerSegments", [
        ("Purchasing Customers", "Purchasing customers"), ("Repeat Purchasers", "Repeat purchasers"),
        ("Repeat Purchaser Rate", "Repeat purchase rate"), ("Purchase Participation", "Purchase participation")])
    visual("CustomerInsights", "SegmentSales", "barChart", "CustomerSegments", (28, 248, 644, 232),
           ("customer_segment",), ("Segment Order Value",), "Reported order value by segment")
    visual("CustomerInsights", "SegmentParticipation", "barChart", "CustomerSegments", (688, 248, 644, 232),
           ("customer_segment",), ("Purchase Participation",), "Purchase participation by segment")
    visual("CustomerInsights", "RepeatPurchasing", "tableEx", "CustomerSegments", (28, 496, 1304, 188),
           ("customer_segment",), ("Purchasing Customers", "Repeat Purchasers", "Repeat Purchaser Rate", "Purchase Participation"),
           "Customer activity by segment")

    cards("MarketingPerformance", "CampaignPerformance", [
        ("Campaign Spend", "Campaign spend"), ("Campaign ROAS", "Reported ROAS"),
        ("Campaign Conversions", "Recorded conversions"), ("Cost per Conversion", "Cost per conversion")])
    visual("MarketingPerformance", "ChannelROAS", "barChart", "CampaignPerformance", (28, 248, 644, 212),
           ("channel",), ("Campaign ROAS",), "Reported ROAS by channel")
    visual("MarketingPerformance", "ChannelCost", "barChart", "CampaignPerformance", (688, 248, 644, 212),
           ("channel",), ("Cost per Conversion",), "Cost per conversion by channel")
    visual("MarketingPerformance", "CampaignMetrics", "tableEx", "CampaignPerformance", (28, 476, 1304, 208),
           ("channel", "campaign_name"), ("Campaign Spend", "Campaign Revenue", "Campaign ROAS",
           "Campaign Conversions", "Cost per Conversion", "Click-Through Rate", "Click-to-Conversion Rate"),
           "Campaign results by channel")


if __name__ == "__main__":
    main()
