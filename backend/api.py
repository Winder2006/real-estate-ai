from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import os
from utils.ml_models import RentPredictor, PropertyPricePredictor
from utils.data_loader import load_and_clean_sales_data
from utils.analysis import calculate_investment_metrics
import numpy_financial as npf

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Load ML models
rent_predictor = None
price_predictor = None
comps_data = None

def load_models():
    global rent_predictor, price_predictor, comps_data
    try:
        rent_predictor = RentPredictor()
        rent_predictor.load_model('models/rent_predictor.joblib')
    except Exception as e:
        print(f"Could not load rent predictor: {e}")
    
    try:
        price_predictor = PropertyPricePredictor()
        price_predictor.load_model('models/price_predictor.joblib')
    except Exception as e:
        print(f"Could not load price predictor: {e}")
    
    try:
        comps_data = load_and_clean_sales_data()
    except Exception as e:
        print(f"Could not load comps data: {e}")

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Real Estate API is running'})

@app.route('/api/analyze', methods=['POST'])
def analyze_property():
    try:
        data = request.json
        
        # Extract property data
        property_data = {
            'address': data.get('address', ''),
            'price': float(data.get('price', 0)),
            'beds': int(data.get('beds', 0)),
            'baths': float(data.get('baths', 0)),
            'sqft': float(data.get('sqft', 0)),
            'neighborhood': data.get('neighborhood', ''),
            'property_type': data.get('propertyType', 'House'),
            'zipcode': data.get('zipcode', '')
        }
        
        # Extract investment assumptions
        assumptions = {
            'down_payment_pct': float(data.get('downPaymentPct', 20)),
            'interest_rate': float(data.get('interestRate', 5.0)),
            'loan_term': int(data.get('loanTerm', 30)),
            'property_tax_rate': float(data.get('propertyTaxRate', 3.0)),
            'insurance_rate': float(data.get('insuranceRate', 0.5)),
            'maintenance_rate': float(data.get('maintenanceRate', 1.0)),
            'capital_reserves_rate': float(data.get('capitalReservesRate', 1.0)),
            'vacancy_rate': float(data.get('vacancyRate', 5.0)),
            'closing_costs_pct': float(data.get('closingCostsPct', 3.0))
        }
        
        # Calculate basic metrics
        price = property_data['price']
        down_payment = price * (assumptions['down_payment_pct'] / 100)
        loan_amount = price - down_payment
        
        # Monthly mortgage payment
        monthly_rate = assumptions['interest_rate'] / 100 / 12
        num_payments = assumptions['loan_term'] * 12
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1) if loan_amount > 0 and monthly_rate > 0 else 0
        
        # Predict rent using ML model if available
        monthly_rent = price * 0.008  # Default estimate
        if rent_predictor and rent_predictor.model is not None:
            try:
                # Prepare input for rent prediction
                rent_input = {
                    'address': property_data['address'],
                    'sqft': property_data['sqft'],
                    'beds': property_data['beds'],
                    'baths': property_data['baths'],
                    'nbhd': property_data['neighborhood'],
                    'property_type': property_data['property_type'],
                    'zipcode': property_data['zipcode']
                }
                predicted_rent = rent_predictor.predict(rent_input)
                if predicted_rent and predicted_rent > 0:
                    monthly_rent = predicted_rent
            except Exception as e:
                print(f"Rent prediction failed: {e}")
        
        # Calculate expenses
        monthly_property_tax = price * (assumptions['property_tax_rate'] / 100) / 12
        monthly_insurance = price * (assumptions['insurance_rate'] / 100) / 12
        monthly_management = monthly_rent * 0.08
        monthly_maintenance = monthly_rent * (assumptions['maintenance_rate'] / 100)
        monthly_capital_reserves = monthly_rent * (assumptions['capital_reserves_rate'] / 100)
        monthly_vacancy = monthly_rent * (assumptions['vacancy_rate'] / 100)
        
        monthly_expenses = (monthly_property_tax + monthly_insurance + monthly_management + 
                           monthly_maintenance + monthly_capital_reserves + monthly_vacancy)
        
        monthly_cash_flow = monthly_rent - monthly_payment - monthly_expenses
        
        # Calculate investment metrics
        annual_operating_expenses = monthly_expenses * 12
        noi = (monthly_rent * 12) - annual_operating_expenses
        cap_rate = (noi / price) * 100 if price > 0 else 0
        
        total_upfront_cost = down_payment + price * (assumptions['closing_costs_pct'] / 100)
        cash_on_cash = (monthly_cash_flow * 12) / total_upfront_cost * 100 if total_upfront_cost > 0 else 0
        
        piti = monthly_payment + monthly_property_tax + monthly_insurance
        break_even_rent = piti + monthly_management + monthly_maintenance + monthly_capital_reserves + monthly_vacancy
        
        rent_to_price = (monthly_rent / price) * 100 if price > 0 else 0
        
        # Total ROI with appreciation
        appreciation = price * 0.03  # 3% appreciation
        total_roi = ((monthly_cash_flow * 12) + appreciation) / total_upfront_cost * 100 if total_upfront_cost > 0 else 0
        
        payback_period = total_upfront_cost / (monthly_cash_flow * 12) if monthly_cash_flow > 0 else float('inf')
        
        # Get comparable properties
        comps = []
        if comps_data is not None:
            try:
                # Filter comps by similar characteristics
                similar_comps = comps_data[
                    (comps_data['beds'] == property_data['beds']) &
                    (comps_data['price'] >= price * 0.8) &
                    (comps_data['price'] <= price * 1.2)
                ].head(5)
                
                for _, comp in similar_comps.iterrows():
                    comps.append({
                        'address': comp.get('address', 'Unknown'),
                        'price': float(comp.get('price', 0)),
                        'beds': int(comp.get('beds', 0)),
                        'baths': float(comp.get('baths', 0)),
                        'sqft': float(comp.get('sqft', 0)),
                        'pricePerSqft': float(comp.get('price', 0)) / float(comp.get('sqft', 1)) if comp.get('sqft', 0) > 0 else 0,
                        'soldDate': comp.get('sale_date', 'Unknown'),
                        'distance': 0.5  # Mock distance
                    })
            except Exception as e:
                print(f"Comps calculation failed: {e}")
        
        # Generate recommendation
        if cap_rate >= 6 and cash_on_cash >= 8 and monthly_cash_flow >= 300:
            recommendation = 'Strong Buy'
        elif cap_rate >= 5 and cash_on_cash >= 6 and monthly_cash_flow >= 200:
            recommendation = 'Buy'
        elif cap_rate >= 4 and cash_on_cash >= 4 and monthly_cash_flow >= 100:
            recommendation = 'Hold'
        else:
            recommendation = "Don't Buy"
        
        return jsonify({
            'success': True,
            'results': {
                'monthlyRent': monthly_rent,
                'monthlyPayment': monthly_payment,
                'monthlyCashFlow': monthly_cash_flow,
                'capRate': cap_rate,
                'cashOnCash': cash_on_cash,
                'breakEvenRent': break_even_rent,
                'rentToPrice': rent_to_price,
                'totalROI': total_roi,
                'paybackPeriod': payback_period if payback_period != float('inf') else 999
            },
            'recommendation': recommendation,
            'comps': comps,
            'propertyData': property_data,
            'assumptions': assumptions
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/market-data', methods=['GET'])
def get_market_data():
    try:
        if comps_data is None:
            return jsonify({
                'success': False,
                'error': 'Market data not available'
            }), 400
        
        # Calculate market statistics
        avg_price = comps_data['price'].mean()
        avg_price_per_sqft = (comps_data['price'] / comps_data['sqft']).mean()
        
        return jsonify({
            'success': True,
            'marketData': {
                'avgPrice': float(avg_price),
                'avgPricePerSqft': float(avg_price_per_sqft),
                'totalProperties': len(comps_data),
                'priceRange': {
                    'min': float(comps_data['price'].min()),
                    'max': float(comps_data['price'].max())
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    print("Loading models...")
    load_models()
    print("Starting Flask API server...")
    app.run(debug=True, host='0.0.0.0', port=5000) 