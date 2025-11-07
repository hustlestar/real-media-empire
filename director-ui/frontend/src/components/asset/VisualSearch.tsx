import React, { useState, useRef } from 'react';
import { Image, Upload, Search, X, SlidersHorizontal, Grid3x3, List, Download, Trash2, Eye } from 'lucide-react';

export interface VisualSearchResult {
  id: string;
  assetType: 'shot' | 'frame' | 'image' | 'reference';
  thumbnailUrl: string;
  videoUrl?: string;
  similarity: number; // 0-100 percentage
  metadata: {
    filename: string;
    resolution: string;
    duration?: number;
    createdAt: Date;
    tags?: string[];
    dominantColors?: string[];
    mood?: string;
    composition?: string;
  };
  source?: {
    filmId?: string;
    shotId?: string;
    version?: number;
  };
}

export interface VisualFilters {
  minSimilarity: number; // 0-100
  assetTypes: Array<'shot' | 'frame' | 'image' | 'reference'>;
  colorMatch?: 'exact' | 'similar' | 'complementary' | 'any';
  compositionMatch?: 'exact' | 'similar' | 'any';
  moodMatch?: 'exact' | 'similar' | 'any';
  dateRange?: {
    start?: Date;
    end?: Date;
  };
}

interface VisualSearchProps {
  onSearch?: (imageFile: File, filters: VisualFilters) => Promise<VisualSearchResult[]>;
  onResultSelect?: (result: VisualSearchResult) => void;
  onDownload?: (result: VisualSearchResult) => void;
  onDelete?: (resultId: string) => void;
  maxResults?: number;
}

