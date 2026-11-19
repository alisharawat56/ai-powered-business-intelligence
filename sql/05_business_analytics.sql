
-- Monthly Business Performance

SELECT
    DATE_TRUNC(
        'month',
        o.order_purchase_timestamp::timestamp
    ) AS month,

    COUNT(DISTINCT o.order_id) AS total_orders,

    ROUND(
        SUM(oi.price)::numeric,
        2
    ) AS monthly_revenue,

    ROUND(
        (
            SUM(oi.price) /
            NULLIF(COUNT(DISTINCT o.order_id), 0)
        )::numeric,
        2
    ) AS average_order_value

FROM orders o

INNER JOIN order_items oi
    ON o.order_id = oi.order_id

WHERE o.order_status = 'delivered'

GROUP BY 1
ORDER BY 1;



-- Weekly Business Performance

SELECT
    DATE_TRUNC(
        'week',
        o.order_purchase_timestamp::timestamp
    ) AS week,

    COUNT(DISTINCT o.order_id) AS total_orders,

    ROUND(
        SUM(oi.price)::numeric,
        2
    ) AS weekly_revenue,

    ROUND(
        (
            SUM(oi.price) /
            NULLIF(COUNT(DISTINCT o.order_id), 0)
        )::numeric,
        2
    ) AS average_order_value

FROM orders o

INNER JOIN order_items oi
    ON o.order_id = oi.order_id

WHERE o.order_status = 'delivered'

GROUP BY 1
ORDER BY 1;


-- Customer Retention and Cohort Analysis

WITH customer_orders AS (
    SELECT DISTINCT
        c.customer_unique_id,
        o.order_id,
        DATE_TRUNC(
            'month',
            o.order_purchase_timestamp::timestamp
        ) AS purchase_month
    FROM customers c
    INNER JOIN orders o
        ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
),

customer_cohorts AS (
    SELECT
        customer_unique_id,
        MIN(purchase_month) AS cohort_month
    FROM customer_orders
    GROUP BY customer_unique_id
),

cohort_activity AS (
    SELECT
        co.cohort_month,
        co.purchase_month,

        (
            EXTRACT(YEAR FROM co.purchase_month)::integer
            - EXTRACT(YEAR FROM co.cohort_month)::integer
        ) * 12
        +
        (
            EXTRACT(MONTH FROM co.purchase_month)::integer
            - EXTRACT(MONTH FROM co.cohort_month)::integer
        ) AS month_number,

        COUNT(DISTINCT co.customer_unique_id) AS active_customers

    FROM customer_orders co
    INNER JOIN customer_cohorts cc
        ON co.customer_unique_id = cc.customer_unique_id
    GROUP BY
        co.cohort_month,
        co.purchase_month
)

SELECT
    cohort_month,
    month_number,
    active_customers,

    FIRST_VALUE(active_customers) OVER (
        PARTITION BY cohort_month
        ORDER BY month_number
    ) AS cohort_size,

    ROUND(
        (
            active_customers * 100.0
            /
            FIRST_VALUE(active_customers) OVER (
                PARTITION BY cohort_month
                ORDER BY month_number
            )
        )::numeric,
        2
    ) AS retention_percentage

FROM cohort_activity
ORDER BY cohort_month, month_number;


-- RFM Customer Segmentation

WITH customer_rfm AS (
    SELECT
        c.customer_unique_id,

        MAX(
            o.order_purchase_timestamp::timestamp
        ) AS last_purchase_date,

        COUNT(DISTINCT o.order_id) AS frequency,

        SUM(oi.price) AS monetary

    FROM customers c

    INNER JOIN orders o
        ON c.customer_id = o.customer_id

    INNER JOIN order_items oi
        ON o.order_id = oi.order_id

    WHERE o.order_status = 'delivered'

    GROUP BY c.customer_unique_id
),

reference_date AS (
    SELECT
        MAX(order_purchase_timestamp::timestamp) + INTERVAL '1 day'
            AS analysis_date
    FROM orders
    WHERE order_status = 'delivered'
)

SELECT
    r.customer_unique_id,

    (d.analysis_date::date - r.last_purchase_date::date)
        AS recency,

    r.frequency,

    ROUND(r.monetary::numeric, 2) AS monetary

FROM customer_rfm r
CROSS JOIN reference_date d
ORDER BY monetary DESC
LIMIT 20;

-- Assign RFM scores
WITH customer_rfm AS (
    SELECT
        c.customer_unique_id,
        MAX(o.order_purchase_timestamp::timestamp) AS last_purchase_date,
        COUNT(DISTINCT o.order_id) AS frequency,
        SUM(oi.price) AS monetary
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    INNER JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
),
reference_date AS (
    SELECT
        MAX(order_purchase_timestamp::timestamp) + INTERVAL '1 day'
        AS analysis_date
    FROM orders
    WHERE order_status = 'delivered'
),
rfm_metrics AS (
    SELECT
        r.customer_unique_id,
        (d.analysis_date::date - r.last_purchase_date::date) AS recency,
        r.frequency,
        r.monetary
    FROM customer_rfm r
    CROSS JOIN reference_date d
),
rfm_scores AS (
    SELECT
        *,
        6 - NTILE(5) OVER (ORDER BY recency ASC) AS recency_score,
        NTILE(5) OVER (ORDER BY frequency ASC) AS frequency_score,
        NTILE(5) OVER (ORDER BY monetary ASC) AS monetary_score
    FROM rfm_metrics
)
SELECT
    customer_unique_id,
    recency,
    frequency,
    ROUND(monetary::numeric, 2) AS monetary,
    recency_score,
    frequency_score,
    monetary_score,
    recency_score + frequency_score + monetary_score AS rfm_total_score
