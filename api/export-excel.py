import json
import sys
import os
from http.server import BaseHTTPRequestHandler

# Add the project root to Python path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from local excel_generator file
try:
    from excel_generator import RealEstateExcelGenerator
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
                
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Extract data from request
            property_data = data.get('propertyData', {})
            results = data.get('analysisResults', {})
            assumptions = data.get('assumptions', {})
            project_name = data.get('projectName', 'Real Estate Pro Forma')
            
            # Generate Excel file
            excel_generator = RealEstateExcelGenerator()
            excel_data = excel_generator.create_pro_forma(
                property_data,
                results,
                assumptions,
                project_name
            )
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_project_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_project_name = safe_project_name.replace(' ', '_')
            filename = f"{safe_project_name}_{timestamp}.xlsx"
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
            self.send_header('Content-Length', str(len(excel_data)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
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
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers() 