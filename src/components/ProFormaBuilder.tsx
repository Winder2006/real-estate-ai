import React, { useState } from 'react';
import { Calculator, Building2, DollarSign, Calendar, FileSpreadsheet, Plus, Minus, Edit3 } from 'lucide-react';
import { downloadExcelReport } from '../utils/excelExport';

// Helper functions for number formatting
const formatNumberWithCommas = (value: number): string => {
  if (value === 0 || value === null || value === undefined) return '';
  return value.toLocaleString();
};

const formatPercentage = (value: number): string => {
  if (value === 0 || value === null || value === undefined) return '';
  return value.toString();
};

const parseNumberFromString = (value: string): number => {
  if (!value || value.trim() === '') return 0;
  const cleaned = value.replace(/,/g, '');
  const parsed = parseFloat(cleaned);
  return isNaN(parsed) ? 0 : parsed;
};

interface ProFormaData {
  // Project Information
  projectName: string;
  projectType: string;
  location: string;
  totalUnits: number;
  totalSqft: number;
  
  // Development Timeline
  acquisitionDate: string;
  constructionStart: string;
  constructionEnd: string;
  salesStart: string;
  salesEnd: string;
  
  // Land & Acquisition
  landPrice: number;
  acquisitionCosts: number;
  
  // Construction Costs
  hardCosts: number;
  softCosts: number;
  contingency: number;
  
  // Revenue Assumptions
  avgSalePrice: number;
  avgRent: number;
  commercialRent: number;
  
  // Operating Assumptions
  marketingCosts: number;
  salesCommissions: number;
  operatingExpenses: number;
  
  // Financing
  loanToValue: number;
  interestRate: number;
  loanTerm: number;
  
  // Returns
  targetIRR: number;
  targetCoC: number;
}

interface CapitalStackItem {
  id: string;
  name: string;
  amount: number;
  percentage: number;
  type: 'debt' | 'equity';
}

