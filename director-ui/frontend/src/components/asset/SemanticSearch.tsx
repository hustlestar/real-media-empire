import React, { useState, useRef } from 'react';
import { Search, Sparkles, Clock, Bookmark, TrendingUp, Filter, Grid3x3, List, Tag, X, Download, Eye } from 'lucide-react';

export interface SemanticSearchResult {
  id: string;
  assetType: 'shot' | 'scene' | 'sequence' | 'reference' | 'prompt';
  title: string;
  description: string;
  thumbnailUrl?: string;
  videoUrl?: string;
  semanticScore: number; // 0-100 relevance score
  metadata: {
    duration?: number;
    resolution?: string;
    createdAt: Date;
    tags: string[];
    prompt?: string;
    style?: string;
    mood?: string;
    subjects?: string[];
  };
  source?: {
    filmId?: string;
    shotId?: string;
    version?: number;
  };
  highlights?: string[]; // Matching keywords
}

export interface SearchQuery {
  text: string;
  filters?: {
    assetTypes?: Array<'shot' | 'scene' | 'sequence' | 'reference' | 'prompt'>;
    dateRange?: {
      start?: Date;
      end?: Date;
    };
    tags?: string[];
    minScore?: number;
    maxResults?: number;
  };
}

interface SemanticSearchProps {
  onSearch?: (query: SearchQuery) => Promise<SemanticSearchResult[]>;
  onResultSelect?: (result: SemanticSearchResult) => void;
  onSaveQuery?: (query: string) => void;
  savedQueries?: string[];
  suggestedQueries?: string[];
}

