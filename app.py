import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import json
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
import os
from pathlib import Path
import utils.analysis as analysis
import utils.data_loader as data_loader
import utils.visualization as visualization
import re
import numpy_financial as npf
import time
# ML model imports
from utils.ml_models import RentPredictor, PropertyPricePredictor

# Set page config
st.set_page_config(
    page_title="Real Estate Investment Analyzer",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 4rem;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0 0;
        gap: 1rem;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'property_data' not in st.session_state:
    st.session_state.property_data = None

# Load datasets
milwaukee_data = data_loader.load_and_clean_sales_data()
comps_data = milwaukee_data  # Use main dataset for comps

# Load ML models
@st.cache_resource
def load_ml_models():
    rent_predictor = RentPredictor()
    try:
        rent_predictor.load_model('models/rent_predictor.joblib')
    except Exception as e:
        rent_predictor = None
    price_predictor = PropertyPricePredictor()
    try:
        price_predictor.load_model('models/price_predictor.joblib')
    except Exception as e:
        price_predictor = None
    return rent_predictor, price_predictor

rent_predictor, price_predictor = load_ml_models()

def colorize(val, positive=True, threshold=5):
    if val is None:
        return "#888"
    if positive:
        return "#22c55e" if val >= threshold else ("#e02424" if val < 0 else "#eab308")
    else:
        return "#e02424" if val < 0 else "#22c55e"

def calculate_metrics(property_data, assumptions):
    """Calculate investment metrics with realistic expense assumptions and new summary metrics"""
    # Robust price extraction
    price_raw = property_data.get('price')
    try:
        price = float(str(price_raw).replace('$', '').replace(',', '')) if price_raw else 0
    except Exception:
        price = 0
    if price == 0:
        st.warning("Price is missing or invalid. Please enter a valid price.")
    down_payment = price * (assumptions['down_payment_pct'] / 100)
    loan_amount = price - down_payment
    # Monthly mortgage payment
    monthly_rate = assumptions['interest_rate'] / 100 / 12
    num_payments = assumptions['loan_term'] * 12
    monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1) if loan_amount > 0 and monthly_rate > 0 else 0
    # Monthly rent
    monthly_rent = assumptions['estimated_rent']
    # Expenses (updated logic)
    annual_property_tax = price * (assumptions['property_tax_rate'] / 100)
    annual_insurance = price * (assumptions['insurance_rate'] / 100)
    annual_management = monthly_rent * 0.08 * 12
    annual_maintenance = monthly_rent * (assumptions['maintenance_rate'] / 100) * 12
    annual_capital_reserves = monthly_rent * (assumptions['capital_reserves_rate'] / 100) * 12
    if assumptions.get('vacancy_mode', 'percent') == 'months' and assumptions.get('vacancy_months') is not None:
        annual_vacancy = monthly_rent * assumptions['vacancy_months']
    else:
        annual_vacancy = monthly_rent * (assumptions['vacancy_rate'] / 100) * 12
    annual_expenses = (
        annual_property_tax +
        annual_insurance +
        annual_management +
        annual_maintenance +
        annual_capital_reserves +
        annual_vacancy
    )
    monthly_expenses = annual_expenses / 12
    monthly_cash_flow = monthly_rent - monthly_payment - monthly_expenses
    # Cap rate: (NOI / Price) * 100, NOI = Gross Rent - Operating Expenses (exclude mortgage)
    annual_operating_expenses = (
        annual_property_tax +
        annual_insurance +
        annual_management +
        annual_maintenance +
        annual_capital_reserves +
        annual_vacancy
    )
    noi = (monthly_rent * 12) - annual_operating_expenses
    cap_rate = (noi / price) * 100 if price > 0 else 0
    # Cash-on-cash: (Annual Cash Flow / Total Upfront Cost) * 100
    total_upfront_cost = down_payment + price * (assumptions['closing_costs_pct'] / 100)
    cash_on_cash = (monthly_cash_flow * 12) / total_upfront_cost * 100 if total_upfront_cost > 0 else 0
    # Break-even rent: (PITI + maintenance + vacancy + capital reserves)
    piti = monthly_payment + (annual_property_tax + annual_insurance) / 12
    monthly_management = annual_management / 12
    monthly_maintenance = annual_maintenance / 12
    monthly_capital_reserves = annual_capital_reserves / 12
    monthly_vacancy = annual_vacancy / 12
    break_even_rent = piti + monthly_management + monthly_maintenance + monthly_capital_reserves + monthly_vacancy
    break_even_formula = f"Break-even Rent = PITI + Management + Maintenance + Capital Reserves + Vacancy"
    break_down = f"PITI = ${piti:.2f}, Management = ${monthly_management:.2f}, Maintenance = ${monthly_maintenance:.2f}, Capital Reserves = ${monthly_capital_reserves:.2f}, Vacancy = ${monthly_vacancy:.2f}"
    # Rent-to-Price Ratio (%)
    rent_to_price = (monthly_rent / price) * 100 if price > 0 else 0
    # Total ROI: (Annual Cash Flow + Principal Paid + Appreciation) / Total Upfront Cost
    # Estimate principal paid in year 1
    principal_paid_yr1 = 0
    if loan_amount > 0 and monthly_rate > 0:
        interest_paid_yr1 = 0
        principal_paid_yr1 = 0
        balance = loan_amount
        for i in range(12):
            interest = balance * monthly_rate
            principal = monthly_payment - interest
            principal_paid_yr1 += principal
            balance -= principal
    appreciation = price * 0.03  # 3% appreciation
    total_roi = ((monthly_cash_flow * 12) + principal_paid_yr1 + appreciation) / total_upfront_cost * 100 if total_upfront_cost > 0 else 0
    # Payback period (years to recover cash investment)
    annual_cash_flow = monthly_cash_flow * 12
    payback_period = total_upfront_cost / annual_cash_flow if annual_cash_flow > 0 else float('inf')
    # IRR & NPV if hold period is set
    irr = None
    npv = None
    if assumptions.get('hold_period'):
        hold = assumptions['hold_period']
        drate = assumptions.get('discount_rate', 8.0) / 100
        cash_flows = [ -total_upfront_cost ] + [ annual_cash_flow ] * hold
        # Add terminal value (sale proceeds at end)
        terminal_value = price * ((1 + 0.03) ** hold)
        cash_flows[-1] += terminal_value
        irr = npf.irr(cash_flows) * 100 if hasattr(npf, 'irr') else None
        npv = npf.npv(drate, cash_flows) if hasattr(npf, 'npv') else None
    # Use manual overrides if provided
    monthly_property_tax = manual_property_tax if manual_property_tax > 0 else (annual_property_tax / 12)
    monthly_insurance = manual_insurance if manual_insurance > 0 else (annual_insurance / 12)
    monthly_management = manual_management if manual_management > 0 else (annual_management / 12)
    monthly_maintenance = manual_maintenance if manual_maintenance > 0 else (annual_maintenance / 12)
    monthly_capital_reserves = manual_capital_reserves if manual_capital_reserves > 0 else (annual_capital_reserves / 12)
    monthly_vacancy = manual_vacancy if manual_vacancy > 0 else (annual_vacancy / 12)
    # Track which are overridden
    overridden = {
        'property_tax': manual_property_tax > 0,
        'insurance': manual_insurance > 0,
        'management': manual_management > 0,
        'maintenance': manual_maintenance > 0,
        'capital_reserves': manual_capital_reserves > 0,
        'vacancy': manual_vacancy > 0
    }
    # Recalculate annuals for summary
    annual_property_tax = monthly_property_tax * 12
    annual_insurance = monthly_insurance * 12
    annual_management = monthly_management * 12
    annual_maintenance = monthly_maintenance * 12
    annual_capital_reserves = monthly_capital_reserves * 12
    annual_vacancy = monthly_vacancy * 12
    annual_expenses = (
        annual_property_tax +
        annual_insurance +
        annual_management +
        annual_maintenance +
        annual_capital_reserves +
        annual_vacancy
    )
    monthly_expenses = annual_expenses / 12
    monthly_cash_flow = monthly_rent - monthly_payment - monthly_expenses
    # Cap rate: (NOI / Price) * 100, NOI = Gross Rent - Operating Expenses (exclude mortgage)
    annual_operating_expenses = (
        annual_property_tax +
        annual_insurance +
        annual_management +
        annual_maintenance +
        annual_capital_reserves +
        annual_vacancy
    )
    noi = (monthly_rent * 12) - annual_operating_expenses
    cap_rate = (noi / price) * 100 if price > 0 else 0
    # Cash-on-cash: (Annual Cash Flow / Total Upfront Cost) * 100
    total_upfront_cost = down_payment + price * (assumptions['closing_costs_pct'] / 100)
    cash_on_cash = (monthly_cash_flow * 12) / total_upfront_cost * 100 if total_upfront_cost > 0 else 0
    # Break-even rent: (PITI + maintenance + vacancy + capital reserves)
    piti = monthly_payment + (annual_property_tax + annual_insurance) / 12
    monthly_management = annual_management / 12
    monthly_maintenance = annual_maintenance / 12
    monthly_capital_reserves = annual_capital_reserves / 12
    monthly_vacancy = annual_vacancy / 12
    break_even_rent = piti + monthly_management + monthly_maintenance + monthly_capital_reserves + monthly_vacancy
    break_even_formula = f"Break-even Rent = PITI + Management + Maintenance + Capital Reserves + Vacancy"
    break_down = f"PITI = ${piti:.2f}, Management = ${monthly_management:.2f}, Maintenance = ${monthly_maintenance:.2f}, Capital Reserves = ${monthly_capital_reserves:.2f}, Vacancy = ${monthly_vacancy:.2f}"
    # Rent-to-Price Ratio (%)
    rent_to_price = (monthly_rent / price) * 100 if price > 0 else 0
    # Total ROI: (Annual Cash Flow + Principal Paid + Appreciation) / Total Upfront Cost
    # Estimate principal paid in year 1
    principal_paid_yr1 = 0
    if loan_amount > 0 and monthly_rate > 0:
        interest_paid_yr1 = 0
        principal_paid_yr1 = 0
        balance = loan_amount
        for i in range(12):
            interest = balance * monthly_rate
            principal = monthly_payment - interest
            principal_paid_yr1 += principal
            balance -= principal
    appreciation = price * 0.03  # 3% appreciation
    total_roi = ((monthly_cash_flow * 12) + principal_paid_yr1 + appreciation) / total_upfront_cost * 100 if total_upfront_cost > 0 else 0
    # Payback period (years to recover cash investment)
    annual_cash_flow = monthly_cash_flow * 12
    payback_period = total_upfront_cost / annual_cash_flow if annual_cash_flow > 0 else float('inf')
    # IRR & NPV if hold period is set
    irr = None
    npv = None
    if assumptions.get('hold_period'):
        hold = assumptions['hold_period']
        drate = assumptions.get('discount_rate', 8.0) / 100
        cash_flows = [ -total_upfront_cost ] + [ annual_cash_flow ] * hold
        # Add terminal value (sale proceeds at end)
        terminal_value = price * ((1 + 0.03) ** hold)
        cash_flows[-1] += terminal_value
        irr = npf.irr(cash_flows) * 100 if hasattr(npf, 'irr') else None
        npv = npf.npv(drate, cash_flows) if hasattr(npf, 'npv') else None
    return {
        'monthly_cash_flow': monthly_cash_flow,
        'cap_rate': cap_rate,
        'cash_on_cash': cash_on_cash,
        'break_even_rent': break_even_rent,
        'total_upfront_cost': total_upfront_cost,
        'break_even_formula': break_even_formula,
        'break_down': break_down,
        'rent_to_price': rent_to_price,
        'total_roi': total_roi,
        'payback_period': payback_period,
        'irr': irr,
        'npv': npv,
        'overridden': overridden
    }

