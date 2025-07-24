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
        
        # Generate each worksheet - Create Pro Forma first so row references are available for Executive Summary
        self._create_proforma_sheet(proforma_ws, property_data, analysis_results, assumptions, project_name)
        self._create_summary_sheet(summary_ws, property_data, analysis_results, assumptions, project_name)
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
        
        # Title formats
        self.title_format = workbook.add_format({
            'font_size': 18,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': self.colors['header_bg'],
            'border': 1,
            'border_color': self.colors['border']
        })
        
        self.subtitle_format = workbook.add_format({
            'font_size': 14,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': self.colors['header_bg'],
            'border': 1,
            'border_color': self.colors['border']
        })
        
        # Header formats
        self.header_format = workbook.add_format({
            'font_size': 12,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': self.colors['header_bg'],
            'border': 1,
            'border_color': self.colors['border'],
            'text_wrap': True
        })
        
        self.section_header_format = workbook.add_format({
            'font_size': 12,
            'bold': True,
            'align': 'left',
            'valign': 'vcenter',
            'bg_color': self.colors['timeline'],
            'font_color': self.colors['white'],
            'border': 1,
            'border_color': self.colors['border']
        })
        
        # Data formats
        self.currency_format = workbook.add_format({
            'num_format': '$#,##0',
            'align': 'right',
            'valign': 'vcenter',
            'border': 1,
            'border_color': self.colors['border']
        })
        
        self.currency_decimal_format = workbook.add_format({
            'num_format': '$#,##0.00',
            'align': 'right',
            'valign': 'vcenter',
            'border': 1,
            'border_color': self.colors['border']
        })
        
        self.percentage_format = workbook.add_format({
            'num_format': '0.0%',
            'align': 'right',
            'valign': 'vcenter',
            'border': 1,
            'border_color': self.colors['border']
        })
        
        self.number_format = workbook.add_format({
            'num_format': '#,##0',
            'align': 'right',
            'valign': 'vcenter',
            'border': 1,
            'border_color': self.colors['border']
        })
        
        self.text_format = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            'border': 1,
            'border_color': self.colors['border']
        })
        
        self.text_center_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': self.colors['border']
        })
        
        # Category-specific formats
        self.revenue_format = workbook.add_format({
            'num_format': '$#,##0',
            'align': 'right',
            'valign': 'vcenter',
            'bg_color': self.colors['revenue'],
            'font_color': 'white',
            'border': 1,
            'border_color': self.colors['border']
        })
        
        self.costs_format = workbook.add_format({
            'num_format': '$#,##0',
            'align': 'right',
            'valign': 'vcenter',
            'bg_color': self.colors['costs'],
            'font_color': 'white',
            'border': 1,
            'border_color': self.colors['border']
        })
        
        self.equity_format = workbook.add_format({
            'num_format': '$#,##0',
            'align': 'right',
            'valign': 'vcenter',
            'bg_color': self.colors['equity'],
            'border': 1,
            'border_color': self.colors['border']
        })

    def _create_summary_sheet(self, ws, property_data, analysis_results, assumptions, project_name):
        """Create the executive summary worksheet"""
        
        # Set column widths
        ws.set_column('A:A', 3)
        ws.set_column('B:B', 25)
        ws.set_column('C:E', 15)
        ws.set_column('F:F', 3)
        ws.set_column('G:H', 20)
        
        row = 0
        
        # Project title
        project_title = project_name if project_name else f"{property_data.get('address', 'Property')} - Pro Forma Analysis"
        ws.merge_range(f'B{row+1}:H{row+1}', project_title, self.title_format)
        row += 2
        
        # Property overview section
        ws.merge_range(f'B{row+1}:E{row+1}', 'PROPERTY OVERVIEW', self.section_header_format)
        row += 1
        
        property_overview = [
            ('Property Type', property_data.get('property_type', 'N/A')),
            ('Address', property_data.get('address', 'N/A')),
            ('Total Units', property_data.get('units', 0)),
            ('Total Square Feet', f"{property_data.get('square_feet', 0):,}"),
            ('Purchase Price', property_data.get('purchase_price', 0)),
            ('Price per Unit', property_data.get('purchase_price', 0) / max(property_data.get('units', 1), 1)),
            ('Price per SF', property_data.get('purchase_price', 0) / max(property_data.get('square_feet', 1), 1))
        ]
        
        for label, value in property_overview:
            ws.write(f'B{row+1}', label, self.text_format)
            if isinstance(value, (int, float)) and 'Price' in label:
                ws.write(f'C{row+1}', value, self.currency_format)
            elif isinstance(value, (int, float)):
                ws.write(f'C{row+1}', value, self.number_format)
            else:
                ws.write(f'C{row+1}', value, self.text_format)
            row += 1
        
        row += 1
        
        # Investment assumptions panel (F-G columns)
        ws.merge_range(f'G{row+1}:H{row+1}', 'KEY ASSUMPTIONS', self.section_header_format)
        row += 1
        
        key_assumptions = [
            ('Hold Period', f"{assumptions.get('hold_period', 5)} years"),
            ('Purchase Price', assumptions.get('purchase_price', 0)),
            ('Down Payment', assumptions.get('down_payment_percent', 0.25)),
            ('Interest Rate', assumptions.get('interest_rate', 0.055)),
            ('Loan Term', f"{assumptions.get('loan_term_years', 30)} years"),
            ('Cap Rate', assumptions.get('cap_rate', 0.055)),
            ('Rent Growth', assumptions.get('annual_rent_growth', 0.03)),
            ('Expense Growth', assumptions.get('annual_expense_growth', 0.025)),
            ('Exit Cap Rate', assumptions.get('exit_cap_rate', 0.06))
        ]
        
        assumption_start_row = row
        for label, value in key_assumptions:
            ws.write(f'G{row+1}', label, self.text_format)
            if isinstance(value, float) and value < 1 and 'years' not in str(value):
                ws.write(f'H{row+1}', value, self.percentage_format)
            elif isinstance(value, (int, float)) and ('Price' in label or '$' in str(value)):
                ws.write(f'H{row+1}', value, self.currency_format)
            else:
                ws.write(f'H{row+1}', value, self.text_format)
            row += 1
        
        # Reset row for financial summary
        row = assumption_start_row
        
        # Financial summary section (B-E columns)
        ws.merge_range(f'B{row+1}:E{row+1}', 'FINANCIAL SUMMARY', self.section_header_format)
        row += 1
        
        # Get first year NOI and property value from Pro Forma sheet (will be calculated when Pro Forma is created)
        first_year_noi_ref = "'Pro Forma Analysis'!E12"  # Year 1 NOI from Pro Forma
        first_year_property_value_ref = "'Pro Forma Analysis'!E23"  # Year 1 property value
        
        financial_summary = [
            ('Year 1 NOI', f"={first_year_noi_ref}"),
            ('Purchase Price', assumptions.get('purchase_price', 0)),
            ('Total Cash Required', analysis_results.get('total_cash_required', 0)),
            ('Cap Rate on Cost', f"={first_year_noi_ref}/{assumptions.get('purchase_price', 1)}"),
            ('Cash-on-Cash Return', f"={first_year_noi_ref}/{analysis_results.get('total_cash_required', 1)}"),
            ('5-Year IRR', analysis_results.get('irr', 0)),
            ('5-Year Total Return', analysis_results.get('total_return_multiple', 0))
        ]
        
        for label, value in financial_summary:
            ws.write(f'B{row+1}', label, self.text_format)
            if isinstance(value, str) and value.startswith('='):
                # This is a formula
                if 'Rate' in label or 'Return' in label or 'IRR' in label:
                    ws.write_formula(f'C{row+1}', value, self.percentage_format)
                else:
                    ws.write_formula(f'C{row+1}', value, self.currency_format)
            elif isinstance(value, float) and value < 1:
                ws.write(f'C{row+1}', value, self.percentage_format)
            elif isinstance(value, (int, float)):
                ws.write(f'C{row+1}', value, self.currency_format)
            else:
                ws.write(f'C{row+1}', value, self.text_format)
            row += 1

    def _create_proforma_sheet(self, ws, property_data, analysis_results, assumptions, project_name):
        """Create the detailed pro forma analysis worksheet"""
        
        # Set column widths
        ws.set_column('A:A', 3)
        ws.set_column('B:B', 25)
        ws.set_column('C:I', 12)
        ws.set_column('J:J', 3)
        ws.set_column('K:L', 15)
        
        row = 0
        
        # Title
        project_title = project_name if project_name else f"{property_data.get('address', 'Property')} - Pro Forma Analysis"
        ws.merge_range(f'B{row+1}:I{row+1}', project_title, self.title_format)
        row += 2
        
        # Year headers
        ws.write('B3', 'Line Item', self.header_format)
        for year in range(6):  # Years 0-5
            if year == 0:
                ws.write(f'{chr(67+year)}3', 'Year 0', self.header_format)
            else:
                ws.write(f'{chr(67+year)}3', f'Year {year}', self.header_format)
        row = 3
        
        # REVENUE SECTION
        ws.write(f'B{row+1}', 'REVENUE', self.section_header_format)
        row += 1
        
        # Gross Potential Rent
        base_rent = property_data.get('annual_rent', 100000)
        rent_growth = assumptions.get('annual_rent_growth', 0.03)
        
        ws.write(f'B{row+1}', 'Gross Potential Rent', self.text_format)
        ws.write(f'C{row+1}', 0, self.currency_format)  # Year 0
        
        # Set up cell references for assumptions (K-L columns)
        assumption_row = 25  # Starting row for assumptions
        self.cell_refs = {
            'purchase_price': f"L{assumption_row + 2}",
            'down_payment_percent': f"L{assumption_row + 3}",
            'interest_rate': f"L{assumption_row + 4}",
            'loan_term_years': f"L{assumption_row + 5}",
            'annual_rent_growth': f"L{assumption_row + 6}",
            'annual_expense_growth': f"L{assumption_row + 7}",
            'vacancy_rate': f"L{assumption_row + 8}",
            'management_fee_percent': f"L{assumption_row + 9}",
            'cap_rate': f"L{assumption_row + 10}",
            'exit_cap_rate': f"L{assumption_row + 11}"
        }
        
        # Gross rent formulas using cell references
        annual_rent_ref = f"L{assumption_row + 1}"  # Base annual rent
        rent_growth_ref = self.cell_refs['annual_rent_growth']
        
        for year in range(1, 6):
            ws.write_formula(row, year + 2, f"={annual_rent_ref}*POWER(1+{rent_growth_ref},{year})", self.currency_format)
        row += 1
        
        # Vacancy Loss
        ws.write(f'B{row+1}', 'Less: Vacancy Loss', self.text_format)
        ws.write(f'C{row+1}', 0, self.currency_format)  # Year 0
        
        vacancy_rate_ref = self.cell_refs['vacancy_rate']
        for year in range(1, 6):
            gross_rent_cell = f"{chr(67+year)}{row}"  # Previous row (gross rent)
            ws.write_formula(row, year + 2, f"=-{gross_rent_cell}*{vacancy_rate_ref}", self.currency_format)
        row += 1
        
        # Effective Gross Income
        ws.write(f'B{row+1}', 'Effective Gross Income', self.text_format)
        ws.write(f'C{row+1}', 0, self.currency_format)  # Year 0
        
        for year in range(1, 6):
            gross_rent_cell = f"{chr(67+year)}{row-1}"
            vacancy_cell = f"{chr(67+year)}{row}"
            ws.write_formula(row, year + 2, f"={gross_rent_cell}+{vacancy_cell}", self.currency_format)
        row += 2
        
        # OPERATING EXPENSES SECTION
        ws.write(f'B{row+1}', 'OPERATING EXPENSES', self.section_header_format)
        row += 1
        
        # Operating expenses
        base_expenses = analysis_results.get('annual_expenses', 30000)
        expense_growth_ref = self.cell_refs['annual_expense_growth']
        base_expenses_ref = f"L{assumption_row + 12}"  # Base expenses reference
        
        expense_items = [
            'Property Management',
            'Insurance', 
            'Property Taxes',
            'Maintenance & Repairs',
            'Utilities',
            'Other Operating Expenses'
        ]
        
        for expense_item in expense_items:
            ws.write(f'B{row+1}', expense_item, self.text_format)
            ws.write(f'C{row+1}', 0, self.currency_format)  # Year 0
            
            for year in range(1, 6):
                expense_fraction = 1/len(expense_items)  # Equal allocation
                ws.write_formula(row, year + 2, f"={base_expenses_ref}*{expense_fraction}*POWER(1+{expense_growth_ref},{year})", self.currency_format)
            row += 1
        
        # Total Operating Expenses
        ws.write(f'B{row+1}', 'Total Operating Expenses', self.text_format)
        ws.write(f'C{row+1}', 0, self.currency_format)  # Year 0
        
        expense_start_row = row - len(expense_items)
        expense_end_row = row - 1
        
        for year in range(1, 6):
            ws.write_formula(row, year + 2, f"=SUM({chr(67+year)}{expense_start_row+1}:{chr(67+year)}{expense_end_row+1})", self.currency_format)
        row += 1
        
        # Net Operating Income
        ws.write(f'B{row+1}', 'Net Operating Income', self.text_format)
        ws.write(f'C{row+1}', 0, self.currency_format)  # Year 0
        
        egi_row = expense_start_row - 2  # EGI row
        total_expenses_row = row - 1
        
        for year in range(1, 6):
            egi_cell = f"{chr(67+year)}{egi_row+1}"
            expenses_cell = f"{chr(67+year)}{total_expenses_row+1}"
            ws.write_formula(row, year + 2, f"={egi_cell}-{expenses_cell}", self.currency_format)
        
        noi_row = row  # Store for later reference
        row += 2
        
        # DEBT SERVICE
        ws.write(f'B{row+1}', 'DEBT SERVICE', self.section_header_format)
        row += 1
        
        # Calculate loan amount and payment
        purchase_price = assumptions.get('purchase_price', 1000000)
        down_payment_percent = assumptions.get('down_payment_percent', 0.25)
        loan_amount = purchase_price * (1 - down_payment_percent)
        
        purchase_price_ref = self.cell_refs['purchase_price']
        down_payment_ref = self.cell_refs['down_payment_percent']
        interest_rate_ref = self.cell_refs['interest_rate']
        loan_term_ref = self.cell_refs['loan_term_years']
        
        # Annual Debt Service
        ws.write(f'B{row+1}', 'Annual Debt Service', self.text_format)
        ws.write(f'C{row+1}', 0, self.currency_format)  # Year 0
        
        # Use PMT function for debt service calculation
        for year in range(1, 6):
            ws.write_formula(row, year + 2, f"=-PMT({interest_rate_ref}/12,{loan_term_ref}*12,{purchase_price_ref}*(1-{down_payment_ref}))*12", self.currency_format)
        
        debt_service_row = row
        row += 1
        
        # Cash Flow Before Tax
        ws.write(f'B{row+1}', 'Cash Flow Before Tax', self.text_format)
        ws.write(f'C{row+1}', 0, self.currency_format)  # Year 0
        
        for year in range(1, 6):
            noi_cell = f"{chr(67+year)}{noi_row+1}"
            debt_service_cell = f"{chr(67+year)}{debt_service_row+1}"
            ws.write_formula(row, year + 2, f"={noi_cell}-{debt_service_cell}", self.currency_format)
        
        cash_flow_row = row
        row += 2
        
        # PROPERTY VALUE & SALE
        ws.write(f'B{row+1}', 'PROPERTY VALUE & SALE', self.section_header_format)
        row += 1
        
        # Property Value (based on NOI and cap rate)
        ws.write(f'B{row+1}', 'Property Value', self.text_format)
        
        cap_rate_ref = self.cell_refs['cap_rate']
        exit_cap_rate_ref = self.cell_refs['exit_cap_rate']
        
        # Year 0 = purchase price
        ws.write_formula(f'C{row+1}', f"={purchase_price_ref}", self.currency_format)
        
        # Years 1-4 use current cap rate, Year 5 uses exit cap rate
        for year in range(1, 5):
            noi_cell = f"{chr(67+year)}{noi_row+1}"
            ws.write_formula(row, year + 2, f"={noi_cell}/{cap_rate_ref}", self.currency_format)
        
        # Year 5 uses exit cap rate
        noi_cell = f"H{noi_row+1}"  # Year 5 NOI
        ws.write_formula(row, 7, f"={noi_cell}/{exit_cap_rate_ref}", self.currency_format)
        
        property_value_row = row
        row += 2
        
        # ASSUMPTIONS PANEL (K-L columns)
        assumption_row = 25
        ws.merge_range(f'K{assumption_row}:L{assumption_row}', 'KEY ASSUMPTIONS', self.section_header_format)
        
        # Create assumption inputs
        assumptions_data = [
            ('Annual Rent (Base)', base_rent),
            ('Purchase Price', assumptions.get('purchase_price', 1000000)),
            ('Down Payment %', assumptions.get('down_payment_percent', 0.25)),
            ('Interest Rate', assumptions.get('interest_rate', 0.055)),
            ('Loan Term (Years)', assumptions.get('loan_term_years', 30)),
            ('Annual Rent Growth', assumptions.get('annual_rent_growth', 0.03)),
            ('Annual Expense Growth', assumptions.get('annual_expense_growth', 0.025)),
            ('Vacancy Rate', assumptions.get('vacancy_rate', 0.05)),
            ('Management Fee %', assumptions.get('management_fee_percent', 0.06)),
            ('Cap Rate', assumptions.get('cap_rate', 0.055)),
            ('Exit Cap Rate', assumptions.get('exit_cap_rate', 0.06)),
            ('Base Operating Expenses', base_expenses)
        ]
        
        for i, (label, value) in enumerate(assumptions_data):
            ws.write(f'K{assumption_row + i + 1}', label, self.text_format)
            if isinstance(value, float) and value < 1 and 'Years' not in label:
                ws.write(f'L{assumption_row + i + 1}', value, self.percentage_format)
            else:
                ws.write(f'L{assumption_row + i + 1}', value, self.currency_format)

    def _create_assumptions_sheet(self, ws, property_data, assumptions):
        """Create the assumptions worksheet with detailed inputs"""
        
        # Set column widths
        ws.set_column('A:A', 3)
        ws.set_column('B:B', 30)
        ws.set_column('C:C', 15)
        ws.set_column('D:D', 40)
        
        row = 0
        
        # Title
        ws.merge_range('B1:D1', 'INVESTMENT ASSUMPTIONS', self.title_format)
        row += 2
        
        # Property assumptions
        ws.write('B3', 'PROPERTY INFORMATION', self.section_header_format)
        ws.write('C3', 'Value', self.header_format)
        ws.write('D3', 'Notes', self.header_format)
        row = 3
        
        property_assumptions = [
            ('Property Type', property_data.get('property_type', 'N/A'), 'Type of real estate investment'),
            ('Address', property_data.get('address', 'N/A'), 'Property location'),
            ('Total Units', property_data.get('units', 0), 'Number of rental units'),
            ('Square Feet', property_data.get('square_feet', 0), 'Total rentable square footage'),
            ('Year Built', property_data.get('year_built', 'N/A'), 'Construction year'),
            ('Purchase Price', assumptions.get('purchase_price', 0), 'Total acquisition cost'),
            ('Annual Rent', property_data.get('annual_rent', 0), 'Current gross rental income')
        ]
        
        for label, value, note in property_assumptions:
            ws.write(f'B{row+1}', label, self.text_format)
            if isinstance(value, (int, float)) and 'Price' in label or 'Rent' in label:
                ws.write(f'C{row+1}', value, self.currency_format)
            elif isinstance(value, (int, float)):
                ws.write(f'C{row+1}', value, self.number_format)
            else:
                ws.write(f'C{row+1}', value, self.text_format)
            ws.write(f'D{row+1}', note, self.text_format)
            row += 1
        
        row += 1
        
        # Financial assumptions
        ws.write(f'B{row+1}', 'FINANCIAL ASSUMPTIONS', self.section_header_format)
        ws.write(f'C{row+1}', 'Value', self.header_format)
        ws.write(f'D{row+1}', 'Notes', self.header_format)
        row += 1
        
        financial_assumptions = [
            ('Hold Period', f"{assumptions.get('hold_period', 5)} years", 'Investment holding period'),
            ('Down Payment %', assumptions.get('down_payment_percent', 0.25), 'Percentage of purchase price as down payment'),
            ('Interest Rate', assumptions.get('interest_rate', 0.055), 'Annual interest rate on loan'),
            ('Loan Term', f"{assumptions.get('loan_term_years', 30)} years", 'Loan amortization period'),
            ('Cap Rate', assumptions.get('cap_rate', 0.055), 'Capitalization rate for valuation'),
            ('Exit Cap Rate', assumptions.get('exit_cap_rate', 0.06), 'Cap rate assumed at sale'),
            ('Annual Rent Growth', assumptions.get('annual_rent_growth', 0.03), 'Expected annual rent increases'),
            ('Annual Expense Growth', assumptions.get('annual_expense_growth', 0.025), 'Expected annual expense increases'),
            ('Vacancy Rate', assumptions.get('vacancy_rate', 0.05), 'Expected vacancy percentage'),
            ('Management Fee', assumptions.get('management_fee_percent', 0.06), 'Property management fee percentage')
        ]
        
        for label, value, note in financial_assumptions:
            ws.write(f'B{row+1}', label, self.text_format)
            if isinstance(value, float) and value < 1:
                ws.write(f'C{row+1}', value, self.percentage_format)
            elif isinstance(value, (int, float)):
                ws.write(f'C{row+1}', value, self.number_format)
            else:
                ws.write(f'C{row+1}', value, self.text_format)
            ws.write(f'D{row+1}', note, self.text_format)
            row += 1

    def _create_sensitivity_sheet(self, ws, property_data, analysis_results, assumptions):
        """Create sensitivity analysis worksheet"""
        
        # Set column widths
        ws.set_column('A:A', 3)
        ws.set_column('B:B', 20)
        ws.set_column('C:H', 12)
        
        row = 0
        
        # Title
        ws.merge_range('B1:H1', 'SENSITIVITY ANALYSIS', self.title_format)
        row += 2
        
        # Cap Rate Sensitivity
        ws.write('B3', 'CAP RATE SENSITIVITY', self.section_header_format)
        row = 3
        
        # Headers
        ws.write('B4', 'Cap Rate', self.header_format)
        ws.write('C4', 'Property Value', self.header_format)
        ws.write('D4', 'IRR', self.header_format)
        ws.write('E4', 'Cash-on-Cash', self.header_format)
        row = 4
        
        # Cap rate scenarios
        base_cap_rate = assumptions.get('cap_rate', 0.055)
        base_noi = analysis_results.get('year_1_noi', 50000)
        
        cap_rate_scenarios = [0.045, 0.05, 0.055, 0.06, 0.065, 0.07]
        
        for cap_rate in cap_rate_scenarios:
            ws.write(f'B{row+1}', cap_rate, self.percentage_format)
            
            # Property value = NOI / Cap Rate
            property_value = base_noi / cap_rate if cap_rate > 0 else 0
            ws.write(f'C{row+1}', property_value, self.currency_format)
            
            # Simplified IRR and Cash-on-Cash calculations
            # These would ideally reference more complex calculations
            irr_estimate = cap_rate + 0.02  # Simplified estimate
            coc_estimate = cap_rate * 1.2   # Simplified estimate
            
            ws.write(f'D{row+1}', irr_estimate, self.percentage_format)
            ws.write(f'E{row+1}', coc_estimate, self.percentage_format)
            row += 1
        
        row += 2
        
        # Rent Growth Sensitivity
        ws.write(f'B{row+1}', 'RENT GROWTH SENSITIVITY', self.section_header_format)
        row += 1
        
        ws.write(f'B{row+1}', 'Rent Growth', self.header_format)
        ws.write(f'C{row+1}', 'Year 5 NOI', self.header_format)
        ws.write(f'D{row+1}', 'IRR Impact', self.header_format)
        row += 1
        
        # Rent growth scenarios
        base_rent = property_data.get('annual_rent', 100000)
        rent_growth_scenarios = [0.02, 0.025, 0.03, 0.035, 0.04, 0.045]
        
        for rent_growth in rent_growth_scenarios:
            ws.write(f'B{row+1}', rent_growth, self.percentage_format)
            
            # Year 5 rent with growth
            year_5_rent = base_rent * ((1 + rent_growth) ** 5)
            year_5_noi = year_5_rent * 0.7  # Assuming 70% margin
            
            ws.write(f'C{row+1}', year_5_noi, self.currency_format)
            
            # IRR impact (simplified)
            irr_impact = base_cap_rate + (rent_growth - 0.03) * 2
            ws.write(f'D{row+1}', irr_impact, self.percentage_format)
            row += 1

    def _setup_print_settings(self, ws):
        """Set up print settings for professional appearance"""
        ws.set_margins(left=0.7, right=0.7, top=0.75, bottom=0.75)
        ws.set_header('&C&14&B' + 'Real Estate Pro Forma Analysis')
        ws.set_footer('&L&D &T&C&P&R&F')
        ws.fit_to_pages(1, 0)  # Fit to 1 page wide, unlimited length
        ws.set_print_scale(85)  # Scale to 85% for better fit 