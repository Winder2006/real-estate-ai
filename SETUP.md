# Quick Setup Guide

## Prerequisites

1. **Python 3.8+** - [Download here](https://www.python.org/downloads/)
2. **Node.js 14+** - [Download here](https://nodejs.org/)

## Installation

### Option 1: Automatic Setup (Recommended)

1. **Run the startup script:**
   ```bash
   python start.py
   ```

This script will:
- Check all dependencies
- Install missing packages
- Start both the Flask API and React frontend
- Open your browser automatically

### Option 2: Manual Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install React dependencies:**
   ```bash
   npm install
   ```

3. **Start the Flask API backend:**
   ```bash
   python api.py
   ```

4. **In a new terminal, start the React frontend:**
   ```bash
   npm start
   ```

## Accessing the Application

- **Frontend**: http://localhost:3000
- **API Backend**: http://localhost:5000

## Features

✅ **Modern React UI** with fintech-inspired blue design  
✅ **Real-time investment analysis** with live calculations  
✅ **Interactive charts** and data visualizations  
✅ **Market comparisons** and property comps  
✅ **Rental analysis** with 5-year projections  
✅ **Investment recommendations** based on key metrics  

## Troubleshooting

### Node.js not found
- Install Node.js from https://nodejs.org/
- Restart your terminal after installation

### Python packages missing
- Run: `pip install -r requirements.txt`

### Port already in use
- Close other applications using ports 3000 or 5000
- Or modify the ports in the respective configuration files

### ML models not loading
- Ensure the `models/` directory contains the trained models
- The app will work with default calculations if models are missing

## Development

- **Frontend code**: `src/` directory
- **Backend API**: `api.py`
- **Python utilities**: `utils/` directory
- **Data files**: `data/` directory

## Support

If you encounter any issues, please check:
1. All prerequisites are installed
2. Dependencies are properly installed
3. Ports 3000 and 5000 are available
4. The `models/` directory contains trained models (optional) 