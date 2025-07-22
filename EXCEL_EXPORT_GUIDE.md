# 📊 Excel Export Feature Guide

## Overview

The Excel Export feature allows users to generate professional, investor-ready Excel pro formas directly from your real estate financial modeling application. This feature creates comprehensive, industry-standard real estate development underwriting models with all the formatting, formulas, and structure that investors expect.

## 🎯 Features

### Professional Formatting
- **Color-coded section headers**: Green for revenue, Blue for costs, Yellow for equity, Gray for timeline
- **Formatted data cells**: Currency, percentage, and number formatting
- **Merged headers** and proper spacing for readability
- **Print-ready layout** with proper scaling and margins

### Comprehensive Analysis Sheets
1. **Executive Summary**: Key metrics and property overview
2. **Pro Forma Analysis**: 5-year detailed financial projections
3. **Assumptions**: All input parameters and market assumptions
4. **Sensitivity Analysis**: Cap rate and cash-on-cash sensitivity tables

### Dynamic Excel Formulas
- **SUM formulas** for totals and subtotals
- **Percentage calculations** for ratios and returns
- **Growth projections** with compounding formulas
- **Conditional logic** for decision-making metrics

### Industry-Standard Sections
- **Gross Rental Income** with growth projections
- **Operating Expenses** breakdown with inflation adjustments
- **Net Operating Income (NOI)** calculations
- **Debt Service** and cash flow analysis
- **Capital Events** including initial investment and sale proceeds
- **Total Investment Returns** with IRR considerations

## 🚀 Usage

### Frontend Integration

The Excel export functionality is integrated into two main components:

#### 1. Investment Analysis Tab
- Located in the top-right corner of the Investment Analysis page
- Primary blue button with download icon
- Exports comprehensive analysis based on current property data

#### 2. Charts & Reports Tab  
- Located in the top-right corner of the Charts & Reports page
- Outline style button for secondary action
- Same comprehensive export functionality

### Button States
- **Default**: "Download Excel Pro Forma" with spreadsheet icon
- **Loading**: "Generating..." with spinning loader
- **Success**: "Downloaded!" with checkmark (3 seconds)
- **Error**: "Export Failed" with error details tooltip (5 seconds)

## 🔧 Technical Implementation

### Backend Architecture

#### Excel Generator (`backend/utils/excel_generator.py`)
```python
class RealEstateExcelGenerator:
    def create_pro_forma(property_data, analysis_results, assumptions, project_name)
    def _create_summary_sheet(ws, ...)
    def _create_proforma_sheet(ws, ...)
    def _create_assumptions_sheet(ws, ...)
    def _create_sensitivity_sheet(ws, ...)
```

#### API Endpoint (`backend/api.py`)
```python
@app.route('/api/export-excel', methods=['POST'])
def export_excel():
    # Accepts JSON data and returns Excel file
```

### Frontend Components

#### ExcelExportButton (`src/components/ExcelExportButton.tsx`)
- Reusable component with multiple style variants
- Built-in validation and error handling
- Customizable size, variant, and styling options

#### Export Utility (`src/utils/excelExport.ts`)
- `downloadExcelReport()`: Main export function
- `validateExportData()`: Input validation
- `generateProjectName()`: Auto-naming utility

## 📊 Excel File Structure

### Sheet 1: Executive Summary
- Property information overview
- Key investment metrics with targets
- Financial summary (monthly/annual)
- Investment recommendation

### Sheet 2: Pro Forma Analysis
- 5-year financial projections
- Year-over-year columns with formulas
- Revenue growth with rent escalation
- Operating expense inflation
- NOI and cash flow calculations
- Capital events and sale proceeds

### Sheet 3: Assumptions
- Property assumptions (price, size, type)
- Financial assumptions (rates, terms, percentages)
- Market assumptions (growth, inflation, costs)

### Sheet 4: Sensitivity Analysis
- Cap rate sensitivity matrix (price vs rent variations)
- Cash-on-cash sensitivity (interest rate vs rent)
- Color-coded performance indicators

## 🎨 Formatting Standards

### Color Scheme
- **Revenue Headers**: `#22C55E` (Green)
- **Cost Headers**: `#3B82F6` (Blue)  
- **Equity Headers**: `#FCD34D` (Yellow)
- **Timeline Headers**: `#6B7280` (Gray)
- **Data Borders**: `#E5E7EB` (Light Gray)

