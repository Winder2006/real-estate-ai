import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Modern color palette
COLOR_SEQ = px.colors.qualitative.Set2

# Helper for consistent layout
MODERN_LAYOUT = dict(
    font=dict(family="Inter, Arial", size=18, color="#223"),
    title_font=dict(size=26, family="Inter, Arial", color="#1a237e"),
    margin=dict(l=60, r=40, t=80, b=80),
    plot_bgcolor="#f8fafc",
    paper_bgcolor="#f8fafc",
    legend=dict(font=dict(size=16), bgcolor="#f8fafc", bordercolor="#e0e7ef", borderwidth=1),
)

def create_cash_flow_chart(monthly_cash_flow, break_even_rent, current_rent):
    """Create a cash flow analysis chart"""
    fig = go.Figure()
    
    # Add cash flow line
    fig.add_trace(go.Scatter(
        x=[current_rent],
        y=[monthly_cash_flow],
        mode='markers+lines',
        name='Cash Flow',
        line=dict(color=COLOR_SEQ[0], width=4),
        marker=dict(size=14)
    ))
    
    # Add break-even point
    fig.add_trace(go.Scatter(
        x=[break_even_rent],
        y=[0],
        mode='markers',
        name='Break-even Point',
        marker=dict(color=COLOR_SEQ[1], size=18, symbol='diamond')
    ))
    
    fig.update_layout(
        title='Cash Flow vs Rent',
        xaxis_title='Monthly Rent ($)',
        yaxis_title='Monthly Cash Flow ($)',
        showlegend=True,
        **MODERN_LAYOUT
    )
    
    return fig

def create_roi_comparison_chart(property_metrics, market_average):
    """Create ROI comparison chart"""
    fig = go.Figure()
    
    # Add property metrics
    fig.add_trace(go.Bar(
        x=['Cap Rate', 'Cash on Cash', 'ROI'],
        y=[
            property_metrics['cap_rate'],
            property_metrics['cash_on_cash'],
            property_metrics['roi']
        ],
        name='Property',
        marker_color=COLOR_SEQ[0]
    ))
    
    # Add market averages
    fig.add_trace(go.Bar(
        x=['Cap Rate', 'Cash on Cash', 'ROI'],
        y=[
            market_average['cap_rate'],
            market_average['cash_on_cash'],
            market_average['roi']
        ],
        name='Market Average',
        marker_color=COLOR_SEQ[1]
    ))
    
    fig.update_layout(
        title='Investment Metrics vs Market Average',
        xaxis_title='Metric',
        yaxis_title='Percentage (%)',
        barmode='group',
        **MODERN_LAYOUT
    )
    
    return fig

def create_expense_breakdown_chart(annual_expenses):
    """Create expense breakdown pie chart"""
    fig = px.pie(
        values=list(annual_expenses.values()),
        names=list(annual_expenses.keys()),
        title='Annual Expenses Breakdown',
        color_discrete_sequence=COLOR_SEQ,
        hole=0.35
    )
    fig.update_traces(textinfo='percent+label', textfont_size=18, pull=[0.05]*len(annual_expenses))
    fig.update_layout(**MODERN_LAYOUT)
    return fig

def create_property_value_trend(historical_values, predicted_value):
    """Create property value trend chart"""
    fig = go.Figure()
    
    # Add historical values
    fig.add_trace(go.Scatter(
        x=historical_values.index,
        y=historical_values.values,
        mode='lines+markers',
        name='Historical Values',
        line=dict(color=COLOR_SEQ[0], width=4),
        marker=dict(size=10)
    ))
    
    # Add predicted value
    fig.add_trace(go.Scatter(
        x=[historical_values.index[-1]],
        y=[predicted_value],
        mode='markers',
        name='Predicted Value',
        marker=dict(color=COLOR_SEQ[1], size=18, symbol='star')
    ))
    
    fig.update_layout(
        title='Property Value Trend',
        xaxis_title='Date',
        yaxis_title='Value ($)',
        showlegend=True,
        **MODERN_LAYOUT
    )
    
    return fig