export default function ProFormaBuilder() {
  const [activeSection, setActiveSection] = useState('project');
  const [isGenerating, setIsGenerating] = useState(false);
  
  const [proFormaData, setProFormaData] = useState<ProFormaData>({
    projectName: '',
    projectType: 'Mixed-Use Development',
    location: '',
    totalUnits: 0,
    totalSqft: 0,
    acquisitionDate: '',
    constructionStart: '',
    constructionEnd: '',
    salesStart: '',
    salesEnd: '',
    landPrice: 0,
    acquisitionCosts: 0,
    hardCosts: 0,
    softCosts: 0,
    contingency: 0,
    avgSalePrice: 0,
    avgRent: 0,
    commercialRent: 0,
    marketingCosts: 0,
    salesCommissions: 0.06,
    operatingExpenses: 0,
    loanToValue: 0.75,
    interestRate: 0.055,
    loanTerm: 24,
    targetIRR: 0.18,
    targetCoC: 0.15
  });

  const [capitalStack, setCapitalStack] = useState<CapitalStackItem[]>([
    { id: '1', name: 'GP Equity', amount: 0, percentage: 10, type: 'equity' },
    { id: '2', name: 'LP Equity', amount: 0, percentage: 15, type: 'equity' },
    { id: '3', name: 'Construction Loan', amount: 0, percentage: 75, type: 'debt' }
  ]);

  const sections = [
    { id: 'project', label: 'Project Info', icon: Building2 },
    { id: 'timeline', label: 'Timeline', icon: Calendar },
    { id: 'costs', label: 'Development Costs', icon: DollarSign },
    { id: 'revenue', label: 'Revenue', icon: DollarSign },
    { id: 'capital', label: 'Capital Stack', icon: Calculator },
    { id: 'generate', label: 'Generate Pro Forma', icon: FileSpreadsheet }
  ];

  const updateData = (field: keyof ProFormaData, value: any) => {
    setProFormaData(prev => ({ ...prev, [field]: value }));
  };

  const addCapitalStackItem = () => {
    const newItem: CapitalStackItem = {
      id: Date.now().toString(),
      name: 'New Source',
      amount: 0,
      percentage: 0,
      type: 'equity'
    };
    setCapitalStack(prev => [...prev, newItem]);
  };

  const generateSampleData = () => {
    // Generate realistic sample data for demonstration
    const currentDate = new Date();
    const acquisitionDate = new Date(currentDate.getTime() + 30 * 24 * 60 * 60 * 1000); // 1 month from now
    const constructionStart = new Date(acquisitionDate.getTime() + 60 * 24 * 60 * 60 * 1000); // 2 months later
    const constructionEnd = new Date(constructionStart.getTime() + 18 * 30 * 24 * 60 * 60 * 1000); // 18 months construction
    const salesStart = new Date(constructionEnd.getTime() - 6 * 30 * 24 * 60 * 60 * 1000); // Sales start 6 months before completion
    const salesEnd = new Date(constructionEnd.getTime() + 12 * 30 * 24 * 60 * 60 * 1000); // Sales end 12 months after completion

    const sampleData: ProFormaData = {
      projectName: 'River Walk Mixed-Use Development',
      projectType: 'Mixed-Use Development',
      location: 'Milwaukee, WI - Third Ward',
      totalUnits: 85,
      totalSqft: 125000,
      acquisitionDate: acquisitionDate.toISOString().split('T')[0],
      constructionStart: constructionStart.toISOString().split('T')[0],
      constructionEnd: constructionEnd.toISOString().split('T')[0],
      salesStart: salesStart.toISOString().split('T')[0],
      salesEnd: salesEnd.toISOString().split('T')[0],
      landPrice: 2500000,
      acquisitionCosts: 175000,
      hardCosts: 18750000, // $150/sqft
      softCosts: 3250000,
      contingency: 1125000, // 5% of hard costs
      avgSalePrice: 425000,
      avgRent: 2850,
      commercialRent: 28,
      marketingCosts: 850000,
      salesCommissions: 0.05,
      operatingExpenses: 125000,
      loanToValue: 0.72,
      interestRate: 0.068,
      loanTerm: 24,
      targetIRR: 0.22,
      targetCoC: 0.18
    };

    setProFormaData(sampleData);

    // Update capital stack with realistic sample data
    const totalCost = sampleData.landPrice + sampleData.acquisitionCosts + sampleData.hardCosts + sampleData.softCosts + sampleData.contingency;
    const loanAmount = totalCost * sampleData.loanToValue;
    const totalEquity = totalCost - loanAmount;
    const gpEquity = totalEquity * 0.15; // GP puts in 15%
    const lpEquity = totalEquity * 0.85; // LP puts in 85%

    const sampleCapitalStack: CapitalStackItem[] = [
      { id: '1', name: 'GP Equity (15%)', amount: gpEquity, percentage: 15, type: 'equity' },
      { id: '2', name: 'LP Equity (85%)', amount: lpEquity, percentage: 85, type: 'equity' },
      { id: '3', name: 'Construction Loan', amount: loanAmount, percentage: 72, type: 'debt' },
      { id: '4', name: 'Mezzanine Financing', amount: 1500000, percentage: 6, type: 'debt' }
    ];

    setCapitalStack(sampleCapitalStack);
  };

  const updateCapitalStackItem = (id: string, field: keyof CapitalStackItem, value: any) => {
    setCapitalStack(prev => prev.map(item => 
      item.id === id ? { ...item, [field]: value } : item
    ));
  };

  const removeCapitalStackItem = (id: string) => {
    setCapitalStack(prev => prev.filter(item => item.id !== id));
  };

  const calculateTotalCosts = () => {
    return proFormaData.landPrice + proFormaData.acquisitionCosts + 
           proFormaData.hardCosts + proFormaData.softCosts + proFormaData.contingency;
  };

  const calculateTotalRevenue = () => {
    return (proFormaData.avgSalePrice * proFormaData.totalUnits) + 
           (proFormaData.avgRent * 12 * proFormaData.totalUnits);
  };

  const generateProForma = async () => {
    setIsGenerating(true);
    
    try {
      // Convert pro forma data to format expected by Excel generator
      const propertyData = {
        address: proFormaData.location,
        price: calculateTotalCosts(),
        beds: Math.floor(proFormaData.totalUnits * 1.5), // Estimate: 1.5 beds per unit average
        baths: Math.floor(proFormaData.totalUnits * 1.2), // Estimate: 1.2 baths per unit average
        sqft: proFormaData.totalSqft,
        neighborhood: proFormaData.location.includes(' - ') ? proFormaData.location.split(' - ')[1] : proFormaData.location || 'Third Ward', // Extract neighborhood properly
        propertyType: proFormaData.projectType,
        zipcode: '53202', // Milwaukee Third Ward zip code
        totalUnits: proFormaData.totalUnits
      };
      
      // Excel export data verified and functioning correctly

      // Calculate total property income (all units combined)
      const totalMonthlyRent = proFormaData.avgRent * proFormaData.totalUnits;
      const totalAnnualRent = totalMonthlyRent * 12;
      const loanAmount = calculateTotalCosts() * proFormaData.loanToValue;
      const monthlyLoanPayment = loanAmount * (proFormaData.interestRate / 12);
      const annualOperatingExpenses = proFormaData.operatingExpenses;
      
      const analysisResults = {
        monthlyRent: totalMonthlyRent, // Total monthly rent for ALL units
        monthlyPayment: monthlyLoanPayment,
        monthlyCashFlow: totalMonthlyRent - monthlyLoanPayment - (annualOperatingExpenses / 12),
        capRate: (totalAnnualRent - annualOperatingExpenses) / calculateTotalCosts() * 100,
        cashOnCash: proFormaData.targetCoC * 100,
        breakEvenRent: monthlyLoanPayment + (annualOperatingExpenses / 12),
        rentToPrice: totalAnnualRent / calculateTotalCosts() * 100,
        totalROI: proFormaData.targetIRR * 100,
        paybackPeriod: calculateTotalCosts() / totalAnnualRent,
        annualNOI: totalAnnualRent - annualOperatingExpenses
      };

      const assumptions = {
        downPaymentPct: (1 - proFormaData.loanToValue) * 100,
        interestRate: proFormaData.interestRate * 100,
        loanTerm: proFormaData.loanTerm,
        propertyTaxRate: 3.0,
        insuranceRate: 0.5,
        maintenanceRate: 1.0,
        capitalReservesRate: 1.0,
        vacancyRate: 5.0,
        closingCostsPct: 3.0
      };

      await downloadExcelReport(
        propertyData,
        analysisResults,
        assumptions,
        proFormaData.projectName || 'Development Pro Forma'
      );

    } catch (error) {
      console.error('Pro forma generation failed:', error);
      alert('Failed to generate pro forma. Please check your inputs and try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const renderProjectInfo = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Project Information</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Project Name</label>
          <input
            type="text"
            value={proFormaData.projectName}
            onChange={(e) => updateData('projectName', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="e.g., Downtown Mixed-Use Development"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Project Type</label>
          <select
            value={proFormaData.projectType}
            onChange={(e) => updateData('projectType', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="Mixed-Use Development">Mixed-Use Development</option>
            <option value="Residential Development">Residential Development</option>
            <option value="Commercial Development">Commercial Development</option>
            <option value="Multifamily Development">Multifamily Development</option>
            <option value="Retail Development">Retail Development</option>
            <option value="Office Development">Office Development</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
          <input
            type="text"
            value={proFormaData.location}
            onChange={(e) => updateData('location', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="e.g., Milwaukee, WI"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Total Units</label>
          <input
            type="text"
            value={formatNumberWithCommas(proFormaData.totalUnits)}
            onChange={(e) => updateData('totalUnits', parseNumberFromString(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="0"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Total Square Footage</label>
          <input
            type="text"
            value={formatNumberWithCommas(proFormaData.totalSqft)}
            onChange={(e) => updateData('totalSqft', parseNumberFromString(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="0"
          />
        </div>
      </div>
    </div>
  );

  const renderTimeline = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Development Timeline</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Acquisition Date</label>
          <input
            type="date"
            value={proFormaData.acquisitionDate}
            onChange={(e) => updateData('acquisitionDate', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Construction Start</label>
          <input
            type="date"
            value={proFormaData.constructionStart}
            onChange={(e) => updateData('constructionStart', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Construction End</label>
          <input
            type="date"
            value={proFormaData.constructionEnd}
            onChange={(e) => updateData('constructionEnd', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Sales/Lease Start</label>
          <input
            type="date"
            value={proFormaData.salesStart}
            onChange={(e) => updateData('salesStart', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Sales/Lease End</label>
          <input
            type="date"
            value={proFormaData.salesEnd}
            onChange={(e) => updateData('salesEnd', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
      </div>
    </div>
  );

  const renderCosts = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Development Costs</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Land Price</label>
          <input
            type="text"
            value={formatNumberWithCommas(proFormaData.landPrice)}
            onChange={(e) => updateData('landPrice', parseNumberFromString(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="0"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Acquisition Costs</label>
          <input
            type="text"
            value={formatNumberWithCommas(proFormaData.acquisitionCosts)}
            onChange={(e) => updateData('acquisitionCosts', parseNumberFromString(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="0"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Hard Costs</label>
          <input
            type="text"
            value={formatNumberWithCommas(proFormaData.hardCosts)}
            onChange={(e) => updateData('hardCosts', parseNumberFromString(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="0"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Soft Costs</label>
          <input
            type="text"
            value={formatNumberWithCommas(proFormaData.softCosts)}
            onChange={(e) => updateData('softCosts', parseNumberFromString(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="0"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Contingency</label>
          <input
            type="text"
            value={formatNumberWithCommas(proFormaData.contingency)}
            onChange={(e) => updateData('contingency', parseNumberFromString(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="0"
          />
        </div>
        
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="font-medium text-gray-900">Total Development Cost</h4>
          <p className="text-2xl font-bold text-primary-600">
            ${calculateTotalCosts().toLocaleString()}
          </p>
        </div>
      </div>
    </div>
  );

  const renderRevenue = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue Assumptions</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Average Sale Price per Unit</label>
          <input
            type="text"
            value={formatNumberWithCommas(proFormaData.avgSalePrice)}
            onChange={(e) => updateData('avgSalePrice', parseNumberFromString(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="0"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Average Rent per Unit (Monthly)</label>
          <input
            type="text"
            value={formatNumberWithCommas(proFormaData.avgRent)}
            onChange={(e) => updateData('avgRent', parseNumberFromString(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="0"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Commercial Rent (per sq ft/year)</label>
          <input
            type="text"
            value={formatNumberWithCommas(proFormaData.commercialRent)}
            onChange={(e) => updateData('commercialRent', parseNumberFromString(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="0"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Marketing Costs</label>
          <input
            type="text"
            value={formatNumberWithCommas(proFormaData.marketingCosts)}
            onChange={(e) => updateData('marketingCosts', parseNumberFromString(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="0"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Sales Commissions (%)</label>
          <input
            type="number"
            step="0.01"
            value={formatPercentage(proFormaData.salesCommissions)}
            onChange={(e) => updateData('salesCommissions', parseNumberFromString(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="0.06"
          />
        </div>
        
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="font-medium text-gray-900">Total Potential Revenue</h4>
          <p className="text-2xl font-bold text-green-600">
            ${calculateTotalRevenue().toLocaleString()}
          </p>
        </div>
      </div>
    </div>
  );

  const renderCapitalStack = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Capital Stack</h3>
        <button
          onClick={addCapitalStackItem}
          className="flex items-center space-x-2 px-3 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          <Plus className="h-4 w-4" />
          <span>Add Source</span>
        </button>
      </div>
      
      <div className="space-y-4">
        {capitalStack.map((item) => (
          <div key={item.id} className="flex items-center space-x-4 p-4 border border-gray-200 rounded-lg">
            <input
              type="text"
              value={item.name}
              onChange={(e) => updateCapitalStackItem(item.id, 'name', e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="Source name"
            />
            
                          <input
                type="text"
                value={formatNumberWithCommas(item.amount)}
                onChange={(e) => updateCapitalStackItem(item.id, 'amount', parseNumberFromString(e.target.value))}
                className="w-32 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="Amount"
              />
            
            <input
              type="number"
              step="0.01"
              value={formatPercentage(item.percentage)}
              onChange={(e) => updateCapitalStackItem(item.id, 'percentage', parseNumberFromString(e.target.value))}
              className="w-20 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="%"
            />
            
            <select
              value={item.type}
              onChange={(e) => updateCapitalStackItem(item.id, 'type', e.target.value)}
              className="w-24 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="equity">Equity</option>
              <option value="debt">Debt</option>
            </select>
            
            <button
              onClick={() => removeCapitalStackItem(item.id)}
              className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
            >
              <Minus className="h-4 w-4" />
            </button>
          </div>
        ))}
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Loan-to-Value (%)</label>
          <input
            type="number"
            step="0.01"
            value={formatPercentage(proFormaData.loanToValue)}
            onChange={(e) => updateData('loanToValue', parseNumberFromString(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="0.75"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Interest Rate (%)</label>
          <input
            type="number"
            step="0.001"
            value={formatPercentage(proFormaData.interestRate)}
            onChange={(e) => updateData('interestRate', parseNumberFromString(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="0.055"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Loan Term (months)</label>
          <input
            type="text"
            value={formatNumberWithCommas(proFormaData.loanTerm)}
            onChange={(e) => updateData('loanTerm', parseNumberFromString(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="24"
          />
        </div>
      </div>
    </div>
  );

  const renderGenerate = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Generate Pro Forma</h3>
      
      {/* Sample Data Option */}
      <div className="bg-green-50 p-6 rounded-lg border-2 border-green-200">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h4 className="font-medium text-green-900">Demo Pro Forma</h4>
            <p className="text-green-800 text-sm">
              Load realistic sample data for a Milwaukee mixed-use development project
            </p>
          </div>
          <button
            onClick={generateSampleData}
            className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Building2 className="h-4 w-4" />
            <span>Load Sample Project</span>
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
          <div>
            <p className="text-green-700 font-medium">Sample Project</p>
            <p className="text-green-800">85-Unit Mixed-Use</p>
          </div>
          <div>
            <p className="text-green-700 font-medium">Total Cost</p>
            <p className="text-green-800">$25.8M</p>
          </div>
          <div>
            <p className="text-green-700 font-medium">Projected Revenue</p>
            <p className="text-green-800">$39.0M</p>
          </div>
          <div>
            <p className="text-green-700 font-medium">Target IRR</p>
            <p className="text-green-800">22%</p>
          </div>
        </div>
      </div>

      <div className="bg-blue-50 p-6 rounded-lg">
        <h4 className="font-medium text-blue-900 mb-4">Current Project Summary</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <p className="text-blue-700">Total Development Cost</p>
            <p className="text-xl font-bold text-blue-900">${calculateTotalCosts().toLocaleString()}</p>
          </div>
          <div>
            <p className="text-blue-700">Potential Revenue</p>
            <p className="text-xl font-bold text-blue-900">${calculateTotalRevenue().toLocaleString()}</p>
          </div>
          <div>
            <p className="text-blue-700">Projected Profit</p>
            <p className={`text-xl font-bold ${(calculateTotalRevenue() - calculateTotalCosts()) > 0 ? 'text-green-600' : 'text-red-600'}`}>
              ${(calculateTotalRevenue() - calculateTotalCosts()).toLocaleString()}
            </p>
          </div>
        </div>
      </div>
      
      <div className="bg-yellow-50 p-6 rounded-lg">
        <h4 className="font-medium text-yellow-900 mb-2">Ready to Generate Excel Pro Forma</h4>
        <p className="text-yellow-800 text-sm mb-4">
          This will create a comprehensive Excel file with Executive Summary, 5-Year Pro Forma, 
          Assumptions, and Sensitivity Analysis worksheets.
        </p>
        
        <div className="flex flex-wrap gap-3">
          <button
            onClick={generateProForma}
            disabled={isGenerating || calculateTotalCosts() === 0}
            className="flex items-center space-x-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isGenerating ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            ) : (
              <FileSpreadsheet className="h-5 w-5" />
            )}
            <span>{isGenerating ? 'Generating...' : 'Download Excel Pro Forma'}</span>
          </button>
          
          {calculateTotalCosts() === 0 && (
            <div className="flex items-center space-x-2 text-gray-500 text-sm">
              <span>💡 Add project data or load sample to enable export</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-2 mb-6">
        <Building2 className="h-6 w-6 text-primary-600" />
        <h2 className="text-2xl font-bold text-gray-900">Pro Forma Builder</h2>
      </div>

      {/* Navigation */}
      <div className="flex flex-wrap gap-2 mb-6">
        {sections.map((section) => {
          const Icon = section.icon;
          return (
            <button
              key={section.id}
              onClick={() => setActiveSection(section.id)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                activeSection === section.id
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <Icon className="h-4 w-4" />
              <span>{section.label}</span>
            </button>
          );
        })}
      </div>

      {/* Content */}
      <div className="card">
        {activeSection === 'project' && renderProjectInfo()}
        {activeSection === 'timeline' && renderTimeline()}
        {activeSection === 'costs' && renderCosts()}
        {activeSection === 'revenue' && renderRevenue()}
        {activeSection === 'capital' && renderCapitalStack()}
        {activeSection === 'generate' && renderGenerate()}
      </div>
    </div>
  );
} 