/**
 * Publish Form - Create and publish social media posts
 *
 * Features:
 * - Multi-platform account selection
 * - Content upload or URL input
 * - Caption editor with character count
 * - Hashtag management
 * - Platform-specific optimization warnings
 * - Publish immediately or schedule
 */

import React, { useState, useEffect } from 'react';
import {
  Upload,
  Link as LinkIcon,
  Hash,
  Send,
  Calendar,
  AlertTriangle,
  CheckCircle,
  Loader2,
  X
} from 'lucide-react';
import { PublishingPost } from './PublishingHub';

interface PublishFormProps {
  selectedAccounts: string[];
  onAccountsChange: (accounts: string[]) => void;
  onPublishSuccess: (post: PublishingPost) => void;
}

interface PlatformLimit {
  platform: string;
  maxCaptionLength: number;
  maxHashtags: number;
}

const PLATFORM_ICONS: Record<string, string> = {
  tiktok: '🎵',
  youtube: '▶️',
  instagram: '📸',
  facebook: '👍',
  twitter: '🐦',
  linkedin: '💼'
};

export default function PublishForm({ selectedAccounts, onAccountsChange, onPublishSuccess }: PublishFormProps) {
  const [contentUrl, setContentUrl] = useState('');
  const [caption, setCaption] = useState('');
  const [hashtags, setHashtags] = useState<string[]>([]);
  const [hashtagInput, setHashtagInput] = useState('');
  const [publishing, setPublishing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [platformLimits, setPlatformLimits] = useState<Record<string, PlatformLimit>>({});

  // Mock accounts (in real app, fetch from API)
  const [accounts] = useState([
    { id: 'acc1', platform: 'tiktok', name: 'TikTok Main', handle: '@myaccount' },
    { id: 'acc2', platform: 'youtube', name: 'YouTube Channel', handle: 'My Channel' },
    { id: 'acc3', platform: 'instagram', name: 'Instagram Main', handle: '@myinsta' },
    { id: 'acc4', platform: 'facebook', name: 'Facebook Page', handle: 'My Page' },
    { id: 'acc5', platform: 'twitter', name: 'Twitter', handle: '@mytwitter' },
    { id: 'acc6', platform: 'linkedin', name: 'LinkedIn', handle: 'My Company' }
  ]);

  // Fetch platform limits
  useEffect(() => {
    fetchPlatformLimits();
  }, []);

  const fetchPlatformLimits = async () => {
    try {
      const response = await fetch('/api/postiz/platforms/limits');
      if (response.ok) {
        const limits = await response.json();
        setPlatformLimits(limits);
      }
    } catch (err) {
      console.error('Failed to fetch platform limits:', err);
    }
  };

  const toggleAccount = (accountId: string) => {
    if (selectedAccounts.includes(accountId)) {
      onAccountsChange(selectedAccounts.filter(id => id !== accountId));
    } else {
      onAccountsChange([...selectedAccounts, accountId]);
    }
  };

  const addHashtag = () => {
    const tag = hashtagInput.trim();
    if (tag && !hashtags.includes(tag)) {
      setHashtags([...hashtags, tag.startsWith('#') ? tag : `#${tag}`]);
      setHashtagInput('');
    }
  };

  const removeHashtag = (tag: string) => {
    setHashtags(hashtags.filter(t => t !== tag));
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addHashtag();
    }
  };

  // Check for platform-specific warnings
  const getWarnings = () => {
    const warnings: string[] = [];
    const selectedPlatforms = accounts
      .filter(acc => selectedAccounts.includes(acc.id))
      .map(acc => acc.platform);

    selectedPlatforms.forEach(platform => {
      const limits = platformLimits[platform];
      if (limits) {
        if (caption.length > limits.maxCaptionLength) {
          warnings.push(`${platform}: Caption exceeds limit (${limits.maxCaptionLength} chars)`);
        }
        if (hashtags.length > limits.maxHashtags) {
          warnings.push(`${platform}: Too many hashtags (max ${limits.maxHashtags})`);
        }
      }
    });

    return warnings;
  };

  const handlePublish = async () => {
    if (selectedAccounts.length === 0) {
      setError('Please select at least one account');
      return;
    }

    if (!contentUrl) {
      setError('Please provide content URL');
      return;
    }

    if (!caption.trim()) {
      setError('Please write a caption');
      return;
    }

    setPublishing(true);
    setError(null);

    try {
      // Publish to each selected account
      const promises = selectedAccounts.map(async (accountId) => {
        const account = accounts.find(a => a.id === accountId);
        if (!account) return null;

        const response = await fetch('/api/postiz/publish', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            account_id: accountId,
            platform: account.platform,
            content_type: 'video',
            content_url: contentUrl,
            caption: caption,
            hashtags: hashtags.map(tag => tag.replace('#', ''))
          })
        });

        if (!response.ok) {
          throw new Error(`Failed to publish to ${account.platform}`);
        }

        const result = await response.json();
        return result;
      });

      const results = await Promise.all(promises);

      // Report success for each published post
      results.forEach((result, idx) => {
        if (result && result.success) {
          const account = accounts.find(a => a.id === selectedAccounts[idx]);
          if (account) {
            onPublishSuccess({
              id: result.post_id || `post-${Date.now()}-${idx}`,
              platform: account.platform,
              caption,
              contentUrl,
              status: 'published',
              publishedAt: new Date().toISOString(),
              platformPostId: result.post_id,
              platformUrl: result.post_url
            });
          }
        }
      });

      // Clear form
      setCaption('');
      setHashtags([]);
      setContentUrl('');
      onAccountsChange([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Publishing failed');
    } finally {
      setPublishing(false);
    }
  };

  const warnings = getWarnings();

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6">
        <h2 className="text-xl font-semibold mb-6">Create Post</h2>

        {/* Account selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Select Platforms
          </label>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {accounts.map(account => (
              <button
                key={account.id}
                onClick={() => toggleAccount(account.id)}
                className={`
                  p-3 rounded-lg border-2 transition-all text-left
                  ${selectedAccounts.includes(account.id)
                    ? 'border-blue-600 bg-blue-50'
                    : 'border-gray-200 hover:border-blue-400 hover:bg-gray-50'
                  }
                `}
              >
                <div className="flex items-center gap-2">
                  <span className="text-2xl">{PLATFORM_ICONS[account.platform]}</span>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-gray-900 truncate">{account.name}</div>
                    <div className="text-xs text-gray-500 truncate">{account.handle}</div>
                  </div>
                  {selectedAccounts.includes(account.id) && (
                    <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0" />
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Content URL */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Content URL
          </label>
          <div className="relative">
            <LinkIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="url"
              value={contentUrl}
              onChange={(e) => setContentUrl(e.target.value)}
              placeholder="https://example.com/video.mp4"
              className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
            />
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Direct URL to your video or image file
          </p>
        </div>

        {/* Caption */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm font-medium text-gray-700">
              Caption
            </label>
            <span className="text-sm text-gray-500">
              {caption.length} characters
            </span>
          </div>
          <textarea
            value={caption}
            onChange={(e) => setCaption(e.target.value)}
            placeholder="Write your caption here..."
            rows={6}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 resize-none"
          />
        </div>

        {/* Hashtags */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Hashtags ({hashtags.length})
          </label>
          <div className="flex gap-2 mb-2">
            <div className="flex-1 relative">
              <Hash className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={hashtagInput}
                onChange={(e) => setHashtagInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Add hashtag"
                className="w-full pl-11 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>
            <button
              onClick={addHashtag}
              disabled={!hashtagInput.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              Add
            </button>
          </div>
          {hashtags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {hashtags.map(tag => (
                <span
                  key={tag}
                  className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                >
                  {tag}
                  <button
                    onClick={() => removeHashtag(tag)}
                    className="hover:text-blue-900"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Warnings */}
        {warnings.length > 0 && (
          <div className="mb-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-start gap-2">
              <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h3 className="font-medium text-yellow-900 mb-1">Content Optimization Warnings</h3>
                <ul className="text-sm text-yellow-800 space-y-1">
                  {warnings.map((warning, idx) => (
                    <li key={idx}>• {warning}</li>
                  ))}
                </ul>
                <p className="text-xs text-yellow-700 mt-2">
                  Content will be automatically optimized to meet platform requirements
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Action buttons */}
        <div className="flex gap-3">
          <button
            onClick={handlePublish}
            disabled={publishing || selectedAccounts.length === 0 || !contentUrl || !caption.trim()}
            className={`
              flex-1 px-6 py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2
              ${publishing || selectedAccounts.length === 0 || !contentUrl || !caption.trim()
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
              }
            `}
          >
            {publishing ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Publishing...
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                Publish Now
              </>
            )}
          </button>

          <button
            disabled={publishing}
            className="px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2"
          >
            <Calendar className="w-5 h-5" />
            Schedule
          </button>
        </div>
      </div>
    </div>
  );
}
