import ExcelJS from 'exceljs';

interface PropertyData {
  address: string;
  price: number;
  beds: number;
  baths: number;
  sqft: number;
  neighborhood: string;
  propertyType: string;
  zipcode: string;
  totalUnits?: number;
}

interface AnalysisResults {
  monthlyRent: number;
  monthlyPayment: number;
  monthlyCashFlow: number;
  capRate: number;
  cashOnCash: number;
  breakEvenRent: number;
  rentToPrice: number;
  totalROI: number;
  paybackPeriod: number;
  annualNOI?: number;
}

interface InvestmentAssumptions {
  downPaymentPct: number;
  interestRate: number;
  loanTerm: number;
  propertyTaxRate: number;
  insuranceRate: number;
  maintenanceRate: number;
  capitalReservesRate: number;
  vacancyRate: number;
  closingCostsPct: number;
}

export class ClientExcelGenerator {
  private colors = {
    revenue: '22C55E',     // Green
    costs: '3B82F6',       // Blue  
    equity: 'FCD34D',      // Yellow
    timeline: '6B7280',    // Gray
    header_bg: 'F3F4F6',   // Light gray
    border: 'E5E7EB'       // Border gray
  };

  async generateProForma(
    propertyData: PropertyData,
    analysisResults: AnalysisResults,
    assumptions: InvestmentAssumptions,
    projectName: string
  ): Promise<ArrayBuffer> {
    const workbook = new ExcelJS.Workbook();
    
    // Create worksheets
    const summaryWs = workbook.addWorksheet('Executive Summary');
    const proformaWs = workbook.addWorksheet('Pro Forma Analysis');
    const assumptionsWs = workbook.addWorksheet('Assumptions');
    const sensitivityWs = workbook.addWorksheet('Sensitivity Analysis');

    // Generate sheets
    await this.createSummarySheet(summaryWs, propertyData, analysisResults, assumptions, projectName);
    await this.createProFormaSheet(proformaWs, propertyData, analysisResults, assumptions, projectName);
    await this.createAssumptionsSheet(assumptionsWs, propertyData, assumptions);
    await this.createSensitivitySheet(sensitivityWs, propertyData, analysisResults, assumptions);

    // Generate buffer
    const buffer = await workbook.xlsx.writeBuffer();
    return buffer;
  }

