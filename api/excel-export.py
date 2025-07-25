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

# FORCE REAL GENERATOR - NO FALLBACK
print("🔧 FORCING import of real excel_generator...")

# Import pandas FIRST - fail hard if not available
print("🔧 Importing pandas...")
import pandas as pd
print("✅ Pandas imported successfully")

# Import the real generator with proper path handling
print("🔧 Importing RealEstateExcelGenerator...")

# Add current directory to Python path for Vercel
import sys
import os
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
    print(f"📍 Added to Python path: {current_dir}")

# Try multiple import strategies
try:
    from excel_generator import RealEstateExcelGenerator
    print("✅ Successfully imported RealEstateExcelGenerator (direct import)")
except ImportError:
    try:
        # Try with explicit path
        sys.path.insert(0, '/var/task/api')
        from excel_generator import RealEstateExcelGenerator
        print("✅ Successfully imported RealEstateExcelGenerator (with /var/task/api path)")
    except ImportError:
        # Try importing from current working directory
        import importlib.util
        excel_gen_path = os.path.join(current_dir, 'excel_generator.py')
        spec = importlib.util.spec_from_file_location("excel_generator", excel_gen_path)
        excel_generator_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(excel_generator_module)
        RealEstateExcelGenerator = excel_generator_module.RealEstateExcelGenerator
        print("✅ Successfully imported RealEstateExcelGenerator (via importlib)")
    
print("✅ RealEstateExcelGenerator import successful")

# Test if we can create an instance
print("🔧 Testing generator instantiation...")
test_generator = RealEstateExcelGenerator()
print("✅ Successfully created RealEstateExcelGenerator instance")

print("🎯 REAL GENERATOR IS ACTIVE - NO FALLBACK!")

from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            print("🔄 POST request received")
            
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
            
            # Generate Excel file using the REAL generator
            print("🏗️ Creating REAL Excel generator...")
            excel_generator = RealEstateExcelGenerator()
            
            print("📋 Calling create_pro_forma on REAL generator...")
            print(f"🔍 Debugging data being passed:")
            print(f"   Property data keys: {list(property_data.keys())}")
            print(f"   Analysis results keys: {list(results.keys())}")
            print(f"   Assumptions keys: {list(assumptions.keys())}")
            print(f"   Sample property data: {dict(list(property_data.items())[:3])}")
            print(f"   Sample analysis results: {dict(list(results.items())[:3])}")
            print(f"   Sample assumptions: {dict(list(assumptions.items())[:3])}")
            
            excel_data = excel_generator.create_pro_forma(
                property_data,
                results,
                assumptions,
                project_name
            )
            
            if excel_data is None:
                print("❌ Excel generation returned None")
                self.send_error(500, "Failed to generate Excel file")
                return
            
            print(f"✅ Excel generated successfully. Size: {len(excel_data)} bytes")
            
            # Generate filename with timestamp
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
            self.end_headers()
            
            self.wfile.write(excel_data)
            print("✅ Response sent successfully")
            
        except Exception as e:
            print(f"❌ Error in handler: {e}")
            print(f"❌ Traceback: {traceback.format_exc()}")
            self.send_error(500, f"Internal server error: {str(e)}")

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Excel Export API is running with REAL generator') 