import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from pathlib import Path

def load_milwaukee_dataset():
    """Load and prepare the Milwaukee real estate dataset"""
    try:
        # In a real implementation, you would load this from a file
        # For now, we'll create a sample dataset
        data = {
            'price': np.random.normal(300000, 50000, 1000),
            'sqft': np.random.normal(2000, 500, 1000),
            'beds': np.random.randint(1, 6, 1000),
            'baths': np.random.randint(1, 4, 1000),
            'year_built': np.random.randint(1950, 2024, 1000),
            'lot_size': np.random.normal(5000, 1000, 1000)
        }
        df = pd.DataFrame(data)
        
        # Prepare features and target
        X = df[['sqft', 'beds', 'baths', 'year_built', 'lot_size']]
        y = df['price']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        return {
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test,
            'data': df
        }
    except Exception as e:
        print(f"Error loading Milwaukee dataset: {str(e)}")
        return None

def load_foreclosure_data():
    """Load foreclosure data"""
    try:
        # In a real implementation, you would load this from a file
        # For now, we'll create a sample dataset
        data = {
            'zip_code': np.random.randint(10000, 99999, 100),
            'foreclosure_rate': np.random.uniform(0, 0.1, 100)
        }
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error loading foreclosure data: {str(e)}")
        return None

def load_comps_data():
    """Load comparable properties data"""
    try:
        # In a real implementation, you would load this from a file
        # For now, we'll create a sample dataset
        data = {
            'price': np.random.normal(300000, 50000, 100),
            'rent': np.random.normal(2000, 500, 100),
            'sqft': np.random.normal(2000, 500, 100),
            'beds': np.random.randint(1, 6, 100),
            'baths': np.random.randint(1, 4, 100),
            'year_built': np.random.randint(1950, 2024, 100),
            'lot_size': np.random.normal(5000, 1000, 100)
        }
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error loading comps data: {str(e)}")
        return None

def save_analysis_results(results, filename):
    """Save analysis results to a file"""
    try:
        results_df = pd.DataFrame(results)
        results_df.to_csv(filename, index=False)
        return True
    except Exception as e:
        print(f"Error saving analysis results: {str(e)}")
        return False

def load_analysis_results(filename):
    """Load analysis results from a file"""
    try:
        return pd.read_csv(filename)
    except Exception as e:
        print(f"Error loading analysis results: {str(e)}")
        return None

def load_and_clean_sales_data():
    files = [
        'data/2019-property-sales-data.csv',
        'data/2020-property-sales-data.csv',
        'data/2021-property-sales-data.csv',
        'data/2022-property-sales-data.csv',
    ]
    dfs = []
    for f in files:
        df = pd.read_csv(f)
        dfs.append(df)
    df = pd.concat(dfs, ignore_index=True)
    # Convert to numeric
    df['FinishedSqft'] = pd.to_numeric(df['FinishedSqft'], errors='coerce')
    df['Sale_price'] = pd.to_numeric(df['Sale_price'], errors='coerce')
    # Drop rows with missing or 0 FinishedSqft or Sale_price
    df = df.dropna(subset=['FinishedSqft', 'Sale_price', 'Sale_date'])
    df = df[(df['FinishedSqft'] > 0) & (df['Sale_price'] > 0)]
    # Ensure Sale_date is datetime
    df['Sale_date'] = pd.to_datetime(df['Sale_date'], errors='coerce')
    df = df.dropna(subset=['Sale_date'])
    # Add price_per_sqft
    df['price_per_sqft'] = df['Sale_price'] / df['FinishedSqft']
    # Extract year
    df['year'] = df['Sale_date'].dt.year
    # Add columns for model compatibility
    df['sqft'] = df['FinishedSqft']
    df['beds'] = df['Bdrms']
    df['baths'] = df['Fbath'].fillna(0) + df['Hbath'].fillna(0)
    df['year_built'] = df['Year_Built']
    df['lot_size'] = df['Lotsize']
    df['price'] = df['Sale_price']
    return df 