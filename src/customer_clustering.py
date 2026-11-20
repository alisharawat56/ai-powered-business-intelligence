
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import (
    adjusted_rand_score,
    normalized_mutual_info_score
)
import os
import joblib

# Load original customer features and scaled features
original_df = pd.read_csv(
    "data/processed/customer_rfm_features.csv"
)

scaled_df = pd.read_csv(
    "data/processed/customer_rfm_scaled.csv"
)

# Train K-Means with 4 clusters
kmeans = KMeans(
    n_clusters=4,
    random_state=42,
    n_init=10
)

original_df["kmeans_cluster"] = kmeans.fit_predict(
    scaled_df
)

# Save trained model
os.makedirs("models", exist_ok=True)

joblib.dump(
    kmeans,
    "models/kmeans_customer_segments.joblib"
)

print("\nTrained K-Means model saved successfully!")

# Save customer-level cluster assignments
original_df.to_csv(
    "data/processed/customer_clusters.csv",
    index=False
)

# Profile each cluster
cluster_summary = original_df.groupby(
    "kmeans_cluster"
).agg(
    customer_count=("customer_unique_id", "count"),
    avg_recency=("recency", "mean"),
    median_recency=("recency", "median"),
    avg_frequency=("frequency", "mean"),
    median_frequency=("frequency", "median"),
    avg_monetary=("monetary", "mean"),
    median_monetary=("monetary", "median")
).round(2)

print("K-Means clustering completed!")

print("\nCluster profiles:")
print(cluster_summary)

print("\nCustomer counts by cluster:")
print(original_df["kmeans_cluster"].value_counts().sort_index())

print("\nRFM segment vs K-Means cluster:")
print(pd.crosstab(
    original_df["rfm_segment"],
    original_df["kmeans_cluster"]
))

# Compare K-Means clusters with RFM segments
ari = adjusted_rand_score(
    original_df["rfm_segment"],
    original_df["kmeans_cluster"]
)

nmi = normalized_mutual_info_score(
    original_df["rfm_segment"],
    original_df["kmeans_cluster"]
)

print("\nClustering agreement evaluation:")
print(f"Adjusted Rand Index: {ari:.4f}")
print(f"Normalized Mutual Information: {nmi:.4f}")