#!/usr/bin/env python3
"""
Real Estate Investment Analyzer - Startup Script

This script starts the Flask API backend and provides instructions for running the React frontend.
"""

import subprocess
import sys
import os
import time
import webbrowser
from threading import Thread

def check_dependencies():
    """Check if required Python packages are installed."""
    required_packages = [
        'flask', 'flask_cors', 'pandas', 'numpy', 'sklearn', 
        'joblib', 'numpy_financial', 'requests', 'fpdf', 'geopy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required Python packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nPlease install them using:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ All Python dependencies are installed")
    return True

def start_flask_api():
    """Start the Flask API server."""
    print("🚀 Starting Flask API server...")
    try:
        subprocess.run([sys.executable, "api.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Flask API server stopped")
    except Exception as e:
        print(f"❌ Error starting Flask API: {e}")

def check_node_installed():
    """Check if Node.js is installed."""
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_react_dependencies():
    """Install React dependencies."""
    print("📦 Installing React dependencies...")
    try:
        subprocess.run(["npm", "install"], check=True)
        print("✅ React dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing React dependencies: {e}")
        return False

def start_react_app():
    """Start the React development server."""
    print("🌐 Starting React development server...")
    try:
        subprocess.run(["npm", "start"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 React development server stopped")
    except Exception as e:
        print(f"❌ Error starting React app: {e}")

def main():
    """Main startup function."""
    print("=" * 60)
    print("🏠 Real Estate Investment Analyzer")
    print("=" * 60)
    
    # Check Python dependencies
    if not check_dependencies():
        return
    
    # Check if Node.js is installed
    if not check_node_installed():
        print("\n❌ Node.js is not installed!")
        print("Please install Node.js from: https://nodejs.org/")
        print("Then run this script again.")
        return
    
    # Install React dependencies if needed
    if not os.path.exists("node_modules"):
        if not install_react_dependencies():
            return
    
    print("\n🎯 Starting the application...")
    print("\nThe application consists of two parts:")
    print("1. Flask API Backend (Port 5000)")
    print("2. React Frontend (Port 3000)")
    
    # Start Flask API in a separate thread
    flask_thread = Thread(target=start_flask_api, daemon=True)
    flask_thread.start()
    
    # Wait a moment for Flask to start
    time.sleep(3)
    
    print("\n✅ Flask API is running on http://localhost:5000")
    print("🌐 React app will start on http://localhost:3000")
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(5)
        try:
            webbrowser.open("http://localhost:3000")
        except:
            pass
    
    browser_thread = Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Start React app
    start_react_app()

if __name__ == "__main__":
    main() 