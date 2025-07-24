import json
import sys
import os
import traceback
from http.server import BaseHTTPRequestHandler

# Test pandas and xlsxwriter imports first
try:
    import pandas as pd
    print("✅ Successfully imported pandas")
except ImportError as e:
    print(f"❌ Failed to import pandas: {e}")

try:
    import xlsxwriter
    print("✅ Successfully imported xlsxwriter")
except ImportError as e:
    print(f"❌ Failed to import xlsxwriter: {e}")

# Import from local excel_generator file
try:
    from excel_generator import RealEstateExcelGenerator
    print("✅ Successfully imported RealEstateExcelGenerator")
except ImportError as e:
    print(f"❌ Failed to import RealEstateExcelGenerator: {e}")
    print(f"❌ Import traceback: {traceback.format_exc()}")
    RealEstateExcelGenerator = None

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