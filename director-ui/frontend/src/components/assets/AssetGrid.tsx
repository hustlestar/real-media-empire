import React from 'react';
import { Check, Star, Video, Image as ImageIcon, Music, FileText } from 'lucide-react';

interface Asset {
  id: string;
  name: string;
  type: 'image' | 'video' | 'audio' | 'document';
  thumbnail: string;
  favorite: boolean;
  size: number;
}

interface AssetGridProps {
  assets: Asset[];
  selectedAssets: Set<string>;
  onSelect: (id: string) => void;
  onAssetClick: (asset: Asset) => void;
}

const AssetGrid: React.FC<AssetGridProps> = ({ assets, selectedAssets, onSelect, onAssetClick }) => {
  const getIcon = (type: string) => {
    switch (type) {
      case 'video': return <Video className="w-6 h-6" />;
      case 'audio': return <Music className="w-6 h-6" />;
      case 'document': return <FileText className="w-6 h-6" />;
      default: return <ImageIcon className="w-6 h-6" />;
    }
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
      {assets.map((asset) => (
        <div
          key={asset.id}
          className={`relative group rounded-lg overflow-hidden border-2 transition cursor-pointer ${
            selectedAssets.has(asset.id)
              ? 'border-blue-500 ring-2 ring-blue-500'
              : 'border-gray-700 hover:border-blue-500'
          }`}
        >
          {/* Checkbox */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              onSelect(asset.id);
            }}
            className={`absolute top-2 left-2 z-10 w-6 h-6 rounded border-2 flex items-center justify-center transition ${
              selectedAssets.has(asset.id)
                ? 'bg-blue-500 border-blue-500'
                : 'bg-gray-900 bg-opacity-70 border-gray-600 hover:border-blue-500'
            }`}
          >
            {selectedAssets.has(asset.id) && <Check className="w-4 h-4 text-white" />}
          </button>

          {/* Favorite */}
          {asset.favorite && (
            <div className="absolute top-2 right-2 z-10">
              <Star className="w-5 h-5 text-yellow-400 fill-yellow-400" />
            </div>
          )}

          {/* Thumbnail */}
          <div
            onClick={() => onAssetClick(asset)}
            className="aspect-square bg-gray-800 flex items-center justify-center"
          >
            {asset.type === 'image' ? (
              <img src={asset.thumbnail} alt={asset.name} className="w-full h-full object-cover" />
            ) : (
              <div className="text-gray-500">{getIcon(asset.type)}</div>
            )}
          </div>

          {/* Info */}
          <div className="p-2 bg-gray-900 bg-opacity-90">
            <div className="text-sm font-semibold truncate">{asset.name}</div>
            <div className="text-xs text-gray-400">{(asset.size / (1024 * 1024)).toFixed(2)} MB</div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default AssetGrid;
