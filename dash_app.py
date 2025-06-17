import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from datetime import datetime
import joblib
from utils.ml_models import RentPredictor
import utils.visualization as visualization
import utils.data_loader as data_loader
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
from dash import dash_table
from dash.dependencies import MATCH, ALL

# Load model
rent_predictor = RentPredictor()
rent_predictor.load_model('models/rent_predictor.joblib')

# Load comps data once at app start
comps_data = data_loader.load_and_clean_sales_data()

# Helper for investment logic
BUY_THRESHOLD_CAP_RATE = 6
BUY_THRESHOLD_CASH_FLOW = 300

def investment_recommendation(cap_rate, cash_flow):
    if cap_rate > BUY_THRESHOLD_CAP_RATE and cash_flow > BUY_THRESHOLD_CASH_FLOW:
        return ("Buy", "#22c55e", "✅ Buy — This appears to be a good investment opportunity!")
    elif cap_rate < BUY_THRESHOLD_CAP_RATE and cash_flow < BUY_THRESHOLD_CASH_FLOW:
        return ("Don't Buy", "#e02424", "❌ Don't Buy — This property does not meet your investment criteria.")
    else:
        return ("Hold", "#eab308", "⏸️ Hold — This property is close, but not quite a buy.")

def needed_numbers(cap_rate, cash_flow, break_even_rent, price):
    needed_cash_flow = max(0, BUY_THRESHOLD_CASH_FLOW - cash_flow)
    needed_cap_rate = max(0, BUY_THRESHOLD_CAP_RATE - cap_rate)
    needed_rent_for_cash_flow = break_even_rent + BUY_THRESHOLD_CASH_FLOW
    needed_rent_for_cap_rate = ((BUY_THRESHOLD_CAP_RATE/100) * price) / 12
    return needed_cash_flow, needed_cap_rate, needed_rent_for_cash_flow, needed_rent_for_cap_rate

# Helper to get feature importances from RentPredictor
def get_feature_importance(model):
    if model.model is not None and hasattr(model.model, 'feature_importances_'):
        feature_names = (model.preprocessor.named_transformers_['num'].get_feature_names_out().tolist() +
                        model.preprocessor.named_transformers_['cat'].get_feature_names_out().tolist())
        importances = model.model.feature_importances_
        return feature_names, importances
    return [], []

# Helper to geocode address
geolocator = Nominatim(user_agent="real_estate_dash", timeout=3)
def geocode_address(address, zipcode=None, city="Milwaukee", state="WI", timeout=3):
    try:
        # Try full address first
        location = geolocator.geocode(address, timeout=timeout)
        if location:
            return location.latitude, location.longitude
        # Try appending city/state/zip
        if address and (zipcode or city or state):
            address_full = address
            if zipcode and zipcode not in address:
                address_full += f", {zipcode}"
            if city and city not in address:
                address_full += f", {city}"
            if state and state not in address:
                address_full += f", {state}"
            location = geolocator.geocode(address_full, timeout=timeout)
            if location:
                return location.latitude, location.longitude
    except Exception:
        pass
    return None, None

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

