import React from 'react';
import { X, Download, Trash2, Tag, Star, Copy } from 'lucide-react';

const AssetDetails: React.FC<any> = ({ asset, onClose, onUpdate }) => (
  <div className="bg-gray-800 rounded-lg p-6 sticky top-6">
    <div className="flex items-center justify-between mb-4">
      <h3 className="font-bold">Asset Details</h3>
      <button onClick={onClose} className="p-2 hover:bg-gray-700 rounded"><X className="w-5 h-5" /></button>
    </div>

    <div className="aspect-square bg-gray-900 rounded mb-4 flex items-center justify-center">
      {asset.type === 'image' ? (
        <img src={asset.thumbnail} alt={asset.name} className="w-full h-full object-contain" />
      ) : (
        <div className="text-gray-500 text-6xl">📄</div>
      )}
    </div>

    <div className="space-y-3 text-sm">
      <div><span className="text-gray-400">Name:</span> <div className="font-semibold">{asset.name}</div></div>
      <div><span className="text-gray-400">Type:</span> <span className="font-semibold">{asset.type}</span></div>
      <div><span className="text-gray-400">Size:</span> <span className="font-semibold">{(asset.size / (1024 * 1024)).toFixed(2)} MB</span></div>
      <div><span className="text-gray-400">Created:</span> <span className="font-semibold">{new Date(asset.created_at).toLocaleDateString()}</span></div>

      <div className="pt-3 border-t border-gray-700">
        <div className="text-gray-400 mb-2">Tags</div>
        <div className="flex flex-wrap gap-2">
          {asset.tags.map((tag: string) => (
            <span key={tag} className="px-2 py-1 bg-blue-600 bg-opacity-30 rounded text-xs">{tag}</span>
          ))}
        </div>
      </div>
    </div>

    <div className="mt-6 space-y-2">
      <button className="w-full py-2 bg-blue-600 hover:bg-blue-500 rounded-lg flex items-center justify-center space-x-2">
        <Download className="w-4 h-4" />
        <span>Download</span>
      </button>
      <button className="w-full py-2 bg-gray-700 hover:bg-gray-600 rounded-lg flex items-center justify-center space-x-2">
        <Star className="w-4 h-4" />
        <span>Toggle Favorite</span>
      </button>
      <button className="w-full py-2 bg-red-600 hover:bg-red-500 rounded-lg flex items-center justify-center space-x-2">
        <Trash2 className="w-4 h-4" />
        <span>Delete</span>
      </button>
    </div>
  </div>
);

export default AssetDetails;