def generate_report(property_data, metrics, assumptions):
    """Generate PDF report"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Real Estate Investment Analysis Report", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    
    # Add property details
    pdf.cell(200, 10, f"Property Address: {property_data['address']}", ln=True)
    pdf.cell(200, 10, f"Purchase Price: ${property_data['price']}", ln=True)
    
    # Add metrics
    pdf.cell(200, 10, f"Monthly Cash Flow: ${metrics['monthly_cash_flow']:.2f}", ln=True)
    pdf.cell(200, 10, f"Cap Rate: {metrics['cap_rate']:.2f}%", ln=True)
    pdf.cell(200, 10, f"Cash on Cash Return: {metrics['cash_on_cash']:.2f}%", ln=True)
    
    # Save report
    report_path = "investment_report.pdf"
    pdf.output(report_path)
    return report_path

def get_zip_code(address):
    import re
    if not isinstance(address, str):
        return None
    match = re.search(r'(\d{5})', address)
    return match.group(1) if match else None

def geocode_address(address):
    """Geocode an address using Nominatim (OpenStreetMap)"""
    import requests
    try:
        url = f"https://nominatim.openstreetmap.org/search"
        params = {"q": address, "format": "json", "limit": 1}
        headers = {"User-Agent": "RealEstateAI/1.0"}
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                return lat, lon
    except Exception:
        pass
    return None, None

# Main app
st.title("🏠 Real Estate Investment Analyzer")

# Sidebar for assumptions
with st.sidebar:
    st.header("Investment Assumptions")
    
    # Loan assumptions
    st.subheader("Loan Details")
    down_payment_pct = st.slider("Down Payment (%)", 0, 100, 20)
    interest_rate = st.slider("Interest Rate (%)", 0.0, 10.0, 5.0, 0.1)
    loan_term = st.slider("Loan Term (years)", 15, 30, 30)
    # Rent assumption (move this up so it's always defined)
    st.subheader("Rental Income")
    estimated_rent = st.number_input("Estimated Monthly Rent ($)", 0, 10000, 2000)
    # Scenario analysis toggles
    st.subheader("Scenario Analysis")
    scenario_mode = st.checkbox("Try Different Down Payments, Interest Rates, and Rents")
    if scenario_mode:
        scenario_down = st.slider("Scenario Down Payment (%)", 0, 100, down_payment_pct)
        scenario_interest = st.slider("Scenario Interest Rate (%)", 0.0, 10.0, interest_rate, 0.1)
        scenario_rent = st.slider("Scenario Monthly Rent ($)", 0, 10000, estimated_rent)
    else:
        scenario_down = down_payment_pct
        scenario_interest = interest_rate
        scenario_rent = estimated_rent
    # Expense assumptions
    st.subheader("Expenses")
    property_tax_rate = st.slider("Property Tax Rate (%)", 0.0, 5.0, 1.5, 0.1)
    insurance_rate = st.slider("Insurance Rate (%)", 0.0, 2.0, 0.5, 0.1)
    maintenance_rate = st.slider("Maintenance Rate (%)", 0.0, 5.0, 1.0, 0.1)
    capital_reserves_rate = st.slider("Capital Reserves Rate (%)", 0.0, 5.0, 1.0, 0.1)
    vacancy_mode = st.radio("Vacancy Calculation Mode", ["% of Rent", "Months per Year"], index=0)
    if vacancy_mode == "% of Rent":
        vacancy_rate = st.slider("Vacancy Rate (% of Rent)", 0.0, 20.0, 5.0, 0.5)
        vacancy_months = None
    else:
        vacancy_months = st.slider("Vacancy (Months per Year)", 0.0, 6.0, 1.0, 0.1)
        vacancy_rate = None
    closing_costs_pct = st.slider("Closing Costs (%)", 0.0, 10.0, 3.0, 0.1)
    # Manual override for expenses
    st.subheader("Manual Expense Overrides (Optional)")
    manual_property_tax = st.number_input("Manual Monthly Property Tax ($)", min_value=0.0, value=0.0, step=10.0, help="Leave 0 to use calculated value")
    manual_insurance = st.number_input("Manual Monthly Insurance ($)", min_value=0.0, value=0.0, step=10.0, help="Leave 0 to use calculated value")
    manual_management = st.number_input("Manual Monthly Management ($)", min_value=0.0, value=0.0, step=10.0, help="Leave 0 to use calculated value")
    manual_maintenance = st.number_input("Manual Monthly Maintenance ($)", min_value=0.0, value=0.0, step=10.0, help="Leave 0 to use calculated value")
    manual_capital_reserves = st.number_input("Manual Monthly Capital Reserves ($)", min_value=0.0, value=0.0, step=10.0, help="Leave 0 to use calculated value")
    manual_vacancy = st.number_input("Manual Monthly Vacancy ($)", min_value=0.0, value=0.0, step=10.0, help="Leave 0 to use calculated value")
    # Projections toggle
    st.subheader("Long-Term Projections")
    show_projection = st.checkbox("Show 5–10 Year Projections (Appreciation & Rent Growth)")
    if show_projection:
        projection_years = st.slider("Projection Years", 5, 20, 10)
        appreciation_rate = st.slider("Annual Appreciation Rate (%)", 0.0, 10.0, 3.0, 0.1)
        rent_growth_rate = st.slider("Annual Rent Growth Rate (%)", 0.0, 10.0, 2.0, 0.1)
    else:
        projection_years = 0
        appreciation_rate = 3.0
        rent_growth_rate = 2.0
    # Hold period and advanced metrics
    st.subheader("Advanced Metrics")
    show_advanced = st.checkbox("Show IRR & NPV (requires hold period)")
    if show_advanced:
        hold_period = st.slider("Hold Period (years)", 1, 30, 10)
        discount_rate = st.slider("Discount Rate for NPV/IRR (%)", 0.0, 20.0, 8.0, 0.1)
    else:
        hold_period = None
        discount_rate = 8.0

# Main content area with tabs
tab1, tab2, tab3 = st.tabs(["🏡 Single Family", "🏢 Duplex/Triplex", "🌳 Land"])

# Helper to safely parse int fields (now also handles commas and text input)
def safe_int(val, default):
    try:
        if val is None:
            return default
        if isinstance(val, int):
            return val
        if isinstance(val, float):
            return int(val)
        s = str(val).replace(",", "").replace("$", "").strip()
        return int(float(s))
    except Exception:
        return default

# Helper for section spacing
SECTION_SPACING = '\n<div style="height:32px;"></div>\n'

# Helper to run analysis and show results
def run_analysis(property_data, assumptions, property_type):
    # Add zip code if possible
    if 'address' in property_data and 'zip_code' not in property_data:
        property_data['zip_code'] = get_zip_code(property_data['address'])
    # Prevent analysis if price or address is missing/invalid
    if not property_data.get('price') or not property_data.get('address'):
        st.error("Address and price are required for analysis. Please enter valid values.")
        return
    # Estimate rent if not provided
    if assumptions['estimated_rent'] == 0:
        est_rent = analysis.estimate_rent_by_comps(property_data, comps_data)
        if est_rent:
            assumptions['estimated_rent'] = int(est_rent)
            st.info(f"Estimated rent from comps: ${int(est_rent):,}")
        elif 'rent' not in comps_data.columns:
            st.warning("No rent data available in your dataset, so rent cannot be estimated from comps. Please enter rent manually.")
    # Add vacancy mode and capital reserves to assumptions
    assumptions['vacancy_mode'] = 'months' if vacancy_mode == 'Months per Year' else 'percent'
    assumptions['vacancy_months'] = vacancy_months
    assumptions['capital_reserves_rate'] = capital_reserves_rate
    if show_advanced:
        assumptions['hold_period'] = hold_period
        assumptions['discount_rate'] = discount_rate
    # Use scenario values for analysis
    assumptions['down_payment_pct'] = scenario_down
    assumptions['interest_rate'] = scenario_interest
    assumptions['estimated_rent'] = scenario_rent
    # Calculate metrics
    metrics = calculate_metrics(property_data, assumptions)
    # ROI
    roi = analysis.calculate_roi(metrics['monthly_cash_flow'], metrics['total_upfront_cost'])
    metrics['roi'] = roi
    # Risk score
    risk_score = None
    # Value prediction
    predicted_value = analysis.predict_property_value(property_data, {
        'X_train': milwaukee_data[['sqft', 'beds', 'baths', 'year_built', 'lot_size']],
        'y_train': milwaukee_data['price']
    })
    # Visualizations
    st.markdown(SECTION_SPACING, unsafe_allow_html=True)
    st.markdown('<div style="box-shadow:0 2px 8px #0001;border-radius:16px;padding:2rem 1rem 1rem 1rem;background:#fff;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:1.4rem;font-weight:700;margin-bottom:1rem;">Summary Metrics</div>', unsafe_allow_html=True)
    metric_keys = [
        ("Monthly Cash Flow", f"${metrics['monthly_cash_flow']:.2f}", colorize(metrics["monthly_cash_flow"], True, 0)),
        ("Cap Rate", f"{metrics['cap_rate']:.2f}%", colorize(metrics["cap_rate"], True, 5)),
        ("Cash on Cash", f"{metrics['cash_on_cash']:.2f}%", colorize(metrics["cash_on_cash"], True, 5)),
        ("Break-even Rent", f"${metrics['break_even_rent']:.2f}", colorize(metrics["break_even_rent"], False)),
        ("Rent-to-Price Ratio", f"{metrics['rent_to_price']:.2f}%", colorize(metrics["rent_to_price"], True, 0.8)),
        ("Total ROI (Yr 1)", f"{metrics['total_roi']:.2f}%", colorize(metrics["total_roi"], True, 5)),
        ("Payback Period", f"{metrics['payback_period']:.2f} yrs", colorize(-metrics["payback_period"] if metrics["payback_period"] > 30 else metrics["payback_period"], False, 10)),
    ]
    if show_advanced and metrics['irr'] is not None:
        metric_keys.append(("IRR", f"{metrics['irr']:.2f}%", colorize(metrics["irr"], True, 5)))
    cols = st.columns(4)
    for i, (label, value, color) in enumerate(metric_keys):
        with cols[i % 4]:
            st.markdown(f"""
                <div style="background:#f8fafc;border-radius:10px;padding:1.2rem 0.5rem;margin-bottom:1rem;box-shadow:0 1px 4px #0001;text-align:center;">
                    <div style="font-size:1.2rem;font-weight:600;color:{color};">{value}</div>
                    <div style="font-size:0.95rem;color:#444;">{label}</div>
                </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.caption(f"{metrics['break_even_formula']}")
    st.caption(f"{metrics['break_down']}")
    st.markdown(SECTION_SPACING, unsafe_allow_html=True)
    # 2. Comparable Properties Scatter Plot
    st.markdown('<div style="box-shadow:0 2px 8px #0001;border-radius:16px;padding:2rem 1rem 1rem 1rem;background:#fff;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:1.4rem;font-weight:700;margin-bottom:1rem;">Comparable Properties</div>', unsafe_allow_html=True)
    st.plotly_chart(visualization.create_comps_scatter(property_data, comps_data))
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(SECTION_SPACING, unsafe_allow_html=True)
    # 3. Investment Recommendation + Button
    st.markdown('<div style="box-shadow:0 2px 8px #0001;border-radius:16px;padding:2rem 1rem 1rem 1rem;background:#fff;text-align:center;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:1.4rem;font-weight:700;margin-bottom:1rem;">Investment Recommendation</div>', unsafe_allow_html=True)
    buy_threshold_cap_rate = 6
    buy_threshold_cash_flow = 300
    if metrics['cap_rate'] > buy_threshold_cap_rate and metrics['monthly_cash_flow'] > buy_threshold_cash_flow:
        st.markdown(
            '<div style="display:flex;align-items:center;font-size:1.5rem;color:green;font-weight:bold;">'
            '✅ Buy &mdash; This appears to be a good investment opportunity!'
            '</div>', unsafe_allow_html=True)
    else:
        if metrics['cap_rate'] < buy_threshold_cap_rate and metrics['monthly_cash_flow'] < buy_threshold_cash_flow:
            st.markdown(
                "<div style='display:flex;align-items:center;font-size:1.5rem;color:#e02424;font-weight:bold;'>"
                "❌ Don't Buy &mdash; This property does not meet your investment criteria." "</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                "<div style='display:flex;align-items:center;font-size:1.5rem;color:#eab308;font-weight:bold;'>"
                "⏸️ Hold &mdash; This property is close, but not quite a buy." "</div>", unsafe_allow_html=True)
        # Show what would be needed to make it a buy
        needed_cash_flow = max(0, buy_threshold_cash_flow - metrics['monthly_cash_flow'])
        needed_cap_rate = max(0, buy_threshold_cap_rate - metrics['cap_rate'])
        needed_rent_for_cash_flow = metrics['break_even_rent'] + buy_threshold_cash_flow
        needed_rent_for_cap_rate = ((buy_threshold_cap_rate/100) * (safe_int(property_data['price'],0)) + (assumptions['property_tax_rate']/100 + assumptions['insurance_rate']/100 + assumptions['maintenance_rate']/100 + assumptions['capital_reserves_rate']/100 + (assumptions['vacancy_months']/12 if assumptions['vacancy_mode']== 'months' and assumptions['vacancy_months'] else assumptions['vacancy_rate']/100)) * safe_int(property_data['price'],0)) / 12
        st.markdown('<div style="margin-top:1rem;font-size:1.1rem;">To make this a <span style="color:green;font-weight:bold;">Buy</span>:</div>', unsafe_allow_html=True)
        st.markdown(f'<ul style="font-size:1.1rem;">'
            f'<li>Monthly cash flow needs to be at least <b>${buy_threshold_cash_flow:,}</b> (currently <b>${metrics["monthly_cash_flow"]:,.2f}</b>)</li>'
            f'<li>Cap rate needs to be at least <b>{buy_threshold_cap_rate}%</b> (currently <b>{metrics["cap_rate"]:.2f}%</b>)</li>'
            f'<li>Minimum rent needed for cash flow: <b>${needed_rent_for_cash_flow:,.0f}/mo</b></li>'
            f'<li>Minimum rent needed for cap rate: <b>${needed_rent_for_cap_rate:,.0f}/mo</b></li>'
            '</ul>', unsafe_allow_html=True)
    st.markdown(SECTION_SPACING, unsafe_allow_html=True)
    # Centered report button
    st.markdown('<div style="display:flex;justify-content:center;margin-top:2rem;margin-bottom:2rem;">', unsafe_allow_html=True)
    if st.button("Generate Investment Report", key=f"report_{property_type}"):
        report_path = generate_report(property_data, metrics, assumptions)
        with open(report_path, "rb") as f:
            st.download_button(
                label="Download PDF Report",
                data=f,
                file_name="investment_report.pdf",
                mime="application/pdf"
            )
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(SECTION_SPACING, unsafe_allow_html=True)
    # 4 & 5. Projections and Sale/Net Profit/ROI side by side
    if show_projection and projection_years > 0:
        col_proj, col_sale = st.columns(2)
        with col_proj:
            st.markdown('<div style="box-shadow:0 2px 8px #0001;border-radius:16px;padding:2rem 1rem 1rem 1rem;background:#fff;">', unsafe_allow_html=True)
            st.markdown('<div style="font-size:1.4rem;font-weight:700;margin-bottom:1rem;">5–10 Year Projections</div>', unsafe_allow_html=True)
            years = list(range(1, projection_years+1))
            values = []
            rents = []
            equities = []
            price_raw = property_data.get('price')
            try:
                price = float(str(price_raw).replace('$', '').replace(',', '')) if price_raw else 0
            except Exception:
                price = 0
            rent = scenario_rent
            balance = price - (price * scenario_down / 100)
            monthly_rate = scenario_interest / 100 / 12
            monthly_payment = balance * (monthly_rate * (1 + monthly_rate)**(loan_term*12)) / ((1 + monthly_rate)**(loan_term*12) - 1) if balance > 0 and monthly_rate > 0 else 0
            for y in years:
                v = price * ((1 + appreciation_rate/100) ** y)
                values.append(v)
                r = rent * ((1 + rent_growth_rate/100) ** y)
                rents.append(r)
                eq = 0
                bal = balance
                for i in range(y*12):
                    interest = bal * monthly_rate
                    principal = monthly_payment - interest
                    eq += principal
                    bal -= principal
                    if bal < 0: break
                equities.append(eq)
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=years, y=values, name="Projected Property Value ($)", line=dict(color="#636EFA")))
            fig.add_trace(go.Scatter(x=years, y=rents, name="Projected Monthly Rent ($)", line=dict(color="#00CC96")))
            fig.add_trace(go.Scatter(x=years, y=equities, name="Projected Equity ($)", line=dict(color="#EF553B")))
            fig.update_layout(title="5–10 Year Projections: Value, Rent, and Equity", xaxis_title="Year", yaxis_title="Dollars ($)")
            st.plotly_chart(fig)
            st.markdown('</div>', unsafe_allow_html=True)
        with col_sale:
            st.markdown('<div style="box-shadow:0 2px 8px #0001;border-radius:16px;padding:2rem 1rem 1rem 1rem;background:#fff;">', unsafe_allow_html=True)
            st.markdown('<div style="font-size:1.4rem;font-weight:700;margin-bottom:1rem;">If I sell this in 5–10 years, what will I make?</div>', unsafe_allow_html=True)
            hold = projection_years
            projected_sale_price = price * ((1 + appreciation_rate/100) ** hold)
            agent_fees = projected_sale_price * 0.06
            closing_costs = projected_sale_price * 0.02
            bal = balance
            for i in range(hold*12):
                interest = bal * monthly_rate
                principal = monthly_payment - interest
                bal -= principal
                if bal < 0: bal = 0
            remaining_loan = max(bal, 0)
            net_sale_proceeds = projected_sale_price - agent_fees - closing_costs - remaining_loan
            total_cash_flow = sum([rent * ((1 + rent_growth_rate/100) ** y) * 12 for y in range(hold)])
            total_profit = net_sale_proceeds + total_cash_flow - price * scenario_down / 100
            total_roi = (total_profit / (price * scenario_down / 100)) * 100 if price * scenario_down / 100 > 0 else 0
            st.markdown(f"""
            <div style='font-size:1.1rem;'>
            <b>Projected Sale Price:</b> ${projected_sale_price:,.0f} <br/>
            <b>Less Agent Fees (6%):</b> -${agent_fees:,.0f} <br/>
            <b>Less Closing Costs (2%):</b> -${closing_costs:,.0f} <br/>
            <b>Less Remaining Loan Balance:</b> -${remaining_loan:,.0f} <br/>
            <b>Net Sale Proceeds:</b> <span style='color:#22c55e;'>${net_sale_proceeds:,.0f}</span> <br/>
            <b>Total Cash Flow Over {hold} Years:</b> ${total_cash_flow:,.0f} <br/>
            <b>Final Net Profit:</b> <span style='color:#22c55e;'>${total_profit:,.0f}</span> <br/>
            <b>Total ROI Over Hold Period:</b> <span style='color:#22c55e;'>{total_roi:.1f}%</span>
            </div>
            """, unsafe_allow_html=True)
            fig2 = go.Figure()
            annual_cash_flows = [rent * ((1 + rent_growth_rate/100) ** y) * 12 for y in range(hold)]
            fig2.add_trace(go.Bar(x=list(range(1, hold+1)), y=annual_cash_flows, name="Annual Cash Flow", marker_color="#00CC96"))
            fig2.add_trace(go.Scatter(x=list(range(1, hold+1)), y=equities[:hold], name="Equity Buildup", line=dict(color="#EF553B")))
            fig2.add_trace(go.Scatter(x=[hold], y=[net_sale_proceeds], name="Net Sale Proceeds", mode="markers+text", marker=dict(color="#636EFA", size=14), text=[f"${net_sale_proceeds:,.0f}"], textposition="top center"))
            fig2.update_layout(title="5–10 Year Cash Flow & Equity at Sale", xaxis_title="Year", yaxis_title="Dollars ($)")
            st.plotly_chart(fig2)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown(SECTION_SPACING, unsafe_allow_html=True)
    # 6. Interactive Map at the bottom
    if property_data.get('address'):
        lat, lon = geocode_address(property_data['address'])
        if lat and lon:
            st.markdown('<div style="box-shadow:0 2px 8px #0001;border-radius:16px;padding:2rem 1rem 1rem 1rem;background:#fff;">', unsafe_allow_html=True)
            st.markdown('<div style="font-size:1.4rem;font-weight:700;margin-bottom:1rem;">Property Location</div>', unsafe_allow_html=True)
            st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}), zoom=15)
            st.markdown('</div>', unsafe_allow_html=True)

