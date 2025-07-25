import json
import sys
import os
import traceback
from http.server import BaseHTTPRequestHandler

# FORCE NEW DEPLOYMENT: 2025-01-24 19:30

# Test xlsxwriter import
print("🔧 Testing xlsxwriter import...")
try:
    import xlsxwriter
    print("✅ Successfully imported xlsxwriter")
except ImportError as e:
    print(f"❌ Failed to import xlsxwriter: {e}")

# Test basic imports
print("🔧 Testing basic imports...")
try:
    from datetime import datetime, timedelta
    print("✅ Successfully imported datetime")
except ImportError as e:
    print(f"❌ Failed to import datetime: {e}")

try:
    import io
    print("✅ Successfully imported io")
except ImportError as e:
    print(f"❌ Failed to import io: {e}")

# Check current directory and files
print("🔧 Checking file system...")
try:
    current_dir = os.getcwd()
    print(f"📁 Current directory: {current_dir}")
    current_files = os.listdir('.')
    print(f"📁 Files in current directory: {current_files}")
except Exception as e:
    print(f"❌ Error checking files: {e}")

# Try different import paths
print("🔧 Testing Excel generator import...")
RealEstateExcelGenerator = None

# Try direct import
try:
    from excel_generator import RealEstateExcelGenerator
    print("✅ Successfully imported RealEstateExcelGenerator")
