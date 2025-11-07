import React, { useState, useEffect } from 'react';
import { X, Search, Image, Video, Music, Star, Check } from 'lucide-react';
import { apiUrl } from '../config/api';

interface Asset {
  id: string;
  name: string;
  type: string;
  url: string;
  thumbnail_url?: string;
  is_favorite: boolean;
  size?: number;
  duration?: number;
}

interface AssetPickerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (asset: Asset) => void;
  filterType?: 'all' | 'image' | 'video' | 'audio';
  title?: string;
}

const AssetPickerModal: React.FC<AssetPickerModalProps> = ({
  isOpen,
  onClose,
  onSelect,
  filterType = 'all',
  title = 'Select Asset'
}) => {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [filteredAssets, setFilteredAssets] = useState<Asset[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState(filterType);
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchAssets();
    }
  }, [isOpen]);

  useEffect(() => {
    applyFilters();
  }, [assets, searchQuery, selectedType, showFavoritesOnly]);

  const fetchAssets = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(apiUrl('/api/assets'));
      const data = await response.json();
      setAssets(data.assets || []);
    } catch (error) {
      console.error('Error fetching assets:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...assets];

    // Type filter
    if (selectedType !== 'all') {
      filtered = filtered.filter(asset => asset.type === selectedType);
    }

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(asset =>
        asset.name.toLowerCase().includes(query)
      );
    }

    // Favorites filter
    if (showFavoritesOnly) {
      filtered = filtered.filter(asset => asset.is_favorite);
    }

    setFilteredAssets(filtered);
  };

  const handleSelect = () => {
    if (selectedAsset) {
      onSelect(selectedAsset);
      onClose();
      setSelectedAsset(null);
      setSearchQuery('');
    }
  };

  if (!isOpen) return null;

  const typeIcons = {
    image: Image,
    video: Video,
    audio: Music,
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return '';
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(1)} MB`;
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-gray-900 rounded-2xl shadow-2xl w-full max-w-5xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-800">
          <h2 className="text-2xl font-bold text-white">{title}</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-800 rounded-lg transition"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Search and Filters */}
        <div className="p-6 border-b border-gray-800 space-y-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search assets..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Type Filters */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setSelectedType('all')}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                selectedType === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setSelectedType('image')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition ${
                selectedType === 'image'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              <Image className="w-4 h-4" />
              Images
            </button>
            <button
              onClick={() => setSelectedType('video')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition ${
                selectedType === 'video'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              <Video className="w-4 h-4" />
              Videos
            </button>
            <button
              onClick={() => setSelectedType('audio')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition ${
                selectedType === 'audio'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              <Music className="w-4 h-4" />
              Audio
            </button>
            <button
              onClick={() => setShowFavoritesOnly(!showFavoritesOnly)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition ml-auto ${
                showFavoritesOnly
                  ? 'bg-yellow-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              <Star className="w-4 h-4" />
              Favorites
            </button>
          </div>
        </div>

        {/* Asset Grid */}
        <div className="flex-1 overflow-y-auto p-6">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-gray-400">Loading assets...</div>
            </div>
          ) : filteredAssets.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 text-gray-400">
              <Image className="w-16 h-16 mb-4 opacity-50" />
              <p>No assets found</p>
              <p className="text-sm mt-2">Try adjusting your filters</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {filteredAssets.map((asset) => {
                const Icon = typeIcons[asset.type as keyof typeof typeIcons] || Image;
                const isSelected = selectedAsset?.id === asset.id;

                return (
                  <div
                    key={asset.id}
                    onClick={() => setSelectedAsset(asset)}
                    className={`relative group cursor-pointer rounded-lg overflow-hidden transition ${
                      isSelected
                        ? 'ring-2 ring-blue-500'
                        : 'hover:ring-2 hover:ring-gray-600'
                    }`}
                  >
                    {/* Thumbnail or Icon */}
                    <div className="aspect-square bg-gray-800 flex items-center justify-center">
                      {asset.thumbnail_url ? (
                        <img
                          src={asset.thumbnail_url}
                          alt={asset.name}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <Icon className="w-12 h-12 text-gray-600" />
                      )}
                    </div>

                    {/* Selected Indicator */}
                    {isSelected && (
                      <div className="absolute top-2 right-2 bg-blue-600 rounded-full p-1">
                        <Check className="w-4 h-4 text-white" />
                      </div>
                    )}

                    {/* Favorite Indicator */}
                    {asset.is_favorite && (
                      <div className="absolute top-2 left-2">
                        <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                      </div>
                    )}

                    {/* Asset Info */}
                    <div className="p-3 bg-gray-800/90 backdrop-blur-sm">
                      <p className="text-white text-sm font-medium truncate">{asset.name}</p>
                      <div className="flex items-center justify-between mt-1">
                        <span className="text-xs text-gray-400">{asset.type}</span>
                        {asset.size && (
                          <span className="text-xs text-gray-400">{formatFileSize(asset.size)}</span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-800 flex items-center justify-between">
          <div className="text-sm text-gray-400">
            {filteredAssets.length} asset{filteredAssets.length !== 1 ? 's' : ''} found
            {selectedAsset && (
              <span className="ml-4 text-white">
                Selected: <span className="font-medium">{selectedAsset.name}</span>
              </span>
            )}
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="px-6 py-2 bg-gray-800 text-white rounded-lg hover:bg-gray-700 transition"
            >
              Cancel
            </button>
            <button
              onClick={handleSelect}
              disabled={!selectedAsset}
              className={`px-6 py-2 rounded-lg font-medium transition ${
                selectedAsset
                  ? 'bg-blue-600 text-white hover:bg-blue-500'
                  : 'bg-gray-800 text-gray-500 cursor-not-allowed'
              }`}
            >
              Select Asset
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssetPickerModal;
