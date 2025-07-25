import { PropertyData, AnalysisResults, InvestmentAssumptions } from '../types';

export const exportToExcel = async (
  propertyData: PropertyData,
  analysisResults: AnalysisResults,
  assumptions: InvestmentAssumptions,
  projectName: string
): Promise<void> => {
  console.log('🚀 Starting Excel export process...');
  console.log('📊 Property Data:', propertyData);
  console.log('📈 Analysis Results:', analysisResults);
  console.log('⚙️ Assumptions:', assumptions);
  console.log('📝 Project Name:', projectName);

  try {
    // Prepare the request payload
    const payload = {
      propertyData: {
        address: propertyData.address,
        price: propertyData.price,
        beds: propertyData.beds,
        baths: propertyData.baths,
        sqft: propertyData.sqft,
        neighborhood: propertyData.neighborhood,
        propertyType: propertyData.propertyType,
        zipcode: propertyData.zipcode,
        totalUnits: propertyData.totalUnits,
        annual_rent: analysisResults.monthlyRent * 12, // Convert to annual
        units: propertyData.totalUnits,
        square_feet: propertyData.sqft,
        property_type: propertyData.propertyType
      },
      analysisResults: {
        monthlyRent: analysisResults.monthlyRent || 0,
        totalCashRequired: analysisResults.totalCashRequired || (propertyData.price * (assumptions.downPaymentPct / 100)),
        irr: (analysisResults.irr || analysisResults.totalROI || 15) / 100,
        totalReturn: analysisResults.totalReturn || 2.0,
        monthlyExpenses: analysisResults.monthlyExpenses || (analysisResults.monthlyRent * 0.35),
        annualExpenses: (analysisResults.monthlyExpenses || (analysisResults.monthlyRent * 0.35)) * 12,
        capRate: (analysisResults.capRate || 6),  // Keep as percentage for backend
        cashOnCash: (analysisResults.cashOnCash || 8), // Keep as percentage for backend  
        monthlyCashFlow: analysisResults.monthlyCashFlow || ((analysisResults.monthlyRent || 0) * 0.15),
        rentToPrice: analysisResults.rentToPrice || ((analysisResults.monthlyRent || 0) * 12 / propertyData.price * 100)
      },
      assumptions: {
        purchasePrice: propertyData.price,
        downPaymentPct: Math.round(assumptions.downPaymentPct * 100) / 100, // Clean up precision
        interestRate: Math.round(assumptions.interestRate * 100) / 100, // Clean up precision
        loanTerm: assumptions.loanTermYears || 30,
        holdPeriod: 5,
        capRate: 5.5,
        annualRentGrowth: 3.0,
        annualExpenseGrowth: 2.5,
        vacancyRate: 5.0,
        managementFeePercent: 6.0,
        exitCapRate: 6.0,
        propertyTaxRate: 3.0,
        insuranceRate: 0.5,
        maintenanceRate: 1.0,
        capitalReservesRate: 1.0,
        closingCostsPct: 3.0,
        noiMargin: 70.0
      },
      projectName: projectName
    };

    console.log('📦 Request payload:', payload);
    console.log('🌐 Making API call to /api/excel-export...');

    // Call the NEW Vercel Python serverless function
    const response = await fetch('/api/excel-export', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    console.log('📡 Response received:', {
      status: response.status,
      statusText: response.statusText,
      headers: Object.fromEntries(response.headers.entries())
    });

    if (!response.ok) {
      console.error('❌ HTTP error response');
      
      // Try to get error details from response body
      try {
        const errorText = await response.text();
        console.error('❌ Error response body:', errorText);
        
        // Try to parse as JSON for structured error
        try {
          const errorJson = JSON.parse(errorText);
          console.error('❌ Parsed error details:', errorJson);
        } catch (e) {
          console.error('❌ Error response is not JSON');
        }
      } catch (e) {
        console.error('❌ Could not read error response body');
      }
      
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    console.log('✅ Response OK, processing blob...');

    // Get the Excel file as a blob
    const blob = await response.blob();
    console.log('📄 Blob received:', {
      size: blob.size,
      type: blob.type
    });
    
    // Create download link
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    
    // Extract filename from response headers or create default
    const contentDisposition = response.headers.get('content-disposition');
    let filename = 'Real_Estate_Pro_Forma.xlsx';
    
    if (contentDisposition) {
      console.log('📁 Content-Disposition header:', contentDisposition);
      const filenameMatch = contentDisposition.match(/filename="(.+)"/);
      if (filenameMatch) {
        filename = filenameMatch[1];
        console.log('📁 Extracted filename:', filename);
      }
    }
    
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    console.log('🎉 Excel export completed successfully!');
    
  } catch (error) {
    console.error('💥 Error exporting Excel:', error);
    console.error('💥 Error stack:', (error as Error).stack);
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