const SemanticSearch: React.FC<SemanticSearchProps> = ({
  onSearch,
  onResultSelect,
  onSaveQuery,
  savedQueries = [],
  suggestedQueries = [
    'dramatic sunset over futuristic cityscape',
    'close-up of character revealing emotion',
    'fast-paced action sequence with explosions',
    'quiet contemplative moment in nature',
    'neon-lit cyberpunk street scene',
    'wide establishing shot of vast landscape',
    'intimate two-person dialogue scene',
    'suspenseful chase through dark corridors'
  ]
}) => {
  const [searchText, setSearchText] = useState('');
  const [results, setResults] = useState<SemanticSearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchHistory, setSearchHistory] = useState<string[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);

  const searchInputRef = useRef<HTMLInputElement>(null);

  // Default filters
  const [filters, setFilters] = useState({
    assetTypes: ['shot', 'scene', 'sequence', 'reference', 'prompt'] as Array<'shot' | 'scene' | 'sequence' | 'reference' | 'prompt'>,
    minScore: 60,
    maxResults: 50
  });

  // Execute search
  const handleSearch = async (queryText?: string) => {
    const text = queryText || searchText;
    if (!text.trim()) return;

    setIsSearching(true);
    setShowHistory(false);

    try {
      const query: SearchQuery = {
        text: text.trim(),
        filters: {
          assetTypes: filters.assetTypes,
          minScore: filters.minScore,
          maxResults: filters.maxResults,
          tags: selectedTags.length > 0 ? selectedTags : undefined
        }
      };

      const searchResults = await onSearch?.(query);
      setResults(searchResults || []);

      // Add to history
      if (!searchHistory.includes(text)) {
        setSearchHistory([text, ...searchHistory].slice(0, 10));
      }
    } catch (error) {
      console.error('Search error:', error);
      alert('Search failed. Please try again.');
    } finally {
      setIsSearching(false);
    }
  };

  // Handle enter key
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  // Use suggested query
  const handleUseSuggestion = (query: string) => {
    setSearchText(query);
    handleSearch(query);
  };

  // Use history item
  const handleUseHistory = (query: string) => {
    setSearchText(query);
    handleSearch(query);
  };

  // Clear search
  const handleClearSearch = () => {
    setSearchText('');
    setResults([]);
    searchInputRef.current?.focus();
  };

  // Save current query
  const handleSaveQuery = () => {
    if (searchText.trim()) {
      onSaveQuery?.(searchText.trim());
    }
  };

  // Filter updates
  const handleFilterChange = (key: string, value: any) => {
    setFilters({ ...filters, [key]: value });
  };

  // Asset type toggle
  const toggleAssetType = (type: 'shot' | 'scene' | 'sequence' | 'reference' | 'prompt') => {
    const current = filters.assetTypes;
    if (current.includes(type)) {
      if (current.length > 1) {
        handleFilterChange('assetTypes', current.filter(t => t !== type));
      }
    } else {
      handleFilterChange('assetTypes', [...current, type]);
    }
  };

  // Tag selection
  const toggleTag = (tag: string) => {
    if (selectedTags.includes(tag)) {
      setSelectedTags(selectedTags.filter(t => t !== tag));
    } else {
      setSelectedTags([...selectedTags, tag]);
    }
  };

  // Get all unique tags from results
  const allTags = Array.from(
    new Set(results.flatMap(r => r.metadata.tags || []))
  ).sort();

  // Get score color
  const getScoreColor = (score: number): string => {
    if (score >= 90) return 'text-green-400';
    if (score >= 80) return 'text-blue-400';
    if (score >= 70) return 'text-yellow-400';
    return 'text-gray-400';
  };

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Sparkles className="w-6 h-6 text-purple-400" />
          <div>
            <h3 className="text-lg font-bold text-white">Semantic Search</h3>
            <p className="text-sm text-gray-400">Find assets using natural language</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {/* View Mode Toggle */}
          <div className="flex items-center bg-gray-900 rounded-lg p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded transition ${
                viewMode === 'grid'
                  ? 'bg-purple-600 text-white'
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
                  ? 'bg-purple-600 text-white'
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
                ? 'bg-purple-600 text-white'
                : 'bg-gray-900 text-gray-400 hover:bg-gray-700'
            }`}
          >
            <Filter className="w-4 h-4" />
            <span>Filters</span>
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <div className="relative">
          <input
            ref={searchInputRef}
            type="text"
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            onKeyPress={handleKeyPress}
            onFocus={() => setShowHistory(true)}
            placeholder="Describe what you're looking for... (e.g., 'dramatic sunset over city')"
            className="w-full px-4 py-3 pl-12 pr-24 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:border-purple-500 focus:outline-none"
          />

          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />

          <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center space-x-2">
            {searchText && (
              <button
                onClick={handleClearSearch}
                className="p-1.5 hover:bg-gray-800 rounded transition"
                title="Clear"
              >
                <X className="w-4 h-4 text-gray-500" />
              </button>
            )}

            <button
              onClick={handleSaveQuery}
              disabled={!searchText.trim()}
              className="p-1.5 hover:bg-gray-800 rounded transition disabled:opacity-50"
              title="Save Query"
            >
              <Bookmark className="w-4 h-4 text-gray-500" />
            </button>

            <button
              onClick={() => handleSearch()}
              disabled={!searchText.trim() || isSearching}
              className="px-4 py-1.5 bg-purple-600 hover:bg-purple-500 disabled:bg-gray-700 disabled:cursor-not-allowed rounded transition text-sm font-medium"
            >
              {isSearching ? 'Searching...' : 'Search'}
            </button>
          </div>
        </div>

        {/* History/Suggestions Dropdown */}
        {showHistory && !results.length && (
          <div className="mt-2 bg-gray-900 border border-gray-700 rounded-lg shadow-xl max-h-96 overflow-y-auto">
            {/* Recent Searches */}
            {searchHistory.length > 0 && (
              <div className="p-3 border-b border-gray-700">
                <div className="flex items-center space-x-2 mb-2">
                  <Clock className="w-4 h-4 text-gray-500" />
                  <span className="text-xs font-semibold text-gray-400">Recent Searches</span>
                </div>
                <div className="space-y-1">
                  {searchHistory.map((query, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleUseHistory(query)}
                      className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-gray-800 rounded transition"
                    >
                      {query}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Saved Queries */}
            {savedQueries.length > 0 && (
              <div className="p-3 border-b border-gray-700">
                <div className="flex items-center space-x-2 mb-2">
                  <Bookmark className="w-4 h-4 text-gray-500" />
                  <span className="text-xs font-semibold text-gray-400">Saved Queries</span>
                </div>
                <div className="space-y-1">
                  {savedQueries.map((query, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleUseHistory(query)}
                      className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-gray-800 rounded transition"
                    >
                      {query}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Suggested Queries */}
            <div className="p-3">
              <div className="flex items-center space-x-2 mb-2">
                <TrendingUp className="w-4 h-4 text-gray-500" />
                <span className="text-xs font-semibold text-gray-400">Suggested Queries</span>
              </div>
              <div className="space-y-1">
                {suggestedQueries.map((query, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleUseSuggestion(query)}
                    className="w-full text-left px-3 py-2 text-sm text-purple-400 hover:bg-gray-800 rounded transition"
                  >
                    {query}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="mb-6 bg-gray-900 rounded-lg p-4 border border-gray-700">
          <h4 className="text-sm font-semibold text-white mb-4">Search Filters</h4>

          <div className="grid grid-cols-3 gap-4">
            {/* Asset Types */}
            <div>
              <label className="block text-xs text-gray-500 mb-2">Asset Types</label>
              <div className="space-y-2">
                {(['shot', 'scene', 'sequence', 'reference', 'prompt'] as const).map(type => (
                  <label key={type} className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={filters.assetTypes.includes(type)}
                      onChange={() => toggleAssetType(type)}
                      className="w-4 h-4 rounded bg-gray-800 border-gray-700 text-purple-600 focus:ring-purple-500"
                    />
                    <span className="text-sm text-gray-300 capitalize">{type}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Minimum Score */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-xs text-gray-500">Min Relevance Score</label>
                <span className="text-xs text-white">{filters.minScore}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={filters.minScore}
                onChange={(e) => handleFilterChange('minScore', parseInt(e.target.value))}
                className="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-purple-600"
              />
            </div>

            {/* Max Results */}
            <div>
              <label className="block text-xs text-gray-500 mb-2">Max Results</label>
              <select
                value={filters.maxResults}
                onChange={(e) => handleFilterChange('maxResults', parseInt(e.target.value))}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white text-sm focus:border-purple-500 focus:outline-none"
              >
                <option value="10">10</option>
                <option value="25">25</option>
                <option value="50">50</option>
                <option value="100">100</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Tag Filter */}
      {allTags.length > 0 && (
        <div className="mb-6">
          <div className="flex items-center space-x-2 mb-3">
            <Tag className="w-4 h-4 text-gray-500" />
            <span className="text-sm text-gray-400">Filter by tags:</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {allTags.map(tag => (
              <button
                key={tag}
                onClick={() => toggleTag(tag)}
                className={`px-3 py-1.5 rounded-full text-xs transition ${
                  selectedTags.includes(tag)
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-900 text-gray-400 hover:bg-gray-700'
                }`}
              >
                {tag}
              </button>
            ))}
            {selectedTags.length > 0 && (
              <button
                onClick={() => setSelectedTags([])}
                className="px-3 py-1.5 bg-red-600 hover:bg-red-500 text-white rounded-full text-xs transition"
              >
                Clear All
              </button>
            )}
          </div>
        </div>
      )}

      {/* Results */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-sm font-semibold text-white">
            {results.length > 0 ? `${results.length} Results` : 'No results yet'}
          </h4>
        </div>

        {results.length === 0 ? (
          <div className="bg-gray-900 rounded-lg p-12 border border-gray-700 text-center">
            <Sparkles className="w-12 h-12 text-gray-600 mx-auto mb-3" />
            <p className="text-gray-400 mb-2">Start searching with natural language</p>
            <p className="text-sm text-gray-500">
              Describe scenes, moods, or visual concepts to find matching assets
            </p>
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-3 gap-4">
            {results.map((result) => (
              <div
                key={result.id}
                onClick={() => onResultSelect?.(result)}
                className="bg-gray-900 rounded-lg border border-gray-700 hover:border-purple-500 overflow-hidden cursor-pointer transition-all"
              >
                {/* Thumbnail */}
                {result.thumbnailUrl ? (
                  <div className="relative aspect-video bg-gray-950">
                    <img
                      src={result.thumbnailUrl}
                      alt={result.title}
                      className="w-full h-full object-cover"
                    />

                    {/* Score Badge */}
                    <div className={`absolute top-2 left-2 px-2 py-1 rounded-full text-xs font-bold ${
                      result.semanticScore >= 90 ? 'bg-green-600' :
                      result.semanticScore >= 80 ? 'bg-blue-600' :
                      result.semanticScore >= 70 ? 'bg-yellow-600' :
                      'bg-gray-600'
                    } text-white`}>
                      {result.semanticScore}% match
                    </div>

                    {/* Asset Type */}
                    <div className="absolute top-2 right-2 px-2 py-1 bg-gray-900/90 text-white text-xs rounded">
                      {result.assetType}
                    </div>
                  </div>
                ) : (
                  <div className="aspect-video bg-gray-950 flex items-center justify-center border-b border-gray-700">
                    <Sparkles className="w-8 h-8 text-gray-600" />
                  </div>
                )}

                {/* Info */}
                <div className="p-4">
                  <h5 className="text-white font-semibold mb-1 truncate">{result.title}</h5>
                  <p className="text-sm text-gray-400 mb-3 line-clamp-2">{result.description}</p>

                  {/* Highlights */}
                  {result.highlights && result.highlights.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-3">
                      {result.highlights.slice(0, 3).map((highlight, idx) => (
                        <span key={idx} className="px-2 py-0.5 bg-purple-600/20 text-purple-400 text-xs rounded">
                          {highlight}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Tags */}
                  {result.metadata.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {result.metadata.tags.slice(0, 3).map((tag, idx) => (
                        <span key={idx} className="px-2 py-0.5 bg-gray-800 text-gray-500 text-xs rounded">
                          #{tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {results.map((result) => (
              <div
                key={result.id}
                onClick={() => onResultSelect?.(result)}
                className="bg-gray-900 rounded-lg border border-gray-700 hover:border-purple-500 p-4 cursor-pointer transition-all"
              >
                <div className="flex items-start space-x-4">
                  {/* Thumbnail */}
                  {result.thumbnailUrl ? (
                    <img
                      src={result.thumbnailUrl}
                      alt={result.title}
                      className="w-32 h-20 object-cover rounded border border-gray-700"
                    />
                  ) : (
                    <div className="w-32 h-20 bg-gray-950 rounded border border-gray-700 flex items-center justify-center">
                      <Sparkles className="w-6 h-6 text-gray-600" />
                    </div>
                  )}

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-1">
                      <h5 className="text-white font-semibold truncate">{result.title}</h5>
                      <span className={`text-xs px-2 py-0.5 rounded ${getScoreColor(result.semanticScore)} bg-gray-800`}>
                        {result.semanticScore}%
                      </span>
                      <span className="text-xs px-2 py-0.5 bg-gray-800 text-gray-400 rounded">
                        {result.assetType}
                      </span>
                    </div>

                    <p className="text-sm text-gray-400 mb-2">{result.description}</p>

                    {/* Highlights */}
                    {result.highlights && result.highlights.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-2">
                        {result.highlights.map((highlight, idx) => (
                          <span key={idx} className="px-2 py-0.5 bg-purple-600/20 text-purple-400 text-xs rounded">
                            {highlight}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Tags and Metadata */}
                    <div className="flex items-center space-x-3 text-xs text-gray-500">
                      {result.metadata.duration && <span>⏱️ {result.metadata.duration}s</span>}
                      {result.metadata.resolution && <span>{result.metadata.resolution}</span>}
                      {result.metadata.tags.length > 0 && (
                        <>
                          <span>•</span>
                          {result.metadata.tags.slice(0, 3).map((tag, idx) => (
                            <span key={idx}>#{tag}</span>
                          ))}
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
                        // Download functionality
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

      {/* Tips */}
      <div className="mt-6 bg-purple-600/10 border border-purple-600/30 rounded-lg p-3">
        <p className="text-xs text-purple-400">
          <strong>💡 Pro Tip:</strong> Use descriptive language about mood, lighting, composition, and subject matter.
          The system understands concepts like "cinematic", "moody", "wide shot", and specific emotions or actions.
        </p>
      </div>
    </div>
  );
};

export default SemanticSearch;