# Helper to map user input to ML model input
def get_ml_input(address, sqft, beds, baths, nbhd, property_type, zipcode):
    return {
        'FinishedSqft': sqft if sqft else None,
        'Bedrooms': beds if beds else None,
        'Bathrooms': baths if baths else None,
        'nbhd': nbhd if nbhd else None,
        'PropertyType': property_type if property_type else None,
        'zipcode': zipcode if zipcode else None
    }

# Single Family Tab
with tab1:
    st.header("Property Information")
    with st.form("property_details1"):
        st.subheader("Manual Property Details")
        col1, col2 = st.columns(2)
        with col1:
            address = st.text_input("Address", key="address1")
            price_str = st.text_input("Price ($)", key="price1")
            beds = st.number_input("Bedrooms", 0, 10, 3, key="beds1", step=None)
            baths = st.number_input("Bathrooms", 0, 10, 2, key="baths1", step=None)
            nbhd = st.text_input("Neighborhood", key="nbhd1")
            property_type = st.selectbox("Property Type", ["House", "Duplex", "Apartment", "Condo"], key="ptype1")
            zipcode = st.text_input("Zip Code", key="zip1")
        with col2:
            sqft_str = st.text_input("Square Footage", key="sqft1")
            lot_size_str = st.text_input("Lot Size (sqft)", key="lot1")
            year_built = st.number_input("Year Built", 1800, 2024, 2000, key="year1", step=None)
            zestimate_str = st.text_input("Zestimate ($)", key="zest1")
        predict_rent = st.form_submit_button("Predict Rent with ML")
        submitted = st.form_submit_button("Analyze Property")
        price = safe_int(price_str, 0)
        sqft = safe_int(sqft_str, 0)
        lot_size = safe_int(lot_size_str, 0)
        zestimate = safe_int(zestimate_str, 0)
        ml_input = get_ml_input(address, sqft, beds, baths, nbhd, property_type, zipcode)
        # Add engineered features for ML model
        if beds and baths:
            ml_input['BedBath'] = beds * baths
        if sqft and beds:
            ml_input['SqftPerBed'] = sqft / beds if beds != 0 else 0
        if sqft:
            ml_input['LogSqft'] = np.log1p(sqft)
        # SaleMonth: try to extract from today if no sale date
        ml_input['SaleMonth'] = datetime.now().month
        predicted_rent = None
        if predict_rent and rent_predictor:
            try:
                prediction = rent_predictor.predict_with_range(ml_input)
                st.success(f"Predicted Rent Range: ${prediction['lower_bound']:,.0f} - ${prediction['upper_bound']:,.0f}")
                st.info(f"Based on our model's accuracy (MAE: ${prediction['confidence_range']:,.0f}), the actual rent is likely to fall within this range.")
                # 1% rule
                if price > 0:
                    one_percent_rent = price * 0.01
                    st.markdown(f"<span style='color:#888;'>1% Rule Rent: <b>${one_percent_rent:,.0f}</b></span>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"ML rent prediction failed: {e}")
        if submitted:
            if price == 0:
                st.warning("Please enter a valid price.")
            property_data = {
                'address': address,
                'price': f"${price:,}" if price else None,
                'beds': beds,
                'baths': baths,
                'sqft': sqft,
                'lot_size': lot_size,
                'year_built': year_built,
                'zestimate': f"${zestimate:,}" if zestimate else None,
                'nbhd': nbhd,
                'PropertyType': property_type,
                'zipcode': zipcode
            }
            st.session_state.property_data = property_data
    if st.session_state.property_data:
        assumptions = {
            'down_payment_pct': down_payment_pct,
            'interest_rate': interest_rate,
            'loan_term': loan_term,
            'property_tax_rate': property_tax_rate,
            'insurance_rate': insurance_rate,
            'maintenance_rate': maintenance_rate,
            'capital_reserves_rate': capital_reserves_rate,
            'vacancy_mode': vacancy_mode,
            'vacancy_months': vacancy_months,
            'vacancy_rate': vacancy_rate if vacancy_mode == '% of Rent' else 0.0,
            'closing_costs_pct': closing_costs_pct,
            'estimated_rent': predicted_rent if predicted_rent else estimated_rent,
            'manual_property_tax': manual_property_tax,
            'manual_insurance': manual_insurance,
            'manual_management': manual_management,
            'manual_maintenance': manual_maintenance,
            'manual_capital_reserves': manual_capital_reserves,
            'manual_vacancy': manual_vacancy
        }
        run_analysis(st.session_state.property_data, assumptions, 'single_family')

# Duplex/Triplex Tab
with tab2:
    st.header("Duplex/Triplex Information")
    with st.form("property_details2"):
        st.subheader("Manual Property Details")
        col1, col2 = st.columns(2)
        with col1:
            address = st.text_input("Address", key="address2")
            price_str = st.text_input("Price ($)", key="price2")
            beds = st.number_input("Bedrooms", 0, 10, 6, key="beds2", step=None)
            baths = st.number_input("Bathrooms", 0, 10, 3, key="baths2", step=None)
            nbhd = st.text_input("Neighborhood", key="nbhd2")
            property_type = st.selectbox("Property Type", ["House", "Duplex", "Apartment", "Condo"], key="ptype2")
            zipcode = st.text_input("Zip Code", key="zip2")
            rent_str = st.text_input("Estimated Monthly Rent ($)", key="rent2")
        with col2:
            sqft_str = st.text_input("Square Footage", key="sqft2")
            lot_size_str = st.text_input("Lot Size (sqft)", key="lot2")
            year_built = st.number_input("Year Built", 1800, 2024, 2005, key="year2", step=None)
            zestimate_str = st.text_input("Zestimate ($)", key="zest2")
        predict_rent = st.form_submit_button("Predict Rent with ML")
        submitted = st.form_submit_button("Analyze Property")
        price = safe_int(price_str, 0)
        sqft = safe_int(sqft_str, 0)
        lot_size = safe_int(lot_size_str, 0)
        zestimate = safe_int(zestimate_str, 0)
        rent = safe_int(rent_str, 0)
        ml_input = get_ml_input(address, sqft, beds, baths, nbhd, property_type, zipcode)
        # Add engineered features for ML model
        if beds and baths:
            ml_input['BedBath'] = beds * baths
        if sqft and beds:
            ml_input['SqftPerBed'] = sqft / beds if beds != 0 else 0
        if sqft:
            ml_input['LogSqft'] = np.log1p(sqft)
        # SaleMonth: try to extract from today if no sale date
        ml_input['SaleMonth'] = datetime.now().month
        predicted_rent = None
        if predict_rent and rent_predictor:
            try:
                predicted_rent = rent_predictor.predict(ml_input)
                st.success(f"Predicted Rent: ${predicted_rent:,.0f}")
                # 1% rule
                if price > 0:
                    one_percent_rent = price * 0.01
                    st.markdown(f"<span style='color:#888;'>1% Rule Rent: <b>${one_percent_rent:,.0f}</b></span>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"ML rent prediction failed: {e}")
        if submitted:
            if price == 0:
                st.warning("Please enter a valid price.")
            property_data = {
                'address': address,
                'price': f"${price:,}" if price else None,
                'beds': beds,
                'baths': baths,
                'sqft': sqft,
                'lot_size': lot_size,
                'year_built': year_built,
                'zestimate': f"${zestimate:,}" if zestimate else None,
                'nbhd': nbhd,
                'PropertyType': property_type,
                'zipcode': zipcode
            }
            st.session_state.property_data2 = property_data
    if 'property_data2' in st.session_state and st.session_state.property_data2:
        rent_val = safe_int(st.session_state.get('rent2', ''), 0)
        if rent_val == 0 and predicted_rent:
            rent_val = int(predicted_rent)
        assumptions = {
            'down_payment_pct': down_payment_pct,
            'interest_rate': interest_rate,
            'loan_term': loan_term,
            'property_tax_rate': property_tax_rate,
            'insurance_rate': insurance_rate,
            'maintenance_rate': maintenance_rate,
            'capital_reserves_rate': capital_reserves_rate,
            'vacancy_mode': vacancy_mode,
            'vacancy_months': vacancy_months,
            'vacancy_rate': vacancy_rate if vacancy_mode == '% of Rent' else 0.0,
            'closing_costs_pct': closing_costs_pct,
            'estimated_rent': rent_val if rent_val else estimated_rent,
            'manual_property_tax': manual_property_tax,
            'manual_insurance': manual_insurance,
            'manual_management': manual_management,
            'manual_maintenance': manual_maintenance,
            'manual_capital_reserves': manual_capital_reserves,
            'manual_vacancy': manual_vacancy
        }
        run_analysis(st.session_state.property_data2, assumptions, 'duplex_triplex')

# Land Tab
with tab3:
    st.header("🌳 Land Information")
    with st.form("property_details3"):
        st.markdown('<div style="background-color:#23272f;padding:2rem 2rem 1rem 2rem;border-radius:18px;box-shadow:0 2px 16px #0002;margin-bottom:1.5rem;">', unsafe_allow_html=True)
        st.markdown('<h3 style="margin-bottom:0.5rem;color:#fff;">Manual Land Details</h3>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            address = st.text_input("Address", key="address3")
            price_str = st.text_input("Price ($)", key="price3")
            lot_size_str = st.text_input("Lot Size (sqft)", key="lot3")
        with col2:
            sqft_str = st.text_input("Buildable Square Footage", key="sqft3")
            year_built = st.number_input("Year Ready (est.)", 1800, 2100, 2025, key="year3", step=None)
        submitted = st.form_submit_button("Analyze Land")
        st.markdown('</div>', unsafe_allow_html=True)
        price = safe_int(price_str, 0)
        sqft = safe_int(sqft_str, 0)
        lot_size = safe_int(lot_size_str, 0)
        if submitted:
            if price == 0:
                st.warning("Please enter a valid price.")
            property_data = {
                'address': address,
                'price': f"${price:,}" if price else None,
                'sqft': sqft,
                'lot_size': lot_size,
                'year_built': year_built
            }
            st.session_state.property_data3 = property_data
    if 'property_data3' in st.session_state and st.session_state.property_data3:
        # Land feasibility analysis
        feasibility = analysis.calculate_land_feasibility(st.session_state.property_data3, comps_data)
        if feasibility:
            st.markdown('<div style="background-color:#181c24;padding:2rem;border-radius:18px;box-shadow:0 2px 16px #0002;margin-top:1.5rem;">', unsafe_allow_html=True)
            st.subheader("🧮 Land Feasibility Analysis")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Potential Value", f"${feasibility['potential_value']:.2f}")
            col2.metric("Development Cost", f"${feasibility['development_cost']:.2f}")
            col3.metric("Potential Profit", f"${feasibility['potential_profit']:.2f}")
            col4.metric("ROI", f"{feasibility['roi']:.2f}%")
            st.plotly_chart(visualization.create_comps_scatter(st.session_state.property_data3, comps_data))
            if st.button("Generate Land Report", key="report_land"):
                # Simple PDF for land
                report_path = generate_report(st.session_state.property_data3, feasibility, {})
                with open(report_path, "rb") as f:
                    st.download_button(
                        label="Download PDF Report",
                        data=f,
                        file_name="land_report.pdf",
                        mime="application/pdf"
                    )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="background-color:#eab30822;padding:1rem 2rem;border-radius:12px;margin-top:1.5rem;display:flex;align-items:center;">'
                        '<span style="font-size:2rem;margin-right:1rem;">⚠️</span>'
                        '<span style="font-size:1.1rem;">Unable to analyze land. Please ensure you have entered a valid price and buildable square footage.</span>'
                        '</div>', unsafe_allow_html=True)
        if address:
            lat, lon = geocode_address(address)
            if lat and lon:
                st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}), zoom=15) 