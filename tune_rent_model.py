import pandas as pd
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
import numpy as np
import os
from pathlib import Path
import matplotlib.pyplot as plt
import warnings
from xgboost import XGBRegressor
import joblib
warnings.filterwarnings('ignore')

# Load your Excel file
excel_path = os.path.join(str(Path.home() / "Desktop"), 'Rent Data.xlsx')
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

# Visualize rent distribution before outlier removal
plt.figure(figsize=(8,4))
plt.hist(df['rent'], bins=50, color='skyblue', edgecolor='k')
plt.title('Rent Distribution (Before Outlier Removal)')
plt.xlabel('Rent')
plt.ylabel('Count')
plt.tight_layout()
plt.show()

# Remove outliers: keep rents between 1st and 99th percentiles
low, high = df['rent'].quantile([0.01, 0.99])
df = df[(df['rent'] >= low) & (df['rent'] <= high)]

# Visualize rent distribution after outlier removal
plt.figure(figsize=(8,4))
plt.hist(df['rent'], bins=50, color='lightgreen', edgecolor='k')
plt.title('Rent Distribution (After Outlier Removal)')
plt.xlabel('Rent')
plt.ylabel('Count')
plt.tight_layout()
plt.show()

# Feature engineering
if 'Bedrooms' in df.columns and 'Bathrooms' in df.columns:
    df['BedBath'] = df['Bedrooms'] * df['Bathrooms']
if 'FinishedSqft' in df.columns and 'Bedrooms' in df.columns:
    df['SqftPerBed'] = df['FinishedSqft'] / df['Bedrooms'].replace(0, np.nan)
if 'FinishedSqft' in df.columns:
    df['LogSqft'] = np.log1p(df['FinishedSqft'])
if 'Sale_date' in df.columns:
    df['SaleMonth'] = pd.to_datetime(df['Sale_date'], errors='coerce').dt.month

# Update feature columns
feature_cols = ['FinishedSqft', 'Bedrooms', 'Bathrooms', 'nbhd', 'PropertyType', 'zipcode',
                'BedBath', 'SqftPerBed', 'LogSqft', 'SaleMonth']
feature_cols = [col for col in feature_cols if col in df.columns]

# Split into train and test sets (after all cleaning/engineering)
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
X_train = train_df[feature_cols]
y_train = train_df['rent']
X_test = test_df[feature_cols]
y_test = test_df['rent']

# Preprocessing pipeline
numeric_features = [col for col in ['FinishedSqft', 'Bedrooms', 'Bathrooms', 'BedBath', 'SqftPerBed', 'LogSqft', 'SaleMonth'] if col in X_train.columns]
categorical_features = [col for col in ['nbhd', 'PropertyType', 'zipcode'] if col in X_train.columns]

numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ]
)

# Try XGBoostRegressor in the same pipeline
pipe_xgb = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', XGBRegressor(objective='reg:squarederror', random_state=42, n_jobs=-1, verbosity=0))
])

param_dist_xgb = {
    'regressor__n_estimators': [100, 200, 300, 400],
    'regressor__max_depth': [3, 5, 7, 9, 12],
    'regressor__learning_rate': [0.01, 0.03, 0.05, 0.1, 0.2],
    'regressor__min_child_weight': [1, 2, 4],
    'regressor__subsample': [0.7, 0.9, 1.0],
    'regressor__colsample_bytree': [0.7, 0.9, 1.0]
}

search_xgb = RandomizedSearchCV(
    pipe_xgb,
    param_distributions=param_dist_xgb,
    n_iter=20,
    cv=5,
    scoring='neg_mean_absolute_error',
    verbose=2,
    n_jobs=-1,
    random_state=42
)

search_xgb.fit(X_train, y_train)

print("\n[XGBoost] Best Parameters:")
print(search_xgb.best_params_)

# Feature importances for XGBoost
importances_xgb = search_xgb.best_estimator_.named_steps['regressor'].feature_importances_
feature_names_xgb = (
    list(search_xgb.best_estimator_.named_steps['preprocessor'].transformers_[0][2]) +
    list(search_xgb.best_estimator_.named_steps['preprocessor'].transformers_[1][1].named_steps['onehot'].get_feature_names_out(categorical_features))
)
importance_df_xgb = pd.DataFrame({'Feature': feature_names_xgb, 'Importance': importances_xgb})
importance_df_xgb = importance_df_xgb.sort_values('Importance', ascending=False)
print("\n[XGBoost] Top 10 Feature Importances:")
print(importance_df_xgb.head(10))

# Evaluate XGBoost on the untouched test set
y_pred_xgb = search_xgb.best_estimator_.predict(X_test)
mae_xgb = mean_absolute_error(y_test, y_pred_xgb)
rmse_xgb = np.sqrt(mean_squared_error(y_test, y_pred_xgb))
print(f"\n[XGBoost] Test MAE: {mae_xgb:.2f}")
print(f"[XGBoost] Test RMSE: {rmse_xgb:.2f}")

# Compare cross-validated MAE to test MAE for XGBoost
cv_mae_xgb = -search_xgb.best_score_
print(f"[XGBoost] Best cross-validated MAE: {cv_mae_xgb:.2f}")
print(f"[XGBoost] Test MAE: {mae_xgb:.2f}")
if abs(mae_xgb - cv_mae_xgb) / cv_mae_xgb < 0.2:
    print("[XGBoost] Model is NOT overfitting (test MAE is close to cross-validated MAE).")
else:
    print("[XGBoost] Warning: Possible overfitting (test MAE is much higher than cross-validated MAE).")

# Compare cross-validated MAE to test MAE for GradientBoostingRegressor
cv_mae = -search.best_score_
print(f"Best cross-validated MAE: {cv_mae:.2f}")
print(f"Test MAE: {mae:.2f}")
if abs(mae - cv_mae) / cv_mae < 0.2:
    print("Model is NOT overfitting (test MAE is close to cross-validated MAE).")
else:
    print("Warning: Possible overfitting (test MAE is much higher than cross-validated MAE).")

# After evaluating GradientBoostingRegressor, save the best estimator
pipe_gb = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', GradientBoostingRegressor(random_state=42))
])
param_dist_gb = {
    'regressor__n_estimators': [100, 200, 300, 400],
    'regressor__max_depth': [3, 5, 7, 9, 12],
    'regressor__learning_rate': [0.01, 0.03, 0.05, 0.1, 0.2],
    'regressor__min_samples_split': [2, 5, 10],
    'regressor__min_samples_leaf': [1, 2, 4]
}
search_gb = RandomizedSearchCV(
    pipe_gb,
    param_distributions=param_dist_gb,
    n_iter=20,
    cv=5,
    scoring='neg_mean_absolute_error',
    verbose=2,
    n_jobs=-1,
    random_state=42
)
search_gb.fit(X_train, y_train)
print("\n[GBR] Best Parameters:")
print(search_gb.best_params_)
# Save the best GradientBoostingRegressor pipeline
os.makedirs('models', exist_ok=True)
joblib.dump(search_gb.best_estimator_, 'models/rent_predictor.joblib')
print("\nSaved best GradientBoostingRegressor model to models/rent_predictor.joblib") 