import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

print("Loading dataset...")
df = pd.read_csv("mental_health_lifestyle.csv")  
print("Dataset loaded successfully!\n")

print(df.info())
print("\nPreview of data:")
print(df.head())

# Handle missing values
df = df.dropna(thresh=int(0.7 * len(df.columns)))

numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
for col in numeric_cols:
    df[col] = df[col].fillna(df[col].mean())

categorical_cols = df.select_dtypes(include=['object']).columns
for col in categorical_cols:
    df[col] = df[col].fillna(df[col].mode()[0])

print("\nMissing values handled successfully.")

# Encode categorical columns
yes_no_cols = ['Exercise']  
for col in yes_no_cols:
    if col in df.columns:
        df[col] = df[col].map({'Yes': 1, 'No': 0})

for col in categorical_cols:
    if col not in yes_no_cols:
        df = pd.get_dummies(df, columns=[col])

print("Categorical variables encoded.")

# Normalize numeric data
scaler = MinMaxScaler()
df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

print("Numeric features normalized (0–1 scale).")

# Create a simple wellness score
df['Wellness_Score'] = df[numeric_cols].mean(axis=1)

# Save final preprocessed dataset
df.to_csv("mental_health_lifestyle_preprocessed.csv", index=False)

print("\nPreprocessing complete!")
