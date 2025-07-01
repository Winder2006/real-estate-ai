# Real Estate Investment Analyzer

A modern, fintech-inspired React application for analyzing real estate investment opportunities. This application provides comprehensive investment analysis with a beautiful, intuitive interface.

## Features

### 🏠 Property Information
- Detailed property input forms
- Address, price, bedrooms, bathrooms, square footage
- Neighborhood and property type selection
- Zip code validation

### 📊 Investment Analysis
- Real-time investment metrics calculation
- Cap rate, cash-on-cash return, and ROI analysis
- Monthly cash flow projections
- Break-even analysis
- Investment recommendations

### 💰 Rental Analysis
- Rental income projections
- Market comparison analysis
- 5-year cash flow forecasting
- Rent-to-price ratio analysis
- Market insights and trends

### 🗺️ Market Comps
- Comparable property analysis
- Recent sales data
- Market trends and statistics
- Price per square foot comparisons
- Neighborhood market insights

### 📈 Charts & Reports
- Interactive data visualizations
- Monthly cash flow breakdown
- Investment metrics vs targets
- 5-year projection charts
- Annual cash flow trends

## Technology Stack

- **Frontend**: React 18 with TypeScript
- **Styling**: Tailwind CSS with custom fintech theme
- **Charts**: Recharts for data visualization
- **Icons**: Lucide React for modern iconography
- **Build Tool**: Create React App

## Design Features

### 🎨 Modern Fintech Design
- Clean, professional blue color scheme
- Responsive design for all devices
- Smooth animations and transitions
- Intuitive navigation with tabbed interface
- Card-based layout for easy scanning

### 📱 Responsive Layout
- Mobile-first design approach
- Tablet and desktop optimized
- Touch-friendly interface elements
- Adaptive grid layouts

## Getting Started

### Prerequisites
- Node.js (version 14 or higher)
- npm or yarn package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd real-estate-ai
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```

4. **Open your browser**
   Navigate to `http://localhost:3000`

### Building for Production

```bash
npm run build
```

This creates an optimized production build in the `build` folder.

## Usage

### 1. Property Information
- Enter the property address, price, and basic details
- Adjust investment assumptions using the sliders
- Click "Analyze Investment" to generate results

### 2. Investment Analysis
- View key investment metrics and recommendations
- Compare your property against market benchmarks
- Analyze cash flow and return on investment

### 3. Rental Analysis
- Review rental income projections
- Compare against market averages
- View 5-year cash flow forecasts

### 4. Market Comps
- Analyze comparable properties
- Review recent sales data
- Understand market trends

### 5. Charts & Reports
- Interactive visualizations of all data
- Export-ready charts and graphs
- Comprehensive investment reports

## Key Metrics Explained

### Cap Rate
- **Formula**: (Net Operating Income / Property Price) × 100
- **Target**: 6% or higher for good investments
- **Purpose**: Measures the return on investment excluding financing

### Cash-on-Cash Return
- **Formula**: (Annual Cash Flow / Total Cash Invested) × 100
- **Target**: 8% or higher for good investments
- **Purpose**: Measures the actual cash return on your investment

### Rent-to-Price Ratio
- **Formula**: (Monthly Rent / Property Price) × 100
- **Target**: 0.8% or higher
- **Purpose**: Indicates rental yield potential

### Break-even Rent
- **Formula**: Total monthly expenses
- **Purpose**: Minimum rent needed to cover all costs

## Customization

### Theme Colors
The application uses a custom blue fintech theme. You can modify colors in:
- `tailwind.config.js` - Primary color definitions
- `src/index.css` - Custom CSS variables

### Adding New Metrics
To add new investment metrics:
1. Update the `AnalysisResults` interface in components
2. Add calculation logic in `App.tsx`
3. Display the metric in relevant components

### Data Sources
Currently uses mock data for demonstration. To integrate real data:
1. Replace mock data functions with API calls
2. Add data fetching logic in components
3. Implement error handling and loading states

## File Structure

```
src/
├── components/
│   ├── PropertyForm.tsx      # Property input form
│   ├── InvestmentMetrics.tsx # Investment analysis display
│   ├── RentalAnalysis.tsx    # Rental income analysis
│   ├── MarketComps.tsx       # Market comparisons
│   └── Charts.tsx           # Data visualizations
├── App.tsx                   # Main application component
├── index.tsx                 # Application entry point
└── index.css                 # Global styles and Tailwind imports
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

---

**Built with ❤️ for real estate investors** 