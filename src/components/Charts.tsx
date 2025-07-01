import React from 'react';
import { BarChart3, PieChart, TrendingUp, DollarSign } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  AreaChart,
  Area
} from 'recharts';

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

interface ChartsProps {
  results: AnalysisResults;
  propertyData: PropertyData;
}

const Charts: React.FC<ChartsProps> = ({ results, propertyData }) => {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  // Monthly cash flow breakdown data
  const cashFlowData = [
    { name: 'Rent Income', value: results.monthlyRent, color: '#22c55e' },
    { name: 'Mortgage', value: -results.monthlyPayment, color: '#ef4444' },
    { name: 'Property Tax', value: -(propertyData.price * 0.03 / 12), color: '#f59e0b' },
    { name: 'Insurance', value: -(propertyData.price * 0.005 / 12), color: '#8b5cf6' },
    { name: 'Maintenance', value: -(results.monthlyRent * 0.01), color: '#06b6d4' },
    { name: 'Management', value: -(results.monthlyRent * 0.08), color: '#84cc16' },
    { name: 'Vacancy', value: -(results.monthlyRent * 0.05), color: '#f97316' }
  ];

  // 5-year cash flow projection
  const projectionData = Array.from({ length: 5 }, (_, i) => {
    const year = i + 1;
    const rentGrowth = Math.pow(1.032, i); // 3.2% annual rent growth
    const projectedRent = results.monthlyRent * rentGrowth;
    const projectedCashFlow = projectedRent - results.monthlyPayment - (results.monthlyRent - results.monthlyPayment - results.monthlyCashFlow);
    
    return {
      year: `Year ${year}`,
      monthlyRent: projectedRent,
      monthlyCashFlow: projectedCashFlow,
      annualCashFlow: projectedCashFlow * 12
    };
  });

  // Investment metrics comparison
  const metricsData = [
    { metric: 'Cap Rate', value: results.capRate, target: 6, color: '#3b82f6' },
    { metric: 'Cash on Cash', value: results.cashOnCash, target: 8, color: '#22c55e' },
    { metric: 'Rent-to-Price', value: results.rentToPrice, target: 0.8, color: '#f59e0b' },
    { metric: 'Total ROI', value: results.totalROI, target: 12, color: '#8b5cf6' }
  ];

  // Monthly breakdown for pie chart
  const monthlyBreakdown = [
    { name: 'Rent Income', value: results.monthlyRent, color: '#22c55e' },
    { name: 'Mortgage Payment', value: results.monthlyPayment, color: '#ef4444' },
    { name: 'Operating Expenses', value: results.monthlyRent - results.monthlyPayment - results.monthlyCashFlow, color: '#f59e0b' }
  ];

  const COLORS = ['#22c55e', '#ef4444', '#f59e0b', '#8b5cf6', '#06b6d4', '#84cc16', '#f97316'];

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-2 mb-6">
        <BarChart3 className="h-6 w-6 text-primary-600" />
        <h2 className="text-2xl font-bold text-gray-900">Charts & Reports</h2>
      </div>

      {/* Monthly Cash Flow Breakdown */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Monthly Cash Flow Breakdown</h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={cashFlowData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip 
                formatter={(value: number) => [formatCurrency(value), 'Amount']}
                labelStyle={{ color: '#374151' }}
              />
              <Bar dataKey="value" fill="#3b82f6">
                {cashFlowData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Monthly Income vs Expenses Pie Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Monthly Income vs Expenses</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <RechartsPieChart>
                <Pie
                  data={monthlyBreakdown}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {monthlyBreakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value: number) => [formatCurrency(value), 'Amount']}
                  labelStyle={{ color: '#374151' }}
                />
              </RechartsPieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Investment Metrics vs Targets */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Investment Metrics vs Targets</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={metricsData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="metric" />
                <YAxis />
                <Tooltip 
                  formatter={(value: number) => [`${value.toFixed(2)}%`, 'Value']}
                  labelStyle={{ color: '#374151' }}
                />
                <Legend />
                <Bar dataKey="value" fill="#3b82f6" name="Current Value" />
                <Bar dataKey="target" fill="#94a3b8" name="Target" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 5-Year Cash Flow Projection */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">5-Year Cash Flow Projection</h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={projectionData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip 
                formatter={(value: number) => [formatCurrency(value), 'Amount']}
                labelStyle={{ color: '#374151' }}
              />
              <Legend />
              <Area 
                type="monotone" 
                dataKey="monthlyRent" 
                stackId="1" 
                stroke="#22c55e" 
                fill="#22c55e" 
                name="Monthly Rent"
              />
              <Area 
                type="monotone" 
                dataKey="monthlyCashFlow" 
                stackId="2" 
                stroke="#3b82f6" 
                fill="#3b82f6" 
                name="Monthly Cash Flow"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Annual Cash Flow Trend */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Annual Cash Flow Trend</h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={projectionData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip 
                formatter={(value: number) => [formatCurrency(value), 'Annual Cash Flow']}
                labelStyle={{ color: '#374151' }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="annualCashFlow" 
                stroke="#3b82f6" 
                strokeWidth={3}
                dot={{ fill: '#3b82f6', strokeWidth: 2, r: 6 }}
                name="Annual Cash Flow"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Key Metrics Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="metric-card">
          <div className="flex items-center justify-between mb-2">
            <DollarSign className="h-5 w-5 text-primary-600" />
            <span className="text-xs font-medium text-primary-700">Monthly Cash Flow</span>
          </div>
          <div className="text-2xl font-bold text-primary-900">
            {formatCurrency(results.monthlyCashFlow)}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Current monthly profit
          </div>
        </div>

        <div className="metric-card">
          <div className="flex items-center justify-between mb-2">
            <TrendingUp className="h-5 w-5 text-primary-600" />
            <span className="text-xs font-medium text-primary-700">Cap Rate</span>
          </div>
          <div className="text-2xl font-bold text-primary-900">
            {results.capRate.toFixed(2)}%
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Net operating income / Price
          </div>
        </div>

        <div className="metric-card">
          <div className="flex items-center justify-between mb-2">
            <BarChart3 className="h-5 w-5 text-primary-600" />
            <span className="text-xs font-medium text-primary-700">Cash on Cash</span>
          </div>
          <div className="text-2xl font-bold text-primary-900">
            {results.cashOnCash.toFixed(2)}%
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Annual return on investment
          </div>
        </div>

        <div className="metric-card">
          <div className="flex items-center justify-between mb-2">
            <DollarSign className="h-5 w-5 text-primary-600" />
            <span className="text-xs font-medium text-primary-700">Total ROI</span>
          </div>
          <div className="text-2xl font-bold text-primary-900">
            {results.totalROI.toFixed(2)}%
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Including appreciation
          </div>
        </div>
      </div>
    </div>
  );
};

export default Charts; 