import React, { useState } from 'react';
import { Building2, Calculator, TrendingUp, MapPin, DollarSign, Home, BarChart3 } from 'lucide-react';
import PropertyForm from './components/PropertyForm.tsx';
import InvestmentMetrics from './components/InvestmentMetrics.tsx';
import RentalAnalysis from './components/RentalAnalysis.tsx';
import MarketComps from './components/MarketComps.tsx';
import Charts from './components/Charts.tsx';

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

function App() {
  const [activeTab, setActiveTab] = useState('property');
  const [propertyData, setPropertyData] = useState<PropertyData>({
    address: '',
    price: 0,
    beds: 0,
    baths: 0,
    sqft: 0,
    neighborhood: '',
    propertyType: 'House',
    zipcode: ''
  });
  
  const [assumptions, setAssumptions] = useState<InvestmentAssumptions>({
    downPaymentPct: 20,
    interestRate: 5.0,
    loanTerm: 30,
    propertyTaxRate: 3.0,
    insuranceRate: 0.5,
    maintenanceRate: 1.0,
    capitalReservesRate: 1.0,
    vacancyRate: 5.0,
    closingCostsPct: 3.0
  });

  const [analysisResults, setAnalysisResults] = useState<AnalysisResults | null>(null);

  const tabs = [
    { id: 'property', label: 'Property Info', icon: Home },
    { id: 'analysis', label: 'Investment Analysis', icon: Calculator },
    { id: 'rental', label: 'Rental Analysis', icon: Building2 },
    { id: 'market', label: 'Market Comps', icon: MapPin },
    { id: 'charts', label: 'Charts & Reports', icon: BarChart3 }
  ];

  const handleAnalyze = () => {
    // Calculate investment metrics
    const price = propertyData.price;
    const downPayment = price * (assumptions.downPaymentPct / 100);
    const loanAmount = price - downPayment;
    const monthlyRate = assumptions.interestRate / 100 / 12;
    const numPayments = assumptions.loanTerm * 12;
    
    // Monthly mortgage payment
    const monthlyPayment = loanAmount * (monthlyRate * Math.pow(1 + monthlyRate, numPayments)) / 
                          (Math.pow(1 + monthlyRate, numPayments) - 1);
    
    // Estimated monthly rent (simplified calculation)
    const monthlyRent = price * 0.008; // Rough estimate: 0.8% of property value
    
    // Monthly expenses
    const monthlyPropertyTax = price * (assumptions.propertyTaxRate / 100) / 12;
    const monthlyInsurance = price * (assumptions.insuranceRate / 100) / 12;
    const monthlyManagement = monthlyRent * 0.08;
    const monthlyMaintenance = monthlyRent * (assumptions.maintenanceRate / 100);
    const monthlyCapitalReserves = monthlyRent * (assumptions.capitalReservesRate / 100);
    const monthlyVacancy = monthlyRent * (assumptions.vacancyRate / 100);
    
    const monthlyExpenses = monthlyPropertyTax + monthlyInsurance + monthlyManagement + 
                           monthlyMaintenance + monthlyCapitalReserves + monthlyVacancy;
    
    const monthlyCashFlow = monthlyRent - monthlyPayment - monthlyExpenses;
    
    // Cap rate
    const annualOperatingExpenses = monthlyExpenses * 12;
    const noi = (monthlyRent * 12) - annualOperatingExpenses;
    const capRate = (noi / price) * 100;
    
    // Cash on cash
    const totalUpfrontCost = downPayment + price * (assumptions.closingCostsPct / 100);
    const cashOnCash = (monthlyCashFlow * 12) / totalUpfrontCost * 100;
    
    // Break even rent
    const piti = monthlyPayment + monthlyPropertyTax + monthlyInsurance;
    const breakEvenRent = piti + monthlyManagement + monthlyMaintenance + 
                         monthlyCapitalReserves + monthlyVacancy;
    
    // Rent to price ratio
    const rentToPrice = (monthlyRent / price) * 100;
    
    // Total ROI (simplified)
    const appreciation = price * 0.03; // 3% appreciation
    const totalROI = ((monthlyCashFlow * 12) + appreciation) / totalUpfrontCost * 100;
    
    // Payback period
    const paybackPeriod = totalUpfrontCost / (monthlyCashFlow * 12);

    setAnalysisResults({
      monthlyRent,
      monthlyPayment,
      monthlyCashFlow,
      capRate,
      cashOnCash,
      breakEvenRent,
      rentToPrice,
      totalROI,
      paybackPeriod
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="bg-primary-600 p-2 rounded-lg">
                <Building2 className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Real Estate Investment Analyzer</h1>
                <p className="text-sm text-gray-500">Smart property investment analysis</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <TrendingUp className="h-5 w-5 text-primary-600" />
              <span className="text-sm font-medium text-gray-700">Fintech Analytics</span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'property' && (
          <PropertyForm
            propertyData={propertyData}
            setPropertyData={setPropertyData}
            assumptions={assumptions}
            setAssumptions={setAssumptions}
            onAnalyze={handleAnalyze}
          />
        )}
        
        {activeTab === 'analysis' && analysisResults && (
          <InvestmentMetrics results={analysisResults} propertyData={propertyData} />
        )}
        
        {activeTab === 'rental' && analysisResults && (
          <RentalAnalysis results={analysisResults} propertyData={propertyData} />
        )}
        
        {activeTab === 'market' && (
          <MarketComps propertyData={propertyData} />
        )}
        
        {activeTab === 'charts' && analysisResults && (
          <Charts results={analysisResults} propertyData={propertyData} />
        )}
      </main>
    </div>
  );
}

export default App; 