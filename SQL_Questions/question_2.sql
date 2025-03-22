-- #########################################################
-- Soru 2 - En Çok Satılan Ürünler (Kategori Bazında)

WITH ProductSales AS (
    SELECT 
        p.category, 
        p.product_name, 
        SUM(oi.quantity) AS total_quantity,
        RANK() OVER (
            PARTITION BY p.category 
            ORDER BY SUM(oi.quantity) DESC
        ) AS sales_rank
    FROM Products p
    JOIN OrderItems oi ON p.product_id = oi.product_id
    GROUP BY p.category, p.product_name
)
SELECT category, product_name, total_quantity
FROM ProductSales
WHERE sales_rank <= 3
ORDER BY category, sales_rank;