import { PropertyData, AnalysisResults, InvestmentAssumptions } from '../types';

export const exportToExcel = async (
  propertyData: PropertyData,
  analysisResults: AnalysisResults,
  assumptions: InvestmentAssumptions,
  projectName: string
): Promise<void> => {
  try {
    // Call the Vercel Python serverless function (uses exact same backend code)
    const response = await fetch('/api/export-excel', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        address: propertyData.address,
        price: propertyData.price,
        beds: propertyData.beds,
        baths: propertyData.baths,
        sqft: propertyData.sqft,
        neighborhood: propertyData.neighborhood,
        propertyType: propertyData.propertyType,
        zipcode: propertyData.zipcode,
        totalUnits: propertyData.totalUnits,
        results: analysisResults,
        assumptions: assumptions,
        projectName: projectName
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Get the Excel file as a blob
    const blob = await response.blob();
    
    // Create download link
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    
    // Extract filename from response headers or create default
    const contentDisposition = response.headers.get('content-disposition');
    let filename = 'Real_Estate_Pro_Forma.xlsx';
    
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="(.+)"/);
      if (filenameMatch) {
        filename = filenameMatch[1];
      }
    }
    
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
  } catch (error) {
    console.error('Error exporting Excel:', error);
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