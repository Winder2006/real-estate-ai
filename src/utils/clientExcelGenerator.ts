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
    // Create workbook
    const workbook = new ExcelJS.Workbook();
    
    // CRITICAL: Force Excel to calculate formulas when file opens
    workbook.calcProperties = {
      fullCalcOnLoad: true,
      calcMode: 'automatic',
      calcOnSave: true,
      forceFullCalc: true
    };
    
    // Create worksheets
    const summaryWs = workbook.addWorksheet('Executive Summary');
    const proformaWs = workbook.addWorksheet('Pro Forma Analysis');
    const assumptionsWs = workbook.addWorksheet('Assumptions');
    const sensitivityWs = workbook.addWorksheet('Sensitivity Analysis');

    // Create formats
    this.createFormats(workbook);

    // Generate sheets in the correct order for cross-sheet references
    await this.createProFormaSheet(proformaWs, propertyData, analysisResults, assumptions, projectName);
    await this.createSummarySheet(summaryWs, propertyData, analysisResults, assumptions, projectName);
    await this.createAssumptionsSheet(assumptionsWs, propertyData, assumptions);
    await this.createSensitivitySheet(sensitivityWs, propertyData, analysisResults, assumptions);

    // Set print settings for all sheets
    [summaryWs, proformaWs, assumptionsWs, sensitivityWs].forEach(ws => {
      ws.pageSetup.paperSize = 9; // A4
      ws.pageSetup.orientation = 'landscape';
      ws.pageSetup.fitToPage = true;
      ws.pageSetup.fitToWidth = 1;
      ws.pageSetup.fitToHeight = 0;
      ws.pageSetup.margins = {
        left: 0.7, right: 0.7,
        top: 0.75, bottom: 0.75,
        header: 0.3, footer: 0.3
      };
    });

    // CRITICAL: Force calculation for all worksheets
    [summaryWs, proformaWs, assumptionsWs, sensitivityWs].forEach(ws => {
      ws.calcProperties = {
        fullCalcOnLoad: true
      };
    });

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
      ['Gross Rental Income', `='Pro Forma Analysis'!B${this.proformaRows.gross_income}/12`, `='Pro Forma Analysis'!B${this.proformaRows.gross_income}`, `=SUM('Pro Forma Analysis'!B${this.proformaRows.gross_income}:F${this.proformaRows.gross_income})`],
      ['Total Operating Expenses', `='Pro Forma Analysis'!B${this.proformaRows.total_expenses}/12`, `='Pro Forma Analysis'!B${this.proformaRows.total_expenses}`, `=SUM('Pro Forma Analysis'!B${this.proformaRows.total_expenses}:F${this.proformaRows.total_expenses})`],
      ['Net Operating Income', `='Pro Forma Analysis'!B${this.proformaRows.noi}/12`, `='Pro Forma Analysis'!B${this.proformaRows.noi}`, `=SUM('Pro Forma Analysis'!B${this.proformaRows.noi}:F${this.proformaRows.noi})`],
      ['Debt Service', `='Pro Forma Analysis'!B${this.proformaRows.debt_service}/12`, `='Pro Forma Analysis'!B${this.proformaRows.debt_service}`, `=SUM('Pro Forma Analysis'!B${this.proformaRows.debt_service}:F${this.proformaRows.debt_service})`],
      ['Before-Tax Cash Flow (Operations)', `='Pro Forma Analysis'!B${this.proformaRows.before_tax_cash_flow}/12`, `='Pro Forma Analysis'!B${this.proformaRows.before_tax_cash_flow}`, `=SUM('Pro Forma Analysis'!B${this.proformaRows.before_tax_cash_flow}:F${this.proformaRows.before_tax_cash_flow})`]
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
    // Initialize row references for cross-sheet use
    this.proformaRows = {};
    
    // Set column widths exactly like backend
    ws.getColumn('A').width = 35;   // Line items (wider for long descriptions)
    ws.getColumn('B').width = 14;   // Year 1
    ws.getColumn('C').width = 14;   // Year 2
    ws.getColumn('D').width = 14;   // Year 3
    ws.getColumn('E').width = 14;   // Year 4
    ws.getColumn('F').width = 14;   // Year 5
    ws.getColumn('G').width = 16;   // Per unit column
    ws.getColumn('H').width = 16;   // Per SF column
    ws.getColumn('I').width = 8;    // Empty columns (narrow)
    ws.getColumn('J').width = 8;    // Empty columns (narrow)
    ws.getColumn('K').width = 25;   // Assumption labels (wider)
    ws.getColumn('L').width = 16;   // Assumption values

    // Define variables for use throughout the sheet - ensure they match the correct property data
    const units = propertyData.totalUnits || 1;
    const sqft = propertyData.sqft || 1000;

    let row = 1; // Start at row 1 (0-indexed)

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

    // SETUP LOCAL ASSUMPTIONS - Move to column K for cleaner layout
    const assumptionCol = 11; // Column K (1-indexed for ExcelJS)
    let assumptionRow = 2;   // Start at row 2 (1-indexed)
    
    ws.mergeCells(`K${assumptionRow}:L${assumptionRow}`);
    const assumptionHeaderCell = ws.getCell(`K${assumptionRow}`);
    assumptionHeaderCell.value = 'KEY ASSUMPTIONS (All values are editable)';
    Object.assign(assumptionHeaderCell, this.formats.sectionHeaderTimeline);
    assumptionRow++;

    // Calculate assumption values from form data - exactly like backend
    const purchasePrice = propertyData.price;
    const downPaymentPct = assumptions.downPaymentPct / 100;
    const interestRate = assumptions.interestRate / 100;
    let loanTerm = assumptions.loanTerm;
    if (loanTerm <= 36) {  // Convert construction to permanent
      loanTerm = 30;
    } else if (loanTerm > 100) {
      loanTerm = loanTerm / 12;
    }
    const closingCostsPct = 0.03;
    const totalUnits = propertyData.totalUnits || 1;
    const totalSqft = propertyData.sqft;
    const totalMonthlyRent = results.monthlyRent;
    const baseAnnualRent = totalMonthlyRent * 12;
    const rentGrowth = 0.03;

    // Validate critical values - ensure they're not undefined
    console.log('Pro Forma Values:', {
      purchasePrice,
      downPaymentPct,
      interestRate,
      loanTerm,
      totalUnits,
      totalSqft,
      totalMonthlyRent,
      baseAnnualRent,
      propertyTaxRate: assumptions.propertyTaxRate / 100,
      insuranceRate: assumptions.insuranceRate / 100,
      maintenanceRate: assumptions.maintenanceRate / 100,
      capitalReservesRate: assumptions.capitalReservesRate / 100
    });

    // Write all assumptions to cells in column K - exactly like backend
    const assumptionData = [
      ['Purchase Price', purchasePrice || 0],
      ['Down Payment %', downPaymentPct || 0.20],
      ['Interest Rate', interestRate || 0.05],
      ['Loan Term (Years)', loanTerm || 30],
      ['Closing Costs %', closingCostsPct],
      ['Property Mgmt %', 0.08],
      ['Property Tax %', (assumptions.propertyTaxRate / 100) || 0.02],
      ['Insurance %', (assumptions.insuranceRate / 100) || 0.005],
      ['Maintenance %', (assumptions.maintenanceRate / 100) || 0.01],
      ['Capital Reserves %', (assumptions.capitalReservesRate / 100) || 0.01],
      ['Utilities %', 0.005],
      ['Legal %', 0.002],
      ['Other Expenses %', 0.003],
      ['Inflation Rate', 0.025],
      ['Total Units', totalUnits || 1],
      ['Total Square Feet', totalSqft || 1000],
      ['Annual Gross Rent', baseAnnualRent || 24000],
      ['Rent Growth Rate', rentGrowth],
      ['Vacancy Rate', 0.05],
      ['NOI Margin', 0.70],
      ['Exit Cap Rate', 0.06],
      ['Selling Costs %', 0.07]
    ];

    assumptionData.forEach(([label, value], index) => {
      const currentRow = assumptionRow + index;
      ws.getCell(`K${currentRow}`).value = label;
      Object.assign(ws.getCell(`K${currentRow}`), this.formats.textBold);
      
      // Ensure value is a number, not undefined
      const numValue = typeof value === 'number' ? value : 0;
      ws.getCell(`L${currentRow}`).value = numValue;
      
      // Apply correct format based on value type
      if (label.includes('%') || label.includes('Rate')) {
        Object.assign(ws.getCell(`L${currentRow}`), this.formats.inputPercentage);
      } else if (label.includes('Price') || label.includes('Rent')) {
        Object.assign(ws.getCell(`L${currentRow}`), this.formats.inputCurrency);
      } else {
        Object.assign(ws.getCell(`L${currentRow}`), this.formats.input);
      }
    });

    // OVERRIDE cell_refs to use LOCAL cells in column L - exactly like backend
    const cellRefs = {
      'purchase_price': `L${assumptionRow + 1}`,
      'down_payment_pct': `L${assumptionRow + 2}`,
      'interest_rate': `L${assumptionRow + 3}`,
      'loan_term': `L${assumptionRow + 4}`,
      'closing_costs_pct': `L${assumptionRow + 5}`,
      'property_mgmt_rate': `L${assumptionRow + 6}`,
      'property_tax_rate': `L${assumptionRow + 7}`,
      'insurance_rate': `L${assumptionRow + 8}`,
      'maintenance_rate': `L${assumptionRow + 9}`,
      'capital_reserves_rate': `L${assumptionRow + 10}`,
      'utilities_rate': `L${assumptionRow + 11}`,
      'legal_rate': `L${assumptionRow + 12}`,
      'other_expenses_rate': `L${assumptionRow + 13}`,
      'inflation_rate': `L${assumptionRow + 14}`,
      'total_units': `L${assumptionRow + 15}`,
      'total_sqft': `L${assumptionRow + 16}`,
      'annual_rent': `L${assumptionRow + 17}`,
      'rent_growth': `L${assumptionRow + 18}`,
      'vacancy_rate': `L${assumptionRow + 19}`,
      'noi_margin': `L${assumptionRow + 20}`,
      'cap_rate_exit': `L${assumptionRow + 21}`,
      'selling_costs_pct': `L${assumptionRow + 22}`
    };

    console.log('Cell References:', cellRefs);
    console.log('Assumption Row starts at:', assumptionRow);

    // Define local references for all calculations
    const totalUnitsRef = cellRefs['total_units'];
    const totalSqftRef = cellRefs['total_sqft'];
    const annualRentRef = cellRefs['annual_rent'];
    const rentGrowthRef = cellRefs['rent_growth'];
    const vacancyRateRef = cellRefs['vacancy_rate'];

    row = 4; // Start the main pro forma at row 4 (1-indexed)

    // Column headers for years - exactly like backend
    ws.getCell(`A${row}`).value = 'Line Item';
    Object.assign(ws.getCell(`A${row}`), this.formats.columnHeader);
    ws.getCell(`B${row}`).value = 'Year 1';
    Object.assign(ws.getCell(`B${row}`), this.formats.columnHeader);
    ws.getCell(`C${row}`).value = 'Year 2';
    Object.assign(ws.getCell(`C${row}`), this.formats.columnHeader);
    ws.getCell(`D${row}`).value = 'Year 3';
    Object.assign(ws.getCell(`D${row}`), this.formats.columnHeader);
    ws.getCell(`E${row}`).value = 'Year 4';
    Object.assign(ws.getCell(`E${row}`), this.formats.columnHeader);
    ws.getCell(`F${row}`).value = 'Year 5';
    Object.assign(ws.getCell(`F${row}`), this.formats.columnHeader);
    ws.getCell(`G${row}`).value = '$ per Unit';
    Object.assign(ws.getCell(`G${row}`), this.formats.columnHeader);
    ws.getCell(`H${row}`).value = '$ per SF';
    Object.assign(ws.getCell(`H${row}`), this.formats.columnHeader);
    row++;

    // GROSS SALES / REVENUE
    ws.mergeCells(`A${row}:H${row}`);
    const grossRentalCell = ws.getCell(`A${row}`);
    grossRentalCell.value = 'GROSS RENTAL INCOME';
    Object.assign(grossRentalCell, this.formats.sectionHeaderRevenue);
    row++;

    // Rental Income - USE CALCULATED VALUES ONLY (like backend does)
    ws.getCell(`A${row}`).value = 'Gross Rental Income';
    Object.assign(ws.getCell(`A${row}`), this.formats.text);

    // Calculate actual values directly in JavaScript (like backend does in Python)
    for (let year = 0; year < 5; year++) {
      const cell = ws.getCell(`${String.fromCharCode(66 + year)}${row}`);
      const calculatedValue = baseAnnualRent * Math.pow(1 + rentGrowth, year);
      cell.value = calculatedValue;
      Object.assign(cell, this.formats.currency);
    }

    // Per unit and per SF calculations with direct values
    ws.getCell(`G${row}`).value = baseAnnualRent / totalUnits;
    Object.assign(ws.getCell(`G${row}`), this.formats.currency);
    ws.getCell(`H${row}`).value = baseAnnualRent / totalSqft;
    Object.assign(ws.getCell(`H${row}`), this.formats.currencyPerSF);
    const rentalIncomeRow = row;
    row++;

    // Other Income - USE CALCULATED VALUES ONLY
    const otherIncomeRate = 0.05;
    ws.getCell(`A${row}`).value = 'Other Income (5% of Gross Rent)';
    Object.assign(ws.getCell(`A${row}`), this.formats.text);
    
    for (let year = 0; year < 5; year++) {
      const cell = ws.getCell(`${String.fromCharCode(66 + year)}${row}`);
      const grossRentalIncome = baseAnnualRent * Math.pow(1 + rentGrowth, year);
      const calculatedValue = grossRentalIncome * otherIncomeRate;
      cell.value = calculatedValue;
      Object.assign(cell, this.formats.currency);
    }
    ws.getCell(`G${row}`).value = (baseAnnualRent * otherIncomeRate) / totalUnits;
    Object.assign(ws.getCell(`G${row}`), this.formats.currency);
    ws.getCell(`H${row}`).value = (baseAnnualRent * otherIncomeRate) / totalSqft;
    Object.assign(ws.getCell(`H${row}`), this.formats.currencyPerSF);
    const otherIncomeRow = row;
    row++;

    // Gross Income Total - USE CALCULATED VALUES ONLY
    ws.getCell(`A${row}`).value = 'TOTAL GROSS INCOME';
    Object.assign(ws.getCell(`A${row}`), this.formats.textBold);
    
    for (let year = 0; year < 5; year++) {
      const cell = ws.getCell(`${String.fromCharCode(66 + year)}${row}`);
      const grossRentalIncome = baseAnnualRent * Math.pow(1 + rentGrowth, year);
      const otherIncome = grossRentalIncome * otherIncomeRate;
      const calculatedValue = grossRentalIncome + otherIncome;
      cell.value = calculatedValue;
      Object.assign(cell, this.formats.currencyBold);
    }
    ws.getCell(`G${row}`).value = (baseAnnualRent * (1 + otherIncomeRate)) / totalUnits;
    Object.assign(ws.getCell(`G${row}`), this.formats.currency);
    ws.getCell(`H${row}`).value = (baseAnnualRent * (1 + otherIncomeRate)) / totalSqft;
    Object.assign(ws.getCell(`H${row}`), this.formats.currencyPerSF);
    const totalGrossIncomeRow = row; // Store this row reference
    // Store gross income row for cross-sheet reference
    this.proformaRows['gross_income'] = totalGrossIncomeRow;
    row += 2;

    // OPERATING EXPENSES
    ws.mergeCells(`A${row}:H${row}`);
    const expensesHeaderCell = ws.getCell(`A${row}`);
    expensesHeaderCell.value = 'OPERATING EXPENSES';
    Object.assign(expensesHeaderCell, this.formats.sectionHeaderCosts);
    row++;

    // Vacancy & Credit Loss - USE CALCULATED VALUES ONLY
    ws.getCell(`A${row}`).value = 'Vacancy & Credit Loss';
    Object.assign(ws.getCell(`A${row}`), this.formats.text);
    
    for (let year = 0; year < 5; year++) {
      const cell = ws.getCell(`${String.fromCharCode(66 + year)}${row}`);
      const grossRentalIncome = baseAnnualRent * Math.pow(1 + rentGrowth, year);
      const otherIncome = grossRentalIncome * otherIncomeRate;
      const totalGrossIncome = grossRentalIncome + otherIncome;
      const calculatedValue = totalGrossIncome * 0.05; // 5% vacancy rate
      cell.value = calculatedValue;
      Object.assign(cell, this.formats.currency);
    }
    ws.getCell(`G${row}`).value = (baseAnnualRent * (1 + otherIncomeRate) * 0.05) / totalUnits;
    Object.assign(ws.getCell(`G${row}`), this.formats.currency);
    ws.getCell(`H${row}`).value = (baseAnnualRent * (1 + otherIncomeRate) * 0.05) / totalSqft;
    Object.assign(ws.getCell(`H${row}`), this.formats.currencyPerSF);
    const vacancyLossRow = row;
    row++;

    // Effective Gross Income - USE CALCULATED VALUES ONLY
    ws.getCell(`A${row}`).value = 'EFFECTIVE GROSS INCOME';
    Object.assign(ws.getCell(`A${row}`), this.formats.textBold);
    
    for (let year = 0; year < 5; year++) {
      const cell = ws.getCell(`${String.fromCharCode(66 + year)}${row}`);
      const grossRentalIncome = baseAnnualRent * Math.pow(1 + rentGrowth, year);
      const otherIncome = grossRentalIncome * otherIncomeRate;
      const totalGrossIncome = grossRentalIncome + otherIncome;
      const vacancyLoss = totalGrossIncome * 0.05;
      const calculatedValue = totalGrossIncome - vacancyLoss;
      cell.value = calculatedValue;
      Object.assign(cell, this.formats.currencyBold);
    }
    const egiValue = baseAnnualRent * (1 + otherIncomeRate) * 0.95; // After vacancy
    ws.getCell(`G${row}`).value = egiValue / totalUnits;
    Object.assign(ws.getCell(`G${row}`), this.formats.currency);
    ws.getCell(`H${row}`).value = egiValue / totalSqft;
    Object.assign(ws.getCell(`H${row}`), this.formats.currencyPerSF);
    const egiRow = row; // Store the EGI row reference
    row += 2;

    // Operating Expenses Detail - Use cell references for ALL rates - exactly like backend
    const propertyMgmtRateRef = cellRefs['property_mgmt_rate'];
    const propertyTaxRateRef = cellRefs['property_tax_rate'];
    const insuranceRateRef = cellRefs['insurance_rate'];
    const maintenanceRateRef = cellRefs['maintenance_rate'];
    const capitalReservesRateRef = cellRefs['capital_reserves_rate'];
    const utilitiesRateRef = cellRefs['utilities_rate'];
    const legalRateRef = cellRefs['legal_rate'];
    const otherExpensesRateRef = cellRefs['other_expenses_rate'];
    const inflationRateRef = cellRefs['inflation_rate'];

    const expenses = [
      ['Property Management', 'percentage', propertyMgmtRateRef, 'egi'],
      ['Property Taxes', 'fixed_rate', propertyTaxRateRef, 'purchase_price'],
      ['Insurance', 'fixed_rate', insuranceRateRef, 'purchase_price'],
      ['Maintenance & Repairs', 'percentage', maintenanceRateRef, 'egi'],
      ['Capital Reserves', 'percentage', capitalReservesRateRef, 'egi'],
      ['Utilities', 'percentage', utilitiesRateRef, 'egi'],
      ['Legal & Professional', 'percentage', legalRateRef, 'egi'],
      ['Other Operating Expenses', 'percentage', otherExpensesRateRef, 'egi']
    ];

    const expenseStartRow = row;

    expenses.forEach(([expenseName, calcType, rateRef, base]) => {
      ws.getCell(`A${row}`).value = expenseName;
      Object.assign(ws.getCell(`A${row}`), this.formats.text);

      if (calcType === 'percentage') {
        for (let year = 0; year < 5; year++) {
          const colLetter = String.fromCharCode(66 + year);
          const cell = ws.getCell(`${colLetter}${row}`);
          
          // GUARANTEED VALUE: Calculate directly first
          const grossRentalIncome = baseAnnualRent * Math.pow(1 + rentGrowth, year);
          const otherIncome = grossRentalIncome * 0.05;
          const totalGrossIncome = grossRentalIncome + otherIncome;
          const vacancyLoss = totalGrossIncome * 0.05;
          const effectiveGrossIncome = totalGrossIncome - vacancyLoss;
          
          // Get the rate based on expense type
          let rate = 0.08; // default property management
          if (expenseName === 'Property Management') rate = 0.08;
          else if (expenseName === 'Maintenance & Repairs') rate = (assumptions.maintenanceRate / 100) || 0.01;
          else if (expenseName === 'Capital Reserves') rate = (assumptions.capitalReservesRate / 100) || 0.01;
          else if (expenseName === 'Utilities') rate = 0.005;
          else if (expenseName === 'Legal & Professional') rate = 0.002;
          else if (expenseName === 'Other Operating Expenses') rate = 0.003;
          
          const calculatedValue = effectiveGrossIncome * rate;
          cell.value = calculatedValue;
          
          // THEN add formula for live updates
          if (baseAnnualRent > 0) {
            cell.value = { formula: `=${colLetter}${egiRow}*${rateRef}` };
          }
          
          Object.assign(cell, this.formats.currency);
        }
      } else if (calcType === 'fixed_rate') {
        // For property taxes and insurance - use local purchase price cell
        for (let year = 0; year < 5; year++) {
          const cell = ws.getCell(`${String.fromCharCode(66 + year)}${row}`);
          
          // GUARANTEED VALUE: Calculate directly first
          let rate = 0.02; // default
          if (expenseName === 'Property Taxes') rate = (assumptions.propertyTaxRate / 100) || 0.02;
          else if (expenseName === 'Insurance') rate = (assumptions.insuranceRate / 100) || 0.005;
          
          const calculatedValue = purchasePrice * rate * Math.pow(1.025, year);
          cell.value = calculatedValue;
          
          // THEN add formula for live updates
          if (purchasePrice > 0) {
            cell.value = { formula: `=${cellRefs['purchase_price']}*${rateRef}*POWER(1+${inflationRateRef},${year})` };
          }
          
          Object.assign(cell, this.formats.currency);
        }
      }

      ws.getCell(`G${row}`).value = { formula: `=B${row}/${totalUnitsRef}` };
      Object.assign(ws.getCell(`G${row}`), this.formats.currency);
      ws.getCell(`H${row}`).value = { formula: `=B${row}/${totalSqftRef}` };
      Object.assign(ws.getCell(`H${row}`), this.formats.currencyPerSF);
      
      row++;
    });

    // Total Operating Expenses - exactly like backend
    ws.getCell(`A${row}`).value = 'TOTAL OPERATING EXPENSES';
    Object.assign(ws.getCell(`A${row}`), this.formats.textBold);
    
    for (let year = 0; year < 5; year++) {
      const colLetter = String.fromCharCode(66 + year); // B, C, D, E, F for years 1-5
      const cell = ws.getCell(`${colLetter}${row}`);
      cell.value = { formula: `=SUM(${colLetter}${expenseStartRow}:${colLetter}${row - 1})` };
      Object.assign(cell, this.formats.currencyBold);
    }
    ws.getCell(`G${row}`).value = { formula: `=B${row}/${totalUnitsRef}` };
    Object.assign(ws.getCell(`G${row}`), this.formats.currency);
    ws.getCell(`H${row}`).value = { formula: `=B${row}/${totalSqftRef}` };
    Object.assign(ws.getCell(`H${row}`), this.formats.currencyPerSF);
    const totalExpensesRow = row; // Store the total expenses row reference
    // Store total expenses row for cross-sheet reference
    this.proformaRows['total_expenses'] = totalExpensesRow;
    row += 2;

    // NET OPERATING INCOME - exactly like backend
    ws.mergeCells(`A${row}:H${row}`);
    const noiHeaderCell = ws.getCell(`A${row}`);
    noiHeaderCell.value = 'NET OPERATING INCOME';
    Object.assign(noiHeaderCell, this.formats.sectionHeaderRevenue);
    row++;

    ws.getCell(`A${row}`).value = 'NET OPERATING INCOME (NOI)';
    Object.assign(ws.getCell(`A${row}`), this.formats.textBold);
    
    // Use the stored row references for accurate calculation
    for (let year = 0; year < 5; year++) {
      const colLetter = String.fromCharCode(66 + year); // B, C, D, E, F for years 1-5
      const cell = ws.getCell(`${colLetter}${row}`);
      cell.value = { formula: `=${colLetter}${egiRow}-${colLetter}${totalExpensesRow}` };
      Object.assign(cell, this.formats.currencyBold);
    }
    ws.getCell(`G${row}`).value = { formula: `=B${row}/${totalUnitsRef}` };
    Object.assign(ws.getCell(`G${row}`), this.formats.currency);
    ws.getCell(`H${row}`).value = { formula: `=B${row}/${totalSqftRef}` };
    Object.assign(ws.getCell(`H${row}`), this.formats.currencyPerSF);
    const noiRow = row;
    // Store NOI row for cross-sheet reference
    this.proformaRows['noi'] = noiRow;
    row += 2;

    // DEBT SERVICE - exactly like backend
    ws.mergeCells(`A${row}:H${row}`);
    const debtHeaderCell = ws.getCell(`A${row}`);
    debtHeaderCell.value = 'DEBT SERVICE';
    Object.assign(debtHeaderCell, this.formats.sectionHeaderCosts);
    row++;

    ws.getCell(`A${row}`).value = 'Annual Debt Service (P&I)';
    Object.assign(ws.getCell(`A${row}`), this.formats.text);

    // Use the backend's debt formula approach - HYBRID
    for (let year = 0; year < 5; year++) {
      const cell = ws.getCell(`${String.fromCharCode(66 + year)}${row}`);
      
      // GUARANTEED VALUE: Calculate directly first
      const loanAmount = purchasePrice * (1 - downPaymentPct);
      const calculatedDebtService = loanAmount * interestRate * 1.1; // Simplified debt service calculation
      cell.value = calculatedDebtService;
      
      // THEN add formula for live updates
      if (purchasePrice > 0) {
        cell.value = { formula: `=(${cellRefs['purchase_price']}*(1-${cellRefs['down_payment_pct']}))*${cellRefs['interest_rate']}*1.1` };
      }
      
      Object.assign(cell, this.formats.currency);
    }
    ws.getCell(`G${row}`).value = { formula: `=B${row}/${totalUnitsRef}` };
    Object.assign(ws.getCell(`G${row}`), this.formats.currency);
    ws.getCell(`H${row}`).value = { formula: `=B${row}/${totalSqftRef}` };
    Object.assign(ws.getCell(`H${row}`), this.formats.currencyPerSF);
    const debtServiceRow = row;
    // Store debt service row for cross-sheet reference
    this.proformaRows['debt_service'] = debtServiceRow;
    row += 2;

    // CASH FLOW FROM OPERATIONS - exactly like backend
    ws.mergeCells(`A${row}:H${row}`);
    const cashFlowHeaderCell = ws.getCell(`A${row}`);
    cashFlowHeaderCell.value = 'CASH FLOW FROM OPERATIONS';
    Object.assign(cashFlowHeaderCell, this.formats.sectionHeaderEquity);
    row++;

    ws.getCell(`A${row}`).value = 'Before-Tax Cash Flow';
    Object.assign(ws.getCell(`A${row}`), this.formats.textBold);
    
    for (let year = 0; year < 5; year++) {
      const colLetter = String.fromCharCode(66 + year); // B, C, D, E, F for years 1-5
      const cell = ws.getCell(`${colLetter}${row}`);
      cell.value = { formula: `=${colLetter}${noiRow}-${colLetter}${debtServiceRow}` };
      Object.assign(cell, this.formats.currencyBold);
    }
    ws.getCell(`G${row}`).value = { formula: `=B${row}/${totalUnitsRef}` };
    Object.assign(ws.getCell(`G${row}`), this.formats.currency);
    ws.getCell(`H${row}`).value = { formula: `=B${row}/${totalSqftRef}` };
    Object.assign(ws.getCell(`H${row}`), this.formats.currencyPerSF);
    const beforeTaxCashFlowRow = row;
    // Store cash flow row for cross-sheet reference
    this.proformaRows['before_tax_cash_flow'] = beforeTaxCashFlowRow;
    row += 2;

    // CAPITAL EVENTS - exactly like backend
    ws.mergeCells(`A${row}:H${row}`);
    const capitalEventsCell = ws.getCell(`A${row}`);
    capitalEventsCell.value = 'CAPITAL EVENTS';
    Object.assign(capitalEventsCell, this.formats.sectionHeaderTimeline);
    row++;

    // Initial Investment - exactly like backend
    ws.getCell(`A${row}`).value = 'Initial Investment';
    Object.assign(ws.getCell(`A${row}`), this.formats.text);
    
    // Initial investment = Down Payment + Closing Costs using local cells
    ws.getCell(`B${row}`).value = { formula: `=-(${cellRefs['purchase_price']}*${cellRefs['down_payment_pct']}+${cellRefs['purchase_price']}*${cellRefs['closing_costs_pct']})` };
    Object.assign(ws.getCell(`B${row}`), this.formats.currency);
    
    for (let year = 1; year < 5; year++) {
      const cell = ws.getCell(`${String.fromCharCode(66 + year)}${row}`);
      cell.value = 0;
      Object.assign(cell, this.formats.currency);
    }
    const initialInvestmentRow = row;
    row++;

    // Property Sale Analysis (Year 5) - exactly like backend
    ws.getCell(`A${row}`).value = 'Property Sale Analysis (Year 5)';
    Object.assign(ws.getCell(`A${row}`), this.formats.textBold);
    row++;

    // Sale Price = NOI Year 5 / Exit Cap Rate - Use local cell references
    const capRateExitRef = cellRefs['cap_rate_exit'];
    ws.getCell(`A${row}`).value = 'Sale Price (NOI ÷ Exit Cap Rate)';
    Object.assign(ws.getCell(`A${row}`), this.formats.text);
    
    for (let year = 0; year < 4; year++) {
      const cell = ws.getCell(`${String.fromCharCode(66 + year)}${row}`);
      cell.value = 0;
      Object.assign(cell, this.formats.currency);
    }
    // Use cell reference for exit cap rate
    ws.getCell(`F${row}`).value = { formula: `=F${noiRow}/${capRateExitRef}` };
    Object.assign(ws.getCell(`F${row}`), this.formats.currency);
    const salePriceRow = row;
    row++;

    // Selling Costs - exactly like backend
    const sellingCostsPctRef = cellRefs['selling_costs_pct'];
    ws.getCell(`A${row}`).value = 'Selling Costs';
    Object.assign(ws.getCell(`A${row}`), this.formats.text);
    
    for (let year = 0; year < 4; year++) {
      const cell = ws.getCell(`${String.fromCharCode(66 + year)}${row}`);
      cell.value = 0;
      Object.assign(cell, this.formats.currency);
    }
    // Reference the sale price in column F (Year 5)
    ws.getCell(`F${row}`).value = { formula: `=F${salePriceRow}*${sellingCostsPctRef}` };
    Object.assign(ws.getCell(`F${row}`), this.formats.currency);
    const sellingCostsRow = row;
    row++;

    // Remaining Loan Balance - exactly like backend
    ws.getCell(`A${row}`).value = 'Remaining Loan Balance';
    Object.assign(ws.getCell(`A${row}`), this.formats.text);
    
    for (let year = 0; year < 4; year++) {
      const cell = ws.getCell(`${String.fromCharCode(66 + year)}${row}`);
      cell.value = 0;
      Object.assign(cell, this.formats.currency);
    }
    // Approximation: 85% of original loan amount remains after 5 years (typical for 30-year loan)
    const remainingBalanceFormula = `=(${cellRefs['purchase_price']}*(1-${cellRefs['down_payment_pct']}))*0.85`;
    ws.getCell(`F${row}`).value = { formula: remainingBalanceFormula };
    Object.assign(ws.getCell(`F${row}`), this.formats.currency);
    const remainingBalanceRow = row;
    row++;

    // Net Sale Proceeds - exactly like backend
    ws.getCell(`A${row}`).value = 'Net Sale Proceeds';
    Object.assign(ws.getCell(`A${row}`), this.formats.textBold);
    
    for (let year = 0; year < 4; year++) {
      const cell = ws.getCell(`${String.fromCharCode(66 + year)}${row}`);
      cell.value = 0;
      Object.assign(cell, this.formats.currency);
    }
    // Formula: Sale Price - Selling Costs - Remaining Loan Balance
    ws.getCell(`F${row}`).value = { formula: `=F${salePriceRow}-F${sellingCostsRow}-F${remainingBalanceRow}` };
    Object.assign(ws.getCell(`F${row}`), this.formats.currencyBold);
    const netSaleProceedsRow = row;
    row += 2;

    // TOTAL RETURNS - exactly like backend
    ws.mergeCells(`A${row}:H${row}`);
    const totalReturnsCell = ws.getCell(`A${row}`);
    totalReturnsCell.value = 'TOTAL INVESTMENT RETURNS';
    Object.assign(totalReturnsCell, this.formats.sectionHeaderEquity);
    row++;

    // Initial Investment (Year 0) - Reference the earlier calculation
    ws.getCell(`A${row}`).value = 'Initial Investment';
    Object.assign(ws.getCell(`A${row}`), this.formats.textBold);
    
    // Reference the initial investment row from capital events
    ws.getCell(`B${row}`).value = { formula: `=B${initialInvestmentRow}` };
    Object.assign(ws.getCell(`B${row}`), this.formats.currencyBold);
    
    for (let year = 1; year < 5; year++) {
      const cell = ws.getCell(`${String.fromCharCode(66 + year)}${row}`);
      cell.value = 0;
      Object.assign(cell, this.formats.currency);
    }
    const initialInvRow = row;
    row++;

    ws.getCell(`A${row}`).value = 'Total Cash Flow';
    Object.assign(ws.getCell(`A${row}`), this.formats.textBold);

    for (let year = 0; year < 5; year++) {
      const colLetter = String.fromCharCode(66 + year); // B, C, D, E, F for years 1-5
      const cell = ws.getCell(`${colLetter}${row}`);
      
      if (year === 0) {
        // Year 1: Initial Investment + Before-Tax Cash Flow
        cell.value = { formula: `=B${initialInvRow}+B${beforeTaxCashFlowRow}` };
      } else if (year === 4) {
        // Year 5: Before-Tax Cash Flow + Net Sale Proceeds
        cell.value = { formula: `=F${beforeTaxCashFlowRow}+F${netSaleProceedsRow}` };
      } else {
        // Years 2-4: Just Before-Tax Cash Flow
        cell.value = { formula: `=${colLetter}${beforeTaxCashFlowRow}` };
      }
      Object.assign(cell, this.formats.currencyBold);
    }
    const totalCashFlowRow = row;
    row += 2;

    // Add IRR and Equity Multiple calculations - exactly like backend
    ws.getCell(`A${row}`).value = 'Investment Performance Metrics';
    Object.assign(ws.getCell(`A${row}`), this.formats.textBold);
    row++;

    // IRR Calculation
    ws.getCell(`A${row}`).value = 'IRR (Internal Rate of Return)';
    Object.assign(ws.getCell(`A${row}`), this.formats.text);
    ws.getCell(`B${row}`).value = { formula: `=IRR(B${totalCashFlowRow}:F${totalCashFlowRow})` };
    Object.assign(ws.getCell(`B${row}`), this.formats.percentage);
    row++;

    // Equity Multiple 
    ws.getCell(`A${row}`).value = 'Equity Multiple';
    Object.assign(ws.getCell(`A${row}`), this.formats.text);
    ws.getCell(`B${row}`).value = { formula: `=SUM(C${totalCashFlowRow}:F${totalCashFlowRow})/ABS(B${totalCashFlowRow})` };
    Object.assign(ws.getCell(`B${row}`), this.formats.number);
    row++;

    // Total ROI (Unlevered) - calculated using formulas  
    ws.getCell(`A${row}`).value = 'Total ROI (Unlevered)';
    Object.assign(ws.getCell(`A${row}`), this.formats.text);
    ws.getCell(`B${row}`).value = { formula: `=(SUM(C${totalCashFlowRow}:F${totalCashFlowRow})/ABS(B${initialInvestmentRow})-1)` };
    Object.assign(ws.getCell(`B${row}`), this.formats.percentage);
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