import json
import sys
import os
from http.server import BaseHTTPRequestHandler

# Add the project root to Python path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from backend.utils.excel_generator import RealEstateExcelGenerator
except ImportError:
    # Fallback if import fails
    RealEstateExcelGenerator = None

from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            if not RealEstateExcelGenerator:
                self.send_error(500, "Excel generator not available")
                return
                
            # Get the request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Extract property data exactly like backend
            property_data = {
                'address': data.get('address', ''),
                'price': float(data.get('price', 0)),
                'beds': int(data.get('beds', 0)),
                'baths': float(data.get('baths', 0)),
                'sqft': float(data.get('sqft', 0)),
                'neighborhood': data.get('neighborhood', ''),
                'propertyType': data.get('propertyType', 'House'),
                'zipcode': data.get('zipcode', ''),
                'totalUnits': int(data.get('totalUnits', 1))
            }
            
            # Extract analysis results
            results = data.get('results', {})
            
            # Extract assumptions
            assumptions = data.get('assumptions', {})
            
            # Get project name if provided
            project_name = data.get('projectName', f"Investment Analysis - {property_data['address']}")
            
            # Generate Excel file using EXACT same backend code
            excel_generator = RealEstateExcelGenerator()
            excel_data = excel_generator.create_pro_forma(
                property_data, 
                results, 
                assumptions, 
                project_name
            )
            
            # Generate filename
            address_clean = property_data.get('address', 'Property').replace(' ', '_').replace(',', '')
            filename = f"Real_Estate_Pro_Forma_{address_clean}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            # Set headers for file download
            self.send_response(200)
            self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
            self.send_header('Content-Length', str(len(excel_data)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Send the Excel file
            self.wfile.write(excel_data)
            
        except Exception as e:
            # Send error response
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = json.dumps({'error': str(e)})
            self.wfile.write(error_response.encode('utf-8'))
            
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers() 