
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, URL
from dotenv import load_dotenv
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "processed"

load_dotenv(PROJECT_ROOT / ".env")

db_url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME", "ecommerce_analytics")
)

engine = create_engine(db_url)

tables = [
    "customers",
    "orders",
    "order_items",
    "payments",
    "reviews",
    "products",
    "sellers"
]

for table in tables:
    file_path = DATA_PATH / f"{table}_cleaned.csv"

    df = pd.read_csv(file_path)

    df.to_sql(
        name=table,
        con=engine,
        if_exists="replace",
        index=False,
        chunksize=1000
    )

    print(f"{table}: {len(df)} rows loaded successfully")

engine.dispose()

print("\nDatabase updated with refined datasets!")