def create_risk_heatmap(foreclosure_data):
    """Create risk heatmap based on foreclosure data"""
    fig = px.density_heatmap(
        foreclosure_data,
        x='longitude',
        y='latitude',
        z='foreclosure_rate',
        title='Foreclosure Risk Heatmap',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(**MODERN_LAYOUT)
    return fig

def create_comps_scatter(property_data, comps_data):
    """Show only comps in the same zip code and similar bed/bath/sqft as the target property. If none, show a message."""
    # Extract target property info
    target_zip = property_data.get('zipcode')
    target_beds = property_data.get('beds') or property_data.get('Bedrooms') or property_data.get('bedrooms')
    target_baths = property_data.get('baths') or property_data.get('Bathrooms') or property_data.get('bathrooms')
    target_sqft = property_data.get('sqft')
    target_price = property_data.get('price')

    # Try to use correct column names for comps_data
    zip_col = 'zipcode' if 'zipcode' in comps_data.columns else 'ZipCode' if 'ZipCode' in comps_data.columns else None
    beds_col = 'beds' if 'beds' in comps_data.columns else 'Bedrooms' if 'Bedrooms' in comps_data.columns else None
    baths_col = 'baths' if 'baths' in comps_data.columns else 'Bathrooms' if 'Bathrooms' in comps_data.columns else None
    sqft_col = 'sqft' if 'sqft' in comps_data.columns else 'FinishedSqft' if 'FinishedSqft' in comps_data.columns else None
    price_col = 'price' if 'price' in comps_data.columns else 'Sale_price' if 'Sale_price' in comps_data.columns else None

    filtered = comps_data.copy()
    # Filter by zip code
    if zip_col and target_zip:
        filtered = filtered[filtered[zip_col] == target_zip]
    # Filter by similar beds (+/-1)
    if beds_col and target_beds is not None:
        filtered = filtered[(filtered[beds_col] >= target_beds - 1) & (filtered[beds_col] <= target_beds + 1)]
    # Filter by similar baths (+/-1)
    if baths_col and target_baths is not None:
        filtered = filtered[(filtered[baths_col] >= target_baths - 1) & (filtered[baths_col] <= target_baths + 1)]
    # Filter by similar sqft (+/-20%)
    if sqft_col and target_sqft is not None:
        filtered = filtered[(filtered[sqft_col] >= target_sqft * 0.8) & (filtered[sqft_col] <= target_sqft * 1.2)]
    # Remove outliers (1st–99th percentile)
    if price_col and sqft_col and not filtered.empty:
        price_low = np.percentile(filtered[price_col], 1)
        sqft_low = np.percentile(filtered[sqft_col], 1)
        filtered = filtered[(filtered[price_col] >= price_low) & (filtered[price_col] <= 800000) &
                            (filtered[sqft_col] >= sqft_low) & (filtered[sqft_col] <= 6000)]
    fig = go.Figure()
    # Add comparable properties
    if not filtered.empty and price_col and sqft_col:
        fig.add_trace(go.Scatter(
            x=filtered[sqft_col],
            y=filtered[price_col],
            mode='markers',
            name='Comparable Properties',
            marker=dict(color=COLOR_SEQ[0], opacity=0.7, size=9, line=dict(width=0.5, color='#223'))
        ))
    # Add target property
    if target_sqft is not None and target_price is not None:
        fig.add_trace(go.Scatter(
            x=[target_sqft],
            y=[target_price],
            mode='markers',
            name='Target Property',
            marker=dict(color=COLOR_SEQ[1], size=22, line=dict(width=2, color='#223'), symbol='star')
        ))
    fig.update_layout(
        title='Comparable Properties Analysis',
        xaxis_title='Square Footage',
        yaxis_title='Price ($)',
        showlegend=True,
        xaxis=dict(tickangle=30, tickfont=dict(size=16)),
        yaxis=dict(tickfont=dict(size=16)),
        **MODERN_LAYOUT
    )
    # If no comps, show a message
    if filtered.empty or not price_col or not sqft_col:
        fig.add_annotation(
            text="No comparable properties found for the selected criteria.",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=22, color="#e02424"),
            align="center"
        )
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        fig.update_layout(showlegend=False)
    return fig 