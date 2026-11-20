"""Run the portfolio queries and export aggregate tables for Excel or Power BI."""

import argparse
import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = {
    "orders": "order_id customer_id order_date order_total",
    "customers": "customer_id customer_segment",
    "products": "product_id category",
    "order_items": "order_id product_id quantity unit_price",
    "marketing_performance": "channel campaign_name impressions clicks conversions spend revenue_generated",
}


def build(data_dir, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(":memory:") as db:
        for table, fields in TABLES.items():
            columns = fields.split()
            db.execute(f"CREATE TABLE {table} ({', '.join(columns)})")
            placeholders = ", ".join("?" for _ in columns)
            with (data_dir / f"{table}.csv").open(encoding="utf-8-sig", newline="") as stream:
                db.executemany(
                    f"INSERT INTO {table} VALUES ({placeholders})",
                    ([row[column] for column in columns] for row in csv.DictReader(stream)),
                )
        for query in sorted((ROOT / "sql").glob("*.sql")):
            result = db.execute(query.read_text(encoding="utf-8"))
            with (output_dir / f"{query.stem}.csv").open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(column[0] for column in result.description)
                writer.writerows(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data" / "raw")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data" / "processed")
    args = parser.parse_args()
    build(args.data_dir, args.output_dir)
