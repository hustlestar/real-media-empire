/**
 * Trend Research - Discover viral trends using Perplexity AI
 *
 * Features:
 * - Platform-specific trend discovery
 * - Hashtag optimization with platform limits
 * - Content strategy generation
 * - Real-time web search powered by Perplexity
 */

import React, { useState } from 'react';
import {
  TrendingUp,
  Hash,
  Search,
  Loader2,
  Sparkles,
  CheckCircle,
  AlertCircle,
  Copy,
  ExternalLink
} from 'lucide-react';

interface Trend {
  name: string;
  description: string;
  hashtags: string[];
  contentStyles: string[];
  exampleContent?: string;
}

interface TrendResearchResult {
  topic: string;
  platform: string;
  trends: Trend[];
}

type Platform = 'tiktok' | 'youtube' | 'instagram' | 'twitter' | 'linkedin';

const PLATFORMS = {
  tiktok: { name: 'TikTok', icon: '📱', color: 'pink', maxHashtags: 30 },
  youtube: { name: 'YouTube', icon: '▶️', color: 'red', maxHashtags: 15 },
  instagram: { name: 'Instagram', icon: '📷', color: 'purple', maxHashtags: 30 },
  twitter: { name: 'Twitter', icon: '🐦', color: 'blue', maxHashtags: 10 },
  linkedin: { name: 'LinkedIn', icon: '💼', color: 'blue', maxHashtags: 30 }
};

