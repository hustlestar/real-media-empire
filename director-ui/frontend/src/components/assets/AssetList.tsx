import React from 'react';
import { Check, Star, Video, Image, Music, FileText } from 'lucide-react';

const AssetList: React.FC<any> = ({ assets, selectedAssets, onSelect, onAssetClick }) => (
  <div className="space-y-2">
    {assets.map((asset: any) => (
      <div
        key={asset.id}
        onClick={() => onAssetClick(asset)}
        className={`flex items-center space-x-4 p-4 rounded-lg cursor-pointer transition ${
          selectedAssets.has(asset.id) ? 'bg-blue-900 bg-opacity-30' : 'bg-gray-800 hover:bg-gray-750'
        }`}
      >
        <input type="checkbox" checked={selectedAssets.has(asset.id)} onChange={() => onSelect(asset.id)} className="w-5 h-5" />
        <div className="w-16 h-16 bg-gray-700 rounded flex items-center justify-center">
          {asset.type === 'image' ? <Image className="w-6 h-6" /> : <Video className="w-6 h-6" />}
        </div>
        <div className="flex-1">
          <div className="font-semibold">{asset.name}</div>
          <div className="text-sm text-gray-400">{asset.type} • {(asset.size / (1024 * 1024)).toFixed(2)} MB</div>
        </div>
        {asset.favorite && <Star className="w-5 h-5 text-yellow-400 fill-yellow-400" />}
      </div>
    ))}
  </div>
);

export default AssetList;