### Number Formats
- **Currency**: `$#,##0` format
- **Percentages**: `0.00%` format
- **Numbers**: `#,##0` format with comma separators
- **Dates**: `mm/dd/yyyy` format

### Layout Features
- **Frozen panes** for easy navigation
- **Column widths** optimized for readability
- **Merged cells** for section headers
- **Centered alignment** for headers and dates
- **Print scaling** to fit page width

## 📋 Data Requirements

### Required Property Data
```javascript
{
  address: string,        // Property address
  price: number,         // Purchase price
  beds: number,          // Number of bedrooms
  baths: number,         // Number of bathrooms
  sqft: number,          // Square footage
  neighborhood: string,   // Neighborhood name
  propertyType: string,   // Property type
  zipcode: string        // ZIP code
}
```

### Required Analysis Results
```javascript
{
  monthlyRent: number,      // Monthly rental income
  monthlyPayment: number,   // Monthly mortgage payment
  monthlyCashFlow: number,  // Monthly net cash flow
  capRate: number,          // Capitalization rate
  cashOnCash: number,       // Cash-on-cash return
  breakEvenRent: number,    // Break-even rental amount
  rentToPrice: number,      // Rent-to-price ratio
  totalROI: number,         // Total return on investment
  paybackPeriod: number     // Investment payback period
}
```

### Required Assumptions
```javascript
{
  downPaymentPct: number,      // Down payment percentage
  interestRate: number,        // Interest rate
  loanTerm: number,           // Loan term in years
  propertyTaxRate: number,    // Property tax rate
  insuranceRate: number,      // Insurance rate
  maintenanceRate: number,    // Maintenance rate
  capitalReservesRate: number, // Capital reserves rate
  vacancyRate: number,        // Vacancy rate
  closingCostsPct: number     // Closing costs percentage
}
```

## 🔍 Error Handling

### Validation Checks
- **Property address**: Must not be empty
- **Property price**: Must be greater than 0
- **Square footage**: Must be greater than 0
- **Monthly rent**: Must be calculated and > 0
- **Financial rates**: Must be greater than 0

### Error States
- **Validation errors**: Clear error messages for missing/invalid data
- **API errors**: Network and server error handling
- **File generation errors**: Backend processing error messages

## 🚀 Deployment Considerations

### Vercel Compatibility
- All Excel generation happens on backend
- Frontend only handles file download
- Compatible with serverless deployment
- No client-side Excel processing required

### Performance
- Excel generation typically takes 1-3 seconds
- File sizes range from 50-150KB
- Memory efficient with streaming approach
- Background processing with progress indicators

## 📈 Usage Examples

### Basic Usage
```typescript
import ExcelExportButton from './components/ExcelExportButton';

<ExcelExportButton
  propertyData={propertyData}
  analysisResults={results}
  assumptions={assumptions}
/>
```

### Custom Styling
```typescript
<ExcelExportButton
  propertyData={propertyData}
  analysisResults={results}
  assumptions={assumptions}
  size="lg"
  variant="outline"
  className="custom-styles"
  projectName="Custom Project Name"
/>
```

### Manual Export
```typescript
import { downloadExcelReport } from '../utils/excelExport';

await downloadExcelReport(
  propertyData,
  analysisResults,
  assumptions,
  'Custom Project Name'
);
```

## 🛠️ Maintenance

### Dependencies
- **xlsxwriter**: Excel file generation
- **openpyxl**: Excel file manipulation
- **flask**: API endpoint framework
- **pandas**: Data processing

### File Locations
- **Backend Generator**: `backend/utils/excel_generator.py`
- **API Endpoint**: `backend/api.py`
- **Frontend Component**: `src/components/ExcelExportButton.tsx`
- **Export Utility**: `src/utils/excelExport.ts`

### Testing
- Run `test_excel_export.py` for backend validation
- Frontend testing via browser console
- API testing with Postman or curl
- File validation with Excel/LibreOffice

---

**💡 Pro Tip**: The generated Excel files are designed to match industry standards used by platforms like LeadDeveloper.com and other professional real estate analysis tools. The formatting and structure are optimized for investor presentations and due diligence processes. 