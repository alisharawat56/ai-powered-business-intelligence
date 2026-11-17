
-- 1. Revenue by product category
-- Only delivered orders are included.
-- Freight is excluded from product revenue.

SELECT
    COALESCE(p.product_category_name, 'unknown') AS product_category,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(oi.order_item_id) AS total_items,
    ROUND(SUM(oi.price)::numeric, 2) AS total_revenue,
    ROUND(AVG(oi.price)::numeric, 2) AS avg_item_price

FROM orders o

INNER JOIN order_items oi
    ON o.order_id = oi.order_id

INNER JOIN products p
    ON oi.product_id = p.product_id

WHERE o.order_status = 'delivered'

GROUP BY p.product_category_name

ORDER BY total_revenue DESC;




-- 2. Monthly revenue analysis


WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC(
            'month',
            o.order_purchase_timestamp::timestamp
        ) AS revenue_month,

        SUM(oi.price) AS total_revenue,
        COUNT(DISTINCT o.order_id) AS total_orders

    FROM orders o

    INNER JOIN order_items oi
        ON o.order_id = oi.order_id

    WHERE o.order_status = 'delivered'

    GROUP BY DATE_TRUNC(
        'month',
        o.order_purchase_timestamp::timestamp
    )
)

SELECT
    TO_CHAR(revenue_month, 'YYYY-MM') AS month,

    ROUND(total_revenue::numeric, 2) AS revenue,

    total_orders,

    ROUND(
        (
            (
                total_revenue - LAG(total_revenue) OVER (
                    ORDER BY revenue_month
                )
            )
            / NULLIF(
                LAG(total_revenue) OVER (
                    ORDER BY revenue_month
                ),
                0
            ) * 100
        )::numeric,
        2
    ) AS revenue_growth_percentage

FROM monthly_revenue

ORDER BY revenue_month;



-- Monthly revenue with missing months included

WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC(
            'month',
            o.order_purchase_timestamp::timestamp
        ) AS revenue_month,
        SUM(oi.price) AS total_revenue,
        COUNT(DISTINCT o.order_id) AS total_orders

    FROM orders o

    INNER JOIN order_items oi
        ON o.order_id = oi.order_id

    WHERE o.order_status = 'delivered'

    GROUP BY 1
),

calendar AS (
    SELECT generate_series(
        (SELECT MIN(revenue_month) FROM monthly_revenue),
        (SELECT MAX(revenue_month) FROM monthly_revenue),
        INTERVAL '1 month'
    ) AS revenue_month
),

complete_revenue AS (
    SELECT
        c.revenue_month,
        COALESCE(m.total_revenue, 0) AS total_revenue,
        COALESCE(m.total_orders, 0) AS total_orders

    FROM calendar c
    LEFT JOIN monthly_revenue m
        ON c.revenue_month = m.revenue_month
)

SELECT
    TO_CHAR(revenue_month, 'YYYY-MM') AS month,
    ROUND(total_revenue::numeric, 2) AS revenue,
    total_orders,

    ROUND(
        (
            (
                total_revenue - LAG(total_revenue) OVER (
                    ORDER BY revenue_month
                )
            )
            / NULLIF(
                LAG(total_revenue) OVER (
                    ORDER BY revenue_month
                ), 0
            ) * 100
        )::numeric,
        2
    ) AS revenue_growth_percentage

FROM complete_revenue
ORDER BY revenue_month;


-- identify orders with unusually high product revenue.
WITH order_revenue AS (
    SELECT
        o.order_id,
        SUM(oi.price) AS total_revenue
    FROM orders o
    INNER JOIN order_items oi
        ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY o.order_id
),
revenue_stats AS (
    SELECT
        AVG(total_revenue) AS avg_revenue,
        STDDEV(total_revenue) AS stddev_revenue
    FROM order_revenue
)
SELECT
    r.order_id,
    ROUND(r.total_revenue::numeric, 2) AS order_revenue,
    ROUND(s.avg_revenue::numeric, 2) AS average_revenue,
    ROUND(s.stddev_revenue::numeric, 2) AS revenue_stddev
FROM order_revenue r
CROSS JOIN revenue_stats s
WHERE r.total_revenue > s.avg_revenue + (3 * s.stddev_revenue)
ORDER BY r.total_revenue DESC
LIMIT 10;
