import React, { useState, useEffect } from 'react';
import { Image, Video, Film, Music, FileText, Grid, List, Search, Filter, Upload, Download, Trash2, Tag, Star } from 'lucide-react';
import AssetGrid from '../components/assets/AssetGrid';
import AssetList from '../components/assets/AssetList';
import AssetFilters from '../components/assets/AssetFilters';
import AssetDetails from '../components/assets/AssetDetails';
import AssetUpload from '../components/assets/AssetUpload';

type ViewMode = 'grid' | 'list';
type AssetType = 'all' | 'image' | 'video' | 'audio' | 'document';

interface Asset {
  id: string;
  name: string;
  type: 'image' | 'video' | 'audio' | 'document';
  url: string;
  thumbnail: string;
  size: number;
  created_at: string;
  modified_at: string;
  tags: string[];
  metadata: Record<string, any>;
  favorite: boolean;
}

const AssetGalleryPage: React.FC = () => {
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [assets, setAssets] = useState<Asset[]>([]);
  const [filteredAssets, setFilteredAssets] = useState<Asset[]>([]);
  const [selectedAssets, setSelectedAssets] = useState<Set<string>>(new Set());
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<AssetType>('all');
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const [filters, setFilters] = useState({
    dateRange: null as [Date, Date] | null,
    tags: [] as string[],
    minSize: null as number | null,
    maxSize: null as number | null,
    favoriteOnly: false
  });

  useEffect(() => {
    fetchAssets();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [assets, searchQuery, filterType, filters]);

  const fetchAssets = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:8000/api/assets');
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

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(asset =>
        asset.name.toLowerCase().includes(query) ||
        asset.tags.some(tag => tag.toLowerCase().includes(query))
      );
    }

    // Type filter
    if (filterType !== 'all') {
      filtered = filtered.filter(asset => asset.type === filterType);
    }

    // Tags filter
    if (filters.tags.length > 0) {
      filtered = filtered.filter(asset =>
        filters.tags.some(tag => asset.tags.includes(tag))
      );
    }

    // Size filter
    if (filters.minSize !== null) {
      filtered = filtered.filter(asset => asset.size >= filters.minSize!);
    }
    if (filters.maxSize !== null) {
      filtered = filtered.filter(asset => asset.size <= filters.maxSize!);
    }

    // Favorite filter
    if (filters.favoriteOnly) {
      filtered = filtered.filter(asset => asset.favorite);
    }

    // Date range filter
    if (filters.dateRange) {
      const [start, end] = filters.dateRange;
      filtered = filtered.filter(asset => {
        const date = new Date(asset.created_at);
        return date >= start && date <= end;
      });
    }

    setFilteredAssets(filtered);
  };

  const handleSelect = (assetId: string) => {
    const newSelected = new Set(selectedAssets);
    if (newSelected.has(assetId)) {
      newSelected.delete(assetId);
    } else {
      newSelected.add(assetId);
    }
    setSelectedAssets(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedAssets.size === filteredAssets.length) {
      setSelectedAssets(new Set());
    } else {
      setSelectedAssets(new Set(filteredAssets.map(a => a.id)));
    }
  };

  const handleDeleteSelected = async () => {
    if (selectedAssets.size === 0) return;
    if (!confirm(`Delete ${selectedAssets.size} asset(s)?`)) return;

    try {
      await fetch('http://localhost:8000/api/assets/batch-delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ asset_ids: Array.from(selectedAssets) })
      });

      await fetchAssets();
      setSelectedAssets(new Set());
    } catch (error) {
      console.error('Error deleting assets:', error);
    }
  };

  const assetStats = {
    total: assets.length,
    images: assets.filter(a => a.type === 'image').length,
    videos: assets.filter(a => a.type === 'video').length,
    audio: assets.filter(a => a.type === 'audio').length,
    documents: assets.filter(a => a.type === 'document').length,
    totalSize: assets.reduce((sum, a) => sum + a.size, 0)
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-gray-900 text-white">
      {/* Header */}
      <header className="bg-black bg-opacity-50 backdrop-blur-md border-b border-gray-700">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Image className="w-8 h-8 text-blue-400" />
              <h1 className="text-2xl font-bold">Asset Gallery</h1>
              <span className="px-3 py-1 bg-blue-500 bg-opacity-20 rounded-full text-sm">
                {filteredAssets.length} assets
              </span>
            </div>

            <div className="flex items-center space-x-4">
              {/* View Mode Toggle */}
              <div className="flex bg-gray-800 rounded-lg p-1">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded transition ${
                    viewMode === 'grid' ? 'bg-blue-600' : 'hover:bg-gray-700'
                  }`}
                >
                  <Grid className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded transition ${
                    viewMode === 'list' ? 'bg-blue-600' : 'hover:bg-gray-700'
                  }`}
                >
                  <List className="w-4 h-4" />
                </button>
              </div>

              <button
                onClick={() => setShowUploadModal(true)}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg transition flex items-center space-x-2"
              >
                <Upload className="w-4 h-4" />
                <span>Upload</span>
              </button>
            </div>
          </div>

          {/* Search and Filters */}
          <div className="mt-4 flex items-center space-x-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search assets by name or tags..."
                className="w-full pl-10 pr-4 py-2 bg-gray-800 bg-opacity-70 border border-gray-700 rounded-lg focus:border-blue-500 focus:outline-none transition"
              />
            </div>

            {/* Type Filter */}
            <div className="flex space-x-2">
              <button
                onClick={() => setFilterType('all')}
                className={`px-4 py-2 rounded-lg transition ${
                  filterType === 'all' ? 'bg-blue-600' : 'bg-gray-800 hover:bg-gray-700'
                }`}
              >
                All ({assetStats.total})
              </button>
              <button
                onClick={() => setFilterType('image')}
                className={`px-4 py-2 rounded-lg transition flex items-center space-x-2 ${
                  filterType === 'image' ? 'bg-blue-600' : 'bg-gray-800 hover:bg-gray-700'
                }`}
              >
                <Image className="w-4 h-4" />
                <span>{assetStats.images}</span>
              </button>
              <button
                onClick={() => setFilterType('video')}
                className={`px-4 py-2 rounded-lg transition flex items-center space-x-2 ${
                  filterType === 'video' ? 'bg-blue-600' : 'bg-gray-800 hover:bg-gray-700'
                }`}
              >
                <Video className="w-4 h-4" />
                <span>{assetStats.videos}</span>
              </button>
              <button
                onClick={() => setFilterType('audio')}
                className={`px-4 py-2 rounded-lg transition flex items-center space-x-2 ${
                  filterType === 'audio' ? 'bg-blue-600' : 'bg-gray-800 hover:bg-gray-700'
                }`}
              >
                <Music className="w-4 h-4" />
                <span>{assetStats.audio}</span>
              </button>
            </div>

            {/* Advanced Filters Button */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`px-4 py-2 rounded-lg transition flex items-center space-x-2 ${
                showFilters ? 'bg-blue-600' : 'bg-gray-800 hover:bg-gray-700'
              }`}
            >
              <Filter className="w-4 h-4" />
              <span>Filters</span>
            </button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-6">
        {/* Bulk Actions Bar */}
        {selectedAssets.size > 0 && (
          <div className="mb-4 bg-blue-900 bg-opacity-20 border border-blue-600 rounded-lg p-4 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <span className="font-semibold">{selectedAssets.size} selected</span>
              <button
                onClick={handleSelectAll}
                className="text-sm text-blue-300 hover:text-blue-100"
              >
                {selectedAssets.size === filteredAssets.length ? 'Deselect All' : 'Select All'}
              </button>
            </div>

            <div className="flex items-center space-x-2">
              <button className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition flex items-center space-x-2">
                <Tag className="w-4 h-4" />
                <span>Add Tags</span>
              </button>
              <button className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition flex items-center space-x-2">
                <Download className="w-4 h-4" />
                <span>Download</span>
              </button>
              <button
                onClick={handleDeleteSelected}
                className="px-3 py-2 bg-red-600 hover:bg-red-500 rounded-lg transition flex items-center space-x-2"
              >
                <Trash2 className="w-4 h-4" />
                <span>Delete</span>
              </button>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Content */}
          <div className={`${selectedAsset ? 'lg:col-span-3' : 'lg:col-span-4'}`}>
            {showFilters && (
              <div className="mb-6">
                <AssetFilters
                  filters={filters}
                  onChange={setFilters}
                />
              </div>
            )}

            {isLoading ? (
              <div className="text-center py-20">
                <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <div>Loading assets...</div>
              </div>
            ) : filteredAssets.length === 0 ? (
              <div className="text-center py-20 text-gray-400">
                <Image className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <div>No assets found</div>
                <button
                  onClick={() => setShowUploadModal(true)}
                  className="mt-4 px-6 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg transition"
                >
                  Upload Assets
                </button>
              </div>
            ) : viewMode === 'grid' ? (
              <AssetGrid
                assets={filteredAssets}
                selectedAssets={selectedAssets}
                onSelect={handleSelect}
                onAssetClick={setSelectedAsset}
              />
            ) : (
              <AssetList
                assets={filteredAssets}
                selectedAssets={selectedAssets}
                onSelect={handleSelect}
                onAssetClick={setSelectedAsset}
              />
            )}
          </div>

          {/* Details Panel */}
          {selectedAsset && (
            <div className="lg:col-span-1">
              <AssetDetails
                asset={selectedAsset}
                onClose={() => setSelectedAsset(null)}
                onUpdate={fetchAssets}
              />
            </div>
          )}
        </div>
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <AssetUpload
          onClose={() => setShowUploadModal(false)}
          onUploadComplete={fetchAssets}
        />
      )}
    </div>
  );
};

export default AssetGalleryPage;
