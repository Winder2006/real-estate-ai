import React from 'react';
import { MapPin, Home, DollarSign, TrendingUp, Search } from 'lucide-react';

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

interface MarketCompsProps {
  propertyData: PropertyData;
}

// Mock comparable properties data
const mockComps = [
  {
    address: '123 Oak St, Milwaukee, WI',
    price: 245000,
    beds: 3,
    baths: 2,
    sqft: 1450,
    pricePerSqft: 169,
    soldDate: '2024-01-15',
    distance: 0.3
  },
  {
    address: '456 Pine Ave, Milwaukee, WI',
    price: 260000,
    beds: 3,
    baths: 2.5,
    sqft: 1600,
    pricePerSqft: 163,
    soldDate: '2024-01-10',
    distance: 0.5
  },
  {
    address: '789 Maple Dr, Milwaukee, WI',
    price: 235000,
    beds: 3,
    baths: 2,
    sqft: 1400,
    pricePerSqft: 168,
    soldDate: '2024-01-05',
    distance: 0.7
  },
  {
    address: '321 Elm St, Milwaukee, WI',
    price: 275000,
    beds: 4,
    baths: 2.5,
    sqft: 1800,
    pricePerSqft: 153,
    soldDate: '2023-12-28',
    distance: 0.8
  },
  {
    address: '654 Birch Rd, Milwaukee, WI',
    price: 250000,
    beds: 3,
    baths: 2,
    sqft: 1550,
    pricePerSqft: 161,
    soldDate: '2023-12-20',
    distance: 1.0
  }
];