export default function TrendResearch() {
  const [topic, setTopic] = useState('');
  const [platform, setPlatform] = useState<Platform>('tiktok');
  const [numTrends, setNumTrends] = useState(3);
  const [isResearching, setIsResearching] = useState(false);
  const [result, setResult] = useState<TrendResearchResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [hashtagContent, setHashtagContent] = useState('');
  const [maxHashtags, setMaxHashtags] = useState(10);
  const [optimizedHashtags, setOptimizedHashtags] = useState<string[]>([]);
  const [isOptimizing, setIsOptimizing] = useState(false);

  const handleResearch = async () => {
    if (!topic.trim()) {
      alert('Please enter a topic');
      return;
    }

    setIsResearching(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('/api/trends/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: topic.trim(),
          platform,
          num_trends: numTrends
        })
      });

      if (!response.ok) {
        throw new Error(`Research failed: ${response.statusText}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsResearching(false);
    }
  };

  const handleOptimizeHashtags = async () => {
    if (!hashtagContent.trim()) {
      alert('Please describe your content');
      return;
    }

    setIsOptimizing(true);
    setError(null);

    try {
      const response = await fetch('/api/trends/optimize-hashtags', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content_description: hashtagContent.trim(),
          platform,
          max_hashtags: maxHashtags
        })
      });

      if (!response.ok) {
        throw new Error(`Optimization failed: ${response.statusText}`);
      }

      const data = await response.json();
      setOptimizedHashtags(data.hashtags);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsOptimizing(false);
    }
  };

  const copyHashtags = (hashtags: string[]) => {
    navigator.clipboard.writeText(hashtags.join(' '));
  };

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-3 mb-2">
          <TrendingUp className="w-8 h-8 text-blue-600" />
          <h1 className="text-2xl font-bold">Trend Research</h1>
        </div>
        <p className="text-gray-600">
          Discover viral trends and optimize hashtags with AI-powered real-time web search
        </p>
      </div>

      {/* Platform Selection */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Select Platform</h2>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {(Object.keys(PLATFORMS) as Platform[]).map((platformKey) => {
            const platformInfo = PLATFORMS[platformKey];
            const isSelected = platform === platformKey;

            return (
              <button
                key={platformKey}
                onClick={() => setPlatform(platformKey)}
                className={`p-4 border-2 rounded-lg transition-all ${
                  isSelected
                    ? `border-${platformInfo.color}-600 bg-${platformInfo.color}-50`
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="text-3xl mb-2">{platformInfo.icon}</div>
                <div className="font-semibold text-sm">{platformInfo.name}</div>
                <div className="text-xs text-gray-600 mt-1">
                  Max {platformInfo.maxHashtags} tags
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Trend Discovery */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-4">
          <Search className="w-5 h-5 text-green-600" />
          <h2 className="text-lg font-semibold">Discover Trends</h2>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Topic or Niche
            </label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., cold showers, AI art, productivity hacks"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              onKeyPress={(e) => e.key === 'Enter' && handleResearch()}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Number of Trends
            </label>
            <select
              value={numTrends}
              onChange={(e) => setNumTrends(parseInt(e.target.value))}
              className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value={1}>1 trend</option>
              <option value={3}>3 trends</option>
              <option value={5}>5 trends</option>
            </select>
          </div>

          <button
            onClick={handleResearch}
            disabled={isResearching || !topic.trim()}
            className={`w-full py-3 rounded-lg font-semibold text-white transition-all flex items-center justify-center gap-2 ${
              isResearching || !topic.trim()
                ? 'bg-gray-300 cursor-not-allowed'
                : 'bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700'
            }`}
          >
            {isResearching ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Researching...
              </>
            ) : (
              <>
                <Search className="w-5 h-5" />
                Research Trends
              </>
            )}
          </button>
        </div>
      </div>

      {/* Results */}
      {result && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <h2 className="text-lg font-semibold">
              Trending in {result.topic} on {PLATFORMS[result.platform as Platform].name}
            </h2>
          </div>

          <div className="space-y-6">
            {result.trends.map((trend, idx) => (
              <div key={idx} className="p-5 bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg border border-blue-200">
                <div className="flex items-start gap-3 mb-3">
                  <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold">
                    {idx + 1}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-bold text-lg text-blue-900">{trend.name}</h3>
                    <p className="text-gray-700 mt-1">{trend.description}</p>
                  </div>
                </div>

                {trend.hashtags && trend.hashtags.length > 0 && (
                  <div className="mb-3">
                    <div className="flex items-center gap-2 mb-2">
                      <Hash className="w-4 h-4 text-blue-600" />
                      <span className="text-sm font-semibold text-blue-900">Hashtags:</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {trend.hashtags.map((tag, tagIdx) => (
                        <span
                          key={tagIdx}
                          className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
                        >
                          #{tag}
                        </span>
                      ))}
                    </div>
                    <button
                      onClick={() => copyHashtags(trend.hashtags)}
                      className="mt-2 text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
                    >
                      <Copy className="w-4 h-4" />
                      Copy hashtags
                    </button>
                  </div>
                )}

                {trend.contentStyles && trend.contentStyles.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <Sparkles className="w-4 h-4 text-purple-600" />
                      <span className="text-sm font-semibold text-purple-900">Content Styles:</span>
                    </div>
                    <ul className="space-y-1">
                      {trend.contentStyles.map((style, styleIdx) => (
                        <li key={styleIdx} className="flex items-center gap-2 text-sm text-gray-700">
                          <div className="w-1.5 h-1.5 rounded-full bg-purple-600"></div>
                          {style}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Hashtag Optimizer */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-4">
          <Hash className="w-5 h-5 text-purple-600" />
          <h2 className="text-lg font-semibold">Hashtag Optimizer</h2>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Describe Your Content
            </label>
            <textarea
              value={hashtagContent}
              onChange={(e) => setHashtagContent(e.target.value)}
              placeholder="e.g., A short video showing a morning routine for productivity with cold shower and meditation"
              rows={3}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Maximum Hashtags ({PLATFORMS[platform].maxHashtags} limit for {PLATFORMS[platform].name})
            </label>
            <input
              type="number"
              value={maxHashtags}
              onChange={(e) => setMaxHashtags(Math.min(parseInt(e.target.value) || 10, PLATFORMS[platform].maxHashtags))}
              min={1}
              max={PLATFORMS[platform].maxHashtags}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            />
          </div>

          <button
            onClick={handleOptimizeHashtags}
            disabled={isOptimizing || !hashtagContent.trim()}
            className={`w-full py-3 rounded-lg font-semibold text-white transition-all flex items-center justify-center gap-2 ${
              isOptimizing || !hashtagContent.trim()
                ? 'bg-gray-300 cursor-not-allowed'
                : 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700'
            }`}
          >
            {isOptimizing ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Optimizing...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                Optimize Hashtags
              </>
            )}
          </button>
        </div>

        {optimizedHashtags.length > 0 && (
          <div className="mt-6 p-5 bg-purple-50 border border-purple-200 rounded-lg">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-purple-900">Optimized Hashtags</h3>
              <button
                onClick={() => copyHashtags(optimizedHashtags)}
                className="px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm flex items-center gap-2 transition-colors"
              >
                <Copy className="w-4 h-4" />
                Copy All
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {optimizedHashtags.map((tag, idx) => (
                <span key={idx} className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium">
                  #{tag}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <span className="text-red-800">{error}</span>
        </div>
      )}
    </div>
  );
}
