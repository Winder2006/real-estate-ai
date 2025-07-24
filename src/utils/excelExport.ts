import { ClientExcelGenerator } from './clientExcelGenerator';

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

export const downloadExcelReport = async (
  propertyData: PropertyData,
  analysisResults: AnalysisResults,
  assumptions: InvestmentAssumptions,
  projectName?: string
): Promise<void> => {
  try {
    // Create project name if not provided
    const finalProjectName = projectName || `Investment Analysis - ${propertyData.address}`;

    // Generate Excel file using client-side generator
    const generator = new ClientExcelGenerator();
    const buffer = await generator.generateProForma(
      propertyData,
      analysisResults,
      assumptions,
      finalProjectName
    );

    // Create blob from buffer
    const blob = new Blob([buffer], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    });
    
    // Create download link
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    
    // Generate filename
    const addressClean = propertyData.address.replace(/[^a-zA-Z0-9]/g, '_');
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[-:]/g, '');
    link.download = `Real_Estate_Pro_Forma_${addressClean}_${timestamp}.xlsx`;
    
    // Trigger download
    document.body.appendChild(link);
    link.click();
    
    // Cleanup
    link.remove();
    window.URL.revokeObjectURL(url);
    
  } catch (error) {
    console.error('Excel export failed:', error);
    throw error;
  }
};

// Generate a project name based on property data
export const generateProjectName = (propertyData: PropertyData): string => {
  const address = propertyData.address || 'Unknown Address';
  const type = propertyData.propertyType || 'Property';
  return `${type} Investment Analysis - ${address}`;
};

// Utility to validate data before export
export const validateExportData = (
  propertyData: PropertyData,
  analysisResults: AnalysisResults,
  assumptions: InvestmentAssumptions
): { isValid: boolean; errors: string[] } => {
  const errors: string[] = [];

  // Validate property data
  if (!propertyData.address || propertyData.address.trim() === '') {
    errors.push('Property address is required');
  }
  
  if (!propertyData.price || propertyData.price <= 0) {
    errors.push('Property price must be greater than 0');
  }
  
  if (!propertyData.sqft || propertyData.sqft <= 0) {
    errors.push('Square footage must be greater than 0');
  }

  // Validate analysis results
  if (!analysisResults.monthlyRent || analysisResults.monthlyRent <= 0) {
    errors.push('Monthly rent must be calculated');
  }

  // Validate assumptions
  if (!assumptions.downPaymentPct || assumptions.downPaymentPct <= 0) {
    errors.push('Down payment percentage must be greater than 0');
  }
  
  if (!assumptions.interestRate || assumptions.interestRate <= 0) {
    errors.push('Interest rate must be greater than 0');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}; 