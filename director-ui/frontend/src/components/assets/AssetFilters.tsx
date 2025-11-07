import React from 'react';

const AssetFilters: React.FC<any> = ({ filters, onChange }) => (
  <div className="bg-gray-800 rounded-lg p-6 space-y-4">
    <h3 className="font-bold mb-4">Advanced Filters</h3>

    <div>
      <label className="block text-sm mb-2">Tags</label>
      <input type="text" placeholder="Enter tags..." className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg" />
    </div>

    <div className="grid grid-cols-2 gap-4">
      <div>
        <label className="block text-sm mb-2">Min Size (MB)</label>
        <input type="number" className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg" />
      </div>
      <div>
        <label className="block text-sm mb-2">Max Size (MB)</label>
        <input type="number" className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg" />
      </div>
    </div>

    <label className="flex items-center space-x-2">
      <input type="checkbox" checked={filters.favoriteOnly} onChange={(e) => onChange({...filters, favoriteOnly: e.target.checked})} />
      <span>Favorites only</span>
    </label>
  </div>
);

export default AssetFilters;