app.layout = dbc.Container([
    html.H2("Real Estate Investment Analyzer (Dash)"),
    dcc.Store(id="base_rent_value"),
    dcc.Store(id="whatif_rent_value"),
    dbc.Row([
        dbc.Col([
            dbc.Label("Compare Scenarios"),
            dbc.Checklist(
                options=[{"label": "Enable", "value": 1}],
                value=[],
                id="compare_toggle",
                switch=True,
                inline=True,
                style={"marginBottom": "1rem"}
            ),
        ], width=3),
    ]),
    dbc.Row([
        # Sidebar controls
        dbc.Col([
            html.H4("Investment Assumptions"),
            dbc.Label("Down Payment (%)"),
            dcc.Slider(0, 100, 5, value=20, id="down_payment_pct", marks={0: "0%", 100: "100%"}, tooltip={"placement": "bottom", "always_visible": True}),
            dbc.Label("Interest Rate (%)"),
            dcc.Slider(0, 10, 0.1, value=5.0, id="interest_rate", marks={0: "0%", 10: "10%"}, tooltip={"placement": "bottom", "always_visible": True}),
            dbc.Label("Loan Term (years)"),
            dcc.Slider(15, 30, 1, value=30, id="loan_term", marks={15: "15", 30: "30"}, tooltip={"placement": "bottom", "always_visible": True}),
            dbc.Label("Property Tax Rate (%)"),
            dcc.Slider(0, 5, 0.1, value=3.0, id="property_tax_rate", marks={0: "0%", 5: "5%"}, tooltip={"placement": "bottom", "always_visible": True}),
            dbc.Label("Insurance Rate (%)"),
            dcc.Slider(0, 2, 0.1, value=0.5, id="insurance_rate", marks={0: "0%", 2: "2%"}, tooltip={"placement": "bottom", "always_visible": True}),
            dbc.Label("Maintenance Rate (%)"),
            dcc.Slider(0, 5, 0.1, value=1.0, id="maintenance_rate", marks={0: "0%", 5: "5%"}, tooltip={"placement": "bottom", "always_visible": True}),
            dbc.Label("Capital Reserves Rate (%)"),
            dcc.Slider(0, 5, 0.1, value=1.0, id="capital_reserves_rate", marks={0: "0%", 5: "5%"}, tooltip={"placement": "bottom", "always_visible": True}),
            dbc.Label("Vacancy Rate (% of Rent)"),
            dcc.Slider(0, 20, 0.5, value=5.0, id="vacancy_rate", marks={0: "0%", 20: "20%"}, tooltip={"placement": "bottom", "always_visible": True}),
            dbc.Label("Closing Costs (%)"),
            dcc.Slider(0, 10, 0.1, value=3.0, id="closing_costs_pct", marks={0: "0%", 10: "10%"}, tooltip={"placement": "bottom", "always_visible": True}),
            html.Br(),
            dbc.Button("Predict & Analyze", id="analyze_btn", color="primary"),
            # Scenario 2 controls (always rendered, visibility controlled by style)
            html.Div(id="scenario2_controls", children=[
                html.Hr(),
                html.H4("What If Scenario"),
                dbc.Label("Down Payment (%)"),
                dcc.Slider(0, 100, 5, value=20, id="down_payment_pct2", marks={0: "0%", 100: "100%"}, tooltip={"placement": "bottom", "always_visible": True}),
                dbc.Label("Interest Rate (%)"),
                dcc.Slider(0, 10, 0.1, value=5.0, id="interest_rate2", marks={0: "0%", 10: "10%"}, tooltip={"placement": "bottom", "always_visible": True}),
                dbc.Label("Loan Term (years)"),
                dcc.Slider(15, 30, 1, value=30, id="loan_term2", marks={15: "15", 30: "30"}, tooltip={"placement": "bottom", "always_visible": True}),
                dbc.Label("Property Tax Rate (%)"),
                dcc.Slider(0, 5, 0.1, value=3.0, id="property_tax_rate2", marks={0: "0%", 5: "5%"}, tooltip={"placement": "bottom", "always_visible": True}),
                dbc.Label("Insurance Rate (%)"),
                dcc.Slider(0, 2, 0.1, value=0.5, id="insurance_rate2", marks={0: "0%", 2: "2%"}, tooltip={"placement": "bottom", "always_visible": True}),
                dbc.Label("Maintenance Rate (%)"),
                dcc.Slider(0, 5, 0.1, value=1.0, id="maintenance_rate2", marks={0: "0%", 5: "5%"}, tooltip={"placement": "bottom", "always_visible": True}),
                dbc.Label("Capital Reserves Rate (%)"),
                dcc.Slider(0, 5, 0.1, value=1.0, id="capital_reserves_rate2", marks={0: "0%", 5: "5%"}, tooltip={"placement": "bottom", "always_visible": True}),
                dbc.Label("Vacancy Rate (% of Rent)"),
                dcc.Slider(0, 20, 0.5, value=5.0, id="vacancy_rate2", marks={0: "0%", 20: "20%"}, tooltip={"placement": "bottom", "always_visible": True}),
                dbc.Label("Closing Costs (%)"),
                dcc.Slider(0, 10, 0.1, value=3.0, id="closing_costs_pct2", marks={0: "0%", 10: "10%"}, tooltip={"placement": "bottom", "always_visible": True}),
                html.Br(),
                html.H5("What If Property Information"),
                dbc.Label("Address"),
                dbc.Input(id="address2", type="text"),
                dbc.Label("Price ($)"),
                dbc.Input(id="price2", type="number"),
                dbc.Label("Bedrooms"),
                dbc.Input(id="beds2", type="number", min=0, max=10, step=1),
                dbc.Label("Bathrooms"),
                dbc.Input(id="baths2", type="number", min=0, max=10, step=1),
                dbc.Label("Square Footage"),
                dbc.Input(id="sqft2", type="number"),
                dbc.Label("Neighborhood"),
                dbc.Input(id="nbhd2", type="text"),
                dbc.Label("Property Type"),
                dcc.Dropdown([
                    {"label": t, "value": t} for t in ["House", "Duplex", "Apartment", "Condo"]
                ], id="ptype2", value="House"),
                dbc.Label("Zip Code"),
                dbc.Input(id="zipcode2", type="text"),
            ], style={"display": "none"}),
        ], width=3),
        # Main content
        dbc.Col([
            html.H4("Property Information"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Address"),
                    dbc.Input(id="address", type="text"),
                    dbc.Label("Price ($)"),
                    dbc.Input(id="price", type="number"),
                    dbc.Label("Bedrooms"),
                    dbc.Input(id="beds", type="number", min=0, max=10, step=1),
                    dbc.Label("Bathrooms"),
                    dbc.Input(id="baths", type="number", min=0, max=10, step=1),
                    dbc.Label("Square Footage"),
                    dbc.Input(id="sqft", type="number"),
                ]),
                dbc.Col([
                    dbc.Label("Neighborhood"),
                    dbc.Input(id="nbhd", type="text"),
                    dbc.Label("Property Type"),
                    dcc.Dropdown([
                        {"label": t, "value": t} for t in ["House", "Duplex", "Apartment", "Condo"]
                    ], id="ptype", value="House"),
                    dbc.Label("Zip Code"),
                    dbc.Input(id="zipcode", type="text"),
                ]),
            ]),
            html.Br(),
            # --- Rental Income Analysis Section ---
            html.Div([
                html.H4("Rental Income Analysis"),
                html.Div([
                    dbc.Label("Third-Party Rent Estimate", html_for="third_party_rent_input", style={"fontWeight": "bold"}),
                    dbc.Input(id="third_party_rent_input", type="number", min=0, step=1, placeholder="e.g. 2200", style={"maxWidth": "300px"}),
                    html.Span("Enter a rent estimate from Zillow, Redfin, Rentometer, or any other third-party source.", style={"fontSize": "0.95em", "color": "#888"}),
                ], style={"marginBottom": "1em"}),
                html.Div([
                    dbc.Label([
                        "ML Predicted Rent ",
                        html.I(className="bi bi-info-circle-fill", id="est_rent_tooltip", style={"marginLeft": "0.5em", "color": "#888"}),
                    ], html_for="ml_rent_input", style={"fontWeight": "bold"}),
                    dbc.Input(id="ml_rent_input", type="number", min=0, step=1, placeholder="e.g. 2200", style={"maxWidth": "300px"}),
                    html.Span("This is the rent predicted by the app's machine learning model. You may adjust it if needed.", style={"fontSize": "0.95em", "color": "#888"}),
                ], style={"marginBottom": "1em"}),
                dbc.RadioItems(
                    id="rent_source_toggle",
                    options=[
                        {"label": "Use Third-Party Rent for Analysis", "value": "third_party"},
                        {"label": "Use ML Predicted Rent for Analysis", "value": "ml"},
                    ],
                    value="ml",
                    inline=True,
                    style={"marginBottom": "1em"},
                ),
                html.Div(id="rent_gap_display"),
                html.Div(id="rent_used_summary", style={"marginTop": "0.5em", "fontWeight": "bold"}),
            ], style={"marginBottom": "2em", "marginTop": "1em", "padding": "1em", "background": "#f8fafc", "borderRadius": "8px", "boxShadow": "0 2px 8px #0001"}),
            html.Div(id="prediction_output"),
            html.Div(id="investment_output"),
            html.Div(id="metrics_output"),
            dbc.Row([
                dbc.Col([dash_table.DataTable(
                    id="comps_table",
                    style_table={"overflowX": "auto", "backgroundColor": "#f8fafc", "borderRadius": "8px", "padding": "8px"},
                    style_header={"backgroundColor": "#e0e7ef", "fontWeight": "bold", "fontSize": "18px"},
                    style_cell={"fontSize": "16px", "fontFamily": "Inter, Arial", "padding": "6px"},
                    page_size=10,
                )], width=6),
                dbc.Col([dcc.Graph(id="expense_pie")], width=6),
            ]),
            dbc.Row([
                dbc.Col([dcc.Graph(id="cashflow_chart")], width=6),
            ]),
            dbc.Row([
                dbc.Col([dcc.Graph(id="feature_importance")], width=6),
                dbc.Col([dcc.Graph(id="geo_map")], width=6),
            ]),
        ], width=9)
    ])
], fluid=True)

