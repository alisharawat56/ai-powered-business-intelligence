
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

# Load customer-level dataset
df = pd.read_csv("data/processed/customer_rfm_features.csv")

# Select numerical features
features = ["recency", "frequency", "monetary"]
X = df[features]

# Apply log transformation to reduce right skew
X_log = np.log1p(X)

# Scale transformed features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_log)

# Convert scaled features into DataFrame
scaled_df = pd.DataFrame(
    X_scaled,
    columns=features
)

# Save scaled features
scaled_df.to_csv(
    "data/processed/customer_rfm_scaled.csv",
    index=False
)

# Display results
print("Log transformation and feature scaling completed!")

print("\nSkewness before transformation:")
print(X.skew().round(3))

print("\nSkewness after transformation:")
print(X_log.skew().round(3))

print("\nScaled feature statistics:")
print(scaled_df.describe().round(3))

print("\nScaled dataset shape:")
print(scaled_df.shape)
