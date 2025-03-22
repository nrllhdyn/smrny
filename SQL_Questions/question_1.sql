-- ############################################
-- Soru 1 - Kümülatif Toplam (Cumulative Sum/Running Total)

SELECT 
    o.customer_id, 
    o.order_date, 
    SUM(oi.quantity * oi.unit_price) OVER (
        PARTITION BY o.customer_id 
        ORDER BY o.order_date 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_total
FROM Orders o
JOIN OrderItems oi ON o.order_id = oi.order_id
ORDER BY o.customer_id, o.order_date;
