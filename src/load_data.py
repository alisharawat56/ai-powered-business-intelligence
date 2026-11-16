
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, URL
from dotenv import load_dotenv
import os


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "raw"

load_dotenv(PROJECT_ROOT / ".env")

print("Project root:", PROJECT_ROOT)
print("Environment file exists:", (PROJECT_ROOT / ".env").exists())
print("DB user:", os.getenv("DB_USER"))
print("DB password loaded:", bool(os.getenv("DB_PASSWORD")))

# --------------------------------------------------
# 2. DATABASE CONFIGURATION
# --------------------------------------------------

db_url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME", "ecommerce_analytics")
)

engine = create_engine(db_url)


# --------------------------------------------------
# 3. DATASET FILES
# --------------------------------------------------

files = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "category_translation": "product_category_name_translation.csv"
}


# --------------------------------------------------
# 4. LOAD CSV FILES INTO PYTHON
# --------------------------------------------------

datasets = {}

for table_name, filename in files.items():

    file_path = DATA_PATH / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}"
        )

    df = pd.read_csv(file_path)

    datasets[table_name] = df

    print(
        f"{table_name}: {df.shape[0]} rows, "
        f"{df.shape[1]} columns"
    )


# --------------------------------------------------
# 5. LOAD DATA INTO POSTGRESQL
# --------------------------------------------------

for table_name, df in datasets.items():

    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="replace",
        index=False,
        chunksize=1000
    )

    print(f"{table_name} successfully loaded!")


# --------------------------------------------------
# 6. VERIFY DATABASE CONNECTION
# --------------------------------------------------

with engine.connect() as connection:

    result = connection.exec_driver_sql(
        "SELECT COUNT(*) FROM orders"
    )

    order_count = result.scalar()

    print("\nDatabase verification successful!")
    print(f"Total orders loaded: {order_count}")


engine.dispose()

print("\nAll datasets loaded successfully!")
