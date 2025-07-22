interface PropertyData {
  address: string;
  price: number;
  beds: number;
  baths: number;
  sqft: number;
  neighborhood: string;
  propertyType: string;
  zipcode: string;
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

interface ExcelExportData {
  address: string;
  price: number;
  beds: number;
  baths: number;
  sqft: number;
  neighborhood: string;
  propertyType: string;
  zipcode: string;
  results: AnalysisResults;
  assumptions: InvestmentAssumptions;
  projectName?: string;
}

export const downloadExcelReport = async (
  propertyData: PropertyData,
  analysisResults: AnalysisResults,
  assumptions: InvestmentAssumptions,
  projectName?: string
): Promise<void> => {
  try {
    // Prepare the data payload
    const exportData: ExcelExportData = {
      ...propertyData,
      results: analysisResults,
      assumptions: assumptions,
      projectName: projectName || `Investment Analysis - ${propertyData.address}`
    };

    // Make API call to backend
    const response = await fetch('http://127.0.0.1:5000/api/export-excel', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(exportData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to generate Excel report');
    }

    // Get the blob from response
    const blob = await response.blob();
    
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

export const generateProjectName = (propertyData: PropertyData): string => {
  const address = propertyData.address || 'Property';
  const type = propertyData.propertyType || 'Investment';
  return `${type} Analysis - ${address}`;
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