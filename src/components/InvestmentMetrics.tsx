import React from 'react';
import { TrendingUp, TrendingDown, DollarSign, Percent, Clock, Target, Zap, Calculator } from 'lucide-react';

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

interface InvestmentMetricsProps {
  results: AnalysisResults;
  propertyData: PropertyData;
}

const InvestmentMetrics: React.FC<InvestmentMetricsProps> = ({ results, propertyData }) => {
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

  const getMetricColor = (value: number, threshold: number, isPositive: boolean = true) => {
    if (isPositive) {
      return value >= threshold ? 'text-success-600' : 'text-danger-600';
    } else {
      return value <= threshold ? 'text-success-600' : 'text-danger-600';
    }
  };

  const getRecommendation = () => {
    const { capRate, cashOnCash, monthlyCashFlow } = results;
    
    if (capRate >= 6 && cashOnCash >= 8 && monthlyCashFlow >= 300) {
      return {
        text: 'Strong Buy',
        color: 'text-success-600',
        bgColor: 'bg-success-50',
        borderColor: 'border-success-200',
        icon: TrendingUp
      };
    } else if (capRate >= 5 && cashOnCash >= 6 && monthlyCashFlow >= 200) {
      return {
        text: 'Buy',
        color: 'text-primary-600',
        bgColor: 'bg-primary-50',
        borderColor: 'border-primary-200',
        icon: TrendingUp
      };
    } else if (capRate >= 4 && cashOnCash >= 4 && monthlyCashFlow >= 100) {
      return {
        text: 'Hold',
        color: 'text-warning-600',
        bgColor: 'bg-warning-50',
        borderColor: 'border-warning-200',
        icon: Target
      };
    } else {
      return {
        text: 'Don\'t Buy',
        color: 'text-danger-600',
        bgColor: 'bg-danger-50',
        borderColor: 'border-danger-200',
        icon: TrendingDown
      };
    }
  };

  const recommendation = getRecommendation();
  const RecommendationIcon = recommendation.icon;

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-2 mb-6">
        <Calculator className="h-6 w-6 text-primary-600" />
        <h2 className="text-2xl font-bold text-gray-900">Investment Analysis</h2>
      </div>

      {/* Recommendation Card */}
      <div className={`card ${recommendation.bgColor} ${recommendation.borderColor} border-2`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <RecommendationIcon className={`h-8 w-8 ${recommendation.color}`} />
            <div>
              <h3 className="text-xl font-bold text-gray-900">Investment Recommendation</h3>
              <p className="text-sm text-gray-600">{propertyData.address}</p>
            </div>
          </div>
          <div className="text-right">
            <div className={`text-2xl font-bold ${recommendation.color}`}>
              {recommendation.text}
            </div>
            <div className="text-sm text-gray-500">
              Based on current metrics
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="metric-card">
          <div className="flex items-center justify-between mb-2">
            <DollarSign className="h-5 w-5 text-primary-600" />
            <span className="text-xs font-medium text-primary-700">Monthly Cash Flow</span>
          </div>
          <div className={`text-2xl font-bold ${getMetricColor(results.monthlyCashFlow, 300)}`}>
            {formatCurrency(results.monthlyCashFlow)}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Target: $300+
          </div>
        </div>

        <div className="metric-card">
          <div className="flex items-center justify-between mb-2">
            <Percent className="h-5 w-5 text-primary-600" />
            <span className="text-xs font-medium text-primary-700">Cap Rate</span>
          </div>
          <div className={`text-2xl font-bold ${getMetricColor(results.capRate, 6)}`}>
            {formatPercent(results.capRate)}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Target: 6%+
          </div>
        </div>

        <div className="metric-card">
          <div className="flex items-center justify-between mb-2">
            <Zap className="h-5 w-5 text-primary-600" />
            <span className="text-xs font-medium text-primary-700">Cash on Cash</span>
          </div>
          <div className={`text-2xl font-bold ${getMetricColor(results.cashOnCash, 8)}`}>
            {formatPercent(results.cashOnCash)}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Target: 8%+
          </div>
        </div>

        <div className="metric-card">
          <div className="flex items-center justify-between mb-2">
            <Clock className="h-5 w-5 text-primary-600" />
            <span className="text-xs font-medium text-primary-700">Payback Period</span>
          </div>
          <div className={`text-2xl font-bold ${getMetricColor(results.paybackPeriod, 10, false)}`}>
            {results.paybackPeriod.toFixed(1)}y
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Target: &lt;10 years
          </div>
        </div>
      </div>

      {/* Detailed Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Monthly Breakdown</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center py-2 border-b border-gray-100">
              <span className="text-gray-600">Monthly Rent</span>
              <span className="font-semibold text-gray-900">{formatCurrency(results.monthlyRent)}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-100">
              <span className="text-gray-600">Mortgage Payment</span>
              <span className="font-semibold text-gray-900">{formatCurrency(results.monthlyPayment)}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-100">
              <span className="text-gray-600">Monthly Cash Flow</span>
              <span className={`font-semibold ${getMetricColor(results.monthlyCashFlow, 300)}`}>
                {formatCurrency(results.monthlyCashFlow)}
              </span>
            </div>
            <div className="flex justify-between items-center py-2">
              <span className="text-gray-600">Break-even Rent</span>
              <span className="font-semibold text-gray-900">{formatCurrency(results.breakEvenRent)}</span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Investment Ratios</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center py-2 border-b border-gray-100">
              <span className="text-gray-600">Rent-to-Price Ratio</span>
              <span className="font-semibold text-gray-900">{formatPercent(results.rentToPrice)}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-100">
              <span className="text-gray-600">Cap Rate</span>
              <span className={`font-semibold ${getMetricColor(results.capRate, 6)}`}>
                {formatPercent(results.capRate)}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-100">
              <span className="text-gray-600">Cash on Cash Return</span>
              <span className={`font-semibold ${getMetricColor(results.cashOnCash, 8)}`}>
                {formatPercent(results.cashOnCash)}
              </span>
            </div>
            <div className="flex justify-between items-center py-2">
              <span className="text-gray-600">Total ROI (1 year)</span>
              <span className={`font-semibold ${getMetricColor(results.totalROI, 12)}`}>
                {formatPercent(results.totalROI)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Property Summary */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Property Summary</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div className="text-sm text-gray-500">Property Price</div>
            <div className="text-lg font-semibold text-gray-900">{formatCurrency(propertyData.price)}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Bedrooms</div>
            <div className="text-lg font-semibold text-gray-900">{propertyData.beds}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Bathrooms</div>
            <div className="text-lg font-semibold text-gray-900">{propertyData.baths}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Square Feet</div>
            <div className="text-lg font-semibold text-gray-900">{propertyData.sqft.toLocaleString()}</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InvestmentMetrics; 