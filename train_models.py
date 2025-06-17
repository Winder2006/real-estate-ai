import pandas as pd
from utils.ml_models import PropertyPricePredictor, RentPredictor
import os
from pathlib import Path
import re
import numpy as np

def load_and_prepare_data():
    """Load and prepare the training data"""
    # Get the desktop path
    desktop_path = str(Path.home() / "Desktop")
    
    # Load your Excel file
    excel_path = os.path.join(desktop_path, 'Rent Data.xlsx')
    print(f"Loading data from: {excel_path}")
    
    # Read the Excel file
    df = pd.read_excel(excel_path)
    
    print("\nInitial data shape:", df.shape)
    print("\nOriginal columns:", df.columns.tolist())
    
    # Rename columns to match our model's expected format
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
                # Extract only the numeric part (handles values like '0.85/ft²')
                df[col] = df[col].astype(str).str.extract(r'([\d\.]+)').astype(float)
            elif col == 'rent':
                df[col] = df[col].astype(str).str.replace('$', '').str.replace(',', '').astype(float)
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce')
    
    print("\nData Quality Report:")
    print("\nMissing values per column:")
    print(df.isnull().sum())
    
    print("\nValid entries per column:")
    print(df.count())
    
    # Basic data cleaning - only remove rows where we have no useful data
    print("\nCleaning data...")
    print("Rows before cleaning:", len(df))
    
    # Keep rows that have at least some useful information
    # For rent prediction, we need at least rent and some features
    rent_mask = df['rent'].notna()
    features_mask = (
        df['FinishedSqft'].notna() |
        df['Bedrooms'].notna() |
        df['Bathrooms'].notna() |
        df['nbhd'].notna() |
        df['PropertyType'].notna() |
        df['zipcode'].notna()
    )
    
    df = df[rent_mask & features_mask]
    print("Rows after cleaning:", len(df))
    
    # Convert date column to datetime if it exists
    if 'Sale_date' in df.columns:
        df['Sale_date'] = pd.to_datetime(df['Sale_date'])
    
    # Calculate sale price from price per sqft if available
    if 'price_per_sqft' in df.columns and 'FinishedSqft' in df.columns:
        df['Sale_price'] = df['price_per_sqft'] * df['FinishedSqft']
    
    # Print data summary
    print("\nData Summary:")
    numeric_cols = ['FinishedSqft', 'rent', 'Sale_price', 'Bedrooms', 'Bathrooms']
    numeric_cols = [col for col in numeric_cols if col in df.columns]
    print(df[numeric_cols].describe())
    
    # Print unique values in categorical columns
    categorical_cols = ['PropertyType', 'nbhd', 'zipcode']
    categorical_cols = [col for col in categorical_cols if col in df.columns]
    for col in categorical_cols:
        print(f"\nUnique {col} values:", df[col].nunique())
        print(f"Most common {col} values:")
        print(df[col].value_counts().head())
    
    # Feature engineering for rent model
    if 'Bedrooms' in df.columns and 'Bathrooms' in df.columns:
        df['BedBath'] = df['Bedrooms'] * df['Bathrooms']
    if 'FinishedSqft' in df.columns and 'Bedrooms' in df.columns:
        df['SqftPerBed'] = df['FinishedSqft'] / df['Bedrooms'].replace(0, np.nan)
    if 'FinishedSqft' in df.columns:
        df['LogSqft'] = np.log1p(df['FinishedSqft'])
    if 'Sale_date' in df.columns:
        df['SaleMonth'] = pd.to_datetime(df['Sale_date'], errors='coerce').dt.month
    # Remove outliers for rent
    if 'rent' in df.columns:
        low, high = df['rent'].quantile([0.01, 0.99])
        df = df[(df['rent'] >= low) & (df['rent'] <= high)]
    
    return df

def main():
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Load and prepare data
    print("Loading and preparing data...")
    df = load_and_prepare_data()
    
    # Train price prediction model if we have price data
    if 'Sale_price' in df.columns:
        price_df = df.dropna(subset=['Sale_price'])
        if not price_df.empty:
            print("\nTraining price prediction model...")
            price_predictor = PropertyPricePredictor()
            price_metrics = price_predictor.train(price_df)
            price_predictor.save_model()
            print("\nPrice Model Metrics:")
            print(f"MAE: ${price_metrics[0]:,.2f}")
            print(f"RMSE: ${price_metrics[1]:,.2f}")
            print(f"R2 Score: {price_metrics[2]:.3f}")
        else:
            print("\nSkipping price prediction model - no valid price data available")
    else:
        print("\nSkipping price prediction model - no price data available")
    
    # Feature columns for rent model
    feature_cols = ['FinishedSqft', 'Bedrooms', 'Bathrooms', 'nbhd', 'PropertyType', 'zipcode',
                    'BedBath', 'SqftPerBed', 'LogSqft', 'SaleMonth']
    feature_cols = [col for col in feature_cols if col in df.columns]
    
    # Train rent prediction model
    print("\nTraining rent prediction model...")
    rent_predictor = RentPredictor()
    rent_metrics = rent_predictor.train(df[feature_cols + ['rent']])
    rent_predictor.save_model()
    print("\nRent Model Metrics:")
    print(f"MAE: ${rent_metrics[0]:,.2f}")
    print(f"RMSE: ${rent_metrics[1]:,.2f}")
    print(f"R2 Score: {rent_metrics[2]:.3f}")

if __name__ == "__main__":
    main() 