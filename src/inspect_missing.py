
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "processed"

tables = ["orders", "reviews", "products"]

for table in tables:
    df = pd.read_csv(DATA_PATH / f"{table}_cleaned.csv")

    print(f"\n{'=' * 45}")
    print(f"{table.upper()} - MISSING VALUE ANALYSIS")
    print("=" * 45)

    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)

    if missing.empty:
        print("No missing values found.")
    else:
        print(missing)

        print("\nMissing percentage:")
        print((missing / len(df) * 100).round(2))


# Investigate missing delivery timestamps
orders = pd.read_csv(DATA_PATH / "orders_cleaned.csv")

print("\nORDER STATUS DISTRIBUTION")
print(orders["order_status"].value_counts(dropna=False))

print("\nDELIVERY DATE MISSING BY ORDER STATUS")
print(
    pd.crosstab(
        orders["order_status"],
        orders["order_delivered_customer_date"].isnull(),
        rownames=["Order Status"],
        colnames=["Delivery Date Missing"]
    )
)

# Check review scores
reviews = pd.read_csv(DATA_PATH / "reviews_cleaned.csv")

print("\nREVIEW SCORE DISTRIBUTION")
print(reviews["review_score"].value_counts(dropna=False).sort_index())