FROM rfm_scores
ORDER BY rfm_total_score DESC
LIMIT 20;


-- Create customer segments
WITH customer_rfm AS (
    SELECT
        c.customer_unique_id,
        MAX(o.order_purchase_timestamp::timestamp) AS last_purchase_date,
        COUNT(DISTINCT o.order_id) AS frequency,
        SUM(oi.price) AS monetary
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    INNER JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
),
reference_date AS (
    SELECT
        MAX(order_purchase_timestamp::timestamp) + INTERVAL '1 day'
        AS analysis_date
    FROM orders
    WHERE order_status = 'delivered'
),
rfm_metrics AS (
    SELECT
        r.customer_unique_id,
        (d.analysis_date::date - r.last_purchase_date::date) AS recency,
        r.frequency,
        r.monetary
    FROM customer_rfm r
    CROSS JOIN reference_date d
),
rfm_scores AS (
    SELECT
        *,
        6 - NTILE(5) OVER (ORDER BY recency ASC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
    FROM rfm_metrics
),
customer_segments AS (
    SELECT
        *,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4
                THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 4
                THEN 'Loyal Customers'
            WHEN r_score >= 4 AND f_score >= 2
                THEN 'Potential Loyalists'
            WHEN r_score <= 2 AND f_score >= 3
                THEN 'At Risk'
            WHEN r_score <= 2 AND f_score <= 2
                THEN 'Hibernating'
            ELSE 'Needs Attention'
        END AS customer_segment
    FROM rfm_scores
)
SELECT
    customer_segment,
    COUNT(*) AS total_customers,
    ROUND(AVG(monetary)::numeric, 2) AS average_customer_revenue,
    ROUND(SUM(monetary)::numeric, 2) AS segment_revenue
FROM customer_segments
GROUP BY customer_segment
ORDER BY segment_revenue DESC;


-- Analyze order value and freight
SELECT
    CASE
        WHEN order_value < 50 THEN 'Under R$50'
        WHEN order_value < 100 THEN 'R$50-R$100'
        WHEN order_value < 250 THEN 'R$100-R$250'
        WHEN order_value < 500 THEN 'R$250-R$500'
        ELSE 'Above R$500'
    END AS order_value_range,

    COUNT(*) AS total_orders,

    ROUND(AVG(order_value)::numeric, 2)
        AS average_order_value,

    ROUND(AVG(freight_value)::numeric, 2)
        AS average_freight,

    ROUND(
        (AVG(freight_value) / NULLIF(AVG(order_value), 0) * 100)::numeric,
        2
    ) AS freight_percentage

FROM (
    SELECT
        o.order_id,
        SUM(oi.price) AS order_value,
        SUM(oi.freight_value) AS freight_value
    FROM orders o
    INNER JOIN order_items oi
        ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
      AND oi.invalid_price = FALSE
    GROUP BY o.order_id
) order_summary

GROUP BY 1
ORDER BY MIN(order_value);


-- High-value and at-risk customers
WITH customer_rfm AS (
    SELECT
        c.customer_unique_id,
        MAX(o.order_purchase_timestamp::timestamp) AS last_purchase_date,
        COUNT(DISTINCT o.order_id) AS frequency,
        SUM(oi.price) AS monetary
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    INNER JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
),
reference_date AS (
    SELECT
        MAX(order_purchase_timestamp::timestamp) + INTERVAL '1 day'
        AS analysis_date
    FROM orders
    WHERE order_status = 'delivered'
),
rfm_metrics AS (
    SELECT
        r.customer_unique_id,
        (d.analysis_date::date - r.last_purchase_date::date) AS recency,
        r.frequency,
        r.monetary
    FROM customer_rfm r
    CROSS JOIN reference_date d
),
rfm_scores AS (
    SELECT
        *,
        6 - NTILE(5) OVER (ORDER BY recency ASC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
    FROM rfm_metrics
),
customer_segments AS (
    SELECT
        *,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4
                THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 4
                THEN 'Loyal Customers'
            WHEN r_score >= 4 AND f_score >= 2
                THEN 'Potential Loyalists'
            WHEN r_score <= 2 AND f_score >= 3
                THEN 'At Risk'
            WHEN r_score <= 2 AND f_score <= 2
                THEN 'Hibernating'
            ELSE 'Needs Attention'
        END AS customer_segment
    FROM rfm_scores
)
SELECT
    customer_segment,
    COUNT(*) AS total_customers,
    ROUND(AVG(recency)::numeric, 1) AS average_recency_days,
    ROUND(AVG(frequency)::numeric, 2) AS average_orders,
    ROUND(AVG(monetary)::numeric, 2) AS average_historical_revenue,
    ROUND(SUM(monetary)::numeric, 2) AS total_historical_revenue
FROM customer_segments
WHERE customer_segment IN ('Champions', 'At Risk')
GROUP BY customer_segment
ORDER BY total_historical_revenue DESC;

