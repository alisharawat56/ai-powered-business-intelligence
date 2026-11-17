
-- Customer purchase behavior

SELECT
    c.customer_unique_id,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(oi.price)::numeric, 2) AS total_revenue,
    ROUND(AVG(oi.price)::numeric, 2) AS average_item_price

FROM customers c

INNER JOIN orders o
    ON c.customer_id = o.customer_id

INNER JOIN order_items oi
    ON o.order_id = oi.order_id

WHERE o.order_status = 'delivered'

GROUP BY c.customer_unique_id

ORDER BY total_revenue DESC;



-- Repeat purchase rate

WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS total_orders

    FROM customers c

    INNER JOIN orders o
        ON c.customer_id = o.customer_id

    WHERE o.order_status = 'delivered'

    GROUP BY c.customer_unique_id
)

SELECT
    COUNT(*) AS total_customers,

    COUNT(*) FILTER (
        WHERE total_orders >= 2
    ) AS repeat_customers,

    ROUND(
        (
            COUNT(*) FILTER (
                WHERE total_orders >= 2
            ) * 100.0 / COUNT(*)
        )::numeric,
        2
    ) AS repeat_purchase_rate_percentage

FROM customer_orders;



-- Top 10 customers by revenue

WITH customer_revenue AS (
    SELECT
        c.customer_unique_id,
        SUM(oi.price) AS total_revenue,
        COUNT(DISTINCT o.order_id) AS total_orders

    FROM customers c

    INNER JOIN orders o
        ON c.customer_id = o.customer_id

    INNER JOIN order_items oi
        ON o.order_id = oi.order_id

    WHERE o.order_status = 'delivered'

    GROUP BY c.customer_unique_id
)

SELECT
    customer_unique_id,
    total_orders,
    ROUND(total_revenue::numeric, 2) AS total_revenue,

    RANK() OVER (
        ORDER BY total_revenue DESC
    ) AS customer_rank

FROM customer_revenue

ORDER BY customer_rank

LIMIT 10;



-- Customer revenue segmentation using NTILE


WITH customer_revenue AS (
    SELECT
        c.customer_unique_id,
        SUM(oi.price) AS total_revenue,
        COUNT(DISTINCT o.order_id) AS total_orders
    FROM customers c
    INNER JOIN orders o
        ON c.customer_id = o.customer_id
    INNER JOIN order_items oi
        ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
),
ranked_customers AS (
    SELECT
        *,
        NTILE(10) OVER (ORDER BY total_revenue DESC) AS revenue_decile
    FROM customer_revenue
),
segment_summary AS (
    SELECT
        CASE
            WHEN revenue_decile IN (1, 2) THEN 'High Value'
            WHEN revenue_decile IN (3, 4, 5) THEN 'Mid Value'
            ELSE 'Low Value'
        END AS customer_segment,
        COUNT(*) AS total_customers,
        SUM(total_revenue) AS segment_revenue,
        AVG(total_revenue) AS avg_customer_revenue,
        MIN(revenue_decile) AS first_decile
    FROM ranked_customers
    GROUP BY 1
)
SELECT
    customer_segment,
    total_customers,
    ROUND(segment_revenue::numeric, 2) AS segment_revenue,
    ROUND(avg_customer_revenue::numeric, 2) AS avg_customer_revenue
FROM segment_summary
ORDER BY first_decile;



-- Payment analysis

SELECT
    p.payment_type,
    COUNT(DISTINCT p.order_id) AS total_orders,
    ROUND(SUM(p.payment_value)::numeric, 2) AS total_payment,
    ROUND(AVG(p.payment_value)::numeric, 2) AS avg_payment
FROM payments p
INNER JOIN orders o
    ON p.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY p.payment_type
ORDER BY total_payment DESC;