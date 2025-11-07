/**
 * Stock Video Selector for Avatar Backgrounds
 *
 * Search and select background videos from multiple providers:
 * - Pexels (primary)
 * - Pixabay
 * - Coverr (curated)
 * - Videezy
 * - Videvo
 */

import React, { useState } from 'react';
import {
  Search,
  Play,
  Download,
  Loader2,
  CheckCircle,
  ExternalLink,
  Filter,
  Star
} from 'lucide-react';

interface VideoResult {
  id: string;
  title: string;
  description: string | null;
  duration: number;
  width: number;
  height: number;
  thumbnail_url: string;
  video_url: string;
  video_files: any[];
  user: string;
  provider: string;
  tags: string[];
  relevance_score?: number;
}

interface StockVideoSelectorProps {
  onSelectVideo: (videoUrl: string, videoInfo: VideoResult) => void;
  defaultQuery?: string;
}

export default function StockVideoSelector({ onSelectVideo, defaultQuery = "" }: StockVideoSelectorProps) {
  const [query, setQuery] = useState(defaultQuery);
  const [results, setResults] = useState<VideoResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedVideo, setSelectedVideo] = useState<VideoResult | null>(null);
  const [previewVideo, setPreviewVideo] = useState<string | null>(null);
  const [orientation, setOrientation] = useState<"landscape" | "portrait" | "square" | null>(null);

  const providerColors = {
    pexels: "bg-blue-100 text-blue-800",
    pixabay: "bg-green-100 text-green-800",
    coverr: "bg-purple-100 text-purple-800",
    videezy: "bg-orange-100 text-orange-800",
    videvo: "bg-pink-100 text-pink-800"
  };

  const handleSearch = async () => {
    if (!query.trim()) {
      alert('Please enter a search query');
      return;
    }

    setIsSearching(true);
    setResults([]);

    try {
      const params = new URLSearchParams({
        query: query.trim(),
        per_page: '15',
        provider: 'both'
      });

      if (orientation) {
        params.append('orientation', orientation);
      }

      const response = await fetch(`/api/stock-videos/search?${params}`);

      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`);
      }

      const data = await response.json();
      setResults(data.videos || []);

    } catch (error) {
      console.error('Search failed:', error);
      alert(`Search failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsSearching(false);
    }
  };

  const handleSelectVideo = (video: VideoResult) => {
    setSelectedVideo(video);
    onSelectVideo(video.video_url, video);
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-4">
      {/* Search Header */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200 p-4">
        <h3 className="font-semibold text-lg mb-3">Background Video Search</h3>

        {/* Search Bar */}
        <div className="flex gap-2 mb-3">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="e.g., business meeting, nature, technology"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button
            onClick={handleSearch}
            disabled={isSearching || !query.trim()}
            className={`px-6 py-2 rounded-lg font-medium text-white transition-colors flex items-center gap-2 ${
              isSearching || !query.trim()
                ? 'bg-gray-300 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {isSearching ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Searching...
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                Search
              </>
            )}
          </button>
        </div>

        {/* Filters */}
        <div className="flex gap-2">
          <span className="text-sm font-medium text-gray-700 py-2">Orientation:</span>
          {[
            { value: null, label: 'Any' },
            { value: 'landscape', label: 'Landscape' },
            { value: 'portrait', label: 'Portrait' },
            { value: 'square', label: 'Square' }
          ].map((opt) => (
            <button
              key={opt.label}
              onClick={() => setOrientation(opt.value as any)}
              className={`px-3 py-1 rounded text-sm transition-colors ${
                orientation === opt.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border border-gray-300 hover:bg-gray-50'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Results Grid */}
      {results.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-semibold">Found {results.length} videos</h4>
            <div className="text-sm text-gray-600">
              Sorted by relevance
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {results.map((video) => (
              <div
                key={video.id}
                className={`border-2 rounded-lg overflow-hidden transition-all cursor-pointer ${
                  selectedVideo?.id === video.id
                    ? 'border-blue-600 shadow-lg'
                    : 'border-gray-200 hover:border-gray-300 hover:shadow'
                }`}
                onClick={() => handleSelectVideo(video)}
              >
                {/* Thumbnail */}
                <div className="relative aspect-video bg-gray-900">
                  <img
                    src={video.thumbnail_url}
                    alt={video.title}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                    }}
                  />

                  {/* Duration Badge */}
                  <div className="absolute bottom-2 right-2 px-2 py-1 bg-black bg-opacity-75 text-white text-xs rounded">
                    {formatDuration(video.duration)}
                  </div>

                  {/* Provider Badge */}
                  <div className={`absolute top-2 left-2 px-2 py-1 rounded text-xs font-medium ${
                    providerColors[video.provider as keyof typeof providerColors] || 'bg-gray-100 text-gray-800'
                  }`}>
                    {video.provider}
                  </div>

                  {/* Relevance Score */}
                  {video.relevance_score && video.relevance_score > 1.5 && (
                    <div className="absolute top-2 right-2 px-2 py-1 bg-yellow-400 text-yellow-900 rounded text-xs font-bold flex items-center gap-1">
                      <Star className="w-3 h-3" />
                      High Match
                    </div>
                  )}

                  {/* Selected Check */}
                  {selectedVideo?.id === video.id && (
                    <div className="absolute inset-0 bg-blue-600 bg-opacity-20 flex items-center justify-center">
                      <CheckCircle className="w-12 h-12 text-white" />
                    </div>
                  )}
                </div>

                {/* Info */}
                <div className="p-3">
                  <div className="font-medium text-sm mb-1 line-clamp-1">{video.title}</div>
                  <div className="text-xs text-gray-500 mb-2">
                    {video.width}x{video.height} • {video.user}
                  </div>

                  {/* Tags */}
                  {video.tags && video.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-2">
                      {video.tags.slice(0, 3).map((tag, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded"
                        >
                          {tag.trim()}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex gap-2 mt-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setPreviewVideo(video.video_url);
                      }}
                      className="flex-1 px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded text-xs font-medium transition-colors flex items-center justify-center gap-1"
                    >
                      <Play className="w-3 h-3" />
                      Preview
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleSelectVideo(video);
                      }}
                      className="flex-1 px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-medium transition-colors flex items-center justify-center gap-1"
                    >
                      <CheckCircle className="w-3 h-3" />
                      Use This
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Video Preview Modal */}
      {previewVideo && (
        <div
          className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50"
          onClick={() => setPreviewVideo(null)}
        >
          <div className="relative max-w-4xl w-full mx-4" onClick={(e) => e.stopPropagation()}>
            <button
              onClick={() => setPreviewVideo(null)}
              className="absolute -top-10 right-0 text-white hover:text-gray-300"
            >
              Close
            </button>
            <video controls autoPlay className="w-full rounded-lg shadow-2xl">
              <source src={previewVideo} />
              Your browser does not support video playback.
            </video>
          </div>
        </div>
      )}

      {/* Popular Topics */}
      <div className="bg-gray-50 rounded-lg border border-gray-200 p-4">
        <h4 className="font-medium text-sm mb-2">Popular Topics:</h4>
        <div className="flex flex-wrap gap-2">
          {[
            'business meeting',
            'nature landscape',
            'technology abstract',
            'city skyline',
            'office workspace',
            'workout gym',
            'cooking kitchen',
            'creative studio'
          ].map((topic) => (
            <button
              key={topic}
              onClick={() => {
                setQuery(topic);
                setTimeout(handleSearch, 100);
              }}
              className="px-3 py-1 bg-white border border-gray-300 hover:border-blue-500 hover:text-blue-600 rounded text-sm transition-colors"
            >
              {topic}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