@app.callback(
    [Output("prediction_output", "children"), Output("investment_output", "children"), Output("metrics_output", "children"), Output("comps_table", "data"), Output("comps_table", "columns"), Output("expense_pie", "figure"),
     Output("cashflow_chart", "figure"), Output("feature_importance", "figure"), Output("geo_map", "figure")],
    Input("analyze_btn", "n_clicks"),
    State("compare_toggle", "value"),
    # Base Case
    State("address", "value"),
    State("price", "value"),
    State("beds", "value"),
    State("baths", "value"),
    State("sqft", "value"),
    State("nbhd", "value"),
    State("ptype", "value"),
    State("zipcode", "value"),
    State("down_payment_pct", "value"),
    State("interest_rate", "value"),
    State("loan_term", "value"),
    State("property_tax_rate", "value"),
    State("insurance_rate", "value"),
    State("maintenance_rate", "value"),
    State("capital_reserves_rate", "value"),
    State("vacancy_rate", "value"),
    State("closing_costs_pct", "value"),
    State("base_rent_value", "data"),
    # What If Scenario
    State("address2", "value"),
    State("price2", "value"),
    State("beds2", "value"),
    State("baths2", "value"),
    State("sqft2", "value"),
    State("nbhd2", "value"),
    State("ptype2", "value"),
    State("zipcode2", "value"),
    State("down_payment_pct2", "value"),
    State("interest_rate2", "value"),
    State("loan_term2", "value"),
    State("property_tax_rate2", "value"),
    State("insurance_rate2", "value"),
    State("maintenance_rate2", "value"),
    State("capital_reserves_rate2", "value"),
    State("vacancy_rate2", "value"),
    State("closing_costs_pct2", "value"),
)
def analyze(n_clicks, compare_toggle,
            address, price, beds, baths, sqft, nbhd, property_type, zipcode,
            down_payment_pct, interest_rate, loan_term, property_tax_rate, insurance_rate,
            maintenance_rate, capital_reserves_rate, vacancy_rate, closing_costs_pct,
            base_rent_value,
            address2, price2, beds2, baths2, sqft2, nbhd2, property_type2, zipcode2,
            down_payment_pct2, interest_rate2, loan_term2, property_tax_rate2, insurance_rate2,
            maintenance_rate2, capital_reserves_rate2, vacancy_rate2, closing_costs_pct2):
    print("[DEBUG] analyze callback triggered")
    try:
        if not n_clicks:
            print("[DEBUG] analyze: n_clicks is None or 0")
            return "", "", "", [], [], {}, {}, {}, {}
        def scenario_outputs(address, price, beds, baths, sqft, nbhd, property_type, zipcode,
                            down_payment_pct, interest_rate, loan_term, property_tax_rate, insurance_rate,
                            maintenance_rate, capital_reserves_rate, vacancy_rate, closing_costs_pct,
                            scenario_label="Base Case", rent_override=None):
            try:
                print(f"[DEBUG] scenario_outputs called for {scenario_label}")
                # Always define *_col variables at the top
                zip_col = 'zipcode' if 'zipcode' in comps_data.columns else 'ZipCode' if 'ZipCode' in comps_data.columns else None
                beds_col = 'beds' if 'beds' in comps_data.columns else 'Bedrooms' if 'Bedrooms' in comps_data.columns else None
                baths_col = 'baths' if 'baths' in comps_data.columns else 'Bathrooms' if 'Bathrooms' in comps_data.columns else None
                sqft_col = 'sqft' if 'sqft' in comps_data.columns else 'FinishedSqft' if 'FinishedSqft' in comps_data.columns else None
                price_col = 'price' if 'price' in comps_data.columns else 'Sale_price' if 'Sale_price' in comps_data.columns else None
                year_col = 'year_built' if 'year_built' in comps_data.columns else 'Year_Built' if 'Year_Built' in comps_data.columns else 'year' if 'year' in comps_data.columns else None
                address_col = 'address' if 'address' in comps_data.columns else 'Address' if 'Address' in comps_data.columns else None
                # Always define filtered as a DataFrame at the top
                filtered = pd.DataFrame()
                try:
                    # Comps table (use property info for this scenario)
                    property_data = {'sqft': sqft, 'price': price, 'zipcode': zipcode, 'beds': beds, 'baths': baths}
                    filtered = comps_data.copy()
                    # Filter by zip code
                    if zip_col and zipcode:
                        filtered = filtered[filtered[zip_col] == zipcode]
                    if beds_col and beds is not None and beds_col in filtered.columns:
                        filtered = filtered[(filtered[beds_col] >= beds - 1) & (filtered[beds_col] <= beds + 1)]
                    if baths_col and baths is not None and baths_col in filtered.columns:
                        filtered = filtered[(filtered[baths_col] >= baths - 1) & (filtered[baths_col] <= baths + 1)]
                    if sqft_col and sqft is not None and sqft_col in filtered.columns:
                        filtered = filtered[(filtered[sqft_col] >= sqft * 0.8) & (filtered[sqft_col] <= sqft * 1.2)]
                    # Remove outliers (1st–99th percentile)
                    if price_col and sqft_col and not filtered.empty and price_col in filtered.columns and sqft_col in filtered.columns:
                        price_low = np.percentile(filtered[price_col], 1)
                        sqft_low = np.percentile(filtered[sqft_col], 1)
                        filtered = filtered[(filtered[price_col] >= price_low) & (filtered[price_col] <= 800000) &
                                            (filtered[sqft_col] >= sqft_low) & (filtered[sqft_col] <= 6000)]
                    # Add BedDiff and BathDiff for sorting
                    if beds_col and beds is not None and beds_col in filtered.columns:
                        filtered['BedDiff'] = (filtered[beds_col] - beds).abs()
                    else:
                        filtered['BedDiff'] = 0
                    if baths_col and baths is not None and baths_col in filtered.columns:
                        filtered['BathDiff'] = (filtered[baths_col] - baths).abs()
                    else:
                        filtered['BathDiff'] = 0
                    # Add PriceDiff for sorting (absolute difference from user price)
                    if price_col and price is not None and price_col in filtered.columns:
                        filtered['PriceDiff'] = (filtered[price_col] - price).abs()
                    else:
                        filtered['PriceDiff'] = 0
                    # Sort by BedDiff, then BathDiff, then PriceDiff
                    sort_cols = ['BedDiff', 'BathDiff', 'PriceDiff']
                    filtered = filtered.sort_values(by=sort_cols, ascending=[True, True, True]) if not filtered.empty else filtered
                    # Prepare columns for display (hide BedDiff, BathDiff, PriceDiff)
                    table_cols = []
                    if address_col: table_cols.append({'name': 'Address', 'id': address_col})
                    if price_col: table_cols.append({'name': 'Price', 'id': price_col, 'type': 'numeric', 'format': {'specifier': '$,.0f'}})
                    if sqft_col: table_cols.append({'name': 'Sqft', 'id': sqft_col})
                    if beds_col: table_cols.append({'name': 'Beds', 'id': beds_col})
                    if baths_col: table_cols.append({'name': 'Baths', 'id': baths_col})
                    if year_col: table_cols.append({'name': 'Year Built', 'id': year_col})
                    if zip_col: table_cols.append({'name': 'Zip Code', 'id': zip_col})
                    table_data = filtered[ [c['id'] for c in table_cols if c['id'] in filtered.columns] ].to_dict('records') if not filtered.empty else []
                    if not table_data:
                        table_data = [{c['id']: 'No comparable properties found.' for c in table_cols}] if table_cols else [{'Notice': 'No comparable properties found.'}]
                except Exception as e:
                    # If anything fails, fallback to empty comps
                    table_cols = []
                    table_data = [{'Notice': f'Comps error: {e}'}]
                    filtered = pd.DataFrame()
                # Prepare ML input
                ml_input = {
                    'FinishedSqft': sqft,
                    'Bedrooms': beds,
                    'Bathrooms': baths,
                    'nbhd': nbhd,
                    'PropertyType': property_type,
                    'zipcode': zipcode
                }
                # Feature engineering
                ml_input['BedBath'] = beds * baths if beds is not None and baths is not None else 0
                ml_input['SqftPerBed'] = sqft / beds if sqft is not None and beds is not None and beds != 0 else 0
                ml_input['LogSqft'] = np.log1p(sqft) if sqft is not None else 0
                ml_input['SaleMonth'] = datetime.now().month
                # ML prediction
                prediction = rent_predictor.predict_with_range(ml_input)
                one_percent_rent = price * 0.01 if price else 0
                # --- Investment calculations ---
                price_val = price or 0
                down_payment = price_val * (down_payment_pct / 100)
                loan_amount = price_val - down_payment
                monthly_rate = (interest_rate / 100) / 12
                num_payments = loan_term * 12
                monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1) if loan_amount > 0 and monthly_rate > 0 else 0
                # Use rent_override if provided, else ML prediction
                monthly_rent = rent_override if rent_override is not None else prediction['predicted_rent']
                try:
                    monthly_rent = float(monthly_rent)
                except Exception:
                    monthly_rent = 0.0
                annual_property_tax = price_val * (property_tax_rate / 100)
                annual_insurance = price_val * (insurance_rate / 100)
                annual_management = monthly_rent * 0.08 * 12
                annual_maintenance = monthly_rent * (maintenance_rate / 100) * 12
                annual_capital_reserves = monthly_rent * (capital_reserves_rate / 100) * 12
                annual_vacancy = monthly_rent * (vacancy_rate / 100) * 12
                annual_expenses = (
                    annual_property_tax + annual_insurance + annual_management +
                    annual_maintenance + annual_capital_reserves + annual_vacancy
                )
                monthly_expenses = annual_expenses / 12
                monthly_cash_flow = monthly_rent - monthly_payment - monthly_expenses
                noi = (monthly_rent * 12) - annual_expenses
                cap_rate = (noi / price_val) * 100 if price_val > 0 else 0
                piti = monthly_payment + (annual_property_tax + annual_insurance) / 12
                monthly_management = annual_management / 12
                monthly_maintenance = annual_maintenance / 12
                monthly_capital_reserves = annual_capital_reserves / 12
                monthly_vacancy = annual_vacancy / 12
                break_even_rent = piti + monthly_management + monthly_maintenance + monthly_capital_reserves + monthly_vacancy
                rec, rec_color, rec_msg = investment_recommendation(cap_rate, monthly_cash_flow)
                needed_cash_flow, needed_cap_rate, needed_rent_for_cash_flow, needed_rent_for_cap_rate = needed_numbers(cap_rate, monthly_cash_flow, break_even_rent, price_val)
                prediction_row = dbc.Row([
                    dbc.Col([
                        html.H4(f"Predicted Rent Range: ${prediction['lower_bound']:,.0f} - ${prediction['upper_bound']:,.0f}"),
                        html.P(f"Based on model MAE (${prediction['confidence_range']:,.0f}), actual rent is likely in this range."),
                        html.P("The analyzer assumes the property is or will be rented at full market rate, based on property size, condition, and comps in the neighborhood.", style={"fontSize": "1.05em", "color": "#666", "marginTop": "0.5em"}),
                    ], width=8),
                    dbc.Col([
                        html.H4(f"1% Rule Rent: ${one_percent_rent:,.0f}", style={"color": "#888"}),
                    ], width=4)
                ])
                invest_metrics = html.Div([
                    html.H5("Investment Recommendation"),
                    html.Div(rec_msg, style={"color": rec_color, "fontWeight": "bold", "fontSize": "1.2rem"}),
                    html.Ul([
                        html.Li(f"Monthly cash flow needs to be at least ${BUY_THRESHOLD_CASH_FLOW:,} (currently ${monthly_cash_flow:,.2f})"),
                        html.Li(f"Cap rate needs to be at least {BUY_THRESHOLD_CAP_RATE}% (currently {cap_rate:.2f}%)"),
                        html.Li(f"Minimum rent needed for cash flow: ${needed_rent_for_cash_flow:,.0f}/mo"),
                        html.Li(f"Minimum rent needed for cap rate: ${needed_rent_for_cap_rate:,.0f}/mo"),
                    ], style={"fontSize": "1.1rem"})
                ], style={"marginTop": "2rem"})
                # --- Metrics Section ---
                total_cash_invested = down_payment + (price_val * (closing_costs_pct / 100))
                cash_on_cash = ((monthly_cash_flow * 12) / total_cash_invested * 100) if total_cash_invested > 0 else 0
                annual_debt_service = monthly_payment * 12
                dscr = (noi / annual_debt_service) if annual_debt_service > 0 else 0
                grm = (price_val / (monthly_rent * 12)) if monthly_rent > 0 else 0
                operating_expense_ratio = (annual_expenses / (monthly_rent * 12)) if monthly_rent > 0 else 0
                break_even_occupancy = (annual_expenses + annual_debt_service) / (monthly_rent * 12) if monthly_rent > 0 else 0
                rent_to_value = (monthly_rent / price_val) if price_val > 0 else 0
                metrics = [
                    {
                        'label': 'Cash-on-Cash Return',
                        'value': f"{cash_on_cash:.2f}%",
                        'desc': '(Annual cash flow / total cash invested)',
                        'benchmark': '> 8%',
                        'good': cash_on_cash > 8
                    },
                    {
                        'label': 'Debt Service Coverage Ratio (DSCR)',
                        'value': f"{dscr:.2f}",
                        'desc': '(NOI / annual debt service)',
                        'benchmark': '> 1.2',
                        'good': dscr > 1.2
                    },
                    {
                        'label': 'Gross Rent Multiplier (GRM)',
                        'value': f"{grm:.2f}",
                        'desc': '(Price / gross annual rent)',
                        'benchmark': '< 10',
                        'good': grm < 10 and grm > 0
                    },
                    {
                        'label': 'Operating Expense Ratio',
                        'value': f"{operating_expense_ratio:.2%}",
                        'desc': '(Expenses / gross income)',
                        'benchmark': '< 50%',
                        'good': operating_expense_ratio < 0.5 and operating_expense_ratio > 0
                    },
                    {
                        'label': 'Break-Even Occupancy Rate',
                        'value': f"{break_even_occupancy:.2%}",
                        'desc': '(Occupancy needed to cover all costs)',
                        'benchmark': '< 85%',
                        'good': break_even_occupancy < 0.85 and break_even_occupancy > 0
                    },
                    {
                        'label': 'Rent-to-Value Ratio',
                        'value': f"{rent_to_value:.2%}",
                        'desc': '(Monthly rent / price)',
                        'benchmark': '> 0.8%',
                        'good': rent_to_value > 0.008
                    },
                ]
                metrics_output = dbc.Card([
                    dbc.CardHeader(f"Key Investment Metrics — {scenario_label}"),
                    dbc.CardBody([
                        html.Table([
                            html.Thead([
                                html.Tr([
                                    html.Th("Metric"),
                                    html.Th("Value"),
                                    html.Th("Benchmark"),
                                    html.Th("Status")
                                ])
                            ]),
                            html.Tbody([
                                html.Tr([
                                    html.Td([
                                        html.B(m['label']), html.Br(),
                                        html.Span(m['desc'], style={"color": "#888", "fontSize": "0.95em"})
                                    ]),
                                    html.Td(m['value']),
                                    html.Td(m['benchmark']),
                                    html.Td(
                                        "✅" if m['good'] else "❌",
                                        style={"color": "#22c55e" if m['good'] else "#e02424", "fontSize": "1.5em", "textAlign": "center"}
                                    )
                                ]) for m in metrics
                            ])
                        ], style={"width": "100%", "fontSize": "1.1rem", "marginTop": "1rem"})
                    ])
                ], style={"marginTop": "2rem", "marginBottom": "2rem", "backgroundColor": "#f8fafc"})
                # Expense breakdown
                annual_expenses_dict = {
                    'Property Tax': annual_property_tax,
                    'Insurance': annual_insurance,
                    'Management': annual_management,
                    'Maintenance': annual_maintenance,
                    'Capital Reserves': annual_capital_reserves,
                    'Vacancy': annual_vacancy
                }
                expense_fig = visualization.create_expense_breakdown_chart(annual_expenses_dict)
                # Feature Importance
                feat_names, feat_imps = get_feature_importance(rent_predictor)
                featimp_fig = go.Figure()
                if feat_names and feat_imps is not None:
                    featimp_fig.add_trace(go.Bar(x=feat_names, y=feat_imps, marker_color='#4F8EF7'))
                    featimp_fig.update_layout(
                        title='ML Feature Importance',
                        xaxis_title='Feature',
                        yaxis_title='Importance',
                        font=dict(size=18, family='Inter, Arial'),
                        title_font=dict(size=26, family='Inter, Arial'),
                        margin=dict(l=60, r=40, t=80, b=120),
                        plot_bgcolor='#f8fafc',
                        paper_bgcolor='#f8fafc',
                        legend=dict(font=dict(size=16), bgcolor='#f8fafc', bordercolor='#e0e7ef', borderwidth=1),
                        xaxis=dict(tickangle=45, tickfont=dict(size=14)),
                        yaxis=dict(tickfont=dict(size=16)),
                    )
                # Geographic Map
                lat, lon = geocode_address(address, zipcode=zipcode) if address else (None, None)
                geo_fig = go.Figure()
                comps_lat, comps_lon, comps_text = [], [], []
                try:
                    # Add comps to map if available and address_col is valid
                    if not filtered.empty and lat and lon and address_col and address_col in filtered.columns:
                        for _, comp in filtered.iterrows():
                            if comp[address_col]:
                                comp_lat, comp_lon = geocode_address(comp[address_col])
                                if comp_lat and comp_lon:
                                    comps_lat.append(comp_lat)
                                    comps_lon.append(comp_lon)
                                    price_str = f"${comp[price_col]:,.0f}" if price_col and price_col in comp else "N/A"
                                    beds_val = comp[beds_col] if beds_col and beds_col in comp else 'N/A'
                                    baths_val = comp[baths_col] if baths_col and baths_col in comp else 'N/A'
                                    sqft_val = comp[sqft_col] if sqft_col and sqft_col in comp else 'N/A'
                                    comps_text.append(f"Price: {price_str}<br>Beds: {beds_val}<br>Baths: {baths_val}<br>Sqft: {sqft_val}")
                        if comps_lat:
                            geo_fig.add_trace(go.Scattermapbox(
                                lat=comps_lat,
                                lon=comps_lon,
                                mode='markers',
                                marker=dict(size=12, color='#4F8EF7', opacity=0.7),
                                name='Comparable Properties',
                                text=comps_text,
                                hoverinfo='text'
                            ))
                    if lat and lon:
                        geo_fig.add_trace(go.Scattermapbox(
                            lat=[lat],
                            lon=[lon],
                            mode='markers',
                            marker=dict(size=18, color='#e02424'),
                            name='Subject Property',
                            text=[f"Subject Property<br>Price: ${price:,.0f}<br>Beds: {beds}<br>Baths: {baths}<br>Sqft: {sqft:,.0f}"],
                            hoverinfo='text'
                        ))
                        all_lats = [lat] + comps_lat if comps_lat else [lat]
                        all_lons = [lon] + comps_lon if comps_lon else [lon]
                        center_lat = sum(all_lats) / len(all_lats)
                        center_lon = sum(all_lons) / len(all_lons)
                        lat_range = max(all_lats) - min(all_lats)
                        lon_range = max(all_lons) - min(all_lons)
                        max_range = max(lat_range, lon_range)
                        zoom = 12 if max_range < 0.01 else 11 if max_range < 0.02 else 10
                        geo_fig.update_layout(
                            mapbox_style="open-street-map",
                            mapbox=dict(
                                center=dict(lat=center_lat, lon=center_lon),
                                zoom=zoom
                            ),
                            title="Property Location with Comparables",
                            font=dict(size=18, family='Inter, Arial'),
                            title_font=dict(size=26, family='Inter, Arial'),
                            margin=dict(l=60, r=40, t=80, b=80),
                            plot_bgcolor='#f8fafc',
                            paper_bgcolor='#f8fafc',
                            legend=dict(
                                font=dict(size=16),
                                bgcolor='#f8fafc',
                                bordercolor='#e0e7ef',
                                borderwidth=1
                            ),
                            showlegend=True
                        )
                    else:
                        milwaukee_lat, milwaukee_lon = 43.0389, -87.9065
                        geo_fig.add_trace(go.Scattermapbox(
                            lat=[milwaukee_lat],
                            lon=[milwaukee_lon],
                            mode='markers',
                            marker=dict(size=14, color='#888'),
                            name='Milwaukee Center',
                            text=["Default Location - Address not found or not provided"]
                        ))
                        geo_fig.update_layout(
                            mapbox_style="open-street-map",
                            mapbox=dict(
                                center=dict(lat=milwaukee_lat, lon=milwaukee_lon),
                                zoom=10
                            ),
                            title="Map: Address not found or not provided (showing Milwaukee)",
                            font=dict(size=18, family='Inter, Arial'),
                            title_font=dict(size=26, family='Inter, Arial'),
                            margin=dict(l=60, r=40, t=80, b=80),
                            plot_bgcolor='#f8fafc',
                            paper_bgcolor='#f8fafc',
                            legend=dict(
                                font=dict(size=16),
                                bgcolor='#f8fafc',
                                bordercolor='#e0e7ef',
                                borderwidth=1
                            ),
                            showlegend=True
                        )
                except Exception as e:
                    # If anything fails, fallback to Milwaukee map
                    milwaukee_lat, milwaukee_lon = 43.0389, -87.9065
                    geo_fig = go.Figure()
                    geo_fig.add_trace(go.Scattermapbox(
                        lat=[milwaukee_lat],
                        lon=[milwaukee_lon],
                        mode='markers',
                        marker=dict(size=14, color='#888'),
                        name='Milwaukee Center',
                        text=[f"Map error: {e}"]
                    ))
                    geo_fig.update_layout(
                        mapbox_style="open-street-map",
                        mapbox=dict(
                            center=dict(lat=milwaukee_lat, lon=milwaukee_lon),
                            zoom=10
                        ),
                        title="Map: Error occurred (showing Milwaukee)",
                        font=dict(size=18, family='Inter, Arial'),
                        title_font=dict(size=26, family='Inter, Arial'),
                        margin=dict(l=60, r=40, t=80, b=80),
                        plot_bgcolor='#f8fafc',
                        paper_bgcolor='#f8fafc',
                        legend=dict(
                            font=dict(size=16),
                            bgcolor='#f8fafc',
                            bordercolor='#e0e7ef',
                            borderwidth=1
                        ),
                        showlegend=True
                    )
                # Cash Flow Over Time (simple projection)
                years = list(range(1, 11))
                rent_growth = 0.02
                cash_flows = []
                rent_proj = monthly_rent
                for y in years:
                    rent_proj = rent_proj * (1 + rent_growth)
                    cash_flows.append(rent_proj - monthly_payment - monthly_expenses)
                cashflow_fig = go.Figure()
                cashflow_fig.add_trace(go.Scatter(x=years, y=cash_flows, mode='lines+markers', name='Projected Cash Flow', line=dict(color='#22c55e', width=4), marker=dict(size=10)))
                cashflow_fig.update_layout(
                    title='Projected Cash Flow Over 10 Years',
                    xaxis_title='Year',
                    yaxis_title='Monthly Cash Flow ($)',
                    font=dict(size=18, family='Inter, Arial'),
                    title_font=dict(size=26, family='Inter, Arial'),
                    margin=dict(l=60, r=40, t=80, b=80),
                    plot_bgcolor='#f8fafc',
                    paper_bgcolor='#f8fafc',
                    legend=dict(font=dict(size=16), bgcolor='#f8fafc', bordercolor='#e0e7ef', borderwidth=1),
                    xaxis=dict(tickfont=dict(size=16)),
                    yaxis=dict(tickfont=dict(size=16)),
                )
                print(f"[DEBUG] scenario_outputs completed for {scenario_label}")
                return prediction_row, invest_metrics, metrics_output, table_data, table_cols, expense_fig, cashflow_fig, featimp_fig, geo_fig
            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                error_msg = f"Scenario calculation failed: {e}\n{tb}"
                print(f"[ERROR] {error_msg}")
                return dbc.Alert(error_msg, color="danger"), "", "", [], [], {}, {}, {}, {}
        try:
            print("[DEBUG] analyze: entering scenario selection")
            if compare_toggle:
                print("[DEBUG] analyze: compare_toggle is enabled")
                base_pred, base_inv, base_metrics, base_table_data, base_table_cols, base_exp, base_cash, base_feat, base_geo = scenario_outputs(
                    address, price, beds, baths, sqft, nbhd, property_type, zipcode,
                    down_payment_pct, interest_rate, loan_term, property_tax_rate, insurance_rate,
                    maintenance_rate, capital_reserves_rate, vacancy_rate, closing_costs_pct, "Base Case", base_rent_value)
                whatif_pred, whatif_inv, whatif_metrics, whatif_cash, whatif_feat, whatif_geo = scenario_outputs(
                    address2, price2, beds2, baths2, sqft2, nbhd2, property_type2, zipcode2,
                    down_payment_pct2, interest_rate2, loan_term2, property_tax_rate2, insurance_rate2,
                    maintenance_rate2, capital_reserves_rate2, vacancy_rate2, closing_costs_pct2, "What If", None)
                print("[DEBUG] analyze: compare_toggle outputs ready")
                return (
                    dbc.Row([
                        dbc.Col([base_pred, base_inv, base_metrics], width=6),
                        dbc.Col([whatif_pred, whatif_inv, whatif_metrics], width=6),
                    ]),
                    None, None, base_table_data, base_table_cols, base_exp, base_cash, base_feat, base_geo
                )
            else:
                print("[DEBUG] analyze: compare_toggle is not enabled")
                prediction_row, invest_metrics, metrics_output, table_data, table_cols, expense_fig, cashflow_fig, featimp_fig, geo_fig = scenario_outputs(
                    address, price, beds, baths, sqft, nbhd, property_type, zipcode,
                    down_payment_pct, interest_rate, loan_term, property_tax_rate, insurance_rate,
                    maintenance_rate, capital_reserves_rate, vacancy_rate, closing_costs_pct, "Base Case", base_rent_value)
                print("[DEBUG] analyze: single scenario outputs ready")
                return prediction_row, invest_metrics, metrics_output, table_data, table_cols, expense_fig, cashflow_fig, featimp_fig, geo_fig
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            error_msg = f"Scenario selection failed: {e}\n{tb}"
            print(f"[ERROR] {error_msg}")
            return dbc.Alert(error_msg, color="danger"), "", "", [], [], {}, {}, {}, {}
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        error_msg = f"Prediction failed: {e}\n{tb}"
        print(f"[ERROR] {error_msg}")
        return dbc.Alert(error_msg, color="danger"), "", "", [], [], {}, {}, {}, {}

