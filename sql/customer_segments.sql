WITH purchasing AS (
    SELECT customer_id, COUNT(DISTINCT order_id) AS orders,
           SUM(CAST(order_total AS REAL)) AS reported_value
    FROM orders
    GROUP BY customer_id
)
SELECT c.customer_segment, COUNT(*) AS registered_customers,
       COUNT(p.customer_id) AS purchasing_customers,
       SUM(CASE WHEN p.orders >= 2 THEN 1 ELSE 0 END) AS repeat_purchasers,
       ROUND(100.0 * SUM(CASE WHEN p.orders >= 2 THEN 1 ELSE 0 END)
             / NULLIF(COUNT(p.customer_id), 0), 2) AS repeat_pct_of_purchasers,
       ROUND(COALESCE(SUM(p.reported_value), 0), 2) AS reported_order_value
FROM customers c
LEFT JOIN purchasing p USING (customer_id)
GROUP BY c.customer_segment
ORDER BY reported_order_value DESC;
