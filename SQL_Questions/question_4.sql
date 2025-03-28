-- ##########################################################
-- ## Soru 4 - Ürün Öneri Sistemi

WITH ProductSales AS (
    SELECT
        p.product_id,
        SUM(oi.quantity) AS total_quantity_sold
    FROM
        Products p
    JOIN
        OrderItems oi ON p.product_id = oi.product_id
    GROUP BY
        p.product_id
),
CustomerPurchasedCategories AS (
    -- Müşterinin daha önce satın aldığı kategoriler
    SELECT DISTINCT
        o.customer_id,
        p.category
    FROM
        Orders o
    JOIN
        OrderItems oi ON o.order_id = oi.order_id
    JOIN
        Products p ON oi.product_id = p.product_id
    WHERE
        o.customer_id = 1 -- Verilen müşteri ID'si (örneğin 1)
),
SameCategoryRecommendations AS (
    -- Aynı kategorideki öneriler (Öncelik 1)
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.price,
        ps.total_quantity_sold,
        'Same Category' AS recommendation_reason,
        1 AS priority
    FROM
        Products p
    JOIN
        ProductSales ps ON p.product_id = ps.product_id
    WHERE
        p.category IN (SELECT category FROM CustomerPurchasedCategories WHERE customer_id = 1)
        AND p.product_id NOT IN (
            SELECT oi.product_id
            FROM Orders o
            JOIN OrderItems oi ON o.order_id = oi.order_id
            WHERE o.customer_id = 1
        )
),
CustomerPurchaseHistory AS (
    -- Her müşterinin satın alma geçmişi (kategoriler ve ürünler)
    SELECT
        o.customer_id,
        p.category,
        oi.product_id
    FROM
        Orders o
    JOIN
        OrderItems oi ON o.order_id = oi.order_id
    JOIN
        Products p ON oi.product_id = p.product_id
),
CustomerSimilarity AS (
    -- Müşteri benzerlik puanı hesaplama (Öncelik 2 için)
    SELECT
        c1.customer_id AS target_customer_id,
        c2.customer_id AS similar_customer_id,
        -- Kategori benzerliği
        COUNT(DISTINCT CASE WHEN c1_hist.category = c2_hist.category THEN c1_hist.category END) AS common_categories_count,
        -- Ürün benzerliği
        COUNT(DISTINCT CASE WHEN c1_hist.product_id = c2_hist.product_id THEN c1_hist.product_id END) AS common_products_count
    FROM
        (SELECT DISTINCT customer_id FROM Orders) c1 -- Tüm müşteriler (target)
    CROSS JOIN
        (SELECT DISTINCT customer_id FROM Orders) c2 -- Tüm müşteriler (similar)
    JOIN
        CustomerPurchaseHistory c1_hist ON c1.customer_id = c1_hist.customer_id
    JOIN
        CustomerPurchaseHistory c2_hist ON c2.customer_id = c2_hist.customer_id
    WHERE
        c1.customer_id = 1 -- Verilen müşteri ID'si (örneğin 1)
        AND c1.customer_id <> c2.customer_id -- Kendisiyle benzerliği hesaplama
    GROUP BY
        c1.customer_id, c2.customer_id
),
WeightedSimilarity AS (
    -- Ağırlıklı benzerlik puanı
    SELECT
        target_customer_id,
        similar_customer_id,
        (0.6 * common_categories_count + 0.4 * common_products_count) AS weighted_similarity_score
    FROM
        CustomerSimilarity
),
SimilarCustomerRecommendations AS (
    -- Benzer müşterilerden öneriler (Öncelik 2)
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.price,
        ps.total_quantity_sold,
        'Similar Customer' AS recommendation_reason,
        2 AS priority
    FROM
        WeightedSimilarity ws
    JOIN
        Orders o_similar ON ws.similar_customer_id = o_similar.customer_id
    JOIN
        OrderItems oi_similar ON o_similar.order_id = oi_similar.order_id
    JOIN
        Products p ON oi_similar.product_id = p.product_id
    JOIN
        ProductSales ps ON p.product_id = ps.product_id
    WHERE
        ws.target_customer_id = 1 -- Verilen müşteri ID'si (örneğin 1)
        AND p.product_id NOT IN (
            SELECT oi.product_id
            FROM Orders o_target
            JOIN OrderItems oi ON o_target.order_id = oi.order_id
            WHERE o_target.customer_id = 1
        )
    GROUP BY
        p.product_id, p.product_name, p.category, p.price, ps.total_quantity_sold, ws.weighted_similarity_score
    ORDER BY
        ws.weighted_similarity_score DESC
    LIMIT 10 -- En benzer müşterilerden en fazla 10 öneri (isteğe bağlı)
),
BestSellingRecommendations AS (
    -- En çok satan ürünler (Öncelik 3)
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.price,
        ps.total_quantity_sold,
        'Best Selling' AS recommendation_reason,
        3 AS priority
    FROM
        Products p
    JOIN
        ProductSales ps ON p.product_id = ps.product_id
    ORDER BY
        ps.total_quantity_sold DESC
    LIMIT 5 -- En çok satan ilk 5 ürün
),
CombinedRecommendations AS (
    -- Tüm önerileri birleştir ve ROW_NUMBER() ekle
    SELECT
        product_id,
        product_name,
        category,
        price,
        total_quantity_sold,
        recommendation_reason,
        priority,
        ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY priority) as rn -- ROW_NUMBER ekle
    FROM
        (
            SELECT product_id, product_name, category, price, total_quantity_sold, recommendation_reason, priority FROM SameCategoryRecommendations
            UNION ALL
            SELECT product_id, product_name, category, price, total_quantity_sold, recommendation_reason, priority FROM SimilarCustomerRecommendations
            UNION ALL
            SELECT product_id, product_name, category, price, total_quantity_sold, recommendation_reason, priority FROM BestSellingRecommendations
        ) AS SubQuery -- Alt sorguya isim ver
)
-- Sonuç: En alakalı 5 ürünü seç ve önceliğe göre sırala, tekrarları kaldır
SELECT
    product_id,
    product_name,
    category,
    price,
    total_quantity_sold
FROM
    CombinedRecommendations
WHERE
    rn = 1 -- Sadece ilk tekrarı (en yüksek öncelikli) seç
ORDER BY
    priority, product_id -- Önceliğe ve ürün ID'sine göre sırala (aynı öncelikteki ürünlerin tutarlılığı için)
LIMIT 5;