# Add this callback to control the visibility of scenario2_controls
@app.callback(
    Output('scenario2_controls', 'style'),
    Input('compare_toggle', 'value')
)
def toggle_scenario2_controls(compare_toggle):
    if compare_toggle:
        return {"display": "block"}
    return {"display": "none"}

# --- Rental Income Analysis Callbacks ---
# Callback to auto-populate ML Predicted Rent after analysis
@app.callback(
    Output("ml_rent_input", "value"),
    Input("prediction_output", "children"),
    prevent_initial_call=True
)
def set_ml_rent_input(pred_output):
    import re
    if pred_output and hasattr(pred_output, 'children') and len(pred_output.children) > 0:
        text = str(pred_output.children[0])
        match = re.search(r"Predicted Rent Range: \$([\d,]+)", text)
        if match:
            try:
                return int(match.group(1).replace(",", ""))
            except Exception:
                return None
    return None

@app.callback(
    Output("rent_gap_display", "children"),
    Output("rent_used_summary", "children"),
    Output("base_rent_value", "data"),
    Input("third_party_rent_input", "value"),
    Input("ml_rent_input", "value"),
    Input("rent_source_toggle", "value"),
    State("prediction_output", "children"),
    prevent_initial_call=True
)
def update_rent_inputs(third_party_rent, ml_rent, rent_source, pred_output):
    import dash

    ml_pred = None
    if pred_output and hasattr(pred_output, 'children') and len(pred_output.children) > 0:
        import re
        text = str(pred_output.children[0])
        match = re.search(r"Predicted Rent Range: \$([\d,]+)", text)
        if match:
            ml_pred = int(match.group(1).replace(",", ""))
    if ml_pred is None:
        ml_pred = ""
    rent_gap = None
    rent_used = None
    rent_value = None
    # Robustly handle empty/invalid values
    def safe_float(val):
        try:
            if val is None or str(val).strip() == '':
                return None
            return float(val)
        except Exception:
            return None
    third_party_val = safe_float(third_party_rent)
    ml_val = safe_float(ml_rent)
    # If both are missing/invalid, do not update outputs
    if third_party_val is None and ml_val is None:
        return dash.no_update, dash.no_update, dash.no_update
    # Rent gap logic
    if third_party_val is not None and ml_val is not None:
        gap = ml_val - third_party_val
        if gap > 0:
            rent_gap = html.Div([
                html.Span(f"💡 ML Predicted Rent is ${gap:,.0f} higher than third-party estimate. Potential upside.", style={"color": "#22c55e", "fontWeight": "bold"})
            ], style={"marginTop": "0.5em"})
        elif gap < 0:
            rent_gap = html.Div([
                html.Span(f"⚠️ ML Predicted Rent is below third-party estimate. Verify assumptions.", style={"color": "#eab308", "fontWeight": "bold"})
            ], style={"marginTop": "0.5em"})
        else:
            rent_gap = None
    else:
        rent_gap = None
    # Rent used for analysis
    if rent_source == "third_party":
        rent_value = third_party_val if third_party_val is not None else None
        rent_used = html.Span(f"Monthly Rent Used for Analysis: ${third_party_val if third_party_val is not None else '(waiting for input)'}", style={"color": "#223"})
    else:
        rent_value = ml_val if ml_val is not None else ml_pred
        rent_used = html.Span(f"Monthly Rent Used for Analysis: ${rent_value if rent_value is not None else '(waiting for input)'}", style={"color": "#223"})
    return rent_gap, rent_used, rent_value

if __name__ == "__main__":
    app.run(debug=True)