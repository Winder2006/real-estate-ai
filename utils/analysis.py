import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

def calculate_roi(monthly_cash_flow, down_payment, annual_appreciation_rate=0.03):
    """Calculate Return on Investment"""
    annual_cash_flow = monthly_cash_flow * 12
    annual_appreciation = down_payment * annual_appreciation_rate
    total_annual_return = annual_cash_flow + annual_appreciation
    roi = (total_annual_return / down_payment) * 100
    return roi

def calculate_break_even_rent(monthly_expenses, monthly_mortgage):
    """Calculate break-even rent"""
    return monthly_expenses + monthly_mortgage

def estimate_rent_by_comps(property_data, comps_data):
    """Estimate rent based on comparable properties"""
    # If 'rent' column is missing, return None and optionally warn
    if 'rent' not in comps_data.columns or 'sqft' not in comps_data.columns:
        return None
    if not comps_data.empty:
        avg_rent_per_sqft = comps_data['rent'].mean() / comps_data['sqft'].mean()
        estimated_rent = property_data['sqft'] * avg_rent_per_sqft
        return estimated_rent
    return None

def calculate_risk_score(property_data, foreclosure_data):
    """Calculate risk score based on foreclosure data"""
    if foreclosure_data is not None:
        zip_code = property_data.get('zip_code')
        if zip_code in foreclosure_data['zip_code'].values:
            foreclosure_rate = foreclosure_data[
                foreclosure_data['zip_code'] == zip_code
            ]['foreclosure_rate'].iloc[0]
            risk_score = 100 - (foreclosure_rate * 100)
            return risk_score
    return None

def predict_property_value(property_data, model_data):
    """Predict property value using the Milwaukee dataset model"""
    try:
        # Prepare features
        features = pd.DataFrame({
            'sqft': [property_data['sqft']],
            'beds': [property_data['beds']],
            'baths': [property_data['baths']],
            'year_built': [property_data['year_built']],
            'lot_size': [property_data['lot_size']]
        })
        
        # Scale features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Make prediction
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(model_data['X_train'], model_data['y_train'])
        predicted_value = model.predict(features_scaled)[0]
        
        return predicted_value
    except Exception as e:
        print(f"Error predicting property value: {str(e)}")
        return None

def calculate_land_feasibility(property_data, comps_data):
    """Calculate land development feasibility with robust input validation"""
    def safe_float(val, default=0.0):
        try:
            if val is None:
                return default
            if isinstance(val, (int, float)):
                return float(val)
            s = str(val).replace(",", "").replace("$", "").strip()
            return float(s)
        except Exception:
            return default

    if not comps_data.empty:
        sqft = safe_float(property_data.get('sqft'), 0)
        price = safe_float(property_data.get('price'), 0)
        if sqft == 0 or price == 0:
            return None  # Or optionally return a dict with an error message
        # Calculate average price per square foot of developed land
        avg_price_per_sqft = comps_data['price'].mean() / comps_data['sqft'].mean()
        # Estimate development costs (simplified)
        development_cost_per_sqft = 150  # Example value
        total_development_cost = sqft * development_cost_per_sqft
        # Calculate potential profit
        potential_value = sqft * avg_price_per_sqft
        current_value = price
        potential_profit = potential_value - current_value - total_development_cost
        return {
            'potential_value': potential_value,
            'development_cost': total_development_cost,
            'potential_profit': potential_profit,
            'roi': (potential_profit / current_value) * 100 if current_value else 0
        }
    return None 