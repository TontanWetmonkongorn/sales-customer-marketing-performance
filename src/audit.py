"""Read classroom CSVs without modifying them; publish aggregate checks only."""
import argparse
import csv
import hashlib
import json
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = ('customers', 'products', 'orders', 'order_items',
         'customer_feedback', 'marketing_performance')


def audit(data_dir):
    tables, inventory = {}, {}
    for name in NAMES:
        path = data_dir / (name + '.csv')
        with path.open(encoding='utf-8-sig', newline='') as stream:
            reader = csv.DictReader(stream)
            rows = list(reader)
            if not reader.fieldnames or not rows:
                raise ValueError(f'{name}: missing columns or empty dataset')
            if any(None in row or any(v is None for v in row.values()) for row in rows):
                raise ValueError(f'{name}: malformed row')
            tables[name] = rows
            inventory[name] = {
                'rows': len(rows), 'columns': reader.fieldnames,
                'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'blank_cells': sum(not value.strip() for row in rows for value in row.values())}
    orders = tables['orders']
    order_ids = {r['order_id'] for r in orders}
    customer_ids = {r['customer_id'] for r in tables['customers']}
    product_ids = {r['product_id'] for r in tables['products']}
    extensions = defaultdict(Decimal)
    for row in tables['order_items']:
        extensions[row['order_id']] += Decimal(row['quantity']) * Decimal(row['unit_price'])
    marketing = tables['marketing_performance']
    tolerance = Decimal('0.02')
    result = {
        'status': 'REVIEW',
        'scope': 'Initial checks only; source definitions and business validity unresolved',
        'inventory': inventory,
        'duplicate_primary_ids': {
            name: len(tables[name]) - len({r[key] for r in tables[name]})
            for name, key in [('customers', 'customer_id'), ('products', 'product_id'),
                              ('orders', 'order_id'), ('customer_feedback', 'feedback_id')]},
        'unmatched_order_customers': sum(r['customer_id'] not in customer_ids for r in orders),
        'unmatched_item_orders': sum(r['order_id'] not in order_ids for r in tables['order_items']),
        'unmatched_item_products': sum(r['product_id'] not in product_ids for r in tables['order_items']),
        'order_item_total_differences_over_0_02': sum(
            abs(Decimal(r['order_total']) - extensions[r['order_id']]) > tolerance for r in orders),
        'roas_differences_over_0_02': sum(
            abs(Decimal(r['roas']) - Decimal(r['revenue_generated']) / Decimal(r['spend'])) > tolerance
            for r in marketing if Decimal(r['spend']) != 0),
        'zero_spend_marketing_rows': sum(Decimal(r['spend']) == 0 for r in marketing),
        'on_time_label_timestamp_disagreements': sum(
            (datetime.fromisoformat(r['actual_delivery_time']) <=
             datetime.fromisoformat(r['promised_delivery_time'])) != (r['delivery_status'] == 'On Time')
            for r in orders),
        'date_ranges': {name: [min(r[key] for r in tables[name]), max(r[key] for r in tables[name])]
                        for name, key in [('orders', 'order_date'), ('marketing_performance', 'date')]}}
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=ROOT / 'data' / 'raw')
    args = parser.parse_args()
    result = audit(args.data_dir)
    output = ROOT / 'reports' / 'data_audit.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('Audit executed; unresolved issues require review. See reports/data_audit.json')
