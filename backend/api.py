from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import os
import io
from datetime import datetime
import sys
import os
# Add parent directory to Python path to access utils
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
print(f"Added to Python path: {parent_dir}")

# Only import what we need for Excel export
from utils.excel_generator import RealEstateExcelGenerator

# Try to import ML models but don't fail if they're not available
try:
from utils.ml_models import RentPredictor, PropertyPricePredictor
    from utils.data_loader import load_and_clean_sales_data, load_rental_data
from utils.analysis import calculate_investment_metrics
    ML_MODELS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  ML models not available: {e}")
    ML_MODELS_AVAILABLE = False
import numpy_financial as npf

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Load ML models
rent_predictor = None
price_predictor = None
comps_data = None
rental_data = None

def load_models():
    global rent_predictor, price_predictor, comps_data, rental_data
    print("Loading models...")
    
    if not ML_MODELS_AVAILABLE:
        print("⚠️  ML models not available - Excel export will still work")
        return
    
    try:
        rent_predictor = RentPredictor()
        rent_predictor.load_model('models/rent_predictor.joblib')
        print("✅ Rent predictor loaded successfully")
    except Exception as e:
        print(f"❌ Could not load rent predictor: {e}")
    
    try:
        price_predictor = PropertyPricePredictor()
        price_predictor.load_model('models/price_predictor.joblib')
        print("✅ Price predictor loaded successfully")
    except Exception as e:
        print(f"❌ Could not load price predictor: {e}")
    
    try:
        # Load sales data for price comparisons
        comps_data = load_and_clean_sales_data()
        print(f"✅ Sales data loaded: {len(comps_data)} records")
    except Exception as e:
        print(f"❌ Could not load sales data: {e}")
    
    try:
        # Load rental data for rent predictions and comparisons
        rental_data = load_rental_data()
        if rental_data is not None:
            print(f"✅ Rental data loaded: {len(rental_data)} records")
        else:
            print("❌ No rental data loaded")
    except Exception as e:
        print(f"❌ Could not load rental data: {e}")

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
        response_data = {'success': True, 'marketData': {}}
        
        # Sales data statistics
        if comps_data is not None:
        avg_price = comps_data['price'].mean()
        avg_price_per_sqft = (comps_data['price'] / comps_data['sqft']).mean()
        
            response_data['marketData']['sales'] = {
                'avgPrice': float(avg_price),
                'avgPricePerSqft': float(avg_price_per_sqft),
                'totalProperties': len(comps_data),
                'priceRange': {
                    'min': float(comps_data['price'].min()),
                    'max': float(comps_data['price'].max())
                }
            }
        
        # Rental data statistics
        if rental_data is not None:
            avg_rent = rental_data['rent'].mean()
            avg_rent_per_sqft = (rental_data['rent'] / rental_data['FinishedSqft']).mean()
            
            response_data['marketData']['rentals'] = {
                'avgRent': float(avg_rent),
                'avgRentPerSqft': float(avg_rent_per_sqft),
                'totalRentals': len(rental_data),
                'rentRange': {
                    'min': float(rental_data['rent'].min()),
                    'max': float(rental_data['rent'].max())
                },
                'avgRentByType': rental_data.groupby('PropertyType')['rent'].mean().to_dict() if 'PropertyType' in rental_data.columns else {},
                'avgRentByNeighborhood': rental_data.groupby('nbhd')['rent'].mean().head(10).to_dict() if 'nbhd' in rental_data.columns else {}
            }
        
        if comps_data is None and rental_data is None:
            return jsonify({
                'success': False,
                'error': 'No market data available'
            }), 400
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/rental-comps', methods=['POST'])
def get_rental_comps():
    """Get comparable rental properties"""
    try:
        if rental_data is None:
            return jsonify({
                'success': False,
                'error': 'Rental data not available'
            }), 400
        
        data = request.json
        bedrooms = data.get('bedrooms', 0)
        bathrooms = data.get('bathrooms', 0)
        sqft = data.get('sqft', 0)
        neighborhood = data.get('neighborhood', '')
        property_type = data.get('propertyType', '')
        
        # Filter rental comps
        filtered_data = rental_data.copy()
        
        # Filter by bedrooms (±1)
        if bedrooms > 0:
            filtered_data = filtered_data[
                (filtered_data['Bedrooms'] >= bedrooms - 1) & 
                (filtered_data['Bedrooms'] <= bedrooms + 1)
            ]
        
        # Filter by bathrooms (±0.5)
        if bathrooms > 0:
            filtered_data = filtered_data[
                (filtered_data['Bathrooms'] >= bathrooms - 0.5) & 
                (filtered_data['Bathrooms'] <= bathrooms + 1)
            ]
        
        # Filter by square footage (±300 sqft)
        if sqft > 0:
            filtered_data = filtered_data[
                (filtered_data['FinishedSqft'] >= sqft - 300) & 
                (filtered_data['FinishedSqft'] <= sqft + 300)
            ]
        
        # Prefer same neighborhood
        if neighborhood:
            neighborhood_matches = filtered_data[filtered_data['nbhd'].str.contains(neighborhood, case=False, na=False)]
            if len(neighborhood_matches) >= 3:
                filtered_data = neighborhood_matches
        
        # Prefer same property type
        if property_type:
            type_matches = filtered_data[filtered_data['PropertyType'].str.contains(property_type, case=False, na=False)]
            if len(type_matches) >= 3:
                filtered_data = type_matches
        
        # Get top 10 most similar
        comps = filtered_data.head(10).to_dict('records')
        
        # Calculate rental statistics
        if len(filtered_data) > 0:
            avg_rent = filtered_data['rent'].mean()
            rent_per_sqft = filtered_data['rent'] / filtered_data['FinishedSqft']
            avg_rent_per_sqft = rent_per_sqft.mean()
        else:
            avg_rent = 0
            avg_rent_per_sqft = 0
        
        return jsonify({
            'success': True,
            'comps': comps,
            'stats': {
                'avgRent': float(avg_rent),
                'avgRentPerSqft': float(avg_rent_per_sqft),
                'totalComps': len(comps),
                'rentRange': {
                    'min': float(filtered_data['rent'].min()) if len(filtered_data) > 0 else 0,
                    'max': float(filtered_data['rent'].max()) if len(filtered_data) > 0 else 0
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/export-excel', methods=['POST'])
def export_excel():
    """Generate and download Excel pro forma"""
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
            'propertyType': data.get('propertyType', 'House'),
            'zipcode': data.get('zipcode', ''),
            'totalUnits': int(data.get('totalUnits', 1))  # Added missing totalUnits!
        }
        
        # Extract analysis results
        results = data.get('results', {})
        
        # Extract assumptions
        assumptions = data.get('assumptions', {})
        
        # Get project name if provided
        project_name = data.get('projectName', f"Investment Analysis - {property_data['address']}")
        
        # Generate Excel file
        excel_generator = RealEstateExcelGenerator()
        excel_data = excel_generator.create_pro_forma(
            property_data, 
            results, 
            assumptions, 
            project_name
        )
        
        # Create a BytesIO object
        excel_file = io.BytesIO(excel_data)
        excel_file.seek(0)
        
        # Generate filename
        address_clean = property_data.get('address', 'Property').replace(' ', '_').replace(',', '')
        filename = f"Real_Estate_Pro_Forma_{address_clean}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"Excel export error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to generate Excel file: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("Loading models...")
    load_models()
    print("Starting Flask API server...")
    app.run(debug=True, host='0.0.0.0', port=5000) 