  private async createSummarySheet(
    ws: ExcelJS.Worksheet,
    propertyData: PropertyData,
    results: AnalysisResults,
    assumptions: InvestmentAssumptions,
    projectName: string
  ) {
    // Set column widths
    ws.columns = [
      { width: 25 }, { width: 20 }, { width: 15 }, { width: 15 }
    ];

    let row = 1;

    // Title
    const titleCell = ws.getCell(`A${row}`);
    titleCell.value = projectName;
    titleCell.font = { name: 'Calibri', size: 18, bold: true, color: { argb: '2563EB' } };
    ws.mergeCells(`A${row}:D${row}`);
    titleCell.alignment = { horizontal: 'center' };
    row += 2;

    // Executive Summary header
    const summaryHeaderCell = ws.getCell(`A${row}`);
    summaryHeaderCell.value = 'Executive Summary';
    summaryHeaderCell.font = { name: 'Calibri', size: 14, bold: true };
    summaryHeaderCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: this.colors.header_bg } };
    ws.mergeCells(`A${row}:D${row}`);
    summaryHeaderCell.alignment = { horizontal: 'center' };
    row += 2;

    // Property Information
    ws.getCell(`A${row}`).value = 'Property Information';
    ws.getCell(`A${row}`).font = { bold: true };
    row++;
    
    ws.getCell(`A${row}`).value = 'Address:';
    ws.getCell(`B${row}`).value = propertyData.address;
    row++;
    
    ws.getCell(`A${row}`).value = 'Price:';
    ws.getCell(`B${row}`).value = propertyData.price;
    ws.getCell(`B${row}`).numFmt = '$#,##0';
    row++;
    
    ws.getCell(`A${row}`).value = 'Size:';
    ws.getCell(`B${row}`).value = `${propertyData.beds} bed / ${propertyData.baths} bath`;
    row++;
    
    ws.getCell(`A${row}`).value = 'Square Feet:';
    ws.getCell(`B${row}`).value = propertyData.sqft;
    ws.getCell(`B${row}`).numFmt = '#,##0';
    row += 2;

    // Key Metrics
    ws.getCell(`A${row}`).value = 'Investment Metrics';
    ws.getCell(`A${row}`).font = { bold: true };
    row++;

    const metrics = [
      ['Monthly Rent:', results.monthlyRent, '$#,##0'],
      ['Monthly Payment:', results.monthlyPayment, '$#,##0'],
      ['Monthly Cash Flow:', results.monthlyCashFlow, '$#,##0'],
      ['Cap Rate:', results.capRate / 100, '0.00%'],
      ['Cash-on-Cash Return:', results.cashOnCash / 100, '0.00%'],
      ['Total ROI:', results.totalROI / 100, '0.00%']
    ];

    metrics.forEach(([label, value, format]) => {
      ws.getCell(`A${row}`).value = label;
      ws.getCell(`B${row}`).value = value;
      ws.getCell(`B${row}`).numFmt = format;
      
      // Color code positive/negative cash flow
      if (label === 'Monthly Cash Flow:') {
        if (typeof value === 'number' && value > 0) {
          ws.getCell(`B${row}`).font = { color: { argb: this.colors.revenue } };
        } else {
          ws.getCell(`B${row}`).font = { color: { argb: 'DC2626' } };
        }
      }
      
      row++;
    });

    row += 2;

    // Investment Summary
    ws.getCell(`A${row}`).value = 'Investment Summary';
    ws.getCell(`A${row}`).font = { bold: true };
    row++;

    const downPayment = propertyData.price * (assumptions.downPaymentPct / 100);
    const closingCosts = propertyData.price * (assumptions.closingCostsPct / 100);
    const totalInvestment = downPayment + closingCosts;

    ws.getCell(`A${row}`).value = 'Down Payment:';
    ws.getCell(`B${row}`).value = downPayment;
    ws.getCell(`B${row}`).numFmt = '$#,##0';
    row++;

    ws.getCell(`A${row}`).value = 'Closing Costs:';
    ws.getCell(`B${row}`).value = closingCosts;
    ws.getCell(`B${row}`).numFmt = '$#,##0';
    row++;

    ws.getCell(`A${row}`).value = 'Total Investment:';
    ws.getCell(`B${row}`).value = totalInvestment;
    ws.getCell(`B${row}`).numFmt = '$#,##0';
    ws.getCell(`B${row}`).font = { bold: true };
    row += 2;

    // Recommendation
    const recommendation = results.cashOnCash > 8 && results.capRate > 6 ? 'STRONG BUY' : 
                          results.cashOnCash > 5 && results.capRate > 4 ? 'BUY' : 'HOLD/PASS';
    
    ws.getCell(`A${row}`).value = 'Recommendation:';
    ws.getCell(`B${row}`).value = recommendation;
    ws.getCell(`B${row}`).font = { bold: true, color: { argb: recommendation === 'STRONG BUY' ? this.colors.revenue : recommendation === 'BUY' ? 'F59E0B' : 'DC2626' } };
  }

  private async createProFormaSheet(
    ws: ExcelJS.Worksheet,
    propertyData: PropertyData,
    results: AnalysisResults,
    assumptions: InvestmentAssumptions,
    projectName: string
  ) {
    // Set column widths
    ws.columns = [
      { width: 25 }, { width: 15 }, { width: 15 }, { width: 15 }, { width: 15 }, { width: 15 }
    ];

    let row = 1;

    // Title
    const titleCell = ws.getCell(`A${row}`);
    titleCell.value = `${projectName} - 5 Year Pro Forma`;
    titleCell.font = { name: 'Calibri', size: 16, bold: true, color: { argb: '2563EB' } };
    ws.mergeCells(`A${row}:F${row}`);
    titleCell.alignment = { horizontal: 'center' };
    row += 2;

    // Year headers
    ws.getCell(`A${row}`).value = 'Item';
    ws.getCell(`A${row}`).font = { bold: true };
    ws.getCell(`A${row}`).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: this.colors.header_bg } };
    
    for (let year = 1; year <= 5; year++) {
      const cell = ws.getCell(`${String.fromCharCode(65 + year)}${row}`);
      cell.value = `Year ${year}`;
      cell.font = { bold: true };
      cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: this.colors.timeline } };
      cell.alignment = { horizontal: 'center' };
    }
    row++;

    // Revenue Section
    ws.getCell(`A${row}`).value = 'REVENUE';
    ws.getCell(`A${row}`).font = { bold: true, color: { argb: 'FFFFFF' } };
    ws.getCell(`A${row}`).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: this.colors.revenue } };
    ws.mergeCells(`A${row}:F${row}`);
    row++;

    // Gross Rental Income
    ws.getCell(`A${row}`).value = 'Gross Rental Income';
    const baseRent = results.monthlyRent * 12;
    for (let year = 1; year <= 5; year++) {
      const cell = ws.getCell(`${String.fromCharCode(65 + year)}${row}`);
      // 3% annual rent growth
      cell.value = baseRent * Math.pow(1.03, year - 1);
      cell.numFmt = '$#,##0';
    }
    row++;

    // Vacancy Loss
    ws.getCell(`A${row}`).value = 'Less: Vacancy Loss';
    for (let year = 1; year <= 5; year++) {
      const cell = ws.getCell(`${String.fromCharCode(65 + year)}${row}`);
      const grossRent = baseRent * Math.pow(1.03, year - 1);
      cell.value = -(grossRent * (assumptions.vacancyRate / 100));
      cell.numFmt = '$#,##0';
      cell.font = { color: { argb: 'DC2626' } };
    }
    row++;

    // Effective Gross Income
    ws.getCell(`A${row}`).value = 'Effective Gross Income';
    ws.getCell(`A${row}`).font = { bold: true };
    for (let year = 1; year <= 5; year++) {
      const cell = ws.getCell(`${String.fromCharCode(65 + year)}${row}`);
      const grossRent = baseRent * Math.pow(1.03, year - 1);
      const vacancy = grossRent * (assumptions.vacancyRate / 100);
      cell.value = grossRent - vacancy;
      cell.numFmt = '$#,##0';
      cell.font = { bold: true };
    }
    row += 2;

    // Expenses Section
    ws.getCell(`A${row}`).value = 'OPERATING EXPENSES';
    ws.getCell(`A${row}`).font = { bold: true, color: { argb: 'FFFFFF' } };
    ws.getCell(`A${row}`).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: this.colors.costs } };
    ws.mergeCells(`A${row}:F${row}`);
    row++;

    // Operating expenses with 2% inflation
    const expenses = [
      ['Property Taxes', propertyData.price * (assumptions.propertyTaxRate / 100)],
      ['Insurance', propertyData.price * (assumptions.insuranceRate / 100)],
      ['Maintenance & Repairs', results.monthlyRent * 12 * (assumptions.maintenanceRate / 100)],
      ['Capital Reserves', results.monthlyRent * 12 * (assumptions.capitalReservesRate / 100)],
      ['Property Management', results.monthlyRent * 12 * 0.08]
    ];

    expenses.forEach(([name, baseAmount]) => {
      ws.getCell(`A${row}`).value = name;
      for (let year = 1; year <= 5; year++) {
        const cell = ws.getCell(`${String.fromCharCode(65 + year)}${row}`);
        cell.value = baseAmount * Math.pow(1.02, year - 1);
        cell.numFmt = '$#,##0';
      }
      row++;
    });

    // Total Operating Expenses
    ws.getCell(`A${row}`).value = 'Total Operating Expenses';
    ws.getCell(`A${row}`).font = { bold: true };
    for (let year = 1; year <= 5; year++) {
      const cell = ws.getCell(`${String.fromCharCode(65 + year)}${row}`);
      const totalExpenses = expenses.reduce((sum, [, baseAmount]) => 
        sum + baseAmount * Math.pow(1.02, year - 1), 0);
      cell.value = totalExpenses;
      cell.numFmt = '$#,##0';
      cell.font = { bold: true };
    }
    row += 2;

    // Net Operating Income
    ws.getCell(`A${row}`).value = 'NET OPERATING INCOME (NOI)';
    ws.getCell(`A${row}`).font = { bold: true, color: { argb: 'FFFFFF' } };
    ws.getCell(`A${row}`).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: this.colors.equity } };
    ws.mergeCells(`A${row}:F${row}`);
    row++;

    for (let year = 1; year <= 5; year++) {
      const cell = ws.getCell(`${String.fromCharCode(65 + year)}${row}`);
      const grossRent = baseRent * Math.pow(1.03, year - 1);
      const vacancy = grossRent * (assumptions.vacancyRate / 100);
      const effectiveIncome = grossRent - vacancy;
      const totalExpenses = expenses.reduce((sum, [, baseAmount]) => 
        sum + baseAmount * Math.pow(1.02, year - 1), 0);
      cell.value = effectiveIncome - totalExpenses;
      cell.numFmt = '$#,##0';
      cell.font = { bold: true, color: { argb: this.colors.equity } };
    }
    row += 2;

    // Debt Service
    ws.getCell(`A${row}`).value = 'DEBT SERVICE';
    ws.getCell(`A${row}`).font = { bold: true };
    for (let year = 1; year <= 5; year++) {
      const cell = ws.getCell(`${String.fromCharCode(65 + year)}${row}`);
      cell.value = results.monthlyPayment * 12;
      cell.numFmt = '$#,##0';
    }
    row++;

    // Cash Flow Before Tax
    ws.getCell(`A${row}`).value = 'CASH FLOW BEFORE TAX';
    ws.getCell(`A${row}`).font = { bold: true };
    for (let year = 1; year <= 5; year++) {
      const cell = ws.getCell(`${String.fromCharCode(65 + year)}${row}`);
      const grossRent = baseRent * Math.pow(1.03, year - 1);
      const vacancy = grossRent * (assumptions.vacancyRate / 100);
      const effectiveIncome = grossRent - vacancy;
      const totalExpenses = expenses.reduce((sum, [, baseAmount]) => 
        sum + baseAmount * Math.pow(1.02, year - 1), 0);
      const noi = effectiveIncome - totalExpenses;
      const debtService = results.monthlyPayment * 12;
      cell.value = noi - debtService;
      cell.numFmt = '$#,##0';
      cell.font = { bold: true };
      
      // Color code positive/negative
      if (noi - debtService > 0) {
        cell.font = { bold: true, color: { argb: this.colors.revenue } };
      } else {
        cell.font = { bold: true, color: { argb: 'DC2626' } };
      }
    }
  }

  private async createAssumptionsSheet(
    ws: ExcelJS.Worksheet,
    propertyData: PropertyData,
    assumptions: InvestmentAssumptions
  ) {
    // Set column widths
    ws.columns = [
      { width: 30 }, { width: 20 }, { width: 15 }
    ];

    let row = 1;

    // Title
    const titleCell = ws.getCell(`A${row}`);
    titleCell.value = 'Investment Assumptions';
    titleCell.font = { name: 'Calibri', size: 16, bold: true, color: { argb: '2563EB' } };
    ws.mergeCells(`A${row}:C${row}`);
    titleCell.alignment = { horizontal: 'center' };
    row += 2;

    // Property Assumptions
    ws.getCell(`A${row}`).value = 'Property Assumptions';
    ws.getCell(`A${row}`).font = { bold: true };
    ws.getCell(`A${row}`).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: this.colors.header_bg } };
    ws.mergeCells(`A${row}:C${row}`);
    row++;

    const propertyAssumptions = [
      ['Purchase Price', propertyData.price, '$#,##0'],
      ['Property Type', propertyData.propertyType, '@'],
      ['Square Feet', propertyData.sqft, '#,##0'],
      ['Bedrooms', propertyData.beds, '0'],
      ['Bathrooms', propertyData.baths, '0.0']
    ];

    propertyAssumptions.forEach(([label, value, format]) => {
      ws.getCell(`A${row}`).value = label;
      ws.getCell(`B${row}`).value = value;
      ws.getCell(`B${row}`).numFmt = format;
      row++;
    });

    row++;

    // Financial Assumptions
    ws.getCell(`A${row}`).value = 'Financial Assumptions';
    ws.getCell(`A${row}`).font = { bold: true };
    ws.getCell(`A${row}`).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: this.colors.header_bg } };
    ws.mergeCells(`A${row}:C${row}`);
    row++;

    const financialAssumptions = [
      ['Down Payment %', assumptions.downPaymentPct / 100, '0.00%'],
      ['Interest Rate', assumptions.interestRate / 100, '0.00%'],
      ['Loan Term (Years)', assumptions.loanTerm, '0'],
      ['Property Tax Rate', assumptions.propertyTaxRate / 100, '0.00%'],
      ['Insurance Rate', assumptions.insuranceRate / 100, '0.00%'],
      ['Maintenance Rate', assumptions.maintenanceRate / 100, '0.00%'],
      ['Capital Reserves Rate', assumptions.capitalReservesRate / 100, '0.00%'],
      ['Vacancy Rate', assumptions.vacancyRate / 100, '0.00%'],
      ['Closing Costs %', assumptions.closingCostsPct / 100, '0.00%']
    ];

    financialAssumptions.forEach(([label, value, format]) => {
      ws.getCell(`A${row}`).value = label;
      ws.getCell(`B${row}`).value = value;
      ws.getCell(`B${row}`).numFmt = format;
      row++;
    });

    row++;

    // Market Assumptions
    ws.getCell(`A${row}`).value = 'Market Assumptions';
    ws.getCell(`A${row}`).font = { bold: true };
    ws.getCell(`A${row}`).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: this.colors.header_bg } };
    ws.mergeCells(`A${row}:C${row}`);
    row++;

    const marketAssumptions = [
      ['Annual Rent Growth', 0.03, '0.00%'],
      ['Annual Expense Inflation', 0.02, '0.00%'],
      ['Annual Appreciation', 0.03, '0.00%'],
      ['Property Management Fee', 0.08, '0.00%']
    ];

    marketAssumptions.forEach(([label, value, format]) => {
      ws.getCell(`A${row}`).value = label;
      ws.getCell(`B${row}`).value = value;
      ws.getCell(`B${row}`).numFmt = format;
      row++;
    });
  }

  private async createSensitivitySheet(
    ws: ExcelJS.Worksheet,
    propertyData: PropertyData,
    results: AnalysisResults,
    assumptions: InvestmentAssumptions
  ) {
    // Set column widths
    ws.columns = Array(8).fill({ width: 12 });

    let row = 1;

    // Title
    const titleCell = ws.getCell(`A${row}`);
    titleCell.value = 'Sensitivity Analysis';
    titleCell.font = { name: 'Calibri', size: 16, bold: true, color: { argb: '2563EB' } };
    ws.mergeCells(`A${row}:H${row}`);
    titleCell.alignment = { horizontal: 'center' };
    row += 2;

    // Cap Rate Sensitivity
    ws.getCell(`A${row}`).value = 'Cap Rate Sensitivity Analysis';
    ws.getCell(`A${row}`).font = { bold: true };
    ws.getCell(`A${row}`).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: this.colors.header_bg } };
    ws.mergeCells(`A${row}:H${row}`);
    row++;

    // Headers
    ws.getCell(`A${row}`).value = 'Cap Rate';
    ws.getCell(`A${row}`).font = { bold: true };
    for (let i = 0; i < 7; i++) {
      const cell = ws.getCell(`${String.fromCharCode(66 + i)}${row}`);
      cell.value = `${4 + i}%`;
      cell.font = { bold: true };
      cell.alignment = { horizontal: 'center' };
    }
    row++;

    // Property values at different cap rates
    const noi = results.annualNOI || (results.monthlyRent * 12 * 0.8); // Fallback NOI estimate
    
    for (let rentMultiplier = 0.9; rentMultiplier <= 1.1; rentMultiplier += 0.05) {
      ws.getCell(`A${row}`).value = `${(rentMultiplier * 100).toFixed(0)}% Rent`;
      
      for (let capRate = 4; capRate <= 10; capRate++) {
        const adjustedNOI = noi * rentMultiplier;
        const propertyValue = adjustedNOI / (capRate / 100);
        const cell = ws.getCell(`${String.fromCharCode(66 + capRate - 4)}${row}`);
        cell.value = propertyValue;
        cell.numFmt = '$#,##0';
        
        // Color code based on current property price
        if (propertyValue > propertyData.price * 1.1) {
          cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'DCFCE7' } }; // Light green
        } else if (propertyValue < propertyData.price * 0.9) {
          cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FEE2E2' } }; // Light red
        }
      }
      row++;
    }

    row += 2;

    // Cash-on-Cash Sensitivity
    ws.getCell(`A${row}`).value = 'Cash-on-Cash Return Sensitivity';
    ws.getCell(`A${row}`).font = { bold: true };
    ws.getCell(`A${row}`).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: this.colors.header_bg } };
    ws.mergeCells(`A${row}:H${row}`);
    row++;

    // Headers
    ws.getCell(`A${row}`).value = 'Down Payment';
    ws.getCell(`A${row}`).font = { bold: true };
    for (let i = 0; i < 7; i++) {
      const cell = ws.getCell(`${String.fromCharCode(66 + i)}${row}`);
      cell.value = `${10 + i * 5}%`;
      cell.font = { bold: true };
      cell.alignment = { horizontal: 'center' };
    }
    row++;

    // Cash-on-cash returns at different down payments and rent levels
    for (let rentMultiplier = 0.9; rentMultiplier <= 1.1; rentMultiplier += 0.05) {
      ws.getCell(`A${row}`).value = `${(rentMultiplier * 100).toFixed(0)}% Rent`;
      
      for (let downPaymentPct = 10; downPaymentPct <= 40; downPaymentPct += 5) {
        const adjustedRent = results.monthlyRent * rentMultiplier;
        const downPayment = propertyData.price * (downPaymentPct / 100);
        const closingCosts = propertyData.price * (assumptions.closingCostsPct / 100);
        const totalInvestment = downPayment + closingCosts;
        const annualCashFlow = (adjustedRent - results.monthlyPayment) * 12;
        const cashOnCash = (annualCashFlow / totalInvestment) * 100;
        
        const cell = ws.getCell(`${String.fromCharCode(66 + (downPaymentPct - 10) / 5)}${row}`);
        cell.value = cashOnCash / 100;
        cell.numFmt = '0.00%';
        
        // Color code based on performance
        if (cashOnCash > 10) {
          cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'DCFCE7' } }; // Light green
        } else if (cashOnCash < 5) {
          cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FEE2E2' } }; // Light red
        }
      }
      row++;
    }
  }
} 