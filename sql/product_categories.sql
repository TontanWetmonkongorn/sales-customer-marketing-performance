SELECT p.category, SUM(CAST(i.quantity AS INTEGER)) AS supplied_units,
       ROUND(SUM(CAST(i.quantity AS INTEGER) * CAST(i.unit_price AS REAL)), 2) AS supplied_item_value
FROM order_items i
JOIN products p USING (product_id)
GROUP BY p.category
ORDER BY supplied_item_value DESC;