const MarketComps: React.FC<MarketCompsProps> = ({ propertyData }) => {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const calculatePricePerSqft = (price: number, sqft: number) => {
    return price / sqft;
  };

  const getMarketStats = () => {
    const avgPrice = mockComps.reduce((sum, comp) => sum + comp.price, 0) / mockComps.length;
    const avgPricePerSqft = mockComps.reduce((sum, comp) => sum + comp.pricePerSqft, 0) / mockComps.length;
    const avgDaysOnMarket = 25; // Mock data
    const priceRange = {
      min: Math.min(...mockComps.map(comp => comp.price)),
      max: Math.max(...mockComps.map(comp => comp.price))
    };

    return {
      avgPrice,
      avgPricePerSqft,
      avgDaysOnMarket,
      priceRange
    };
  };

  const marketStats = getMarketStats();
  const subjectPricePerSqft = calculatePricePerSqft(propertyData.price, propertyData.sqft);

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-2 mb-6">
        <MapPin className="h-6 w-6 text-primary-600" />
        <h2 className="text-2xl font-bold text-gray-900">Market Comps</h2>
      </div>

      {/* Market Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="metric-card">
          <div className="flex items-center justify-between mb-2">
            <DollarSign className="h-5 w-5 text-primary-600" />
            <span className="text-xs font-medium text-primary-700">Avg Sale Price</span>
          </div>
          <div className="text-2xl font-bold text-primary-900">
            {formatCurrency(marketStats.avgPrice)}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {mockComps.length} recent sales
          </div>
        </div>

        <div className="metric-card">
          <div className="flex items-center justify-between mb-2">
            <Home className="h-5 w-5 text-primary-600" />
            <span className="text-xs font-medium text-primary-700">Avg Price/Sq Ft</span>
          </div>
          <div className="text-2xl font-bold text-primary-900">
            ${marketStats.avgPricePerSqft.toFixed(0)}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Market benchmark
          </div>
        </div>

        <div className="metric-card">
          <div className="flex items-center justify-between mb-2">
            <TrendingUp className="h-5 w-5 text-primary-600" />
            <span className="text-xs font-medium text-primary-700">Days on Market</span>
          </div>
          <div className="text-2xl font-bold text-primary-900">
            {marketStats.avgDaysOnMarket}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Average time to sell
          </div>
        </div>

        <div className="metric-card">
          <div className="flex items-center justify-between mb-2">
            <Search className="h-5 w-5 text-primary-600" />
            <span className="text-xs font-medium text-primary-700">Price Range</span>
          </div>
          <div className="text-2xl font-bold text-primary-900">
            {formatCurrency(marketStats.priceRange.min)}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            to {formatCurrency(marketStats.priceRange.max)}
          </div>
        </div>
      </div>

      {/* Subject Property vs Market */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Subject Property vs Market</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="flex justify-between items-center py-2 border-b border-gray-100">
              <span className="text-gray-600">Your Property Price</span>
              <span className="font-semibold text-gray-900">{formatCurrency(propertyData.price)}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-100">
              <span className="text-gray-600">Market Average</span>
              <span className="font-semibold text-gray-900">{formatCurrency(marketStats.avgPrice)}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-100">
              <span className="text-gray-600">Price Difference</span>
              <span className={`font-semibold ${
                propertyData.price > marketStats.avgPrice ? 'text-danger-600' : 'text-success-600'
              }`}>
                {propertyData.price > marketStats.avgPrice ? '+' : ''}
                {formatCurrency(propertyData.price - marketStats.avgPrice)}
              </span>
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center py-2 border-b border-gray-100">
              <span className="text-gray-600">Your Price/Sq Ft</span>
              <span className="font-semibold text-gray-900">${subjectPricePerSqft.toFixed(0)}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-100">
              <span className="text-gray-600">Market Average</span>
              <span className="font-semibold text-gray-900">${marketStats.avgPricePerSqft.toFixed(0)}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-100">
              <span className="text-gray-600">Price/Sq Ft Difference</span>
              <span className={`font-semibold ${
                subjectPricePerSqft > marketStats.avgPricePerSqft ? 'text-danger-600' : 'text-success-600'
              }`}>
                {subjectPricePerSqft > marketStats.avgPricePerSqft ? '+' : ''}
                ${(subjectPricePerSqft - marketStats.avgPricePerSqft).toFixed(0)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Comparable Properties */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Comparable Sales</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 text-sm font-medium text-gray-700">Address</th>
                <th className="text-right py-3 text-sm font-medium text-gray-700">Price</th>
                <th className="text-right py-3 text-sm font-medium text-gray-700">Beds/Baths</th>
                <th className="text-right py-3 text-sm font-medium text-gray-700">Sq Ft</th>
                <th className="text-right py-3 text-sm font-medium text-gray-700">Price/Sq Ft</th>
                <th className="text-right py-3 text-sm font-medium text-gray-700">Sold Date</th>
                <th className="text-right py-3 text-sm font-medium text-gray-700">Distance</th>
              </tr>
            </thead>
            <tbody>
              {mockComps.map((comp, index) => (
                <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 text-sm text-gray-900">
                    <div className="flex items-center space-x-2">
                      <MapPin className="h-4 w-4 text-gray-400" />
                      <span>{comp.address}</span>
                    </div>
                  </td>
                  <td className="py-3 text-sm text-gray-900 text-right font-medium">
                    {formatCurrency(comp.price)}
                  </td>
                  <td className="py-3 text-sm text-gray-900 text-right">
                    {comp.beds}/{comp.baths}
                  </td>
                  <td className="py-3 text-sm text-gray-900 text-right">
                    {comp.sqft.toLocaleString()}
                  </td>
                  <td className="py-3 text-sm text-gray-900 text-right">
                    ${comp.pricePerSqft}
                  </td>
                  <td className="py-3 text-sm text-gray-900 text-right">
                    {formatDate(comp.soldDate)}
                  </td>
                  <td className="py-3 text-sm text-gray-900 text-right">
                    {comp.distance} mi
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Market Trends */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Market Trends</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600 mb-1">+5.2%</div>
            <div className="text-sm text-blue-800">Price Growth (YoY)</div>
            <div className="text-xs text-blue-600 mt-1">Strong appreciation</div>
          </div>
          
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600 mb-1">-12%</div>
            <div className="text-sm text-green-800">Days on Market</div>
            <div className="text-xs text-green-600 mt-1">Faster sales</div>
          </div>
          
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600 mb-1">+8.5%</div>
            <div className="text-sm text-purple-800">Inventory Growth</div>
            <div className="text-xs text-purple-600 mt-1">More options</div>
          </div>
        </div>
      </div>

      {/* Market Insights */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Market Insights</h3>
        <div className="space-y-3">
          <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg">
            <TrendingUp className="h-5 w-5 text-green-600" />
            <div>
              <div className="font-medium text-green-900">Strong Market</div>
              <div className="text-sm text-green-700">Prices up 5.2% year-over-year with strong demand</div>
            </div>
          </div>
          
          <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
            <Home className="h-5 w-5 text-blue-600" />
            <div>
              <div className="font-medium text-blue-900">Good Inventory</div>
              <div className="text-sm text-blue-700">Similar properties available for comparison</div>
            </div>
          </div>
          
          <div className="flex items-center space-x-3 p-3 bg-yellow-50 rounded-lg">
            <Search className="h-5 w-5 text-yellow-600" />
            <div>
              <div className="font-medium text-yellow-900">Competitive Pricing</div>
              <div className="text-sm text-yellow-700">Your property is priced competitively vs market</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarketComps; 