except ImportError as e:
    print(f"❌ Failed direct import: {e}")
    print(f"❌ Traceback: {traceback.format_exc()}")
    
    # Try creating a comprehensive Excel generator
    print("🔧 Creating comprehensive Excel generator...")
    try:
        class ComprehensiveExcelGenerator:
            def __init__(self):
                self.colors = {
                    'revenue': '#22C55E',
                    'costs': '#3B82F6', 
                    'equity': '#FCD34D',
                    'timeline': '#6B7280',
                    'header_bg': '#F3F4F6',
                    'white': '#FFFFFF',
                    'border': '#E5E7EB'
                }
            
            def create_pro_forma(self, property_data, results, assumptions, project_name):
                import xlsxwriter
                import io
                
                output = io.BytesIO()
                workbook = xlsxwriter.Workbook(output, {'in_memory': True})
                
                # Create formats
                title_format = workbook.add_format({
                    'font_size': 18, 'bold': True, 'align': 'center',
                    'bg_color': self.colors['header_bg'], 'border': 1
                })
                
                header_format = workbook.add_format({
                    'font_size': 12, 'bold': True, 'align': 'center',
                    'bg_color': self.colors['header_bg'], 'border': 1
                })
                
                section_header_format = workbook.add_format({
                    'font_size': 12, 'bold': True, 'align': 'left',
                    'bg_color': self.colors['timeline'], 'font_color': self.colors['white'], 'border': 1
                })
                
                currency_format = workbook.add_format({
                    'num_format': '$#,##0', 'align': 'right', 'border': 1
                })
                
                percentage_format = workbook.add_format({
                    'num_format': '0.0%', 'align': 'right', 'border': 1
                })
                
                text_format = workbook.add_format({
                    'align': 'left', 'border': 1
                })
                
                # EXECUTIVE SUMMARY
                summary_ws = workbook.add_worksheet('Executive Summary')
                summary_ws.set_column('A:A', 3)
                summary_ws.set_column('B:B', 25)
                summary_ws.set_column('C:E', 15)
                
                summary_ws.merge_range('B1:E1', project_name, title_format)
                
                # Property Overview
                summary_ws.merge_range('B3:E3', 'PROPERTY OVERVIEW', section_header_format)
                
                prop_data = [
                    ('Property Type', property_data.get('propertyType', 'Mixed-Use')),
                    ('Address', property_data.get('address', 'Milwaukee, WI')),
                    ('Total Units', property_data.get('totalUnits', 85)),
                    ('Square Feet', property_data.get('sqft', 75000)),
                    ('Purchase Price', assumptions.get('purchase_price', 25800000))
                ]
                
                row = 4
                for label, value in prop_data:
                    summary_ws.write(f'B{row}', label, text_format)
                    if isinstance(value, (int, float)) and 'Price' in label:
                        summary_ws.write(f'C{row}', value, currency_format)
                    elif isinstance(value, (int, float)):
                        summary_ws.write(f'C{row}', value, currency_format)
                    else:
                        summary_ws.write(f'C{row}', value, text_format)
                    row += 1
                
                # Financial Summary
                summary_ws.merge_range(f'B{row+1}:E{row+1}', 'FINANCIAL SUMMARY', section_header_format)
                row += 2
                
                # Calculate key metrics
                annual_rent = results.get('monthly_rent', 325000) * 12
                purchase_price = assumptions.get('purchase_price', 25800000)
                total_cash = results.get('total_cash_required', 6450000)
                noi = annual_rent * 0.65
                
                # Ensure we have valid numbers
                if annual_rent is None or annual_rent == 0:
                    annual_rent = 3900000  # Default annual rent
                if purchase_price is None or purchase_price == 0:
                    purchase_price = 25800000  # Default purchase price
                if total_cash is None or total_cash == 0:
                    total_cash = 6450000  # Default total cash
                
                financial_data = [
                    ('Year 1 NOI', noi),
                    ('Purchase Price', purchase_price),
                    ('Total Cash Required', total_cash),
                    ('Cap Rate on Cost', noi / purchase_price),
                    ('Cash-on-Cash Return', noi / total_cash),
                    ('5-Year IRR', results.get('irr', 0.22) or 0.22),
                    ('Total Return Multiple', results.get('total_return_multiple', 2.1) or 2.1)
                ]
                
                for label, value in financial_data:
                    summary_ws.write(f'B{row}', label, text_format)
                    if 'Rate' in label or 'Return' in label or 'IRR' in label:
                        summary_ws.write(f'C{row}', value, percentage_format)
                    else:
                        summary_ws.write(f'C{row}', value, currency_format)
                    row += 1
                
                # PRO FORMA ANALYSIS
                proforma_ws = workbook.add_worksheet('Pro Forma Analysis')
                proforma_ws.set_column('A:A', 3)
                proforma_ws.set_column('B:B', 25)
                proforma_ws.set_column('C:H', 12)
                
                proforma_ws.merge_range('B1:H1', f'{project_name} - Pro Forma Analysis', title_format)
                
                # Year headers
                proforma_ws.write('B3', 'Line Item', header_format)
                for year in range(6):
                    col = chr(67 + year)
                    if year == 0:
                        proforma_ws.write(f'{col}3', 'Year 0', header_format)
                    else:
                        proforma_ws.write(f'{col}3', f'Year {year}', header_format)
                
                # Revenue section
                row = 4
                proforma_ws.write(f'B{row}', 'REVENUE', section_header_format)
                row += 1
                
                # Gross Potential Rent
                proforma_ws.write(f'B{row}', 'Gross Potential Rent', text_format)
                proforma_ws.write(f'C{row}', 0, currency_format)  # Year 0
                
                base_rent = annual_rent
                rent_growth = assumptions.get('annual_rent_growth', 0.03) or 0.03
                
                for year in range(1, 6):
                    rent_value = base_rent * ((1 + rent_growth) ** year)
                    col = chr(67 + year)
                    proforma_ws.write(f'{col}{row}', rent_value, currency_format)
                row += 1
                
                # Vacancy Loss
                proforma_ws.write(f'B{row}', 'Less: Vacancy Loss', text_format)
                proforma_ws.write(f'C{row}', 0, currency_format)
                
                vacancy_rate = assumptions.get('vacancy_rate', 0.05) or 0.05
                for year in range(1, 6):
                    rent_value = base_rent * ((1 + rent_growth) ** year)
                    vacancy_loss = -rent_value * vacancy_rate
                    col = chr(67 + year)
                    proforma_ws.write(f'{col}{row}', vacancy_loss, currency_format)
                row += 1
                
                # Net Operating Income
                proforma_ws.write(f'B{row}', 'Net Operating Income', text_format)
                proforma_ws.write(f'C{row}', 0, currency_format)
                
                # Safe calculation with proper fallbacks
                base_expenses = results.get('annual_expenses') or 1000000
                if base_expenses is None or base_expenses == 0:
                    base_expenses = 1000000  # Default expenses
                
                for year in range(1, 6):
                    rent_value = base_rent * ((1 + rent_growth) ** year)
                    vacancy_loss = rent_value * vacancy_rate
                    operating_expenses = base_expenses * ((1 + 0.025) ** year)
                    noi_value = rent_value - vacancy_loss - operating_expenses
                    col = chr(67 + year)
                    proforma_ws.write(f'{col}{row}', noi_value, currency_format)
                row += 2
                
                # ASSUMPTIONS SHEET
                assumptions_ws = workbook.add_worksheet('Assumptions')
                assumptions_ws.set_column('B:B', 30)
                assumptions_ws.set_column('C:C', 15)
                
                assumptions_ws.merge_range('B1:C1', 'INVESTMENT ASSUMPTIONS', title_format)
                
                assumptions_data = [
                    ('Purchase Price', assumptions.get('purchase_price', 25800000)),
                    ('Down Payment %', assumptions.get('down_payment_percent', 0.25)),
                    ('Interest Rate', assumptions.get('interest_rate', 0.055)),
                    ('Loan Term (Years)', assumptions.get('loan_term_years', 30)),
                    ('Annual Rent Growth', assumptions.get('annual_rent_growth', 0.03)),
                    ('Vacancy Rate', assumptions.get('vacancy_rate', 0.05)),
                    ('Cap Rate', assumptions.get('cap_rate', 0.055)),
                    ('Exit Cap Rate', assumptions.get('exit_cap_rate', 0.06))
                ]
                
                row = 3
                for label, value in assumptions_data:
                    assumptions_ws.write(f'B{row}', label, text_format)
                    if isinstance(value, float) and value < 1:
                        assumptions_ws.write(f'C{row}', value, percentage_format)
                    else:
                        assumptions_ws.write(f'C{row}', value, currency_format)
                    row += 1
                
                workbook.close()
                output.seek(0)
                return output.getvalue()
        
        RealEstateExcelGenerator = ComprehensiveExcelGenerator
        print("✅ Created comprehensive Excel generator")
    except Exception as fallback_error:
        print(f"❌ Even comprehensive generator failed: {fallback_error}")

