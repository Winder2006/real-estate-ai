import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
import matplotlib.pyplot as plt
from utils.ml_models import RentPredictor
import os
from pathlib import Path

# Load your Excel file (update path if needed)
desktop_path = str(Path.home() / "Desktop")
excel_path = os.path.join(desktop_path, 'Rent Data.xlsx')
df = pd.read_excel(excel_path)

# Rename columns to match model's expected format
column_mapping = {
    'Neighborhood': 'nbhd',
    'Rent ($)': 'rent',
    'Size (ft²)': 'FinishedSqft',
    '$/ft²': 'price_per_sqft',
    'Beds': 'Bedrooms',
    'Baths': 'Bathrooms',
    'Building Type': 'PropertyType',
    'Last Seen': 'Sale_date',
    'Zip-Code': 'zipcode'
}
df = df.rename(columns=column_mapping)

# Convert numeric columns to proper types
numeric_columns = ['rent', 'FinishedSqft', 'price_per_sqft', 'Bedrooms', 'Bathrooms']
for col in numeric_columns:
    if col in df.columns:
        if col == 'price_per_sqft':
            df[col] = df[col].astype(str).str.extract(r'([\d\.]+)').astype(float)
        elif col == 'rent':
            df[col] = df[col].astype(str).str.replace('$', '').str.replace(',', '').astype(float)
        else:
            df[col] = pd.to_numeric(df[col], errors='coerce')

# Basic cleaning: keep rows with rent and at least one feature
df = df[df['rent'].notna() & (
    df['FinishedSqft'].notna() |
    df['Bedrooms'].notna() |
    df['Bathrooms'].notna() |
    df['nbhd'].notna() |
    df['PropertyType'].notna() |
    df['zipcode'].notna()
)]

# Split into train and test
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

# Prepare features and target
feature_cols = ['FinishedSqft', 'Bedrooms', 'Bathrooms', 'nbhd', 'PropertyType', 'zipcode']
X_train = train_df[feature_cols]
y_train = train_df['rent']
X_test = test_df[feature_cols]
y_test = test_df['rent']

# Train the model
model = RentPredictor()
model.train(train_df)

# Predict on the test set
y_pred = [model.predict(row.to_dict()) for _, row in X_test.iterrows()]

# Evaluate
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print(f"MAE: {mae:.2f}")
print(f"RMSE: {rmse:.2f}")

# Scatter plot: Actual vs Predicted
plt.figure(figsize=(8,6))
plt.scatter(y_test, y_pred, alpha=0.5)
plt.xlabel('Actual Rent')
plt.ylabel('Predicted Rent')
plt.title('Actual vs Predicted Rent')
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
plt.tight_layout()
plt.show() 