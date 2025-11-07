/**
 * Platform Limits - Display content limits and requirements for each platform
 */

import React, { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, FileText, Hash, Image, Video } from 'lucide-react';

interface PlatformLimit {
  platform: string;
  maxCaptionLength: number;
  maxHashtags: number;
  maxVideoSizeMb: number;
  maxImageSizeMb: number;
  supportedFormats: string[];
  requiresApproval: boolean;
}

const PLATFORM_ICONS: Record<string, string> = {
  tiktok: '🎵',
  youtube: '▶️',
  instagram: '📸',
  facebook: '👍',
  twitter: '🐦',
  linkedin: '💼'
};

export default function PlatformLimits() {
  const [limits, setLimits] = useState<Record<string, PlatformLimit>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPlatformLimits();
  }, []);

  const fetchPlatformLimits = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/postiz/platforms/limits');

      if (!response.ok) {
        throw new Error('Failed to fetch platform limits');
      }

      const data = await response.json();
      setLimits(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-500">Loading platform information...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <AlertCircle className="w-12 h-12 text-red-600 mx-auto mb-4" />
        <p className="text-red-600">{error}</p>
        <button
          onClick={fetchPlatformLimits}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  const formatFileSize = (mb: number) => {
    if (mb >= 1000) {
      return `${(mb / 1000).toFixed(0)} GB`;
    }
    return `${mb} MB`;
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Platform Requirements</h2>
        <p className="text-gray-600">
          Content limits and requirements for each social media platform
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {Object.entries(limits).map(([platform, limit]) => (
          <div
            key={platform}
            className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden"
          >
            {/* Platform header */}
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 px-6 py-4 border-b border-gray-200">
              <div className="flex items-center gap-3">
                <span className="text-3xl">{PLATFORM_ICONS[platform]}</span>
                <h3 className="text-xl font-semibold capitalize">{platform}</h3>
              </div>
            </div>

            {/* Limits details */}
            <div className="p-6 space-y-4">
              {/* Caption length */}
              <div className="flex items-start gap-3">
                <FileText className="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <div className="text-sm font-medium text-gray-700">Caption Length</div>
                  <div className="text-lg font-semibold text-gray-900">
                    {limit.maxCaptionLength.toLocaleString()} characters
                  </div>
                </div>
              </div>

              {/* Hashtags */}
              <div className="flex items-start gap-3">
                <Hash className="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <div className="text-sm font-medium text-gray-700">Hashtags</div>
                  <div className="text-lg font-semibold text-gray-900">
                    {limit.maxHashtags} maximum
                  </div>
                </div>
              </div>

              {/* Video size */}
              <div className="flex items-start gap-3">
                <Video className="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <div className="text-sm font-medium text-gray-700">Video Size</div>
                  <div className="text-lg font-semibold text-gray-900">
                    {formatFileSize(limit.maxVideoSizeMb)} max
                  </div>
                </div>
              </div>

              {/* Image size */}
              <div className="flex items-start gap-3">
                <Image className="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <div className="text-sm font-medium text-gray-700">Image Size</div>
                  <div className="text-lg font-semibold text-gray-900">
                    {formatFileSize(limit.maxImageSizeMb)} max
                  </div>
                </div>
              </div>

              {/* Supported formats */}
              <div>
                <div className="text-sm font-medium text-gray-700 mb-2">Supported Formats</div>
                <div className="flex flex-wrap gap-2">
                  {limit.supportedFormats.map(format => (
                    <span
                      key={format}
                      className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium uppercase"
                    >
                      {format}
                    </span>
                  ))}
                </div>
              </div>

              {/* Approval status */}
              <div className="pt-4 border-t border-gray-200">
                {limit.requiresApproval ? (
                  <div className="flex items-center gap-2 text-sm text-yellow-700">
                    <AlertCircle className="w-4 h-4" />
                    <span>Requires approval before publishing</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2 text-sm text-green-700">
                    <CheckCircle className="w-4 h-4" />
                    <span>Instant publishing available</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* General tips */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-semibold text-blue-900 mb-3">💡 Publishing Tips</h3>
        <ul className="text-sm text-blue-800 space-y-2">
          <li>• Content is automatically optimized to meet platform requirements</li>
          <li>• Captions that exceed limits will be truncated with "..."</li>
          <li>• Excess hashtags will be removed, keeping the most important ones</li>
          <li>• Use high-quality videos and images for best engagement</li>
          <li>• Test mode allows preview without consuming credits</li>
        </ul>
      </div>
    </div>
  );
}