const VisualSearch: React.FC<VisualSearchProps> = ({
  onSearch,
  onResultSelect,
  onDownload,
  onDelete,
  maxResults = 50
}) => {
  const [queryImage, setQueryImage] = useState<string | null>(null);
  const [queryFile, setQueryFile] = useState<File | null>(null);
  const [results, setResults] = useState<VisualSearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedResultIds, setSelectedResultIds] = useState<string[]>([]);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const dropZoneRef = useRef<HTMLDivElement>(null);

  // Default filters
  const [filters, setFilters] = useState<VisualFilters>({
    minSimilarity: 70,
    assetTypes: ['shot', 'frame', 'image', 'reference'],
    colorMatch: 'any',
    compositionMatch: 'any',
    moodMatch: 'any'
  });

  // Handle file selection
  const handleFileSelect = (file: File) => {
    if (!file.type.startsWith('image/')) {
      alert('Please select an image file');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      setQueryImage(e.target?.result as string);
      setQueryFile(file);
      setResults([]); // Clear previous results
    };
    reader.readAsDataURL(file);
  };

  // File input change
  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  // Drag and drop
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();

    const file = e.dataTransfer.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  // Paste from clipboard
  const handlePaste = async () => {
    try {
      const clipboardItems = await navigator.clipboard.read();
      for (const item of clipboardItems) {
        for (const type of item.types) {
          if (type.startsWith('image/')) {
            const blob = await item.getType(type);
            const file = new File([blob], 'pasted-image.png', { type });
            handleFileSelect(file);
            break;
          }
        }
      }
    } catch (error) {
      console.error('Paste error:', error);
      alert('Failed to paste image. Please try uploading instead.');
    }
  };

  // Clear query
  const handleClearQuery = () => {
    setQueryImage(null);
    setQueryFile(null);
    setResults([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Execute search
  const handleSearch = async () => {
    if (!queryFile) {
      alert('Please select an image first');
      return;
    }

    setIsSearching(true);
    try {
      const searchResults = await onSearch?.(queryFile, filters);
      setResults(searchResults || []);
    } catch (error) {
      console.error('Search error:', error);
      alert('Search failed. Please try again.');
    } finally {
      setIsSearching(false);
    }
  };

  // Filter updates
  const handleFilterChange = (key: keyof VisualFilters, value: any) => {
    setFilters({ ...filters, [key]: value });
  };

  // Asset type toggle
  const toggleAssetType = (type: 'shot' | 'frame' | 'image' | 'reference') => {
    const current = filters.assetTypes;
    if (current.includes(type)) {
      if (current.length > 1) {
        handleFilterChange('assetTypes', current.filter(t => t !== type));
      }
    } else {
      handleFilterChange('assetTypes', [...current, type]);
    }
  };

  // Result selection
  const toggleResultSelection = (resultId: string) => {
    if (selectedResultIds.includes(resultId)) {
      setSelectedResultIds(selectedResultIds.filter(id => id !== resultId));
    } else {
      setSelectedResultIds([...selectedResultIds, resultId]);
    }
  };

  // Bulk actions
  const handleBulkDownload = () => {
    const selected = results.filter(r => selectedResultIds.includes(r.id));
    selected.forEach(result => onDownload?.(result));
  };

  const handleBulkDelete = () => {
    if (confirm(`Delete ${selectedResultIds.length} selected assets?`)) {
      selectedResultIds.forEach(id => onDelete?.(id));
      setSelectedResultIds([]);
      setResults(results.filter(r => !selectedResultIds.includes(r.id)));
    }
  };

  // Get similarity color
  const getSimilarityColor = (similarity: number): string => {
    if (similarity >= 90) return 'text-green-400';
    if (similarity >= 80) return 'text-blue-400';
    if (similarity >= 70) return 'text-yellow-400';
    return 'text-gray-400';
  };

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Image className="w-6 h-6 text-blue-400" />
          <div>
            <h3 className="text-lg font-bold text-white">Visual Search</h3>
            <p className="text-sm text-gray-400">Find similar assets by image</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {/* View Mode Toggle */}
          <div className="flex items-center bg-gray-900 rounded-lg p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded transition ${
                viewMode === 'grid'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
              title="Grid View"
            >
              <Grid3x3 className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded transition ${
                viewMode === 'list'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
              title="List View"
            >
              <List className="w-4 h-4" />
            </button>
          </div>

          {/* Filters Toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`px-3 py-2 rounded-lg transition flex items-center space-x-2 ${
              showFilters
                ? 'bg-blue-600 text-white'
                : 'bg-gray-900 text-gray-400 hover:bg-gray-700'
            }`}
          >
            <SlidersHorizontal className="w-4 h-4" />
            <span>Filters</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Query Image Panel */}
        <div className="space-y-4">
          <h4 className="text-sm font-semibold text-white">Query Image</h4>

          {/* Upload Area */}
          {!queryImage ? (
            <div
              ref={dropZoneRef}
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center bg-gray-900 hover:border-blue-500 transition cursor-pointer"
              onClick={() => fileInputRef.current?.click()}
            >
              <Upload className="w-12 h-12 text-gray-600 mx-auto mb-3" />
              <p className="text-gray-400 mb-2">Drop image here or click to browse</p>
              <p className="text-xs text-gray-500">Supports JPG, PNG, WebP</p>

              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileInputChange}
                className="hidden"
              />
            </div>
          ) : (
            <div className="relative bg-gray-900 rounded-lg overflow-hidden border border-gray-700">
              <img
                src={queryImage}
                alt="Query"
                className="w-full h-64 object-contain"
              />

              <button
                onClick={handleClearQuery}
                className="absolute top-2 right-2 p-2 bg-red-600 hover:bg-red-500 rounded-full transition"
                title="Clear"
              >
                <X className="w-4 h-4 text-white" />
              </button>
            </div>
          )}

          {/* Paste Button */}
          <button
            onClick={handlePaste}
            className="w-full px-3 py-2 bg-gray-900 hover:bg-gray-700 border border-gray-700 rounded-lg transition text-sm text-gray-300"
          >
            Paste from Clipboard
          </button>

          {/* Search Button */}
          <button
            onClick={handleSearch}
            disabled={!queryFile || isSearching}
            className="w-full px-4 py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg transition flex items-center justify-center space-x-2 font-medium"
          >
            <Search className={`w-5 h-5 ${isSearching ? 'animate-spin' : ''}`} />
            <span>{isSearching ? 'Searching...' : 'Search Similar'}</span>
          </button>

          {/* Filters Panel */}
          {showFilters && (
            <div className="bg-gray-900 rounded-lg p-4 border border-gray-700 space-y-4">
              <h5 className="text-sm font-semibold text-white">Search Filters</h5>

              {/* Minimum Similarity */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-xs text-gray-500">Min Similarity</label>
                  <span className="text-xs text-white">{filters.minSimilarity}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="5"
                  value={filters.minSimilarity}
                  onChange={(e) => handleFilterChange('minSimilarity', parseInt(e.target.value))}
                  className="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
              </div>

              {/* Asset Types */}
              <div>
                <label className="block text-xs text-gray-500 mb-2">Asset Types</label>
                <div className="grid grid-cols-2 gap-2">
                  {(['shot', 'frame', 'image', 'reference'] as const).map(type => (
                    <button
                      key={type}
                      onClick={() => toggleAssetType(type)}
                      className={`px-3 py-2 rounded text-xs transition ${
                        filters.assetTypes.includes(type)
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                      }`}
                    >
                      {type.charAt(0).toUpperCase() + type.slice(1)}
                    </button>
                  ))}
                </div>
              </div>

              {/* Color Match */}
              <div>
                <label className="block text-xs text-gray-500 mb-2">Color Match</label>
                <select
                  value={filters.colorMatch}
                  onChange={(e) => handleFilterChange('colorMatch', e.target.value)}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white text-sm focus:border-blue-500 focus:outline-none"
                >
                  <option value="any">Any</option>
                  <option value="exact">Exact</option>
                  <option value="similar">Similar</option>
                  <option value="complementary">Complementary</option>
                </select>
              </div>

              {/* Composition Match */}
              <div>
                <label className="block text-xs text-gray-500 mb-2">Composition</label>
                <select
                  value={filters.compositionMatch}
                  onChange={(e) => handleFilterChange('compositionMatch', e.target.value)}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white text-sm focus:border-blue-500 focus:outline-none"
                >
                  <option value="any">Any</option>
                  <option value="exact">Exact</option>
                  <option value="similar">Similar</option>
                </select>
              </div>

              {/* Mood Match */}
              <div>
                <label className="block text-xs text-gray-500 mb-2">Mood</label>
                <select
                  value={filters.moodMatch}
                  onChange={(e) => handleFilterChange('moodMatch', e.target.value)}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white text-sm focus:border-blue-500 focus:outline-none"
                >
                  <option value="any">Any</option>
                  <option value="exact">Exact</option>
                  <option value="similar">Similar</option>
                </select>
              </div>
            </div>
          )}
        </div>

        {/* Results Panel */}
        <div className="col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold text-white">
              Results ({results.length})
              {results.length >= maxResults && ` • Showing top ${maxResults}`}
            </h4>

            {selectedResultIds.length > 0 && (
              <div className="flex items-center space-x-2">
                <span className="text-xs text-gray-400">{selectedResultIds.length} selected</span>
                <button
                  onClick={handleBulkDownload}
                  className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 rounded text-xs transition flex items-center space-x-1"
                >
                  <Download className="w-3 h-3" />
                  <span>Download</span>
                </button>
                <button
                  onClick={handleBulkDelete}
                  className="px-3 py-1.5 bg-red-600 hover:bg-red-500 rounded text-xs transition flex items-center space-x-1"
                >
                  <Trash2 className="w-3 h-3" />
                  <span>Delete</span>
                </button>
              </div>
            )}
          </div>

          {/* Results Display */}
          {results.length === 0 ? (
            <div className="bg-gray-900 rounded-lg p-12 border border-gray-700 text-center">
              <Search className="w-12 h-12 text-gray-600 mx-auto mb-3" />
              <p className="text-gray-400 mb-2">
                {queryImage ? 'No results found' : 'Upload an image to start searching'}
              </p>
              <p className="text-sm text-gray-500">
                {queryImage ? 'Try adjusting your filters or using a different image' : 'We\'ll find visually similar assets'}
              </p>
            </div>
          ) : viewMode === 'grid' ? (
            <div className="grid grid-cols-3 gap-4 max-h-[800px] overflow-y-auto pr-2">
              {results.map((result) => (
                <div
                  key={result.id}
                  onClick={() => toggleResultSelection(result.id)}
                  className={`bg-gray-900 rounded-lg border-2 overflow-hidden cursor-pointer transition-all ${
                    selectedResultIds.includes(result.id)
                      ? 'border-blue-500'
                      : 'border-gray-700 hover:border-gray-600'
                  }`}
                >
                  {/* Thumbnail */}
                  <div className="relative aspect-video bg-gray-950 group">
                    <img
                      src={result.thumbnailUrl}
                      alt={result.metadata.filename}
                      className="w-full h-full object-cover"
                    />

                    {/* Similarity Badge */}
                    <div className={`absolute top-2 left-2 px-2 py-1 rounded-full text-xs font-bold ${
                      result.similarity >= 90 ? 'bg-green-600' :
                      result.similarity >= 80 ? 'bg-blue-600' :
                      result.similarity >= 70 ? 'bg-yellow-600' :
                      'bg-gray-600'
                    } text-white`}>
                      {result.similarity}%
                    </div>

                    {/* Asset Type Badge */}
                    <div className="absolute top-2 right-2 px-2 py-1 bg-gray-900/90 text-white text-xs rounded">
                      {result.assetType}
                    </div>

                    {/* Actions Overlay */}
                    <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition flex items-center justify-center space-x-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onResultSelect?.(result);
                        }}
                        className="p-2 bg-white/20 hover:bg-white/30 rounded-full transition"
                        title="View"
                      >
                        <Eye className="w-4 h-4 text-white" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onDownload?.(result);
                        }}
                        className="p-2 bg-white/20 hover:bg-white/30 rounded-full transition"
                        title="Download"
                      >
                        <Download className="w-4 h-4 text-white" />
                      </button>
                    </div>
                  </div>

                  {/* Metadata */}
                  <div className="p-3">
                    <p className="text-white text-sm font-medium truncate mb-1">
                      {result.metadata.filename}
                    </p>
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>{result.metadata.resolution}</span>
                      {result.metadata.duration && <span>{result.metadata.duration}s</span>}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-2 max-h-[800px] overflow-y-auto pr-2">
              {results.map((result) => (
                <div
                  key={result.id}
                  onClick={() => toggleResultSelection(result.id)}
                  className={`bg-gray-900 rounded-lg border-2 p-4 cursor-pointer transition-all ${
                    selectedResultIds.includes(result.id)
                      ? 'border-blue-500'
                      : 'border-gray-700 hover:border-gray-600'
                  }`}
                >
                  <div className="flex items-center space-x-4">
                    {/* Thumbnail */}
                    <img
                      src={result.thumbnailUrl}
                      alt={result.metadata.filename}
                      className="w-24 h-16 object-cover rounded border border-gray-700"
                    />

                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <p className="text-white font-medium truncate">{result.metadata.filename}</p>
                        <span className={`text-xs px-2 py-0.5 rounded ${getSimilarityColor(result.similarity)} bg-gray-800`}>
                          {result.similarity}% match
                        </span>
                      </div>
                      <div className="flex items-center space-x-3 text-xs text-gray-500">
                        <span>{result.assetType}</span>
                        <span>•</span>
                        <span>{result.metadata.resolution}</span>
                        {result.metadata.duration && (
                          <>
                            <span>•</span>
                            <span>{result.metadata.duration}s</span>
                          </>
                        )}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onResultSelect?.(result);
                        }}
                        className="p-2 bg-gray-800 hover:bg-gray-700 rounded transition"
                        title="View"
                      >
                        <Eye className="w-4 h-4 text-gray-400" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onDownload?.(result);
                        }}
                        className="p-2 bg-gray-800 hover:bg-gray-700 rounded transition"
                        title="Download"
                      >
                        <Download className="w-4 h-4 text-gray-400" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Tips */}
      <div className="mt-6 bg-blue-600/10 border border-blue-600/30 rounded-lg p-3">
        <p className="text-xs text-blue-400">
          <strong>💡 Pro Tip:</strong> For best results, use clear reference images with good lighting and composition.
          The system analyzes color palettes, composition patterns, and visual mood to find matches.
        </p>
      </div>
    </div>
  );
};

export default VisualSearch;
