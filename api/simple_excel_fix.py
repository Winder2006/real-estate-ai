import xlsxwriter
import io
from datetime import datetime

class SimpleExcelGenerator:
    def create_pro_forma(self, property_data, analysis_results, assumptions, project_name):
        """Create a simple but working Excel pro forma with actual calculations"""
        
        # Extract key data
        purchase_price = property_data.get('price', 25800000)
        monthly_rent = analysis_results.get('monthlyRent', 242250)
        annual_rent = monthly_rent * 12
        total_units = property_data.get('totalUnits', 127)
        
        # Create Excel file
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        # Create formats
        currency_format = workbook.add_format({'num_format': '$#,##0', 'border': 1})
        percentage_format = workbook.add_format({'num_format': '0.0%', 'border': 1})
        header_format = workbook.add_format({
            'bold': True, 'align': 'center', 'bg_color': '#F3F4F6', 'border': 1
        })
        title_format = workbook.add_format({
            'font_size': 16, 'bold': True, 'align': 'center', 'bg_color': '#E5E7EB'
        })
        
        # Create Pro Forma sheet
        ws = workbook.add_worksheet('Pro Forma Analysis')
        ws.set_column('A:A', 25)
        ws.set_column('B:F', 12)
        
        # Title
        ws.merge_range('A1:F1', f'5-Year Pro Forma Analysis - {project_name}', title_format)
        
        # Headers
        row = 2
        ws.write(row, 0, 'Line Item', header_format)
        for year in range(5):
            ws.write(row, year + 1, f'Year {year + 1}', header_format)
        row += 1
        
        # GROSS RENTAL INCOME
        ws.write(row, 0, 'GROSS RENTAL INCOME', header_format)
        row += 1
        
        ws.write(row, 0, 'Gross Rental Income')
        for year in range(5):
            year_rent = annual_rent * ((1.03) ** year)  # 3% growth
            ws.write(row, year + 1, year_rent, currency_format)
        row += 2
        
        # OPERATING EXPENSES  
        ws.write(row, 0, 'OPERATING EXPENSES', header_format)
        row += 1
        
        # Calculate expenses as percentage of rental income
        expense_items = [
            ('Property Management', 0.08),
            ('Property Taxes', 0.03),
            ('Insurance', 0.005),
            ('Maintenance & Repairs', 0.02),
            ('Utilities', 0.01),
            ('Other Operating Expenses', 0.01)
        ]
        
        total_expense_rows = []
        for item_name, expense_rate in expense_items:
            ws.write(row, 0, item_name)
            expense_row_values = []
            for year in range(5):
                year_rent = annual_rent * ((1.03) ** year)
                expense_amount = year_rent * expense_rate
                ws.write(row, year + 1, expense_amount, currency_format)
                expense_row_values.append(expense_amount)
            total_expense_rows.append(expense_row_values)
            row += 1
        
        # Total Operating Expenses
        ws.write(row, 0, 'TOTAL OPERATING EXPENSES', header_format)
        for year in range(5):
            total_expenses = sum(expense_row[year] for expense_row in total_expense_rows)
            ws.write(row, year + 1, total_expenses, currency_format)
        row += 2
        
        # NET OPERATING INCOME
        ws.write(row, 0, 'NET OPERATING INCOME', header_format)
        row += 1
        
        ws.write(row, 0, 'Net Operating Income (NOI)')
        noi_values = []
        for year in range(5):
            year_rent = annual_rent * ((1.03) ** year)
            total_expenses = sum(expense_row[year] for expense_row in total_expense_rows)
            noi = year_rent - total_expenses
            ws.write(row, year + 1, noi, currency_format)
            noi_values.append(noi)
        row += 2
        
        # DEBT SERVICE
        ws.write(row, 0, 'DEBT SERVICE', header_format)
        row += 1
        
        # Calculate debt service
        down_payment_pct = assumptions.get('downPaymentPct', 28) / 100
        loan_amount = purchase_price * (1 - down_payment_pct)
        interest_rate = assumptions.get('interestRate', 6.8) / 100
        loan_term = assumptions.get('loanTerm', 30)
        
        # Monthly payment calculation
        monthly_rate = interest_rate / 12
        num_payments = loan_term * 12
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
        annual_debt_service = monthly_payment * 12
        
        ws.write(row, 0, 'Annual Debt Service (P&I)')
        for year in range(5):
            ws.write(row, year + 1, annual_debt_service, currency_format)
        row += 2
        
        # CASH FLOW FROM OPERATIONS
        ws.write(row, 0, 'CASH FLOW FROM OPERATIONS', header_format)
        row += 1
        
        ws.write(row, 0, 'Before-Tax Cash Flow')
        for year in range(5):
            cash_flow = noi_values[year] - annual_debt_service
            ws.write(row, year + 1, cash_flow, currency_format)
        
        workbook.close()
        output.seek(0)
        return output.getvalue() 