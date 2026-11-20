WITH monthly AS (
    SELECT substr(order_date, 1, 7) AS month,
           COUNT(DISTINCT order_id) AS orders,
           SUM(CAST(order_total AS REAL)) AS reported_value
    FROM orders
    GROUP BY substr(order_date, 1, 7)
)
SELECT month, orders, ROUND(reported_value, 2) AS reported_order_value,
       ROUND(reported_value / NULLIF(orders, 0), 2) AS average_order_value,
       CASE WHEN month IN ('2023-03', '2024-11') THEN 'Partial' ELSE 'Within coverage' END AS coverage
FROM monthly
ORDER BY month;
