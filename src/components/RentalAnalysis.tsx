import React from 'react';
import { Building2, DollarSign, TrendingUp, AlertCircle, CheckCircle, Info } from 'lucide-react';

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

interface RentalAnalysisProps {
  results: AnalysisResults;
  propertyData: PropertyData;
}

const RentalAnalysis: React.FC<RentalAnalysisProps> = ({ results, propertyData }) => {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatPercent = (value: number) => {
    return `${value.toFixed(2)}%`;
  };

  // Mock rental market data
  const marketData = {
    avgRentPerSqft: 1.2,
    avgRentPerBedroom: 800,
    marketVacancyRate: 4.5,
    rentGrowthRate: 3.2,
    daysOnMarket: 25
  };

  const calculateRentPerSqft = () => {
    return results.monthlyRent / propertyData.sqft;
  };

  const calculateRentPerBedroom = () => {
    return results.monthlyRent / propertyData.beds;
  };

  const getRentAnalysis = () => {
    const rentPerSqft = calculateRentPerSqft();
    const rentPerBedroom = calculateRentPerBedroom();
    
    const insights = [];
    
    if (rentPerSqft > marketData.avgRentPerSqft) {
      insights.push({
        type: 'positive',
        icon: CheckCircle,
        text: `Rent per sq ft ($${rentPerSqft.toFixed(2)}) is above market average ($${marketData.avgRentPerSqft})`
      });
    } else {
      insights.push({
        type: 'warning',
        icon: AlertCircle,
        text: `Rent per sq ft ($${rentPerSqft.toFixed(2)}) is below market average ($${marketData.avgRentPerSqft})`
      });
    }
    
    if (rentPerBedroom > marketData.avgRentPerBedroom) {
      insights.push({
        type: 'positive',
        icon: CheckCircle,
        text: `Rent per bedroom ($${rentPerBedroom.toFixed(0)}) is above market average ($${marketData.avgRentPerBedroom})`
      });
    } else {
      insights.push({
        type: 'warning',
        icon: AlertCircle,
        text: `Rent per bedroom ($${rentPerBedroom.toFixed(0)}) is below market average ($${marketData.avgRentPerBedroom})`
      });
    }
    
    return insights;
  };

  const insights = getRentAnalysis();

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-2 mb-6">
        <Building2 className="h-6 w-6 text-primary-600" />
        <h2 className="text-2xl font-bold text-gray-900">Rental Analysis</h2>
      </div>

      {/* Rental Income Overview */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-4">
          <DollarSign className="h-5 w-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Rental Income Overview</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-primary-600 mb-1">
              {formatCurrency(results.monthlyRent)}
            </div>
            <div className="text-sm text-gray-600">Monthly Rent</div>
            <div className="text-xs text-gray-500 mt-1">
              {formatCurrency(results.monthlyRent * 12)} annually
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-success-600 mb-1">
              {formatCurrency(results.monthlyCashFlow)}
            </div>
            <div className="text-sm text-gray-600">Monthly Cash Flow</div>
            <div className="text-xs text-gray-500 mt-1">
              {formatCurrency(results.monthlyCashFlow * 12)} annually
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-warning-600 mb-1">
              {formatCurrency(results.breakEvenRent)}
            </div>
            <div className="text-sm text-gray-600">Break-even Rent</div>
            <div className="text-xs text-gray-500 mt-1">
              Minimum rent needed
            </div>
          </div>
        </div>
      </div>

      {/* Market Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Rental Market Analysis</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center py-2 border-b border-gray-100">
              <span className="text-gray-600">Rent per Sq Ft</span>
              <span className="font-semibold text-gray-900">
                ${calculateRentPerSqft().toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-100">
              <span className="text-gray-600">Market Average</span>
              <span className="font-semibold text-gray-900">
                ${marketData.avgRentPerSqft}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-100">
              <span className="text-gray-600">Rent per Bedroom</span>
              <span className="font-semibold text-gray-900">
                {formatCurrency(calculateRentPerBedroom())}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-100">
              <span className="text-gray-600">Market Average</span>
              <span className="font-semibold text-gray-900">
                {formatCurrency(marketData.avgRentPerBedroom)}
              </span>
            </div>
            <div className="flex justify-between items-center py-2">
              <span className="text-gray-600">Rent-to-Price Ratio</span>
              <span className="font-semibold text-gray-900">
                {formatPercent(results.rentToPrice)}
              </span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Market Insights</h3>
          <div className="space-y-4">
            <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
              <TrendingUp className="h-5 w-5 text-blue-600" />
              <div>
                <div className="font-medium text-blue-900">Rent Growth</div>
                <div className="text-sm text-blue-700">{marketData.rentGrowthRate}% annually</div>
              </div>
            </div>
            
            <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <div>
                <div className="font-medium text-green-900">Low Vacancy</div>
                <div className="text-sm text-green-700">{marketData.marketVacancyRate}% market rate</div>
              </div>
            </div>
            
            <div className="flex items-center space-x-3 p-3 bg-purple-50 rounded-lg">
              <Info className="h-5 w-5 text-purple-600" />
              <div>
                <div className="font-medium text-purple-900">Fast Market</div>
                <div className="text-sm text-purple-700">{marketData.daysOnMarket} days average</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Rental Insights */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Rental Insights</h3>
        <div className="space-y-3">
          {insights.map((insight, index) => {
            const Icon = insight.icon;
            return (
              <div
                key={index}
                className={`flex items-center space-x-3 p-3 rounded-lg ${
                  insight.type === 'positive' 
                    ? 'bg-green-50 border border-green-200' 
                    : 'bg-yellow-50 border border-yellow-200'
                }`}
              >
                <Icon className={`h-5 w-5 ${
                  insight.type === 'positive' ? 'text-green-600' : 'text-yellow-600'
                }`} />
                <span className={`text-sm ${
                  insight.type === 'positive' ? 'text-green-800' : 'text-yellow-800'
                }`}>
                  {insight.text}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Cash Flow Projection */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">5-Year Cash Flow Projection</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 text-sm font-medium text-gray-700">Year</th>
                <th className="text-right py-2 text-sm font-medium text-gray-700">Monthly Rent</th>
                <th className="text-right py-2 text-sm font-medium text-gray-700">Monthly Cash Flow</th>
                <th className="text-right py-2 text-sm font-medium text-gray-700">Annual Cash Flow</th>
                <th className="text-right py-2 text-sm font-medium text-gray-700">Cumulative</th>
              </tr>
            </thead>
            <tbody>
              {[1, 2, 3, 4, 5].map((year) => {
                const rentGrowth = Math.pow(1 + marketData.rentGrowthRate / 100, year - 1);
                const projectedRent = results.monthlyRent * rentGrowth;
                const projectedCashFlow = projectedRent - results.monthlyPayment - (results.monthlyRent - results.monthlyPayment - results.monthlyCashFlow);
                const annualCashFlow = projectedCashFlow * 12;
                const cumulative = Array.from({ length: year }, (_, i) => {
                  const yearRent = results.monthlyRent * Math.pow(1 + marketData.rentGrowthRate / 100, i);
                  const yearCashFlow = yearRent - results.monthlyPayment - (results.monthlyRent - results.monthlyPayment - results.monthlyCashFlow);
                  return yearCashFlow * 12;
                }).reduce((sum, val) => sum + val, 0);
                
                return (
                  <tr key={year} className="border-b border-gray-100">
                    <td className="py-2 text-sm text-gray-900">Year {year}</td>
                    <td className="py-2 text-sm text-gray-900 text-right">{formatCurrency(projectedRent)}</td>
                    <td className="py-2 text-sm text-gray-900 text-right">{formatCurrency(projectedCashFlow)}</td>
                    <td className="py-2 text-sm text-gray-900 text-right">{formatCurrency(annualCashFlow)}</td>
                    <td className="py-2 text-sm text-gray-900 text-right">{formatCurrency(cumulative)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default RentalAnalysis; 