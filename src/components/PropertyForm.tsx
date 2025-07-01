import React from 'react';
import { Home, Calculator, Settings, Play } from 'lucide-react';

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

interface PropertyFormProps {
  propertyData: PropertyData;
  setPropertyData: (data: PropertyData) => void;
  assumptions: InvestmentAssumptions;
  setAssumptions: (assumptions: InvestmentAssumptions) => void;
  onAnalyze: () => void;
}

const PropertyForm: React.FC<PropertyFormProps> = ({
  propertyData,
  setPropertyData,
  assumptions,
  setAssumptions,
  onAnalyze
}) => {
  const handlePropertyChange = (field: keyof PropertyData, value: string | number) => {
    setPropertyData({
      ...propertyData,
      [field]: value
    });
  };

  const handleAssumptionChange = (field: keyof InvestmentAssumptions, value: number) => {
    setAssumptions({
      ...assumptions,
      [field]: value
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-2 mb-6">
        <Home className="h-6 w-6 text-primary-600" />
        <h2 className="text-2xl font-bold text-gray-900">Property Information</h2>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Property Information */}
        <div className="card">
          <div className="flex items-center space-x-2 mb-4">
            <Home className="h-5 w-5 text-primary-600" />
            <h3 className="text-lg font-semibold text-gray-900">Property Details</h3>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Address
              </label>
              <input
                type="text"
                value={propertyData.address}
                onChange={(e) => handlePropertyChange('address', e.target.value)}
                className="input-field"
                placeholder="123 Main St, Milwaukee, WI"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Price ($)
                </label>
                <input
                  type="number"
                  value={propertyData.price || ''}
                  onChange={(e) => handlePropertyChange('price', Number(e.target.value))}
                  className="input-field"
                  placeholder="250000"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Square Feet
                </label>
                <input
                  type="number"
                  value={propertyData.sqft || ''}
                  onChange={(e) => handlePropertyChange('sqft', Number(e.target.value))}
                  className="input-field"
                  placeholder="1500"
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Bedrooms
                </label>
                <input
                  type="number"
                  value={propertyData.beds || ''}
                  onChange={(e) => handlePropertyChange('beds', Number(e.target.value))}
                  className="input-field"
                  min="0"
                  max="10"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Bathrooms
                </label>
                <input
                  type="number"
                  value={propertyData.baths || ''}
                  onChange={(e) => handlePropertyChange('baths', Number(e.target.value))}
                  className="input-field"
                  min="0"
                  max="10"
                  step="0.5"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Zip Code
                </label>
                <input
                  type="text"
                  value={propertyData.zipcode}
                  onChange={(e) => handlePropertyChange('zipcode', e.target.value)}
                  className="input-field"
                  placeholder="53202"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Neighborhood
                </label>
                <input
                  type="text"
                  value={propertyData.neighborhood}
                  onChange={(e) => handlePropertyChange('neighborhood', e.target.value)}
                  className="input-field"
                  placeholder="Downtown"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Property Type
                </label>
                <select
                  value={propertyData.propertyType}
                  onChange={(e) => handlePropertyChange('propertyType', e.target.value)}
                  className="input-field"
                >
                  <option value="House">House</option>
                  <option value="Duplex">Duplex</option>
                  <option value="Apartment">Apartment</option>
                  <option value="Condo">Condo</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Investment Assumptions */}
        <div className="card">
          <div className="flex items-center space-x-2 mb-4">
            <Settings className="h-5 w-5 text-primary-600" />
            <h3 className="text-lg font-semibold text-gray-900">Investment Assumptions</h3>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Down Payment: {assumptions.downPaymentPct}%
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={assumptions.downPaymentPct}
                onChange={(e) => handleAssumptionChange('downPaymentPct', Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Interest Rate: {assumptions.interestRate}%
              </label>
              <input
                type="range"
                min="0"
                max="10"
                step="0.1"
                value={assumptions.interestRate}
                onChange={(e) => handleAssumptionChange('interestRate', Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Loan Term: {assumptions.loanTerm} years
              </label>
              <input
                type="range"
                min="15"
                max="30"
                value={assumptions.loanTerm}
                onChange={(e) => handleAssumptionChange('loanTerm', Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Property Tax Rate: {assumptions.propertyTaxRate}%
              </label>
              <input
                type="range"
                min="0"
                max="5"
                step="0.1"
                value={assumptions.propertyTaxRate}
                onChange={(e) => handleAssumptionChange('propertyTaxRate', Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Insurance Rate: {assumptions.insuranceRate}%
              </label>
              <input
                type="range"
                min="0"
                max="2"
                step="0.1"
                value={assumptions.insuranceRate}
                onChange={(e) => handleAssumptionChange('insuranceRate', Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Maintenance Rate: {assumptions.maintenanceRate}%
              </label>
              <input
                type="range"
                min="0"
                max="5"
                step="0.1"
                value={assumptions.maintenanceRate}
                onChange={(e) => handleAssumptionChange('maintenanceRate', Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Vacancy Rate: {assumptions.vacancyRate}%
              </label>
              <input
                type="range"
                min="0"
                max="20"
                step="0.5"
                value={assumptions.vacancyRate}
                onChange={(e) => handleAssumptionChange('vacancyRate', Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Analyze Button */}
      <div className="flex justify-center">
        <button
          onClick={onAnalyze}
          disabled={!propertyData.price || !propertyData.address}
          className="btn-primary flex items-center space-x-2 px-8 py-3 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Play className="h-5 w-5" />
          <span>Analyze Investment</span>
        </button>
      </div>

      <style jsx>{`
        .slider::-webkit-slider-thumb {
          appearance: none;
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: #2563eb;
          cursor: pointer;
        }
        
        .slider::-moz-range-thumb {
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: #2563eb;
          cursor: pointer;
          border: none;
        }
      `}</style>
    </div>
  );
};

export default PropertyForm; 