import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

def calculate_investment_metrics(property_data, analysis_results, assumptions):
    """Calculate comprehensive investment metrics for a property"""
    
    price = property_data.get('price', 0)
    monthly_rent = analysis_results.get('monthlyRent', 0)
    
    # Basic calculations
    down_payment = price * (assumptions.get('downPaymentPct', 20) / 100)
    loan_amount = price - down_payment
    
    # Monthly mortgage payment calculation
    monthly_rate = assumptions.get('interestRate', 5.0) / 100 / 12
    num_payments = assumptions.get('loanTerm', 30) * 12
    
    if loan_amount > 0 and monthly_rate > 0:
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    else:
        monthly_payment = 0
    
    # Operating expenses
    monthly_property_tax = price * (assumptions.get('propertyTaxRate', 3.0) / 100) / 12
    monthly_insurance = price * (assumptions.get('insuranceRate', 0.5) / 100) / 12
    monthly_management = monthly_rent * 0.08  # 8% management fee
    monthly_maintenance = monthly_rent * (assumptions.get('maintenanceRate', 1.0) / 100)
    monthly_capital_reserves = monthly_rent * (assumptions.get('capitalReservesRate', 1.0) / 100)
    monthly_vacancy = monthly_rent * (assumptions.get('vacancyRate', 5.0) / 100)
    
    total_monthly_expenses = (monthly_property_tax + monthly_insurance + monthly_management + 
                             monthly_maintenance + monthly_capital_reserves + monthly_vacancy)
    
    monthly_cash_flow = monthly_rent - monthly_payment - total_monthly_expenses
    
    # Investment metrics
    annual_noi = (monthly_rent * 12) - (total_monthly_expenses * 12)
    cap_rate = (annual_noi / price) * 100 if price > 0 else 0
    
    total_upfront_cost = down_payment + price * (assumptions.get('closingCostsPct', 3.0) / 100)
    cash_on_cash = (monthly_cash_flow * 12) / total_upfront_cost * 100 if total_upfront_cost > 0 else 0
    
    break_even_rent = monthly_payment + total_monthly_expenses
    rent_to_price = (monthly_rent / price) * 100 if price > 0 else 0
    
    # Total ROI with appreciation
    appreciation = price * 0.03  # 3% appreciation
    total_roi = ((monthly_cash_flow * 12) + appreciation) / total_upfront_cost * 100 if total_upfront_cost > 0 else 0
    
    payback_period = total_upfront_cost / (monthly_cash_flow * 12) if monthly_cash_flow > 0 else float('inf')
    
    return {
        'monthlyRent': monthly_rent,
        'monthlyPayment': monthly_payment,
        'monthlyCashFlow': monthly_cash_flow,
        'capRate': cap_rate,
        'cashOnCash': cash_on_cash,
        'breakEvenRent': break_even_rent,
        'rentToPrice': rent_to_price,
        'totalROI': total_roi,
        'paybackPeriod': payback_period if payback_period != float('inf') else 999,
        'totalUpfrontCost': total_upfront_cost,
        'annualNOI': annual_noi
    }

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