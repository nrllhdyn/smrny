-- ##########################################################
-- Soru 3 - Sipariş Aralıklarını Bulma

WITH OrderGaps AS (
    SELECT 
        customer_id, 
        order_date, 
        LAG(order_date) OVER (
            PARTITION BY customer_id 
            ORDER BY order_date
        ) AS previous_order_date
    FROM Orders
)
SELECT 
    customer_id, 
    AVG(order_date - previous_order_date) AS avg_order_gap
FROM OrderGaps
WHERE previous_order_date IS NOT NULL
GROUP BY customer_id;