
import pandas as pd
import numpy as np
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = PROJECT_ROOT / "data" / "raw"
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed"

PROCESSED_PATH.mkdir(parents=True, exist_ok=True)

# Dataset files
files = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv"
}

datasets = {}

# Load datasets
for name, filename in files.items():
    path = RAW_PATH / filename

    df = pd.read_csv(path)
    datasets[name] = df

    print(f"\n{name.upper()}")
    print("Shape:", df.shape)
    print("Missing values:", df.isnull().sum().sum())
    print("Duplicate rows:", df.duplicated().sum())


# Remove exact duplicate rows
for name, df in datasets.items():
    datasets[name] = df.drop_duplicates().copy()


# Convert date columns
date_columns = {
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ],
    "order_items": ["shipping_limit_date"],
    "reviews": ["review_creation_date", "review_answer_timestamp"]
}

for table, columns in date_columns.items():
    for column in columns:
        datasets[table][column] = pd.to_datetime(
            datasets[table][column],
            errors="coerce"
        )


# Check invalid numeric values
datasets["order_items"]["price"] = pd.to_numeric(
    datasets["order_items"]["price"],
    errors="coerce"
)

datasets["order_items"]["freight_value"] = pd.to_numeric(
    datasets["order_items"]["freight_value"],
    errors="coerce"
)

datasets["payments"]["payment_value"] = pd.to_numeric(
    datasets["payments"]["payment_value"],
    errors="coerce"
)


# Flag invalid values rather than silently deleting records
datasets["order_items"]["invalid_price"] = (
    datasets["order_items"]["price"] < 0
)

datasets["payments"]["invalid_payment"] = (
    datasets["payments"]["payment_value"] < 0
)


# Save cleaned datasets
for name, df in datasets.items():
    output_path = PROCESSED_PATH / f"{name}_cleaned.csv"
    df.to_csv(output_path, index=False)

    print(f"\nSaved {name}: {df.shape}")


print("\nInitial data cleaning completed!")