from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            print("🔄 POST request received")
            
            if not RealEstateExcelGenerator:
                print("❌ RealEstateExcelGenerator not available")
                self.send_error(500, "Excel generator not available")
                return
            
            print("✅ RealEstateExcelGenerator is available")
                
            content_length = int(self.headers.get('Content-Length', 0))
            print(f"📥 Content-Length: {content_length}")
            
            post_data = self.rfile.read(content_length)
            print(f"📄 Raw data length: {len(post_data)}")
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                print(f"✅ JSON parsed successfully. Keys: {list(data.keys())}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                self.send_error(400, f"Invalid JSON: {e}")
                return
            
            # Extract data from request
            property_data = data.get('propertyData', {})
            results = data.get('analysisResults', {})
            assumptions = data.get('assumptions', {})
            project_name = data.get('projectName', 'Real Estate Pro Forma')
            
            print(f"📊 Property data keys: {list(property_data.keys())}")
            print(f"📈 Results keys: {list(results.keys())}")
            print(f"⚙️ Assumptions keys: {list(assumptions.keys())}")
            print(f"📝 Project name: {project_name}")
            
            # Generate Excel file
            print("🏗️ Creating Excel generator...")
            excel_generator = RealEstateExcelGenerator()
            
            print("📋 Calling create_pro_forma...")
            excel_data = excel_generator.create_pro_forma(
                property_data,
                results,
                assumptions,
                project_name
            )
            print(f"✅ Excel generated successfully. Size: {len(excel_data)} bytes")
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_project_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_project_name = safe_project_name.replace(' ', '_')
            filename = f"{safe_project_name}_{timestamp}.xlsx"
            print(f"📁 Generated filename: {filename}")
            
            # Send response
            print("📤 Sending response...")
            self.send_response(200)
            self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
            self.send_header('Content-Length', str(len(excel_data)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            self.wfile.write(excel_data)
            print("✅ Response sent successfully")
            
        except Exception as e:
            print(f"❌ Error in do_POST: {e}")
            print(f"❌ Error type: {type(e).__name__}")
            print(f"❌ Traceback: {traceback.format_exc()}")
            
            # Send error response
            try:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                error_response = json.dumps({
                    'error': str(e),
                    'type': type(e).__name__,
                    'traceback': traceback.format_exc()
                })
                self.wfile.write(error_response.encode('utf-8'))
                print("❌ Error response sent")
            except Exception as send_error:
                print(f"❌ Failed to send error response: {send_error}")

    def do_OPTIONS(self):
        print("🔄 OPTIONS request received")
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        print("✅ OPTIONS response sent") 