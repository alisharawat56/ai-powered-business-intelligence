
import os
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine, text, URL

# Load database credentials
load_dotenv()

db_url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME")
)

engine = create_engine(db_url)

# Customer-level RFM query
query = """
WITH customer_rfm AS (
    SELECT
        c.customer_unique_id,
        MAX(o.order_purchase_timestamp::timestamp) AS last_purchase_date,
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
),
rfm_metrics AS (
    SELECT
        r.customer_unique_id,
        (d.analysis_date::date - r.last_purchase_date::date)
            AS recency,
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
        END AS rfm_segment
    FROM rfm_scores
)
SELECT
    customer_unique_id,
    recency,
    frequency,
    monetary,
    rfm_segment
FROM customer_segments
ORDER BY customer_unique_id;
"""

# Extract customer-level features
with engine.connect() as connection:
    customer_data = pd.read_sql_query(
        text(query),
        connection
    )

# Create processed directory if necessary
os.makedirs("data/processed", exist_ok=True)

# Save the dataset
output_path = "data/processed/customer_rfm_features.csv"
customer_data.to_csv(output_path, index=False)

print("Customer feature dataset created successfully!")
print("Dataset shape:", customer_data.shape)

print("\nFirst five records:")
print(customer_data.head())

print("\nMissing values:")
print(customer_data.isnull().sum())

print("\nRFM segment distribution:")
print(customer_data["rfm_segment"].value_counts())
