import React, { useState } from 'react';
import { FileSpreadsheet, Download, AlertCircle, CheckCircle } from 'lucide-react';
import { downloadExcelReport, validateExportData, generateProjectName } from '../utils/excelExport';

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

interface ExcelExportButtonProps {
  propertyData: PropertyData;
  analysisResults: AnalysisResults;
  assumptions: InvestmentAssumptions;
  projectName?: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'primary' | 'secondary' | 'outline';
  showIcon?: boolean;
}

export default function ExcelExportButton({
  propertyData,
  analysisResults,
  assumptions,
  projectName,
  className = '',
  size = 'md',
  variant = 'primary',
  showIcon = true
}: ExcelExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false);
  const [exportStatus, setExportStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState<string>('');

  const handleExport = async () => {
    setIsExporting(true);
    setExportStatus('idle');
    setErrorMessage('');

    try {
      // Validate data before export
      const validation = validateExportData(propertyData, analysisResults, assumptions);
      
      if (!validation.isValid) {
        throw new Error(`Validation failed: ${validation.errors.join(', ')}`);
      }

      // Generate project name if not provided
      const finalProjectName = projectName || generateProjectName(propertyData);

      // Download the Excel file
      await downloadExcelReport(propertyData, analysisResults, assumptions, finalProjectName);
      
      setExportStatus('success');
      
      // Reset success status after 3 seconds
      setTimeout(() => {
        setExportStatus('idle');
      }, 3000);

    } catch (error) {
      console.error('Excel export failed:', error);
      setExportStatus('error');
      setErrorMessage(error instanceof Error ? error.message : 'Export failed');
      
      // Reset error status after 5 seconds
      setTimeout(() => {
        setExportStatus('idle');
        setErrorMessage('');
      }, 5000);
    } finally {
      setIsExporting(false);
    }
  };

  // Determine button styling based on props
  const getSizeClasses = () => {
    switch (size) {
      case 'sm': return 'px-3 py-1.5 text-sm';
      case 'lg': return 'px-6 py-3 text-lg';
      default: return 'px-4 py-2 text-base';
    }
  };

  const getVariantClasses = () => {
    switch (variant) {
      case 'secondary':
        return 'bg-gray-600 hover:bg-gray-700 text-white border-gray-600';
      case 'outline':
        return 'bg-transparent hover:bg-primary-50 text-primary-600 border-primary-600 border-2';
      default:
        return 'bg-primary-600 hover:bg-primary-700 text-white border-primary-600';
    }
  };

  const getStatusIcon = () => {
    if (isExporting) {
      return (
        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
      );
    }
    
    switch (exportStatus) {
      case 'success':
        return <CheckCircle className="h-4 w-4" />;
      case 'error':
        return <AlertCircle className="h-4 w-4" />;
      default:
        return showIcon ? <FileSpreadsheet className="h-4 w-4" /> : null;
    }
  };

  const getButtonText = () => {
    if (isExporting) return 'Generating...';
    if (exportStatus === 'success') return 'Downloaded!';
    if (exportStatus === 'error') return 'Export Failed';
    return 'Download Excel Pro Forma';
  };

  const isDisabled = isExporting;

  return (
    <div className="relative">
      <button
        onClick={handleExport}
        disabled={isDisabled}
        className={`
          inline-flex items-center space-x-2 font-medium rounded-lg
          transition-all duration-200 border
          ${getSizeClasses()}
          ${getVariantClasses()}
          ${isDisabled ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-lg'}
          ${exportStatus === 'success' ? 'bg-green-600 hover:bg-green-700 border-green-600' : ''}
          ${exportStatus === 'error' ? 'bg-red-600 hover:bg-red-700 border-red-600' : ''}
          ${className}
        `}
      >
        {getStatusIcon()}
        <span>{getButtonText()}</span>
      </button>

      {/* Error message tooltip */}
      {exportStatus === 'error' && errorMessage && (
        <div className="absolute top-full left-0 mt-2 p-3 bg-red-50 border border-red-200 rounded-lg shadow-lg z-10 min-w-max">
          <div className="flex items-start space-x-2">
            <AlertCircle className="h-4 w-4 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-red-800">Export Failed</p>
              <p className="text-xs text-red-600 mt-1">{errorMessage}</p>
            </div>
          </div>
        </div>
      )}

      {/* Success message */}
      {exportStatus === 'success' && (
        <div className="absolute top-full left-0 mt-2 p-3 bg-green-50 border border-green-200 rounded-lg shadow-lg z-10">
          <div className="flex items-center space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <p className="text-sm font-medium text-green-800">Excel file downloaded successfully!</p>
          </div>
        </div>
      )}
    </div>
  );
} 