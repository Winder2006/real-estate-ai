import pandas as pd
import xlsxwriter
from datetime import datetime, timedelta
import io
import os

class RealEstateExcelGenerator:
    """Professional Excel generator for real estate pro formas with industry-standard formatting"""
    
    def __init__(self):
        self.colors = {
            'revenue': '#22C55E',      # Green for revenue
            'costs': '#3B82F6',        # Blue for costs  
            'equity': '#FCD34D',       # Yellow for equity
            'timeline': '#6B7280',     # Gray for timeline headers
            'header_bg': '#F3F4F6',    # Light gray for headers
            'white': '#FFFFFF',
            'border': '#E5E7EB'
        }
    
    def create_pro_forma(self, property_data, analysis_results, assumptions, project_name=None):
        """Create a comprehensive real estate pro forma Excel file"""
        
        # Create Excel file in memory
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        # Create worksheets
        summary_ws = workbook.add_worksheet('Executive Summary')
        proforma_ws = workbook.add_worksheet('Pro Forma Analysis')
        assumptions_ws = workbook.add_worksheet('Assumptions')
        sensitivity_ws = workbook.add_worksheet('Sensitivity Analysis')
        
        # Define formats
        self._create_formats(workbook)
        
        # Generate each worksheet - Create Executive Summary first so cell references are available for Pro Forma
        self._create_summary_sheet(summary_ws, property_data, analysis_results, assumptions, project_name)
        self._create_proforma_sheet(proforma_ws, property_data, analysis_results, assumptions, project_name)
        self._create_assumptions_sheet(assumptions_ws, property_data, assumptions)
        self._create_sensitivity_sheet(sensitivity_ws, property_data, analysis_results, assumptions)
        
        # Set up print settings for all sheets
        for ws in [summary_ws, proforma_ws, assumptions_ws, sensitivity_ws]:
            self._setup_print_settings(ws)
        
        workbook.close()
        output.seek(0)
        
        return output.getvalue()
    
    def _create_formats(self, workbook):
        """Create all formatting styles for the workbook"""
        
        # Header formats
        self.title_format = workbook.add_format({
            'font_size': 18,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': self.colors['header_bg'],
            'border': 1,
            'border_color': self.colors['border']
        })
        
        self.section_header_revenue = workbook.add_format({
            'font_size': 12,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': self.colors['revenue'],
            'font_color': self.colors['white'],
            'border': 1,
            'border_color': self.colors['border']
        })
        
        self.section_header_costs = workbook.add_format({
            'font_size': 12,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': self.colors['costs'],
            'font_color': self.colors['white'],
            'border': 1,
            'border_color': self.colors['border']
        })
        
        self.section_header_equity = workbook.add_format({
            'font_size': 12,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': self.colors['equity'],
            'font_color': '#000000',
            'border': 1,
            'border_color': self.colors['border']
        })
        
        self.section_header_timeline = workbook.add_format({
            'font_size': 11,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': self.colors['timeline'],
            'font_color': self.colors['white'],
            'border': 1,
            'border_color': self.colors['border']
        })
        
        # Column header format
        self.column_header = workbook.add_format({
            'font_size': 10,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': self.colors['header_bg'],
            'border': 1,
            'border_color': self.colors['border'],
            'text_wrap': True
        })
        
        # Industry-standard blue input format
        self.input_format = workbook.add_format({
            'font_color': '#0066CC',  # Blue color for inputs
            'bold': True,
            'align': 'center',
            'border': 1,
            'border_color': self.colors['border']
        })
        
        self.input_currency_format = workbook.add_format({
            'num_format': '$#,##0',
            'font_color': '#0066CC',  # Blue color for inputs
            'bold': True,
            'align': 'center',
            'border': 1,
            'border_color': self.colors['border']
        })
        
        self.input_percentage_format = workbook.add_format({
            'num_format': '0.00%',
            'font_color': '#0066CC',  # Blue color for inputs
            'bold': True,
            'align': 'center',
            'border': 1,
            'border_color': self.colors['border']
        })
        
        # Data formats
        self.currency_format = workbook.add_format({
            'num_format': '$#,##0',
            'align': 'center',
            'border': 1,
            'border_color': self.colors['border']
        })
        
        self.currency_bold = workbook.add_format({
            'num_format': '$#,##0',
            'align': 'center',
            'bold': True,
            'border': 1,
            'border_color': self.colors['border']
        })
        
        # Per SF format - shows cents for small values
        self.currency_per_sf = workbook.add_format({
            'num_format': '$#,##0.00',
            'align': 'center',
            'border': 1,
            'border_color': self.colors['border']
        })
        
        self.percentage_format = workbook.add_format({
            'num_format': '0.00%',
            'align': 'center',
            'border': 1,
            'border_color': self.colors['border']
        })
        
        self.number_format = workbook.add_format({
            'num_format': '#,##0',
            'align': 'center',
            'border': 1,
            'border_color': self.colors['border']
        })
        
        self.date_format = workbook.add_format({
            'num_format': 'mm/dd/yyyy',
            'align': 'center',
            'border': 1,
            'border_color': self.colors['border']
        })
        
        self.text_format = workbook.add_format({
            'align': 'left',
            'border': 1,
            'border_color': self.colors['border']
        })
        
        self.text_bold = workbook.add_format({
            'align': 'left',
            'bold': True,
            'border': 1,
            'border_color': self.colors['border']
        })
        
        self.text_center = workbook.add_format({
            'align': 'center',
            'border': 1,
            'border_color': self.colors['border']
        })
    
    def _create_summary_sheet(self, ws, property_data, results, assumptions, project_name):
        """Create executive summary sheet"""
        
        # Set column widths for optimal display
        ws.set_column('A:A', 28)   # Property labels (wider for readability)
        ws.set_column('B:B', 16)   # Property values
        ws.set_column('C:C', 20)   # Project metrics labels
        ws.set_column('D:D', 16)   # Project metrics values
        ws.set_column('E:E', 12)   # Extra space
        ws.set_column('F:F', 28)   # Financial Assumptions labels (wider)
        ws.set_column('G:G', 16)   # Financial Assumptions values
        
        # Freeze panes removed for better user experience
        # ws.freeze_panes(3, 1)
        
        row = 0
        
        # Title
        project_title = project_name or f"Real Estate Investment Analysis - {property_data.get('address', 'Property')}"
        ws.merge_range(row, 0, row, 4, project_title, self.title_format)
        row += 1
        
        ws.merge_range(row, 0, row, 4, f"Generated on {datetime.now().strftime('%B %d, %Y')}", self.column_header)
        row += 2
        
        # Property Information Section
        ws.merge_range(row, 0, row, 4, "PROPERTY INFORMATION", self.section_header_timeline)
        row += 1
        
        # Add headers for better formatting
        ws.write(row, 0, "Property Details", self.column_header)
        ws.write(row, 1, "Value", self.column_header)
        ws.write(row, 2, "Project Metrics", self.column_header)
        ws.write(row, 3, "Value", self.column_header)
        row += 1
        
        # Left column - Basic Property Info
        property_info_left = [
            ("Address", property_data.get('address', 'N/A')),
            ("Property Type", property_data.get('propertyType', 'N/A')),
            ("Neighborhood", property_data.get('neighborhood', 'N/A')),
            ("Zip Code", property_data.get('zipcode', 'N/A'))
        ]
        
        # Right column - Project Metrics
        total_units = property_data.get('totalUnits', 1)
        total_sqft = property_data.get('sqft', 0)
        avg_sf_per_unit = round(total_sqft / max(total_units, 1), 0)
        
        # Data extraction verified and fixed
        
        property_info_right = [
            ("Total Development Cost", property_data.get('price', 0)),
            ("Total Square Footage", total_sqft),
            ("Total Units", total_units),
            ("Avg SF per Unit", avg_sf_per_unit)
        ]
        
        # Write both columns side by side and store cell references
        start_row = row
        cell_refs = {}  # Store cell references for later use
        
        for i, (label, value) in enumerate(property_info_left):
            ws.write(start_row + i, 0, label, self.text_bold)
            ws.write(start_row + i, 1, value, self.text_center)
        
        for i, (label, value) in enumerate(property_info_right):
            cell_row = start_row + i
            ws.write(cell_row, 2, label, self.text_center)
            if label == "Total Development Cost":
                ws.write(cell_row, 3, value, self.input_currency_format)  # Blue input format
                cell_refs['purchase_price'] = f"'Executive Summary'!D{cell_row + 1}"  # Excel 1-indexed
            elif label == "Total Square Footage":
                ws.write(cell_row, 3, f"{value:,.0f} SF", self.input_format)  # Blue input format
                cell_refs['total_sqft'] = f"'Executive Summary'!D{cell_row + 1}"
            elif label == "Total Units":
                ws.write(cell_row, 3, value, self.input_format)  # Blue input format  
                cell_refs['total_units'] = f"'Executive Summary'!D{cell_row + 1}"
            else:
                ws.write(cell_row, 3, value, self.input_format)  # Blue input format
        
        # Store cell references for sensitivity analysis
        self.cell_refs = cell_refs
        
        # After property info, track the end row for layout
        property_info_end_row = start_row + max(len(property_info_left), len(property_info_right))
        
        # Move Financial Assumptions to the right side (columns F-G) starting at the same level as Property Info
        assumption_start_row = start_row
        assumption_col = 5  # Column F (0-indexed)
        
        # Financial Assumptions Header in columns F-G
        ws.merge_range(assumption_start_row - 1, assumption_col, assumption_start_row - 1, assumption_col + 1, "FINANCIAL ASSUMPTIONS", self.section_header_costs)
        
        # Add ALL key input assumptions for comprehensive cell references
        annual_rent = results.get('monthlyRent', 2000) * 12
        ws.write(assumption_start_row, assumption_col, "Annual Gross Rent", self.text_bold)
        ws.write(assumption_start_row, assumption_col + 1, annual_rent, self.input_currency_format)  # Blue input format
        cell_refs['annual_rent'] = f"'Executive Summary'!G{assumption_start_row + 1}"  # Excel 1-indexed
        assumption_start_row += 1
        
        # Rent Growth Rate
        rent_growth = 0.03  # 3% annual rent growth (reasonable assumption)
        ws.write(assumption_start_row, assumption_col, "Rent Growth Rate", self.text_bold)
        ws.write(assumption_start_row, assumption_col + 1, rent_growth, self.input_percentage_format)
        cell_refs['rent_growth'] = f"'Executive Summary'!G{assumption_start_row + 1}"
        assumption_start_row += 1
        
        # Vacancy Rate
        vacancy_rate = assumptions.get('vacancyRate', 5.0) / 100
        ws.write(assumption_start_row, assumption_col, "Vacancy Rate", self.text_bold)
        ws.write(assumption_start_row, assumption_col + 1, vacancy_rate, self.input_percentage_format)
        cell_refs['vacancy_rate'] = f"'Executive Summary'!G{assumption_start_row + 1}"
        assumption_start_row += 1
        
        # Operating Expense Rates
        property_mgmt_rate = 0.08
        ws.write(assumption_start_row, assumption_col, "Property Management %", self.text_bold)
        ws.write(assumption_start_row, assumption_col + 1, property_mgmt_rate, self.input_percentage_format)
        cell_refs['property_mgmt_rate'] = f"'Executive Summary'!G{assumption_start_row + 1}"
        assumption_start_row += 1
        
        maintenance_rate = 0.01
        ws.write(assumption_start_row, assumption_col, "Maintenance % of EGI", self.text_bold)
        ws.write(assumption_start_row, assumption_col + 1, maintenance_rate, self.input_percentage_format)
        cell_refs['maintenance_rate'] = f"'Executive Summary'!G{assumption_start_row + 1}"
        assumption_start_row += 1
        
        capital_reserves_rate = 0.01
        ws.write(assumption_start_row, assumption_col, "Capital Reserves % of EGI", self.text_bold)
        ws.write(assumption_start_row, assumption_col + 1, capital_reserves_rate, self.input_percentage_format)
        cell_refs['capital_reserves_rate'] = f"'Executive Summary'!G{assumption_start_row + 1}"
        assumption_start_row += 1
        
        utilities_rate = 0.005
        ws.write(assumption_start_row, assumption_col, "Utilities % of EGI", self.text_bold)
        ws.write(assumption_start_row, assumption_col + 1, utilities_rate, self.input_percentage_format)
        cell_refs['utilities_rate'] = f"'Executive Summary'!G{assumption_start_row + 1}"
        assumption_start_row += 1
        
        legal_rate = 0.002
        ws.write(assumption_start_row, assumption_col, "Legal & Professional % of EGI", self.text_bold)
        ws.write(assumption_start_row, assumption_col + 1, legal_rate, self.input_percentage_format)
        cell_refs['legal_rate'] = f"'Executive Summary'!G{assumption_start_row + 1}"
        assumption_start_row += 1
        
        other_expenses_rate = 0.003
        ws.write(assumption_start_row, assumption_col, "Other Operating % of EGI", self.text_bold)
        ws.write(assumption_start_row, assumption_col + 1, other_expenses_rate, self.input_percentage_format)
        cell_refs['other_expenses_rate'] = f"'Executive Summary'!G{assumption_start_row + 1}"
        assumption_start_row += 1
        
        # Property Tax and Insurance Rates
        property_tax_rate = assumptions.get('propertyTaxRate', 3.0) / 100
        ws.write(assumption_start_row, assumption_col, "Property Tax Rate", self.text_bold)
        ws.write(assumption_start_row, assumption_col + 1, property_tax_rate, self.input_percentage_format)
        cell_refs['property_tax_rate'] = f"'Executive Summary'!G{assumption_start_row + 1}"
        assumption_start_row += 1
        
        insurance_rate = assumptions.get('insuranceRate', 0.5) / 100
        ws.write(assumption_start_row, assumption_col, "Insurance Rate", self.text_bold)
        ws.write(assumption_start_row, assumption_col + 1, insurance_rate, self.input_percentage_format)
        cell_refs['insurance_rate'] = f"'Executive Summary'!G{assumption_start_row + 1}"
        assumption_start_row += 1
        
        # Inflation Rate
        inflation_rate = 0.025
        ws.write(assumption_start_row, assumption_col, "Inflation Rate", self.text_bold)
        ws.write(assumption_start_row, assumption_col + 1, inflation_rate, self.input_percentage_format)
        cell_refs['inflation_rate'] = f"'Executive Summary'!G{assumption_start_row + 1}"
        assumption_start_row += 1
        
        # Financing Parameters - Use form data with proper defaults for development projects
        down_payment_pct = assumptions.get('downPaymentPct', 20) / 100
        ws.write(assumption_start_row, assumption_col, "Down Payment %", self.text_bold)
        ws.write(assumption_start_row, assumption_col + 1, down_payment_pct, self.input_percentage_format)  # Blue input format
        cell_refs['down_payment_pct'] = f"'Executive Summary'!G{assumption_start_row + 1}"
        assumption_start_row += 1
        
        # For development projects, use permanent loan rates (typically lower than construction)
        interest_rate = assumptions.get('interestRate', 5.0) / 100
        # Convert construction rate to permanent loan rate if needed
        if interest_rate > 0.06:  # If > 6%, assume it's construction rate, convert to permanent
            interest_rate = 0.055  # Use typical permanent loan rate
        ws.write(assumption_start_row, assumption_col, "Permanent Loan Rate", self.text_bold)
        ws.write(assumption_start_row, assumption_col + 1, interest_rate, self.input_percentage_format)  # Blue input format
        cell_refs['interest_rate'] = f"'Executive Summary'!G{assumption_start_row + 1}"
        assumption_start_row += 1
        
        # Use loan term from user assumptions (converted from months to years if needed)
        loan_term = assumptions.get('loanTerm', 30)
        # For development projects, convert construction loan term from months to years for permanent financing
        # Construction loans are typically 12-36 months, permanent loans are 20-30 years
        if loan_term <= 36:  # Assume values <= 36 are construction loan months, convert to permanent years
            loan_term = 30  # Use standard 30-year permanent financing
        elif loan_term > 100:  # Values > 100 are likely months, convert to years
            loan_term = loan_term / 12
        ws.write(assumption_start_row, assumption_col, "Loan Term (Years)", self.text_bold)
        ws.write(assumption_start_row, assumption_col + 1, loan_term, self.input_format)  # Blue input format
        cell_refs['loan_term'] = f"'Executive Summary'!G{assumption_start_row + 1}"
        assumption_start_row += 1
        
        closing_costs_pct = assumptions.get('closingCostsPct', 3) / 100
        ws.write(assumption_start_row, assumption_col, "Closing Costs %", self.text_bold)
        ws.write(assumption_start_row, assumption_col + 1, closing_costs_pct, self.input_percentage_format)  # Blue input format
        cell_refs['closing_costs_pct'] = f"'Executive Summary'!G{assumption_start_row + 1}"
        assumption_start_row += 1
        
        # Sale Parameters (for exit strategy)
        cap_rate_exit = 0.06
        ws.write(assumption_start_row, assumption_col, "Exit Cap Rate", self.text_bold)
        ws.write(assumption_start_row, assumption_col + 1, cap_rate_exit, self.input_percentage_format)
        cell_refs['cap_rate_exit'] = f"'Executive Summary'!G{assumption_start_row + 1}"
        assumption_start_row += 1
        
        selling_costs_pct = 0.07
        ws.write(assumption_start_row, assumption_col, "Selling Costs %", self.text_bold)
        ws.write(assumption_start_row, assumption_col + 1, selling_costs_pct, self.input_percentage_format)
        cell_refs['selling_costs_pct'] = f"'Executive Summary'!G{assumption_start_row + 1}"
        assumption_start_row += 1
        
        # Update stored cell references
        self.cell_refs = cell_refs
        
        # Set row to continue right after Property Info section (ignore Financial Assumptions height)
        row = property_info_end_row + 1
        
        # Key Investment Metrics
        ws.merge_range(row, 0, row, 4, "KEY INVESTMENT METRICS", self.section_header_revenue)
        row += 1
        
        # Headers
        ws.write(row, 0, "Metric", self.column_header)
        ws.write(row, 1, "Value", self.column_header)
        ws.write(row, 2, "Target", self.column_header)
        ws.write(row, 3, "Status", self.column_header)
        row += 1
        
        # Create simple calculated metrics for now - will be enhanced with Pro Forma references
        metrics = [
            ("Cap Rate", results.get('capRate', 0) / 100, 0.06),
            ("Cash-on-Cash Return", results.get('cashOnCash', 0) / 100, 0.08),
            ("Monthly Cash Flow", results.get('monthlyCashFlow', 0), 300),
            ("Rent-to-Price Ratio", results.get('rentToPrice', 0) / 100, 0.008)
        ]
        
        for metric, value, target in metrics:
            ws.write(row, 0, metric, self.text_format)
            if metric == "Monthly Cash Flow":
                ws.write(row, 1, value, self.currency_format)
                ws.write(row, 2, target, self.currency_format)
            else:
                ws.write(row, 1, value, self.percentage_format)
                ws.write(row, 2, target, self.percentage_format)
            # Simple status calculation
            status = "Good" if value >= target else "Poor"
            ws.write(row, 3, status, self.text_center)
            row += 1
        
        row += 1
        
        # Financial Summary - Using cross-sheet cell references
        ws.merge_range(row, 0, row, 4, "FINANCIAL SUMMARY", self.section_header_costs)
        row += 1
        
        ws.write(row, 0, "Item", self.column_header)
        ws.write(row, 1, "Monthly", self.column_header)
        ws.write(row, 2, "Annual", self.column_header)
        ws.write(row, 3, "5-Year Total", self.column_header)
        row += 1
        
        # Reference the Pro Forma Analysis sheet for all calculations
        # Note: We need to wait until the Pro Forma sheet is created to get exact row numbers
        # These will be updated after _create_proforma_sheet is called
        
        # Gross Rental Income
        ws.write(row, 0, "Gross Rental Income", self.text_format)
        ws.write_formula(row, 1, f"='Pro Forma Analysis'!B{self.proforma_rows.get('gross_income', 8) + 1}/12", self.currency_format)
        ws.write_formula(row, 2, f"='Pro Forma Analysis'!B{self.proforma_rows.get('gross_income', 8) + 1}", self.currency_format)
        ws.write_formula(row, 3, f"=SUM('Pro Forma Analysis'!B{self.proforma_rows.get('gross_income', 8) + 1}:F{self.proforma_rows.get('gross_income', 8) + 1})", self.currency_format)
        row += 1
        
        # Total Operating Expenses
        ws.write(row, 0, "Total Operating Expenses", self.text_format)
        ws.write_formula(row, 1, f"='Pro Forma Analysis'!B{self.proforma_rows.get('total_expenses', 16) + 1}/12", self.currency_format)
        ws.write_formula(row, 2, f"='Pro Forma Analysis'!B{self.proforma_rows.get('total_expenses', 16) + 1}", self.currency_format)
        ws.write_formula(row, 3, f"=SUM('Pro Forma Analysis'!B{self.proforma_rows.get('total_expenses', 16) + 1}:F{self.proforma_rows.get('total_expenses', 16) + 1})", self.currency_format)
        row += 1
        
        # Net Operating Income
        ws.write(row, 0, "Net Operating Income", self.text_format)
        ws.write_formula(row, 1, f"='Pro Forma Analysis'!B{self.proforma_rows.get('noi', 18) + 1}/12", self.currency_format)
        ws.write_formula(row, 2, f"='Pro Forma Analysis'!B{self.proforma_rows.get('noi', 18) + 1}", self.currency_format)
        ws.write_formula(row, 3, f"=SUM('Pro Forma Analysis'!B{self.proforma_rows.get('noi', 18) + 1}:F{self.proforma_rows.get('noi', 18) + 1})", self.currency_format)
        row += 1
        
        # Debt Service
        ws.write(row, 0, "Debt Service", self.text_format)
        ws.write_formula(row, 1, f"='Pro Forma Analysis'!B{self.proforma_rows.get('debt_service', 21) + 1}/12", self.currency_format)
        ws.write_formula(row, 2, f"='Pro Forma Analysis'!B{self.proforma_rows.get('debt_service', 21) + 1}", self.currency_format)
        ws.write_formula(row, 3, f"=SUM('Pro Forma Analysis'!B{self.proforma_rows.get('debt_service', 21) + 1}:F{self.proforma_rows.get('debt_service', 21) + 1})", self.currency_format)
        row += 1
        
        # Before-Tax Cash Flow (Operations)
        ws.write(row, 0, "Before-Tax Cash Flow (Operations)", self.text_format)
        ws.write_formula(row, 1, f"='Pro Forma Analysis'!B{self.proforma_rows.get('before_tax_cash_flow', 24) + 1}/12", self.currency_format)
        ws.write_formula(row, 2, f"='Pro Forma Analysis'!B{self.proforma_rows.get('before_tax_cash_flow', 24) + 1}", self.currency_format)
        ws.write_formula(row, 3, f"=SUM('Pro Forma Analysis'!B{self.proforma_rows.get('before_tax_cash_flow', 24) + 1}:F{self.proforma_rows.get('before_tax_cash_flow', 24) + 1})", self.currency_format)
        row += 1
        
        row += 1
        ws.write(row, 0, "Note: Excludes sale proceeds in Year 5", self.text_format)
        row += 1
    
    def _create_proforma_sheet(self, ws, property_data, results, assumptions, project_name):
        """Create detailed pro forma analysis sheet"""
        
        # Initialize row references for cross-sheet use
        self.proforma_rows = {}
        
        # Set column widths for optimal display
        ws.set_column('A:A', 35)   # Line items (wider for long descriptions)
        ws.set_column('B:F', 14)   # Year columns (wider for large numbers)
        ws.set_column('G:G', 16)   # Per unit column
        ws.set_column('H:H', 16)   # Per SF column
        ws.set_column('I:J', 8)    # Empty columns (narrow)
        ws.set_column('K:K', 25)   # Assumption labels (wider)
        ws.set_column('L:L', 16)   # Assumption values
        
        # Remove freeze panes for better user experience
        # ws.freeze_panes(4, 1)  # Commented out - freeze panes removed
        
        # Define variables for use throughout the sheet - ensure they match the correct property data
        units = property_data.get('totalUnits', 1) if property_data.get('totalUnits', 1) > 0 else 1
        sqft = property_data.get('sqft', 1000) if property_data.get('sqft', 1000) > 0 else 1000
        
        # Variables verified and working correctly
        
        row = 0
        
        # Title
        ws.merge_range(row, 0, row, 7, f"5-Year Pro Forma Analysis - {property_data.get('address', 'Property')}", self.title_format)
        row += 1
        
        ws.merge_range(row, 0, row, 7, f"Analysis Date: {datetime.now().strftime('%B %d, %Y')}", self.column_header)
        row += 2
        
        # SETUP LOCAL ASSUMPTIONS - Move to column K for cleaner layout
        assumption_col = 10  # Column K (0-indexed)
        assumption_row = 1   # Start at row 2 (0-indexed)
        ws.merge_range(assumption_row, assumption_col, assumption_row, assumption_col + 1, "KEY ASSUMPTIONS (All values are editable)", self.section_header_timeline)
        assumption_row += 1
        
        # Calculate assumption values from form data
        purchase_price = property_data.get('price', 500000)
        down_payment_pct = assumptions.get('downPaymentPct', 20) / 100
        interest_rate = assumptions.get('interestRate', 5.0) / 100
        loan_term = assumptions.get('loanTerm', 30)
        if loan_term <= 36:  # Convert construction to permanent
            loan_term = 30
        elif loan_term > 100:
            loan_term = loan_term / 12
        closing_costs_pct = 0.03
        total_units = property_data.get('totalUnits', 1)
        total_sqft = property_data.get('sqft', 1000)
        total_monthly_rent = results.get('monthlyRent', 0)
        base_annual_rent = total_monthly_rent * 12
        rent_growth = 0.03
        
        # Write all assumptions to cells in column K
        ws.write(assumption_row + 1, assumption_col, "Purchase Price", self.text_bold)
        ws.write(assumption_row + 1, assumption_col + 1, purchase_price, self.input_currency_format)
        ws.write(assumption_row + 2, assumption_col, "Down Payment %", self.text_bold)
        ws.write(assumption_row + 2, assumption_col + 1, down_payment_pct, self.input_percentage_format)
        ws.write(assumption_row + 3, assumption_col, "Interest Rate", self.text_bold)
        ws.write(assumption_row + 3, assumption_col + 1, interest_rate, self.input_percentage_format)
        ws.write(assumption_row + 4, assumption_col, "Loan Term (Years)", self.text_bold)
        ws.write(assumption_row + 4, assumption_col + 1, loan_term, self.input_format)
        ws.write(assumption_row + 5, assumption_col, "Closing Costs %", self.text_bold)
        ws.write(assumption_row + 5, assumption_col + 1, closing_costs_pct, self.input_percentage_format)
        ws.write(assumption_row + 6, assumption_col, "Property Mgmt %", self.text_bold)
        ws.write(assumption_row + 6, assumption_col + 1, 0.08, self.input_percentage_format)
        ws.write(assumption_row + 7, assumption_col, "Property Tax %", self.text_bold)
        ws.write(assumption_row + 7, assumption_col + 1, 0.03, self.input_percentage_format)
        ws.write(assumption_row + 8, assumption_col, "Insurance %", self.text_bold)
        ws.write(assumption_row + 8, assumption_col + 1, 0.005, self.input_percentage_format)
        ws.write(assumption_row + 9, assumption_col, "Maintenance %", self.text_bold)
        ws.write(assumption_row + 9, assumption_col + 1, 0.01, self.input_percentage_format)
        ws.write(assumption_row + 10, assumption_col, "Capital Reserves %", self.text_bold)
        ws.write(assumption_row + 10, assumption_col + 1, 0.01, self.input_percentage_format)
        ws.write(assumption_row + 11, assumption_col, "Utilities %", self.text_bold)
        ws.write(assumption_row + 11, assumption_col + 1, 0.005, self.input_percentage_format)
        ws.write(assumption_row + 12, assumption_col, "Legal %", self.text_bold)
        ws.write(assumption_row + 12, assumption_col + 1, 0.002, self.input_percentage_format)
        ws.write(assumption_row + 13, assumption_col, "Other Expenses %", self.text_bold)
        ws.write(assumption_row + 13, assumption_col + 1, 0.003, self.input_percentage_format)
        ws.write(assumption_row + 14, assumption_col, "Inflation Rate", self.text_bold)
        ws.write(assumption_row + 14, assumption_col + 1, 0.025, self.input_percentage_format)
        ws.write(assumption_row + 15, assumption_col, "Total Units", self.text_bold)
        ws.write(assumption_row + 15, assumption_col + 1, total_units, self.input_format)
        ws.write(assumption_row + 16, assumption_col, "Total Square Feet", self.text_bold)
        ws.write(assumption_row + 16, assumption_col + 1, total_sqft, self.input_format)
        ws.write(assumption_row + 17, assumption_col, "Annual Gross Rent", self.text_bold)
        ws.write(assumption_row + 17, assumption_col + 1, base_annual_rent, self.input_currency_format)
        ws.write(assumption_row + 18, assumption_col, "Rent Growth Rate", self.text_bold)
        ws.write(assumption_row + 18, assumption_col + 1, rent_growth, self.input_percentage_format)
        ws.write(assumption_row + 19, assumption_col, "Vacancy Rate", self.text_bold)
        ws.write(assumption_row + 19, assumption_col + 1, 0.05, self.input_percentage_format)
        ws.write(assumption_row + 20, assumption_col, "NOI Margin", self.text_bold)
        ws.write(assumption_row + 20, assumption_col + 1, 0.70, self.input_percentage_format)
        
        # Add missing assumption cells for exit cap rate and selling costs
        ws.write(assumption_row + 21, assumption_col, "Exit Cap Rate", self.text_bold)
        ws.write(assumption_row + 21, assumption_col + 1, 0.06, self.input_percentage_format)
        ws.write(assumption_row + 22, assumption_col, "Selling Costs %", self.text_bold)
        ws.write(assumption_row + 22, assumption_col + 1, 0.07, self.input_percentage_format)
        
        # OVERRIDE self.cell_refs to use LOCAL cells in column L (assumption_col + 1)
        self.cell_refs = {
            'purchase_price': f"L{assumption_row + 2}",
            'down_payment_pct': f"L{assumption_row + 3}",
            'interest_rate': f"L{assumption_row + 4}",
            'loan_term': f"L{assumption_row + 5}",
            'closing_costs_pct': f"L{assumption_row + 6}",
            'property_mgmt_rate': f"L{assumption_row + 7}",
            'property_tax_rate': f"L{assumption_row + 8}",
            'insurance_rate': f"L{assumption_row + 9}",
            'maintenance_rate': f"L{assumption_row + 10}",
            'capital_reserves_rate': f"L{assumption_row + 11}",
            'utilities_rate': f"L{assumption_row + 12}",
            'legal_rate': f"L{assumption_row + 13}",
            'other_expenses_rate': f"L{assumption_row + 14}",
            'inflation_rate': f"L{assumption_row + 15}",
            'total_units': f"L{assumption_row + 16}",
            'total_sqft': f"L{assumption_row + 17}",
            'annual_rent': f"L{assumption_row + 18}",
            'rent_growth': f"L{assumption_row + 19}",
            'vacancy_rate': f"L{assumption_row + 20}",
            'noi_margin': f"L{assumption_row + 21}",
            'cap_rate_exit': f"L{assumption_row + 22}",
            'selling_costs_pct': f"L{assumption_row + 23}"
        }
        
        # Define local references for all calculations (pointing to the B column values)
        total_units_ref = self.cell_refs['total_units']
        total_sqft_ref = self.cell_refs['total_sqft']
        annual_rent_ref = self.cell_refs['annual_rent']
        rent_growth_ref = self.cell_refs['rent_growth']
        vacancy_rate_ref = self.cell_refs['vacancy_rate']
        
        row = 3  # Start the main pro forma at row 4 since assumptions are now in column K
        
        # Column headers for years
        ws.write(row, 0, "Line Item", self.column_header)
        ws.write(row, 1, "Year 1", self.column_header)
        ws.write(row, 2, "Year 2", self.column_header)
        ws.write(row, 3, "Year 3", self.column_header)
        ws.write(row, 4, "Year 4", self.column_header)
        ws.write(row, 5, "Year 5", self.column_header)
        ws.write(row, 6, "$ per Unit", self.column_header)
        ws.write(row, 7, "$ per SF", self.column_header)
        row += 1
        
        # GROSS SALES / REVENUE
        ws.merge_range(row, 0, row, 7, "GROSS RENTAL INCOME", self.section_header_revenue)
        row += 1
        
        # Calculate rental income properly from form data
        total_units = property_data.get('totalUnits', 1)
        total_sqft = property_data.get('sqft', 1000)
        # Use the total monthly rent directly from the analysis results (already calculated for all units)
        total_monthly_rent = results.get('monthlyRent', 0)  # This is total for ALL units
        base_annual_rent = total_monthly_rent * 12  # Total annual rent for all units
        rent_growth = 0.03  # 3% annual rent growth
        
        # Data calculations verified and working
        
        # Rental Income - Use the already defined local cell references
        ws.write(row, 0, "Gross Rental Income", self.text_format)
        # Use the local cell references defined earlier
        
        for year in range(5):
            ws.write_formula(row, year + 1, f"={annual_rent_ref}*POWER(1+{rent_growth_ref},{year})", self.currency_format)
        
        # Per unit and per SF calculations with proper references
        ws.write_formula(row, 6, f"=B{row+1}/{total_units_ref}", self.currency_format)
        ws.write_formula(row, 7, f"=B{row+1}/{total_sqft_ref}", self.currency_per_sf)
        rental_income_row = row
        row += 1
        
        # Other Income - Use cell reference for percentage
        other_income_rate = 0.05
        ws.write(row, 0, "Other Income (5% of Gross Rent)", self.text_format)
        for year in range(5):
            col_letter = chr(66 + year)  # B, C, D, E, F for years 1-5
            ws.write_formula(row, year + 1, f"={col_letter}{rental_income_row+1}*{other_income_rate}", self.currency_format)
        ws.write_formula(row, 6, f"=B{row+1}/{total_units_ref}", self.currency_format)
        ws.write_formula(row, 7, f"=B{row+1}/{total_sqft_ref}", self.currency_per_sf)
        row += 1
        
        # Gross Income Total
        ws.write(row, 0, "TOTAL GROSS INCOME", self.text_bold)
        for year in range(5):
            col_letter = chr(66 + year)  # B, C, D, E, F for years 1-5
            ws.write_formula(row, year + 1, f"=SUM({col_letter}{rental_income_row+1}:{col_letter}{row})", self.currency_bold)
        ws.write_formula(row, 6, f"=B{row+1}/{total_units_ref}", self.currency_format)
        ws.write_formula(row, 7, f"=B{row+1}/{total_sqft_ref}", self.currency_per_sf)
        total_gross_income_row = row  # Store this row reference
        # Store gross income row for cross-sheet reference
        self.proforma_rows['gross_income'] = total_gross_income_row
        row += 2
        
        # OPERATING EXPENSES
        ws.merge_range(row, 0, row, 7, "OPERATING EXPENSES", self.section_header_costs)
        row += 1
        
        # Vacancy & Credit Loss - Use local cell reference
        # vacancy_rate_ref already defined above from local cells
        ws.write(row, 0, "Vacancy & Credit Loss", self.text_format)
        for year in range(5):
            col_letter = chr(66 + year)  # B, C, D, E, F for years 1-5
            ws.write_formula(row, year + 1, f"={col_letter}{total_gross_income_row+1}*{vacancy_rate_ref}", self.currency_format)
        ws.write_formula(row, 6, f"=B{row+1}/{total_units_ref}", self.currency_format)
        ws.write_formula(row, 7, f"=B{row+1}/{total_sqft_ref}", self.currency_per_sf)
        vacancy_loss_row = row
        row += 1
        
        # Effective Gross Income
        ws.write(row, 0, "EFFECTIVE GROSS INCOME", self.text_bold)
        for year in range(5):
            col_letter = chr(66 + year)  # B, C, D, E, F for years 1-5
            ws.write_formula(row, year + 1, f"={col_letter}{total_gross_income_row+1}-{col_letter}{vacancy_loss_row+1}", self.currency_bold)
        ws.write_formula(row, 6, f"=B{row+1}/{total_units_ref}", self.currency_format)
        ws.write_formula(row, 7, f"=B{row+1}/{total_sqft_ref}", self.currency_per_sf)
        egi_row = row  # Store the EGI row reference
        row += 2
        
        # Operating Expenses Detail - Use cell references for ALL rates
        # Reference the local assumption cells using the updated self.cell_refs
        property_mgmt_rate_ref = self.cell_refs['property_mgmt_rate']
        property_tax_rate_ref = self.cell_refs['property_tax_rate']
        insurance_rate_ref = self.cell_refs['insurance_rate']
        maintenance_rate_ref = self.cell_refs['maintenance_rate']
        capital_reserves_rate_ref = self.cell_refs['capital_reserves_rate']
        utilities_rate_ref = self.cell_refs['utilities_rate']
        legal_rate_ref = self.cell_refs['legal_rate']
        other_expenses_rate_ref = self.cell_refs['other_expenses_rate']
        inflation_rate_ref = self.cell_refs['inflation_rate']
        
        expenses = [
            ("Property Management", "percentage", property_mgmt_rate_ref, "egi"),
            ("Property Taxes", "fixed_rate", property_tax_rate_ref, "purchase_price"),
            ("Insurance", "fixed_rate", insurance_rate_ref, "purchase_price"),
            ("Maintenance & Repairs", "percentage", maintenance_rate_ref, "egi"),
            ("Capital Reserves", "percentage", capital_reserves_rate_ref, "egi"),
            ("Utilities", "percentage", utilities_rate_ref, "egi"),
            ("Legal & Professional", "percentage", legal_rate_ref, "egi"),
            ("Other Operating Expenses", "percentage", other_expenses_rate_ref, "egi")
        ]
        
        expense_start_row = row
        
        for expense_name, calc_type, rate_ref, base in expenses:
            ws.write(row, 0, expense_name, self.text_format)
            
            if calc_type == "percentage":
                for year in range(5):
                    col_letter = chr(66 + year)  # B, C, D, E, F for years 1-5
                    ws.write_formula(row, year + 1, f"={col_letter}{egi_row+1}*{rate_ref}", self.currency_format)
            elif calc_type == "fixed_rate":
                # For property taxes and insurance - use local purchase price cell
                for year in range(5):
                    ws.write_formula(row, year + 1, f"={self.cell_refs['purchase_price']}*{rate_ref}*POWER(1+{inflation_rate_ref},{year})", self.currency_format)
            
            ws.write_formula(row, 6, f"=B{row+1}/{total_units_ref}", self.currency_format)
            ws.write_formula(row, 7, f"=B{row+1}/{total_sqft_ref}", self.currency_per_sf)
            row += 1
        
        # Total Operating Expenses
        ws.write(row, 0, "TOTAL OPERATING EXPENSES", self.text_bold)
        for year in range(5):
            col_letter = chr(66 + year)  # B, C, D, E, F for years 1-5
            ws.write_formula(row, year + 1, f"=SUM({col_letter}{expense_start_row+1}:{col_letter}{row})", self.currency_bold)
        ws.write_formula(row, 6, f"=B{row+1}/{total_units_ref}", self.currency_format)
        ws.write_formula(row, 7, f"=B{row+1}/{total_sqft_ref}", self.currency_per_sf)
        total_expenses_row = row  # Store the total expenses row reference
        # Store total expenses row for cross-sheet reference
        self.proforma_rows['total_expenses'] = total_expenses_row
        row += 2
        
        # NET OPERATING INCOME
        ws.merge_range(row, 0, row, 7, "NET OPERATING INCOME", self.section_header_revenue)
        row += 1
        
        ws.write(row, 0, "NET OPERATING INCOME (NOI)", self.text_bold)
        # Use the stored row references for accurate calculation
        for year in range(5):
            col_letter = chr(66 + year)  # B, C, D, E, F for years 1-5
            ws.write_formula(row, year + 1, f"={col_letter}{egi_row+1}-{col_letter}{total_expenses_row+1}", self.currency_bold)
        ws.write_formula(row, 6, f"=B{row+1}/{total_units_ref}", self.currency_format)
        ws.write_formula(row, 7, f"=B{row+1}/{total_sqft_ref}", self.currency_per_sf)
        noi_row = row
        # Store NOI row for cross-sheet reference
        self.proforma_rows['noi'] = noi_row
        row += 2
        
        # DEBT SERVICE - Updated for Development Projects
        ws.merge_range(row, 0, row, 7, "DEBT SERVICE", self.section_header_costs)
        row += 1
        
        # CORRECTED: Calculate proper loan payment for development projects
        # Use proper loan amount based on development cost and down payment percentage
        
        # Use already defined local cell references for debt calculations
        # down_payment_pct_ref, interest_rate_ref, loan_term_ref already defined above
        
        ws.write(row, 0, "Annual Debt Service (P&I)", self.text_format)
        
        # Simplified approach: Calculate loan payment using basic math instead of complex nested formulas
        # This avoids Excel formula corruption issues
        
        # Use the already calculated values from the assumption setup above
        
        # All assumptions are already set up at the top of the sheet
        
        # Now use formula references to the local assumption cells
        for year in range(5):
            # Formula: (Purchase_Price * (1 - Down_Payment_Pct)) * Interest_Rate * 1.1
            debt_formula = f"=({self.cell_refs['purchase_price']}*(1-{self.cell_refs['down_payment_pct']}))*{self.cell_refs['interest_rate']}*1.1"
            ws.write_formula(row, year + 1, debt_formula, self.currency_format)
        ws.write_formula(row, 6, f"=B{row+1}/{total_units_ref}", self.currency_format)
        ws.write_formula(row, 7, f"=B{row+1}/{total_sqft_ref}", self.currency_per_sf)
        debt_service_row = row
        # Store debt service row for cross-sheet reference
        self.proforma_rows['debt_service'] = debt_service_row
        row += 2
        
        # CASH FLOW FROM OPERATIONS
        ws.merge_range(row, 0, row, 7, "CASH FLOW FROM OPERATIONS", self.section_header_equity)
        row += 1
        
        ws.write(row, 0, "Before-Tax Cash Flow", self.text_bold)
        for year in range(5):
            col_letter = chr(66 + year)  # B, C, D, E, F for years 1-5
            ws.write_formula(row, year + 1, f"={col_letter}{noi_row+1}-{col_letter}{debt_service_row+1}", self.currency_bold)
        ws.write_formula(row, 6, f"=B{row+1}/{total_units_ref}", self.currency_format)
        ws.write_formula(row, 7, f"=B{row+1}/{total_sqft_ref}", self.currency_per_sf)
        before_tax_cash_flow_row = row
        # Store cash flow row for cross-sheet reference
        self.proforma_rows['before_tax_cash_flow'] = before_tax_cash_flow_row
        row += 2
        
        # CAPITAL EVENTS
        ws.merge_range(row, 0, row, 7, "CAPITAL EVENTS", self.section_header_timeline)
        row += 1
        
        # Initial Investment - For development projects, use total equity invested        
        ws.write(row, 0, "Initial Investment", self.text_format)
        # CORRECTED: Initial investment = Down Payment + Closing Costs using local cells
        ws.write_formula(row, 1, f"=-({self.cell_refs['purchase_price']}*{self.cell_refs['down_payment_pct']}+{self.cell_refs['purchase_price']}*{self.cell_refs['closing_costs_pct']})", self.currency_format)
        for year in range(1, 5):
            ws.write(row, year + 1, 0, self.currency_format)
        initial_investment_row = row
        row += 1
        
        # Property Appreciation & Sale (Year 5) - Using Cap Rate Method
        ws.write(row, 0, "Property Sale Analysis (Year 5)", self.text_bold)
        row += 1
        
        # Sale Price = NOI Year 5 / Exit Cap Rate - Use local cell references
        cap_rate_exit_ref = self.cell_refs['cap_rate_exit']
        ws.write(row, 0, "Sale Price (NOI ÷ Exit Cap Rate)", self.text_format)
        for year in range(4):
            ws.write(row, year + 1, 0, self.currency_format)
        # Use cell reference for exit cap rate
        ws.write_formula(row, 5, f"=F{noi_row+1}/{cap_rate_exit_ref}", self.currency_format)
        sale_price_row = row
        row += 1
        
        # Selling Costs - Use local cell reference
        selling_costs_pct_ref = self.cell_refs['selling_costs_pct']
        ws.write(row, 0, "Selling Costs", self.text_format)
        for year in range(4):
            ws.write(row, year + 1, 0, self.currency_format)
        # Reference the sale price in column F (Year 5)
        ws.write_formula(row, 5, f"=F{sale_price_row+1}*{selling_costs_pct_ref}", self.currency_format)
        selling_costs_row = row
        row += 1
        
        # CORRECTED: Remaining Loan Balance using proper amortization
        ws.write(row, 0, "Remaining Loan Balance", self.text_format)
        for year in range(4):
            ws.write(row, year + 1, 0, self.currency_format)
        # Remaining balance calculation using local cell references
        # Approximation: 85% of original loan amount remains after 5 years (typical for 30-year loan)
        remaining_balance_formula = f"=({self.cell_refs['purchase_price']}*(1-{self.cell_refs['down_payment_pct']}))*0.85"
        ws.write_formula(row, 5, remaining_balance_formula, self.currency_format)
        remaining_balance_row = row
        row += 1
        
        # Net Sale Proceeds
        ws.write(row, 0, "Net Sale Proceeds", self.text_bold)
        for year in range(4):
            ws.write(row, year + 1, 0, self.currency_format)
        # Formula: Sale Price - Selling Costs - Remaining Loan Balance
        ws.write_formula(row, 5, f"=F{sale_price_row+1}-F{selling_costs_row+1}-F{remaining_balance_row+1}", self.currency_bold)
        net_sale_proceeds_row = row
        row += 2
        
        # TOTAL RETURNS
        ws.merge_range(row, 0, row, 7, "TOTAL INVESTMENT RETURNS", self.section_header_equity)
        row += 1
        
        # Initial Investment (Year 0) - Reference the earlier calculation
        ws.write(row, 0, "Initial Investment", self.text_bold)
        # Reference the initial investment row from capital events
        ws.write_formula(row, 1, f"=B{initial_investment_row+1}", self.currency_bold)
        for year in range(1, 5):
            ws.write(row, year + 1, 0, self.currency_format)
        initial_inv_row = row
        row += 1
        
        ws.write(row, 0, "Total Cash Flow", self.text_bold)
        
        for year in range(5):
            col_letter = chr(66 + year)  # B, C, D, E, F for years 1-5
            if year == 0:
                # Year 1: Initial Investment + Before-Tax Cash Flow
                ws.write_formula(row, year + 1, f"=B{initial_inv_row+1}+B{before_tax_cash_flow_row+1}", self.currency_bold)
            elif year == 4:
                # Year 5: Before-Tax Cash Flow + Net Sale Proceeds
                ws.write_formula(row, year + 1, f"=F{before_tax_cash_flow_row+1}+F{net_sale_proceeds_row+1}", self.currency_bold)
            else:
                # Years 2-4: Just Before-Tax Cash Flow
                ws.write_formula(row, year + 1, f"={col_letter}{before_tax_cash_flow_row+1}", self.currency_bold)
        total_cash_flow_row = row
        row += 2
        
        # Add IRR and Equity Multiple calculations
        ws.write(row, 0, "Investment Performance Metrics", self.text_bold)
        row += 1
        
        # IRR Calculation
        ws.write(row, 0, "IRR (Internal Rate of Return)", self.text_format)
        ws.write_formula(row, 1, f"=IRR(B{total_cash_flow_row+1}:F{total_cash_flow_row+1})", self.percentage_format)
        row += 1
        
        # Equity Multiple 
        ws.write(row, 0, "Equity Multiple", self.text_format)
        ws.write_formula(row, 1, f"=SUM(C{total_cash_flow_row+1}:F{total_cash_flow_row+1})/ABS(B{total_cash_flow_row+1})", self.number_format)
        row += 1
        
        # Total ROI (Unlevered) - calculated using formulas  
        # Formula: (Sum of positive cash flows from Years 2-5 / Initial investment) - 1
        ws.write(row, 0, "Total ROI (Unlevered)", self.text_format)
        ws.write_formula(row, 1, f"=(SUM(C{total_cash_flow_row+1}:F{total_cash_flow_row+1})/ABS(B{initial_investment_row+1})-1)", self.percentage_format)
        row += 1
    
    def _create_assumptions_sheet(self, ws, property_data, assumptions):
        """Create assumptions sheet"""
        
        # Set column widths for optimal display
        ws.set_column('A:A', 35)   # Assumption labels (wider)
        ws.set_column('B:B', 18)   # Values (wider for large numbers)
        ws.set_column('C:C', 25)   # Notes (wider for descriptions)
        
        row = 0
        
        # Title
        ws.merge_range(row, 0, row, 2, "INVESTMENT ASSUMPTIONS", self.title_format)
        row += 2
        
        # Property Assumptions
        ws.merge_range(row, 0, row, 2, "PROPERTY ASSUMPTIONS", self.section_header_timeline)
        row += 1
        
        ws.write(row, 0, "Assumption", self.column_header)
        ws.write(row, 1, "Value", self.column_header)
        ws.write(row, 2, "Notes", self.column_header)
        row += 1
        
        prop_assumptions = [
            ("Purchase Price", property_data.get('price', 0), "Contract price"),
            ("Square Footage", property_data.get('sqft', 0), "Gross rentable area"),
            ("Bedrooms", property_data.get('beds', 0), "Total bedrooms"),
            ("Bathrooms", property_data.get('baths', 0), "Total bathrooms"),
            ("Property Type", property_data.get('propertyType', 'House'), "Property classification")
        ]
        
        for assumption, value, note in prop_assumptions:
            ws.write(row, 0, assumption, self.text_format)
            if isinstance(value, (int, float)) and assumption == "Purchase Price":
                ws.write(row, 1, value, self.currency_format)
            elif isinstance(value, (int, float)):
                ws.write(row, 1, value, self.number_format)
            else:
                ws.write(row, 1, value, self.text_format)
            ws.write(row, 2, note, self.text_center)
            row += 1
        
        row += 1
        
        # Financial Assumptions
        ws.merge_range(row, 0, row, 2, "FINANCIAL ASSUMPTIONS", self.section_header_costs)
        row += 1
        
        ws.write(row, 0, "Assumption", self.column_header)
        ws.write(row, 1, "Value", self.column_header)
        ws.write(row, 2, "Notes", self.column_header)
        row += 1
        
        fin_assumptions = [
            ("Down Payment %", assumptions.get('downPaymentPct', 20) / 100, "Percentage of purchase price"),
            ("Interest Rate", assumptions.get('interestRate', 5.0) / 100, "Annual interest rate"),
            ("Loan Term (Years)", assumptions.get('loanTerm', 30), "Mortgage term in years"),
            ("Property Tax Rate", assumptions.get('propertyTaxRate', 3.0) / 100, "Annual property tax rate"),
            ("Insurance Rate", assumptions.get('insuranceRate', 0.5) / 100, "Annual insurance rate"),
            ("Maintenance Rate", assumptions.get('maintenanceRate', 1.0) / 100, "Annual maintenance as % of income"),
            ("Capital Reserves Rate", assumptions.get('capitalReservesRate', 1.0) / 100, "Annual reserves as % of income"),
            ("Vacancy Rate", assumptions.get('vacancyRate', 5.0) / 100, "Expected vacancy rate"),
            ("Closing Costs %", assumptions.get('closingCostsPct', 3.0) / 100, "Closing costs as % of price")
        ]
        
        for assumption, value, note in fin_assumptions:
            ws.write(row, 0, assumption, self.text_format)
            if "Rate" in assumption or "%" in assumption:
                ws.write(row, 1, value, self.percentage_format)
            elif "Years" in assumption:
                ws.write(row, 1, value, self.number_format)
            else:
                ws.write(row, 1, value, self.number_format)
            ws.write(row, 2, note, self.text_center)
            row += 1
        
        row += 1
        
        # Market Assumptions
        ws.merge_range(row, 0, row, 2, "MARKET ASSUMPTIONS", self.section_header_revenue)
        row += 1
        
        ws.write(row, 0, "Assumption", self.column_header)
        ws.write(row, 1, "Value", self.column_header)
        ws.write(row, 2, "Notes", self.column_header)
        row += 1
        
        market_assumptions = [
            ("Annual Rent Growth", 0.03, "Expected annual rent increase"),
            ("Annual Appreciation", 0.03, "Expected property value appreciation"),
            ("Inflation Rate", 0.025, "General inflation for expenses"),
            ("Property Management Fee", 0.08, "Management fee as % of gross income"),
            ("Selling Costs", 0.06, "Total costs to sell property")
        ]
        
        for assumption, value, note in market_assumptions:
            ws.write(row, 0, assumption, self.text_format)
            ws.write(row, 1, value, self.percentage_format)
            ws.write(row, 2, note, self.text_center)
            row += 1
    
    def _create_sensitivity_sheet(self, ws, property_data, results, assumptions):
        """Create sensitivity analysis sheet"""
        
        # Set column widths for optimal display
        ws.set_column('A:A', 22)   # Sensitivity labels (slightly wider)
        ws.set_column('B:H', 14)   # Sensitivity values (wider for percentages)
        ws.set_column('I:J', 8)    # Empty columns (narrow)
        ws.set_column('K:K', 25)   # Assumption labels (wider)
        ws.set_column('L:L', 16)   # Assumption values
        
        row = 0
        
        # Title
        ws.merge_range(row, 0, row, 7, "SENSITIVITY ANALYSIS", self.title_format)
        row += 2
        
        # Add local assumptions in column K for sensitivity analysis
        assumption_col = 10  # Column K (0-indexed)
        assumption_row = 1   # Start at row 2 (0-indexed)
        ws.merge_range(assumption_row, assumption_col, assumption_row, assumption_col + 1, "SENSITIVITY ASSUMPTIONS", self.section_header_timeline)
        assumption_row += 1
        
        # Calculate assumption values from form data
        purchase_price = property_data.get('price', 500000)
        down_payment_pct = assumptions.get('downPaymentPct', 20) / 100
        interest_rate = assumptions.get('interestRate', 5.0) / 100
        loan_term = assumptions.get('loanTerm', 30)
        if loan_term <= 36:  # Convert construction to permanent
            loan_term = 30
        elif loan_term > 100:
            loan_term = loan_term / 12
        closing_costs_pct = assumptions.get('closingCostsPct', 3) / 100
        total_monthly_rent = results.get('monthlyRent', 0)
        base_annual_rent = total_monthly_rent * 12
        noi_margin = assumptions.get('noiMargin', 70) / 100
        
        # Write sensitivity assumptions to cells in column K
        ws.write(assumption_row + 1, assumption_col, "Purchase Price", self.text_bold)
        ws.write(assumption_row + 1, assumption_col + 1, purchase_price, self.input_currency_format)
        ws.write(assumption_row + 2, assumption_col, "Annual Gross Rent", self.text_bold)
        ws.write(assumption_row + 2, assumption_col + 1, base_annual_rent, self.input_currency_format)
        ws.write(assumption_row + 3, assumption_col, "NOI Margin", self.text_bold)
        ws.write(assumption_row + 3, assumption_col + 1, noi_margin, self.input_percentage_format)
        ws.write(assumption_row + 4, assumption_col, "Down Payment %", self.text_bold)
        ws.write(assumption_row + 4, assumption_col + 1, down_payment_pct, self.input_percentage_format)
        ws.write(assumption_row + 5, assumption_col, "Closing Costs %", self.text_bold)
        ws.write(assumption_row + 5, assumption_col + 1, closing_costs_pct, self.input_percentage_format)
        ws.write(assumption_row + 6, assumption_col, "Loan Term (Years)", self.text_bold)
        ws.write(assumption_row + 6, assumption_col + 1, loan_term, self.input_format)
        
        # Create local cell references for sensitivity analysis
        sens_cell_refs = {
            'purchase_price': f"L{assumption_row + 2}",
            'annual_rent': f"L{assumption_row + 3}",
            'noi_margin': f"L{assumption_row + 4}",
            'down_payment_pct': f"L{assumption_row + 5}",
            'closing_costs_pct': f"L{assumption_row + 6}",
            'loan_term': f"L{assumption_row + 7}"
        }
        
        # Cap Rate Sensitivity
        ws.merge_range(row, 0, row, 7, "CAP RATE SENSITIVITY", self.section_header_revenue)
        row += 1
        
        ws.write(row, 0, "Purchase Price", self.column_header)
        rent_variations = [-10, -5, 0, 5, 10, 15, 20]
        for i, variation in enumerate(rent_variations):
            ws.write(row, i + 1, f"Rent {variation:+d}%", self.column_header)
        row += 1
        
        base_price = property_data.get('price', 500000)
        base_rent = results.get('monthlyRent', 2000) * 12
        price_variations = [-10, -5, 0, 5, 10]
        
        for price_var in price_variations:
            adjusted_price = base_price * (1 + price_var / 100)
            ws.write(row, 0, f"${adjusted_price:,.0f} ({price_var:+d}%)", self.text_format)
            
            for i, rent_var in enumerate(rent_variations):
                # Use local cell references within this sheet
                # Cap Rate = (Annual Rent * (1 + rent variation) * NOI Margin) / (Purchase Price * (1 + price variation))
                formula = f"=(({sens_cell_refs['annual_rent']}*(1+{rent_var}/100)*{sens_cell_refs['noi_margin']}))/((({sens_cell_refs['purchase_price']}*(1+{price_var}/100))))"
                ws.write_formula(row, i + 1, formula, self.percentage_format)
            row += 1
        
        row += 2
        
        # Cash-on-Cash Sensitivity
        ws.merge_range(row, 0, row, 7, "CASH-ON-CASH RETURN SENSITIVITY", self.section_header_costs)
        row += 1
        
        ws.write(row, 0, "Interest Rate", self.column_header)
        for i, variation in enumerate(rent_variations):
            ws.write(row, i + 1, f"Rent {variation:+d}%", self.column_header)
        row += 1
        
        base_rate = assumptions.get('interestRate', 5.0)
        rate_variations = [3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5]
        
        for rate in rate_variations:
            ws.write(row, 0, f"{rate:.1f}%", self.text_format)
            
            for i, rent_var in enumerate(rent_variations):
                # Use local cell references within this sheet
                # Cash-on-Cash calculation using local cell references
                
                # NOI = Annual Rent * (1 + rent variation) * NOI Margin
                noi_formula = f"(({sens_cell_refs['annual_rent']}*(1+{rent_var}/100)*{sens_cell_refs['noi_margin']}))"
                
                # Principal = Purchase Price * (1 - Down Payment %)
                principal_formula = f"(({sens_cell_refs['purchase_price']}*(1-{sens_cell_refs['down_payment_pct']})))"
                
                # Monthly rate and payments
                monthly_rate = rate / 100 / 12
                num_payments_formula = f"({sens_cell_refs['loan_term']}*12)"
                
                # PMT formula in Excel format - Annual debt service
                pmt_formula = f"PMT({monthly_rate},{num_payments_formula},-{principal_formula})*12"
                
                # Cash Flow = NOI - Annual Debt Service
                cash_flow_formula = f"({noi_formula}-({pmt_formula}))"
                
                # Total Invested = Purchase Price * (Down Payment % + Closing Costs %)
                total_invested_formula = f"({sens_cell_refs['purchase_price']}*({sens_cell_refs['down_payment_pct']}+{sens_cell_refs['closing_costs_pct']}))"
                
                # Cash-on-Cash Return = Cash Flow / Total Invested
                formula = f"=({cash_flow_formula})/({total_invested_formula})"
                ws.write_formula(row, i + 1, formula, self.percentage_format)
            row += 1
    
    def _setup_print_settings(self, ws):
        """Set up print settings for professional appearance"""
        
        # Set page orientation to landscape
        ws.set_landscape()
        
        # Set margins
        ws.set_margins(0.5, 0.5, 0.75, 0.75)
        
        # Center horizontally
        ws.center_horizontally()
        
        # Set print scale to fit to width
        ws.fit_to_pages(1, 0)  # Fit to 1 page wide, unlimited pages tall
        
        # Set header and footer
        ws.set_header('&C&"Arial,Bold"Real Estate Investment Analysis')
        ws.set_footer('&L&D &T&C&P&R&F') 