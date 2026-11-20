
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# Load scaled customer features
df = pd.read_csv("data/processed/customer_rfm_scaled.csv")

# Store results
inertias = []
silhouette_scores = []

# Test different numbers of clusters
k_values = range(2, 9)

for k in k_values:
    print(f"Evaluating {k} clusters...")

    kmeans = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10
    )

    labels = kmeans.fit_predict(df)

    # Store inertia
    inertias.append(kmeans.inertia_)

    # Calculate silhouette score on a sample
    score = silhouette_score(
        df,
        labels,
        sample_size=5000,
        random_state=42
    )

    silhouette_scores.append(score)

    print(f"Silhouette Score: {score:.4f}")

# Plot Elbow Method
plt.figure(figsize=(8, 5))
plt.plot(k_values, inertias, marker="o")
plt.xlabel("Number of Clusters")
plt.ylabel("Inertia")
plt.title("Elbow Method")
plt.xticks(list(k_values))
plt.grid(True)
plt.savefig("data/processed/elbow_method.png")
plt.show()

# Plot Silhouette Scores
plt.figure(figsize=(8, 5))
plt.plot(k_values, silhouette_scores, marker="o")
plt.xlabel("Number of Clusters")
plt.ylabel("Silhouette Score")
plt.title("Silhouette Score by Number of Clusters")
plt.xticks(list(k_values))
plt.grid(True)
plt.savefig("data/processed/silhouette_scores.png")
plt.show()

print("\nEvaluation completed!")
