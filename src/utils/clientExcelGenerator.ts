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
    revenue: '22C55E',      // Green for revenue
    costs: '3B82F6',        // Blue for costs  
    equity: 'FCD34D',       // Yellow for equity
    timeline: '6B7280',     // Gray for timeline headers
    header_bg: 'F3F4F6',    // Light gray for headers
    white: 'FFFFFF',
    border: 'E5E7EB',
    input: '0066CC'         // Blue for input cells
  };

  private formats: any = {};
  private proformaRows: any = {};

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

    // Create formats
    this.createFormats(workbook);

    // Generate sheets in the correct order
    await this.createProFormaSheet(proformaWs, propertyData, analysisResults, assumptions, projectName);
    await this.createSummarySheet(summaryWs, propertyData, analysisResults, assumptions, projectName);
    await this.createAssumptionsSheet(assumptionsWs, propertyData, assumptions);
    await this.createSensitivitySheet(sensitivityWs, propertyData, analysisResults, assumptions);

    // Set up print settings
    [summaryWs, proformaWs, assumptionsWs, sensitivityWs].forEach(ws => {
      ws.pageSetup = {
        orientation: 'landscape',
        fitToPage: true,
        fitToWidth: 1,
        fitToHeight: 0,
        margins: { left: 0.5, right: 0.5, top: 0.75, bottom: 0.75, header: 0.3, footer: 0.3 }
      };
      ws.headerFooter.oddHeader = '&C&"Arial,Bold"Real Estate Investment Analysis';
      ws.headerFooter.oddFooter = '&L&D &T&C&P&R&F';
    });

    // Generate buffer
    const buffer = await workbook.xlsx.writeBuffer();
    return buffer;
  }

  private createFormats(workbook: ExcelJS.Workbook) {
    // Title format
    this.formats.title = {
      font: { size: 18, bold: true },
      alignment: { horizontal: 'center', vertical: 'middle' },
      fill: { type: 'pattern', pattern: 'solid', fgColor: { argb: this.colors.header_bg } },
      border: {
        top: { style: 'thin', color: { argb: this.colors.border } },
        left: { style: 'thin', color: { argb: this.colors.border } },
        bottom: { style: 'thin', color: { argb: this.colors.border } },
        right: { style: 'thin', color: { argb: this.colors.border } }
      }
    };

    // Section headers
    this.formats.sectionHeaderRevenue = {
      font: { size: 12, bold: true, color: { argb: this.colors.white } },
      alignment: { horizontal: 'center', vertical: 'middle' },
      fill: { type: 'pattern', pattern: 'solid', fgColor: { argb: this.colors.revenue } },
      border: {
        top: { style: 'thin', color: { argb: this.colors.border } },
        left: { style: 'thin', color: { argb: this.colors.border } },
        bottom: { style: 'thin', color: { argb: this.colors.border } },
        right: { style: 'thin', color: { argb: this.colors.border } }
      }
    };

    this.formats.sectionHeaderCosts = {
      font: { size: 12, bold: true, color: { argb: this.colors.white } },
      alignment: { horizontal: 'center', vertical: 'middle' },
      fill: { type: 'pattern', pattern: 'solid', fgColor: { argb: this.colors.costs } },
      border: {
        top: { style: 'thin', color: { argb: this.colors.border } },
        left: { style: 'thin', color: { argb: this.colors.border } },
        bottom: { style: 'thin', color: { argb: this.colors.border } },
        right: { style: 'thin', color: { argb: this.colors.border } }
      }
    };

    this.formats.sectionHeaderEquity = {
      font: { size: 12, bold: true, color: { argb: '000000' } },
      alignment: { horizontal: 'center', vertical: 'middle' },
      fill: { type: 'pattern', pattern: 'solid', fgColor: { argb: this.colors.equity } },
      border: {
        top: { style: 'thin', color: { argb: this.colors.border } },
        left: { style: 'thin', color: { argb: this.colors.border } },
        bottom: { style: 'thin', color: { argb: this.colors.border } },
        right: { style: 'thin', color: { argb: this.colors.border } }
      }
    };

    this.formats.sectionHeaderTimeline = {
      font: { size: 11, bold: true, color: { argb: this.colors.white } },
      alignment: { horizontal: 'center', vertical: 'middle' },
      fill: { type: 'pattern', pattern: 'solid', fgColor: { argb: this.colors.timeline } },
      border: {
        top: { style: 'thin', color: { argb: this.colors.border } },
        left: { style: 'thin', color: { argb: this.colors.border } },
        bottom: { style: 'thin', color: { argb: this.colors.border } },
        right: { style: 'thin', color: { argb: this.colors.border } }
      }
    };

    // Column header
    this.formats.columnHeader = {
      font: { size: 10, bold: true },
      alignment: { horizontal: 'center', vertical: 'middle', wrapText: true },
      fill: { type: 'pattern', pattern: 'solid', fgColor: { argb: this.colors.header_bg } },
      border: {
        top: { style: 'thin', color: { argb: this.colors.border } },
        left: { style: 'thin', color: { argb: this.colors.border } },
        bottom: { style: 'thin', color: { argb: this.colors.border } },
        right: { style: 'thin', color: { argb: this.colors.border } }
      }
    };

    // Input formats (blue)
    this.formats.input = {
      font: { color: { argb: this.colors.input }, bold: true },
      alignment: { horizontal: 'center' },
      border: {
        top: { style: 'thin', color: { argb: this.colors.border } },
        left: { style: 'thin', color: { argb: this.colors.border } },
        bottom: { style: 'thin', color: { argb: this.colors.border } },
        right: { style: 'thin', color: { argb: this.colors.border } }
      }
    };

    this.formats.inputCurrency = {
      ...this.formats.input,
      numFmt: '$#,##0'
    };

    this.formats.inputPercentage = {
      ...this.formats.input,
      numFmt: '0.00%'
    };

    // Data formats
    this.formats.currency = {
      numFmt: '$#,##0',
      alignment: { horizontal: 'center' },
      border: {
        top: { style: 'thin', color: { argb: this.colors.border } },
        left: { style: 'thin', color: { argb: this.colors.border } },
        bottom: { style: 'thin', color: { argb: this.colors.border } },
        right: { style: 'thin', color: { argb: this.colors.border } }
      }
    };

    this.formats.currencyBold = {
      ...this.formats.currency,
      font: { bold: true }
    };

    this.formats.currencyPerSF = {
      numFmt: '$#,##0.00',
      alignment: { horizontal: 'center' },
      border: {
        top: { style: 'thin', color: { argb: this.colors.border } },
        left: { style: 'thin', color: { argb: this.colors.border } },
        bottom: { style: 'thin', color: { argb: this.colors.border } },
        right: { style: 'thin', color: { argb: this.colors.border } }
      }
    };

    this.formats.percentage = {
      numFmt: '0.00%',
      alignment: { horizontal: 'center' },
      border: {
        top: { style: 'thin', color: { argb: this.colors.border } },
        left: { style: 'thin', color: { argb: this.colors.border } },
        bottom: { style: 'thin', color: { argb: this.colors.border } },
        right: { style: 'thin', color: { argb: this.colors.border } }
      }
    };

    this.formats.number = {
      numFmt: '#,##0',
      alignment: { horizontal: 'center' },
      border: {
        top: { style: 'thin', color: { argb: this.colors.border } },
        left: { style: 'thin', color: { argb: this.colors.border } },
        bottom: { style: 'thin', color: { argb: this.colors.border } },
        right: { style: 'thin', color: { argb: this.colors.border } }
      }
    };

    this.formats.text = {
      alignment: { horizontal: 'left' },
      border: {
        top: { style: 'thin', color: { argb: this.colors.border } },
        left: { style: 'thin', color: { argb: this.colors.border } },
        bottom: { style: 'thin', color: { argb: this.colors.border } },
        right: { style: 'thin', color: { argb: this.colors.border } }
      }
    };

    this.formats.textBold = {
      ...this.formats.text,
      font: { bold: true }
    };

    this.formats.textCenter = {
      alignment: { horizontal: 'center' },
      border: {
        top: { style: 'thin', color: { argb: this.colors.border } },
        left: { style: 'thin', color: { argb: this.colors.border } },
        bottom: { style: 'thin', color: { argb: this.colors.border } },
        right: { style: 'thin', color: { argb: this.colors.border } }
      }
    };
  }

  private async createSummarySheet(
    ws: ExcelJS.Worksheet,
    propertyData: PropertyData,
    results: AnalysisResults,
    assumptions: InvestmentAssumptions,
    projectName: string
  ) {
    // Set column widths to match backend exactly
    ws.getColumn('A').width = 28;   // Property labels
    ws.getColumn('B').width = 16;   // Property values
    ws.getColumn('C').width = 20;   // Project metrics labels
    ws.getColumn('D').width = 16;   // Project metrics values
    ws.getColumn('E').width = 12;   // Spacer
    ws.getColumn('F').width = 25;   // Financial assumption labels
    ws.getColumn('G').width = 16;   // Financial assumption values

    let row = 1;
    const projectTitle = projectName || `Real Estate Investment Analysis - ${propertyData.address}`;
    ws.mergeCells(`A${row}:G${row}`);
    const titleCell = ws.getCell(`A${row}`);
    titleCell.value = projectTitle;
    Object.assign(titleCell, this.formats.title);
    row++;

    ws.mergeCells(`A${row}:G${row}`);
    const dateCell = ws.getCell(`A${row}`);
    dateCell.value = `Generated on ${new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}`;
    Object.assign(dateCell, this.formats.columnHeader);
    row += 2;

    // PROPERTY INFORMATION header
    ws.mergeCells(`A${row}:G${row}`);
    const propInfoCell = ws.getCell(`A${row}`);
    propInfoCell.value = 'PROPERTY INFORMATION';
    Object.assign(propInfoCell, this.formats.sectionHeaderTimeline);
    row++;

    // Column headers for property info
    ws.getCell(`A${row}`).value = 'Property Details';
    Object.assign(ws.getCell(`A${row}`), this.formats.columnHeader);
    ws.getCell(`B${row}`).value = 'Value';
    Object.assign(ws.getCell(`B${row}`), this.formats.columnHeader);
    ws.getCell(`C${row}`).value = 'Project Metrics';
    Object.assign(ws.getCell(`C${row}`), this.formats.columnHeader);
    ws.getCell(`D${row}`).value = 'Value';
    Object.assign(ws.getCell(`D${row}`), this.formats.columnHeader);
    
    // Financial Assumptions header in columns F-G
    ws.mergeCells(`F${row}:G${row}`);
    const finAssumpHeaderCell = ws.getCell(`F${row}`);
    finAssumpHeaderCell.value = 'FINANCIAL ASSUMPTIONS';
    Object.assign(finAssumpHeaderCell, this.formats.sectionHeaderCosts);
    row++;

    const propertyInfoLeft = [
      ['Address', propertyData.address],
      ['Property Type', propertyData.propertyType],
      ['Neighborhood', propertyData.neighborhood],
      ['Zip Code', propertyData.zipcode]
    ];

    const totalUnits = propertyData.totalUnits || 1;
    const totalSqft = propertyData.sqft;
    const avgSfPerUnit = Math.round(totalSqft / Math.max(totalUnits, 1));

    const propertyInfoRight = [
      ['Total Development Cost', propertyData.price],
      ['Total Square Footage', totalSqft],
      ['Total Units', totalUnits],
      ['Avg SF per Unit', avgSfPerUnit]
    ];

    // Financial Assumptions (right side panel) - exactly like backend
    const annualRent = results.monthlyRent * 12;
    const financialAssumptions = [
      ['Annual Gross Rent', annualRent, 'inputCurrency'],
      ['Rent Growth Rate', 0.03, 'inputPercentage'],
      ['Vacancy Rate', 0.05, 'inputPercentage'],
      ['Property Management %', 0.08, 'inputPercentage'],
      ['Maintenance % of EGI', 0.01, 'inputPercentage'],
      ['Capital Reserves % of EGI', 0.01, 'inputPercentage'],
      ['Utilities % of EGI', 0.005, 'inputPercentage'],
      ['Legal & Professional % of EGI', 0.002, 'inputPercentage'],
      ['Other Operating % of EGI', 0.003, 'inputPercentage'],
      ['Property Tax Rate', assumptions.propertyTaxRate / 100, 'inputPercentage'],
      ['Insurance Rate', assumptions.insuranceRate / 100, 'inputPercentage'],
      ['Inflation Rate', 0.025, 'inputPercentage'],
      ['Down Payment %', assumptions.downPaymentPct / 100, 'inputPercentage'],
      ['Permanent Loan Rate', assumptions.interestRate / 100, 'inputPercentage'],
      ['Loan Term (Years)', assumptions.loanTerm, 'input'],
      ['Closing Costs %', 0.03, 'inputPercentage'],
      ['Exit Cap Rate', 0.06, 'inputPercentage'],
      ['Selling Costs %', 0.07, 'inputPercentage']
    ];

    const startRow = row;
    const maxRows = Math.max(propertyInfoLeft.length, propertyInfoRight.length, financialAssumptions.length);
    
    for (let i = 0; i < maxRows; i++) {
      const currentRow = startRow + i;
      
      // Left side - Property Details
      if (i < propertyInfoLeft.length) {
        ws.getCell(`A${currentRow}`).value = propertyInfoLeft[i][0];
        Object.assign(ws.getCell(`A${currentRow}`), this.formats.textBold);
        ws.getCell(`B${currentRow}`).value = propertyInfoLeft[i][1];
        Object.assign(ws.getCell(`B${currentRow}`), this.formats.textCenter);
      }
      
      // Center - Project Metrics
      if (i < propertyInfoRight.length) {
        ws.getCell(`C${currentRow}`).value = propertyInfoRight[i][0];
        Object.assign(ws.getCell(`C${currentRow}`), this.formats.textCenter);

        if (propertyInfoRight[i][0] === 'Total Development Cost') {
          ws.getCell(`D${currentRow}`).value = propertyInfoRight[i][1];
          Object.assign(ws.getCell(`D${currentRow}`), this.formats.inputCurrency);
        } else if (propertyInfoRight[i][0] === 'Total Square Footage') {
          ws.getCell(`D${currentRow}`).value = `${propertyInfoRight[i][1].toLocaleString()} SF`;
          Object.assign(ws.getCell(`D${currentRow}`), this.formats.input);
        } else {
          ws.getCell(`D${currentRow}`).value = propertyInfoRight[i][1];
          Object.assign(ws.getCell(`D${currentRow}`), this.formats.input);
        }
      }
      
      // Right side - Financial Assumptions
      if (i < financialAssumptions.length) {
        ws.getCell(`F${currentRow}`).value = financialAssumptions[i][0];
        Object.assign(ws.getCell(`F${currentRow}`), this.formats.textBold);
        ws.getCell(`G${currentRow}`).value = financialAssumptions[i][1];
        Object.assign(ws.getCell(`G${currentRow}`), this.formats[financialAssumptions[i][2] as keyof typeof this.formats]);
      }
    }

    row = startRow + maxRows + 1;

    // KEY INVESTMENT METRICS
    ws.mergeCells(`A${row}:D${row}`);
    const metricsHeaderCell = ws.getCell(`A${row}`);
    metricsHeaderCell.value = 'KEY INVESTMENT METRICS';
    Object.assign(metricsHeaderCell, this.formats.sectionHeaderRevenue);
    row++;

    ws.getCell(`A${row}`).value = 'Metric';
    Object.assign(ws.getCell(`A${row}`), this.formats.columnHeader);
    ws.getCell(`B${row}`).value = 'Value';
    Object.assign(ws.getCell(`B${row}`), this.formats.columnHeader);
    ws.getCell(`C${row}`).value = 'Target';
    Object.assign(ws.getCell(`C${row}`), this.formats.columnHeader);
    ws.getCell(`D${row}`).value = 'Status';
    Object.assign(ws.getCell(`D${row}`), this.formats.columnHeader);
    row++;

    const metrics = [
      ['Cap Rate', results.capRate / 100, 0.06],
      ['Cash-on-Cash Return', results.cashOnCash / 100, 0.08],
      ['Monthly Cash Flow', results.monthlyCashFlow, 300],
      ['Rent-to-Price Ratio', results.rentToPrice / 100, 0.008]
    ];

    metrics.forEach(([metric, value, target]) => {
      ws.getCell(`A${row}`).value = metric;
      Object.assign(ws.getCell(`A${row}`), this.formats.text);

      const valueCell = ws.getCell(`B${row}`);
      valueCell.value = value;

      const targetCell = ws.getCell(`C${row}`);
      targetCell.value = target;

      if (metric === 'Monthly Cash Flow') {
        Object.assign(valueCell, this.formats.currency);
        Object.assign(targetCell, this.formats.currency);
        if (typeof value === 'number' && value > 0) {
          valueCell.font = { color: { argb: this.colors.revenue } };
        } else {
          valueCell.font = { color: { argb: 'DC2626' } };
        }
      } else {
        Object.assign(valueCell, this.formats.percentage);
        Object.assign(targetCell, this.formats.percentage);
      }

      const status = (typeof value === 'number' && value >= target) ? 'Good' : 'Poor';
      const statusCell = ws.getCell(`D${row}`);
      statusCell.value = status;
      Object.assign(statusCell, this.formats.textCenter);
      statusCell.font = { color: { argb: status === 'Good' ? this.colors.revenue : 'DC2626' } };

      row++;
    });

    row += 1;

    // FINANCIAL SUMMARY - Use cross-sheet references to Pro Forma
    ws.mergeCells(`A${row}:D${row}`);
    const financialHeaderCell = ws.getCell(`A${row}`);
    financialHeaderCell.value = 'FINANCIAL SUMMARY';
    Object.assign(financialHeaderCell, this.formats.sectionHeaderCosts);
    row++;

    ws.getCell(`A${row}`).value = 'Item';
    Object.assign(ws.getCell(`A${row}`), this.formats.columnHeader);
    ws.getCell(`B${row}`).value = 'Monthly';
    Object.assign(ws.getCell(`B${row}`), this.formats.columnHeader);
    ws.getCell(`C${row}`).value = 'Annual';
    Object.assign(ws.getCell(`C${row}`), this.formats.columnHeader);
    ws.getCell(`D${row}`).value = '5-Year Total';
    Object.assign(ws.getCell(`D${row}`), this.formats.columnHeader);
    row++;

    // Reference the Pro Forma Analysis sheet for all calculations using stored row numbers
    const financialItems = [
      ['Gross Rental Income', `='Pro Forma Analysis'!B${this.proformaRows.grossIncome}/12`, `='Pro Forma Analysis'!B${this.proformaRows.grossIncome}`, `=SUM('Pro Forma Analysis'!B${this.proformaRows.grossIncome}:F${this.proformaRows.grossIncome})`],
      ['Total Operating Expenses', `='Pro Forma Analysis'!B${this.proformaRows.totalExpenses}/12`, `='Pro Forma Analysis'!B${this.proformaRows.totalExpenses}`, `=SUM('Pro Forma Analysis'!B${this.proformaRows.totalExpenses}:F${this.proformaRows.totalExpenses})`],
      ['Net Operating Income', `='Pro Forma Analysis'!B${this.proformaRows.noi}/12`, `='Pro Forma Analysis'!B${this.proformaRows.noi}`, `=SUM('Pro Forma Analysis'!B${this.proformaRows.noi}:F${this.proformaRows.noi})`],
      ['Debt Service', `='Pro Forma Analysis'!B${this.proformaRows.debtService}/12`, `='Pro Forma Analysis'!B${this.proformaRows.debtService}`, `=SUM('Pro Forma Analysis'!B${this.proformaRows.debtService}:F${this.proformaRows.debtService})`],
      ['Before-Tax Cash Flow (Operations)', `='Pro Forma Analysis'!B${this.proformaRows.cashFlow}/12`, `='Pro Forma Analysis'!B${this.proformaRows.cashFlow}`, `=SUM('Pro Forma Analysis'!B${this.proformaRows.cashFlow}:F${this.proformaRows.cashFlow})`]
    ];

    financialItems.forEach(([item, monthlyFormula, annualFormula, fiveYearFormula]) => {
      ws.getCell(`A${row}`).value = item;
      Object.assign(ws.getCell(`A${row}`), this.formats.text);
      
      ws.getCell(`B${row}`).value = { formula: monthlyFormula };
      Object.assign(ws.getCell(`B${row}`), this.formats.currency);
      
      ws.getCell(`C${row}`).value = { formula: annualFormula };
      Object.assign(ws.getCell(`C${row}`), this.formats.currency);
      
      ws.getCell(`D${row}`).value = { formula: fiveYearFormula };
      Object.assign(ws.getCell(`D${row}`), this.formats.currency);
      
      row++;
    });

    // Add the "Note: Excludes sale proceeds in Year 5" note
    row += 1;
    ws.getCell(`A${row}`).value = 'Note: Excludes sale proceeds in Year 5';
    Object.assign(ws.getCell(`A${row}`), this.formats.text);
  }

  private async createProFormaSheet(
    ws: ExcelJS.Worksheet,
    propertyData: PropertyData,
    results: AnalysisResults,
    assumptions: InvestmentAssumptions,
    projectName: string
  ) {
    // Set column widths for optimal display
    ws.getColumn('A').width = 35;   // Line items
    ws.getColumn('B').width = 14;   // Year 1
    ws.getColumn('C').width = 14;   // Year 2
    ws.getColumn('D').width = 14;   // Year 3
    ws.getColumn('E').width = 14;   // Year 4
    ws.getColumn('F').width = 14;   // Year 5
    ws.getColumn('G').width = 16;   // Per unit
    ws.getColumn('H').width = 16;   // Per SF
    ws.getColumn('I').width = 8;    // Empty
    ws.getColumn('J').width = 8;    // Empty
    ws.getColumn('K').width = 25;   // Assumption labels
    ws.getColumn('L').width = 16;   // Assumption values

    let row = 1;

    // Title
    ws.mergeCells(`A${row}:H${row}`);
    const titleCell = ws.getCell(`A${row}`);
    titleCell.value = `5-Year Pro Forma Analysis - ${propertyData.address}`;
    Object.assign(titleCell, this.formats.title);
    row++;

    ws.mergeCells(`A${row}:H${row}`);
    const dateCell = ws.getCell(`A${row}`);
    dateCell.value = `Analysis Date: ${new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}`;
    Object.assign(dateCell, this.formats.columnHeader);
    row += 2;

    // Store assumption cell references for formulas - reference Executive Summary sheet
    const cellRefs: { [key: string]: string } = {
      'purchase_price': "'Executive Summary'!D5",
      'total_units': "'Executive Summary'!D7",
      'total_sqft': "'Executive Summary'!D6",
      'annual_rent': "'Executive Summary'!G5",
      'rent_growth_rate': "'Executive Summary'!G6",
      'vacancy_rate': "'Executive Summary'!G7",
      'property_mgmt': "'Executive Summary'!G8",
      'maintenance_rate': "'Executive Summary'!G9",
      'capital_reserves_rate': "'Executive Summary'!G10",
      'utilities_rate': "'Executive Summary'!G11",
      'legal_rate': "'Executive Summary'!G12",
      'other_expenses_rate': "'Executive Summary'!G13",
      'property_tax_rate': "'Executive Summary'!G14",
      'insurance_rate': "'Executive Summary'!G15",
      'inflation_rate': "'Executive Summary'!G16",
      'down_payment': "'Executive Summary'!G17",
      'interest_rate': "'Executive Summary'!G18",
      'loan_term_years': "'Executive Summary'!G19",
      'closing_costs': "'Executive Summary'!G20",
      'exit_cap_rate': "'Executive Summary'!G21",
      'selling_costs': "'Executive Summary'!G22"
    };

    // Main pro forma starts at row 4
    row = 4;

    // Column headers
    ws.getCell(`A${row}`).value = 'Line Item';
    Object.assign(ws.getCell(`A${row}`), this.formats.columnHeader);
    
    for (let year = 1; year <= 5; year++) {
      const cell = ws.getCell(`${String.fromCharCode(65 + year)}${row}`);
      cell.value = `Year ${year}`;
      Object.assign(cell, this.formats.columnHeader);
    }
    
    ws.getCell(`G${row}`).value = '$ per Unit';
    Object.assign(ws.getCell(`G${row}`), this.formats.columnHeader);
    ws.getCell(`H${row}`).value = '$ per SF';
    Object.assign(ws.getCell(`H${row}`), this.formats.columnHeader);
    row++;

    // GROSS RENTAL INCOME
    ws.mergeCells(`A${row}:H${row}`);
    const grossRentalCell = ws.getCell(`A${row}`);
    grossRentalCell.value = 'GROSS RENTAL INCOME';
    Object.assign(grossRentalCell, this.formats.sectionHeaderRevenue);
    row++;

    // Rental Income - Use Excel formulas referencing assumption cells
    ws.getCell(`A${row}`).value = 'Gross Rental Income';
    Object.assign(ws.getCell(`A${row}`), this.formats.text);

    for (let year = 1; year <= 5; year++) {
      const cell = ws.getCell(`${String.fromCharCode(65 + year)}${row}`);
      cell.value = { formula: `=${cellRefs['annual_rent']}*POWER(1+${cellRefs['rent_growth_rate']},${year-1})` };
      Object.assign(cell, this.formats.currency);
    }

    ws.getCell(`G${row}`).value = { formula: `=B${row}/${cellRefs['total_units']}` };
    Object.assign(ws.getCell(`G${row}`), this.formats.currency);
    ws.getCell(`H${row}`).value = { formula: `=B${row}/${cellRefs['total_sqft']}` };
    Object.assign(ws.getCell(`H${row}`), this.formats.currencyPerSF);
    
    const rentalIncomeRow = row;
    row++;

    // Other Income
    ws.getCell(`A${row}`).value = 'Other Income (5% of Gross Rent)';
    Object.assign(ws.getCell(`A${row}`), this.formats.text);

    for (let year = 1; year <= 5; year++) {
      const cell = ws.getCell(`${String.fromCharCode(65 + year)}${row}`);
      cell.value = { formula: `=${String.fromCharCode(65 + year)}${rentalIncomeRow}*0.05` };
      Object.assign(cell, this.formats.currency);
    }

    ws.getCell(`G${row}`).value = { formula: `=B${row}/${cellRefs['total_units']}` };
    Object.assign(ws.getCell(`G${row}`), this.formats.currency);
    ws.getCell(`H${row}`).value = { formula: `=B${row}/${cellRefs['total_sqft']}` };
    Object.assign(ws.getCell(`H${row}`), this.formats.currencyPerSF);
    
    const otherIncomeRow = row;
    row++;

    // Total Gross Income
    ws.getCell(`A${row}`).value = 'TOTAL GROSS INCOME';
    Object.assign(ws.getCell(`A${row}`), this.formats.textBold);

    for (let year = 1; year <= 5; year++) {
      const cell = ws.getCell(`${String.fromCharCode(65 + year)}${row}`);
      cell.value = { formula: `=${String.fromCharCode(65 + year)}${rentalIncomeRow}+${String.fromCharCode(65 + year)}${otherIncomeRow}` };
      Object.assign(cell, this.formats.currencyBold);
    }

    ws.getCell(`G${row}`).value = { formula: `=B${row}/${cellRefs['total_units']}` };
    Object.assign(ws.getCell(`G${row}`), this.formats.currencyBold);
    ws.getCell(`H${row}`).value = { formula: `=B${row}/${cellRefs['total_sqft']}` };
    Object.assign(ws.getCell(`H${row}`), this.formats.currencyBold);
    
    const totalGrossIncomeRow = row;
    row++;

    // Vacancy Loss
    ws.getCell(`A${row}`).value = 'Less: Vacancy Loss';
    Object.assign(ws.getCell(`A${row}`), this.formats.text);

    for (let year = 1; year <= 5; year++) {
      const cell = ws.getCell(`${String.fromCharCode(65 + year)}${row}`);
      cell.value = { formula: `=-${String.fromCharCode(65 + year)}${totalGrossIncomeRow}*${cellRefs['vacancy_rate']}` };
      Object.assign(cell, this.formats.currency);
      cell.font = { color: { argb: 'DC2626' } };
    }

    ws.getCell(`G${row}`).value = { formula: `=B${row}/${cellRefs['total_units']}` };
    Object.assign(ws.getCell(`G${row}`), this.formats.currency);
    ws.getCell(`H${row}`).value = { formula: `=B${row}/${cellRefs['total_sqft']}` };
    Object.assign(ws.getCell(`H${row}`), this.formats.currencyPerSF);
    
    const vacancyRow = row;
    row++;

    // Effective Gross Income
    ws.mergeCells(`A${row}:H${row}`);
    const egiCell = ws.getCell(`A${row}`);
    egiCell.value = 'EFFECTIVE GROSS INCOME (EGI)';
    Object.assign(egiCell, this.formats.sectionHeaderRevenue);
    row++;

    ws.getCell(`A${row}`).value = 'Effective Gross Income';
    Object.assign(ws.getCell(`A${row}`), this.formats.textBold);

    for (let year = 1; year <= 5; year++) {
      const cell = ws.getCell(`${String.fromCharCode(65 + year)}${row}`);
      cell.value = { formula: `=${String.fromCharCode(65 + year)}${totalGrossIncomeRow}+${String.fromCharCode(65 + year)}${vacancyRow}` };
      Object.assign(cell, this.formats.currencyBold);
    }

    ws.getCell(`G${row}`).value = { formula: `=B${row}/${cellRefs['total_units']}` };
    Object.assign(ws.getCell(`G${row}`), this.formats.currencyBold);
    ws.getCell(`H${row}`).value = { formula: `=B${row}/${cellRefs['total_sqft']}` };
    Object.assign(ws.getCell(`H${row}`), this.formats.currencyBold);
    
    const egiRow = row;
    row += 2;

    // OPERATING EXPENSES
    ws.mergeCells(`A${row}:H${row}`);
    const expensesHeaderCell = ws.getCell(`A${row}`);
    expensesHeaderCell.value = 'OPERATING EXPENSES';
    Object.assign(expensesHeaderCell, this.formats.sectionHeaderCosts);
    row++;

    // Operating expenses - use Excel formulas
    const expenses = [
      ['Property Management', 'percentage', cellRefs['property_mgmt'], 'egi'],
      ['Property Taxes', 'fixed_rate', cellRefs['property_tax_rate'], 'purchase_price'],
      ['Insurance', 'fixed_rate', cellRefs['insurance_rate'], 'purchase_price'],
      ['Maintenance & Repairs', 'percentage', cellRefs['maintenance_rate'], 'egi'],
      ['Capital Reserves', 'percentage', cellRefs['capital_reserves_rate'], 'egi'],
      ['Utilities', 'percentage', cellRefs['utilities_rate'], 'egi'],
      ['Legal & Professional', 'percentage', cellRefs['legal_rate'], 'egi'],
      ['Other Operating Expenses', 'percentage', cellRefs['other_expenses_rate'], 'egi']
    ];

    const expenseStartRow = row;

    expenses.forEach(([expenseName, calcType, rateRef, base]) => {
      ws.getCell(`A${row}`).value = expenseName;
      Object.assign(ws.getCell(`A${row}`), this.formats.text);

      if (calcType === 'percentage') {
        for (let year = 1; year <= 5; year++) {
          const cell = ws.getCell(`${String.fromCharCode(65 + year)}${row}`);
          cell.value = { formula: `=${String.fromCharCode(65 + year)}${egiRow}*${rateRef}` };
          Object.assign(cell, this.formats.currency);
        }
      } else if (calcType === 'fixed_rate') {
        for (let year = 1; year <= 5; year++) {
          const cell = ws.getCell(`${String.fromCharCode(65 + year)}${row}`);
          cell.value = { formula: `=${cellRefs['purchase_price']}*${rateRef}*POWER(1+${cellRefs['inflation_rate']},${year-1})` };
          Object.assign(cell, this.formats.currency);
        }
      }

      ws.getCell(`G${row}`).value = { formula: `=B${row}/${cellRefs['total_units']}` };
      Object.assign(ws.getCell(`G${row}`), this.formats.currency);
      ws.getCell(`H${row}`).value = { formula: `=B${row}/${cellRefs['total_sqft']}` };
      Object.assign(ws.getCell(`H${row}`), this.formats.currencyPerSF);
      
      row++;
    });

    // Total Operating Expenses
    ws.getCell(`A${row}`).value = 'TOTAL OPERATING EXPENSES';
    Object.assign(ws.getCell(`A${row}`), this.formats.textBold);

    for (let year = 1; year <= 5; year++) {
      const cell = ws.getCell(`${String.fromCharCode(65 + year)}${row}`);
      cell.value = { formula: `=SUM(${String.fromCharCode(65 + year)}${expenseStartRow}:${String.fromCharCode(65 + year)}${row-1})` };
      Object.assign(cell, this.formats.currencyBold);
    }

    ws.getCell(`G${row}`).value = { formula: `=B${row}/${cellRefs['total_units']}` };
    Object.assign(ws.getCell(`G${row}`), this.formats.currencyBold);
    ws.getCell(`H${row}`).value = { formula: `=B${row}/${cellRefs['total_sqft']}` };
    Object.assign(ws.getCell(`H${row}`), this.formats.currencyBold);
    
    const totalExpensesRow = row;
    row += 2;

    // NET OPERATING INCOME
    ws.mergeCells(`A${row}:H${row}`);
    const noiHeaderCell = ws.getCell(`A${row}`);
    noiHeaderCell.value = 'NET OPERATING INCOME (NOI)';
    Object.assign(noiHeaderCell, this.formats.sectionHeaderEquity);
    row++;

    ws.getCell(`A${row}`).value = 'Net Operating Income';
    Object.assign(ws.getCell(`A${row}`), this.formats.textBold);

    for (let year = 1; year <= 5; year++) {
      const cell = ws.getCell(`${String.fromCharCode(65 + year)}${row}`);
      cell.value = { formula: `=${String.fromCharCode(65 + year)}${egiRow}-${String.fromCharCode(65 + year)}${totalExpensesRow}` };
      Object.assign(cell, this.formats.currencyBold);
      cell.font = { bold: true, color: { argb: this.colors.equity } };
    }

    ws.getCell(`G${row}`).value = { formula: `=B${row}/${cellRefs['total_units']}` };
    Object.assign(ws.getCell(`G${row}`), this.formats.currencyBold);
    ws.getCell(`H${row}`).value = { formula: `=B${row}/${cellRefs['total_sqft']}` };
    Object.assign(ws.getCell(`H${row}`), this.formats.currencyBold);
    
    const noiRow = row;
    row += 2;

    // DEBT SERVICE - Use Excel PMT formula like backend
    ws.getCell(`A${row}`).value = 'DEBT SERVICE';
    Object.assign(ws.getCell(`A${row}`), this.formats.textBold);

    for (let year = 1; year <= 5; year++) {
      const cell = ws.getCell(`${String.fromCharCode(65 + year)}${row}`);
      // Use PMT formula: =PMT(rate, nper, pv) where pv is loan amount
      const loanAmount = `(${cellRefs['purchase_price']}*(1-${cellRefs['down_payment']}))`;
      const monthlyRate = `(${cellRefs['interest_rate']}/12)`;
      const numPayments = `(${cellRefs['loan_term_years']}*12)`;
      cell.value = { formula: `=-PMT(${monthlyRate},${numPayments},${loanAmount})*12` };
      Object.assign(cell, this.formats.currency);
    }

    ws.getCell(`G${row}`).value = { formula: `=B${row}/${cellRefs['total_units']}` };
    Object.assign(ws.getCell(`G${row}`), this.formats.currency);
    ws.getCell(`H${row}`).value = { formula: `=B${row}/${cellRefs['total_sqft']}` };
    Object.assign(ws.getCell(`H${row}`), this.formats.currencyPerSF);
    
    const debtServiceRow = row;
    row++;

    // CASH FLOW BEFORE TAX
    ws.getCell(`A${row}`).value = 'CASH FLOW BEFORE TAX';
    Object.assign(ws.getCell(`A${row}`), this.formats.textBold);

    for (let year = 1; year <= 5; year++) {
      const cell = ws.getCell(`${String.fromCharCode(65 + year)}${row}`);
      cell.value = { formula: `=${String.fromCharCode(65 + year)}${noiRow}-${String.fromCharCode(65 + year)}${debtServiceRow}` };
      Object.assign(cell, this.formats.currencyBold);
      
      // Use conditional formatting for positive/negative
      cell.font = { bold: true, color: { argb: this.colors.revenue } };
    }

    ws.getCell(`G${row}`).value = { formula: `=B${row}/${cellRefs['total_units']}` };
    Object.assign(ws.getCell(`G${row}`), this.formats.currencyBold);
    ws.getCell(`H${row}`).value = { formula: `=B${row}/${cellRefs['total_sqft']}` };
    Object.assign(ws.getCell(`H${row}`), this.formats.currencyBold);
    
    const cashFlowRow = row;
    row += 2;

    // CAPITAL EVENTS
    ws.mergeCells(`A${row}:H${row}`);
    const capitalEventsCell = ws.getCell(`A${row}`);
    capitalEventsCell.value = 'CAPITAL EVENTS';
    Object.assign(capitalEventsCell, this.formats.sectionHeaderTimeline);
    row++;

    // Initial Investment
    ws.getCell(`A${row}`).value = 'Initial Investment';
    Object.assign(ws.getCell(`A${row}`), this.formats.text);

    ws.getCell(`B${row}`).value = { formula: `=-(${cellRefs['purchase_price']}*${cellRefs['down_payment']}+${cellRefs['purchase_price']}*${cellRefs['closing_costs']})` };
    Object.assign(ws.getCell(`B${row}`), this.formats.currency);

    for (let year = 2; year <= 5; year++) {
      const cell = ws.getCell(`${String.fromCharCode(65 + year)}${row}`);
      cell.value = 0;
      Object.assign(cell, this.formats.currency);
    }
    
    const initialInvestmentRow = row;
    row++;

    // Property Sale (Year 5)
    ws.getCell(`A${row}`).value = 'Property Sale Analysis (Year 5)';
    Object.assign(ws.getCell(`A${row}`), this.formats.textBold);
    row++;

    // Sale Price
    ws.getCell(`A${row}`).value = 'Sale Price (NOI ÷ Exit Cap Rate)';
    Object.assign(ws.getCell(`A${row}`), this.formats.text);

    for (let year = 1; year <= 4; year++) {
      const cell = ws.getCell(`${String.fromCharCode(65 + year)}${row}`);
      cell.value = 0;
      Object.assign(cell, this.formats.currency);
    }

    ws.getCell(`F${row}`).value = { formula: `=F${noiRow}/${cellRefs['exit_cap_rate']}` };
    Object.assign(ws.getCell(`F${row}`), this.formats.currency);
    
    const salePriceRow = row;
    row++;

    // Selling Costs
    ws.getCell(`A${row}`).value = 'Selling Costs';
    Object.assign(ws.getCell(`A${row}`), this.formats.text);

    for (let year = 1; year <= 4; year++) {
      const cell = ws.getCell(`${String.fromCharCode(65 + year)}${row}`);
      cell.value = 0;
      Object.assign(cell, this.formats.currency);
    }

    ws.getCell(`F${row}`).value = { formula: `=F${salePriceRow}*${cellRefs['selling_costs']}` };
    Object.assign(ws.getCell(`F${row}`), this.formats.currency);
    
    const sellingCostsRow = row;
    row++;

    // Net Sale Proceeds
    ws.getCell(`A${row}`).value = 'Net Sale Proceeds';
    Object.assign(ws.getCell(`A${row}`), this.formats.textBold);

    for (let year = 1; year <= 4; year++) {
      const cell = ws.getCell(`${String.fromCharCode(65 + year)}${row}`);
      cell.value = 0;
      Object.assign(cell, this.formats.currency);
    }

    ws.getCell(`F${row}`).value = { formula: `=F${salePriceRow}-F${sellingCostsRow}` };
    Object.assign(ws.getCell(`F${row}`), this.formats.currencyBold);
    
    const netSaleProceedsRow = row;
    row += 2;

    // TOTAL CASH FLOW
    ws.getCell(`A${row}`).value = 'TOTAL CASH FLOW (Operating + Capital)';
    Object.assign(ws.getCell(`A${row}`), this.formats.textBold);

    for (let year = 1; year <= 4; year++) {
      const cell = ws.getCell(`${String.fromCharCode(65 + year)}${row}`);
      cell.value = { formula: `=${String.fromCharCode(65 + year)}${cashFlowRow}+${String.fromCharCode(65 + year)}${initialInvestmentRow}` };
      Object.assign(cell, this.formats.currencyBold);
      cell.font = { bold: true, color: { argb: this.colors.revenue } };
    }

    // Year 5 includes sale proceeds
    ws.getCell(`F${row}`).value = { formula: `=F${cashFlowRow}+F${netSaleProceedsRow}` };
    Object.assign(ws.getCell(`F${row}`), this.formats.currencyBold);
    ws.getCell(`F${row}`).font = { bold: true, color: { argb: this.colors.revenue } };

    ws.getCell(`G${row}`).value = { formula: `=B${row}/${cellRefs['total_units']}` };
    Object.assign(ws.getCell(`G${row}`), this.formats.currencyBold);
    ws.getCell(`H${row}`).value = { formula: `=B${row}/${cellRefs['total_sqft']}` };
    Object.assign(ws.getCell(`H${row}`), this.formats.currencyBold);

    // Store pro forma row references for use in Executive Summary
    this.proformaRows = {
      grossIncome: rentalIncomeRow,
      totalExpenses: totalExpensesRow,
      noi: noiRow,
      debtService: debtServiceRow,
      cashFlow: cashFlowRow
    };
  }

  private async createAssumptionsSheet(
    ws: ExcelJS.Worksheet,
    propertyData: PropertyData,
    assumptions: InvestmentAssumptions
  ) {
    // Set column widths
    ws.getColumn('A').width = 35;
    ws.getColumn('B').width = 18;
    ws.getColumn('C').width = 25;

    let row = 1;

    // Title
    ws.mergeCells(`A${row}:C${row}`);
    const titleCell = ws.getCell(`A${row}`);
    titleCell.value = 'INVESTMENT ASSUMPTIONS';
    Object.assign(titleCell, this.formats.title);
    row += 2;

    // Property Assumptions
    ws.mergeCells(`A${row}:C${row}`);
    const propAssumptionsCell = ws.getCell(`A${row}`);
    propAssumptionsCell.value = 'PROPERTY ASSUMPTIONS';
    Object.assign(propAssumptionsCell, this.formats.sectionHeaderTimeline);
    row++;

    ws.getCell(`A${row}`).value = 'Assumption';
    Object.assign(ws.getCell(`A${row}`), this.formats.columnHeader);
    ws.getCell(`B${row}`).value = 'Value';
    Object.assign(ws.getCell(`B${row}`), this.formats.columnHeader);
    ws.getCell(`C${row}`).value = 'Notes';
    Object.assign(ws.getCell(`C${row}`), this.formats.columnHeader);
    row++;

    const propAssumptions = [
      ['Purchase Price', propertyData.price, 'Contract price', 'currency'],
      ['Square Footage', propertyData.sqft, 'Gross rentable area', 'number'],
      ['Bedrooms', propertyData.beds, 'Total bedrooms', 'number'],
      ['Bathrooms', propertyData.baths, 'Total bathrooms', 'number'],
      ['Property Type', propertyData.propertyType, 'Property classification', 'text']
    ];

    propAssumptions.forEach(([assumption, value, note, format]) => {
      ws.getCell(`A${row}`).value = assumption;
      Object.assign(ws.getCell(`A${row}`), this.formats.text);
      
      ws.getCell(`B${row}`).value = value;
      Object.assign(ws.getCell(`B${row}`), this.formats[format as keyof typeof this.formats]);
      
      ws.getCell(`C${row}`).value = note;
      Object.assign(ws.getCell(`C${row}`), this.formats.textCenter);
      
      row++;
    });

    row++;

    // Financial Assumptions
    ws.mergeCells(`A${row}:C${row}`);
    const finAssumptionsCell = ws.getCell(`A${row}`);
    finAssumptionsCell.value = 'FINANCIAL ASSUMPTIONS';
    Object.assign(finAssumptionsCell, this.formats.sectionHeaderCosts);
    row++;

    ws.getCell(`A${row}`).value = 'Assumption';
    Object.assign(ws.getCell(`A${row}`), this.formats.columnHeader);
    ws.getCell(`B${row}`).value = 'Value';
    Object.assign(ws.getCell(`B${row}`), this.formats.columnHeader);
    ws.getCell(`C${row}`).value = 'Notes';
    Object.assign(ws.getCell(`C${row}`), this.formats.columnHeader);
    row++;

    const finAssumptions = [
      ['Down Payment %', assumptions.downPaymentPct / 100, 'Percentage of purchase price', 'percentage'],
      ['Interest Rate', assumptions.interestRate / 100, 'Annual interest rate', 'percentage'],
      ['Loan Term (Years)', assumptions.loanTerm, 'Mortgage term in years', 'number'],
      ['Property Tax Rate', assumptions.propertyTaxRate / 100, 'Annual property tax rate', 'percentage'],
      ['Insurance Rate', assumptions.insuranceRate / 100, 'Annual insurance rate', 'percentage'],
      ['Maintenance Rate', assumptions.maintenanceRate / 100, 'Annual maintenance as % of income', 'percentage'],
      ['Capital Reserves Rate', assumptions.capitalReservesRate / 100, 'Annual reserves as % of income', 'percentage'],
      ['Vacancy Rate', assumptions.vacancyRate / 100, 'Expected vacancy rate', 'percentage'],
      ['Closing Costs %', assumptions.closingCostsPct / 100, 'Closing costs as % of price', 'percentage']
    ];

    finAssumptions.forEach(([assumption, value, note, format]) => {
      ws.getCell(`A${row}`).value = assumption;
      Object.assign(ws.getCell(`A${row}`), this.formats.text);
      
      ws.getCell(`B${row}`).value = value;
      Object.assign(ws.getCell(`B${row}`), this.formats[format as keyof typeof this.formats]);
      
      ws.getCell(`C${row}`).value = note;
      Object.assign(ws.getCell(`C${row}`), this.formats.textCenter);
      
      row++;
    });

    row++;

    // Market Assumptions
    ws.mergeCells(`A${row}:C${row}`);
    const marketAssumptionsCell = ws.getCell(`A${row}`);
    marketAssumptionsCell.value = 'MARKET ASSUMPTIONS';
    Object.assign(marketAssumptionsCell, this.formats.sectionHeaderRevenue);
    row++;

    ws.getCell(`A${row}`).value = 'Assumption';
    Object.assign(ws.getCell(`A${row}`), this.formats.columnHeader);
    ws.getCell(`B${row}`).value = 'Value';
    Object.assign(ws.getCell(`B${row}`), this.formats.columnHeader);
    ws.getCell(`C${row}`).value = 'Notes';
    Object.assign(ws.getCell(`C${row}`), this.formats.columnHeader);
    row++;

    const marketAssumptions = [
      ['Annual Rent Growth', 0.03, 'Expected annual rent increase', 'percentage'],
      ['Annual Appreciation', 0.03, 'Expected property value appreciation', 'percentage'],
      ['Inflation Rate', 0.025, 'General inflation for expenses', 'percentage'],
      ['Property Management Fee', 0.08, 'Management fee as % of gross income', 'percentage'],
      ['Selling Costs', 0.06, 'Total costs to sell property', 'percentage']
    ];

    marketAssumptions.forEach(([assumption, value, note, format]) => {
      ws.getCell(`A${row}`).value = assumption;
      Object.assign(ws.getCell(`A${row}`), this.formats.text);
      
      ws.getCell(`B${row}`).value = value;
      Object.assign(ws.getCell(`B${row}`), this.formats[format as keyof typeof this.formats]);
      
      ws.getCell(`C${row}`).value = note;
      Object.assign(ws.getCell(`C${row}`), this.formats.textCenter);
      
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
    for (let i = 1; i <= 8; i++) {
      ws.getColumn(i).width = 12;
    }

    let row = 1;

    // Title
    ws.mergeCells(`A${row}:H${row}`);
    const titleCell = ws.getCell(`A${row}`);
    titleCell.value = 'Sensitivity Analysis';
    Object.assign(titleCell, this.formats.title);
    row += 2;

    // Cap Rate Sensitivity
    ws.mergeCells(`A${row}:H${row}`);
    const capRateHeaderCell = ws.getCell(`A${row}`);
    capRateHeaderCell.value = 'Cap Rate Sensitivity Analysis';
    Object.assign(capRateHeaderCell, this.formats.sectionHeaderRevenue);
    row++;

    // Headers
    ws.getCell(`A${row}`).value = 'Cap Rate';
    Object.assign(ws.getCell(`A${row}`), this.formats.columnHeader);
    
    for (let i = 0; i < 7; i++) {
      const cell = ws.getCell(`${String.fromCharCode(66 + i)}${row}`);
      cell.value = `${4 + i}%`;
      Object.assign(cell, this.formats.columnHeader);
    }
    row++;

    // Property values at different cap rates
    const noi = results.annualNOI || (results.monthlyRent * 12 * 0.8);
    
    for (let rentMultiplier = 0.9; rentMultiplier <= 1.1; rentMultiplier += 0.05) {
      ws.getCell(`A${row}`).value = `${(rentMultiplier * 100).toFixed(0)}% Rent`;
      Object.assign(ws.getCell(`A${row}`), this.formats.text);
      
      for (let capRate = 4; capRate <= 10; capRate++) {
        const adjustedNOI = noi * rentMultiplier;
        const propertyValue = adjustedNOI / (capRate / 100);
        const cell = ws.getCell(`${String.fromCharCode(66 + capRate - 4)}${row}`);
        cell.value = propertyValue;
        Object.assign(cell, this.formats.currency);
        
        // Color code based on current property price
        if (propertyValue > propertyData.price * 1.1) {
          cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'DCFCE7' } };
        } else if (propertyValue < propertyData.price * 0.9) {
          cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FEE2E2' } };
        }
      }
      row++;
    }

    row += 2;

    // Cash-on-Cash Sensitivity
    ws.mergeCells(`A${row}:H${row}`);
    const cocHeaderCell = ws.getCell(`A${row}`);
    cocHeaderCell.value = 'Cash-on-Cash Return Sensitivity';
    Object.assign(cocHeaderCell, this.formats.sectionHeaderCosts);
    row++;

    // Headers
    ws.getCell(`A${row}`).value = 'Down Payment';
    Object.assign(ws.getCell(`A${row}`), this.formats.columnHeader);
    
    for (let i = 0; i < 7; i++) {
      const cell = ws.getCell(`${String.fromCharCode(66 + i)}${row}`);
      cell.value = `${10 + i * 5}%`;
      Object.assign(cell, this.formats.columnHeader);
    }
    row++;

    // Cash-on-cash returns at different down payments and rent levels
    for (let rentMultiplier = 0.9; rentMultiplier <= 1.1; rentMultiplier += 0.05) {
      ws.getCell(`A${row}`).value = `${(rentMultiplier * 100).toFixed(0)}% Rent`;
      Object.assign(ws.getCell(`A${row}`), this.formats.text);
      
      for (let downPaymentPct = 10; downPaymentPct <= 40; downPaymentPct += 5) {
        const adjustedRent = results.monthlyRent * rentMultiplier;
        const downPayment = propertyData.price * (downPaymentPct / 100);
        const closingCosts = propertyData.price * (assumptions.closingCostsPct / 100);
        const totalInvestment = downPayment + closingCosts;
        const annualCashFlow = (adjustedRent - results.monthlyPayment) * 12;
        const cashOnCash = (annualCashFlow / totalInvestment) * 100;
        
        const cell = ws.getCell(`${String.fromCharCode(66 + (downPaymentPct - 10) / 5)}${row}`);
        cell.value = cashOnCash / 100;
        Object.assign(cell, this.formats.percentage);
        
        // Color code based on performance
        if (cashOnCash > 10) {
          cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'DCFCE7' } };
        } else if (cashOnCash < 5) {
          cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FEE2E2' } };
        }
      }
      row++;
    }
  }
}