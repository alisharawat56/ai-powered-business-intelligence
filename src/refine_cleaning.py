
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "processed"

# Load cleaned datasets
orders = pd.read_csv(DATA_PATH / "orders_cleaned.csv")
products = pd.read_csv(DATA_PATH / "products_cleaned.csv")
reviews = pd.read_csv(DATA_PATH / "reviews_cleaned.csv")


# 1. Orders: flag delivered orders missing delivery dates
orders["delivery_date_missing_flag"] = (
    (orders["order_status"] == "delivered")
    & (orders["order_delivered_customer_date"].isnull())
)

print("Delivered orders missing delivery date:")
print(orders["delivery_date_missing_flag"].sum())

print("\nAffected orders:")
print(
    orders.loc[
        orders["delivery_date_missing_flag"],
        ["order_id", "order_status", "order_purchase_timestamp"]
    ]
)


# 2. Products: identify missing categories
products["category_missing_flag"] = (
    products["product_category_name"].isnull()
)

print("\nProducts missing category:")
print(products["category_missing_flag"].sum())

products["product_category_name"] = (
    products["product_category_name"].fillna("unknown")
)


# Flag missing physical dimensions
dimension_columns = [
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm"
]

products["dimensions_missing_flag"] = (
    products[dimension_columns].isnull().any(axis=1)
)

print("\nProducts with missing physical dimensions:")
print(products["dimensions_missing_flag"].sum())


# 3. Reviews: preserve missing comments
print("\nMissing review scores:")
print(reviews["review_score"].isnull().sum())

print("Missing review messages:")
print(reviews["review_comment_message"].isnull().sum())

# No artificial comments or scores are added.


# Save refined datasets
orders.to_csv(DATA_PATH / "orders_cleaned.csv", index=False)
products.to_csv(DATA_PATH / "products_cleaned.csv", index=False)
reviews.to_csv(DATA_PATH / "reviews_cleaned.csv", index=False)

print("\nRefined cleaning completed successfully!")
