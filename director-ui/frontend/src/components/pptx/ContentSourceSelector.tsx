import React from 'react';
import { Sparkles, Youtube, Globe, Upload, Check } from 'lucide-react';

type ContentSource = 'ai' | 'youtube' | 'web' | 'file';

interface ContentSourceSelectorProps {
  selected: ContentSource;
  onSelect: (source: ContentSource) => void;
  config: any;
  onChange: (updates: any) => void;
}

const ContentSourceSelector: React.FC<ContentSourceSelectorProps> = ({
  selected,
  onSelect,
  config,
  onChange
}) => {
  return (
    <div className="space-y-6">
      {/* Source Type Selector */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <button
          onClick={() => onSelect('ai')}
          className={`p-4 rounded-lg transition border-2 ${
            selected === 'ai'
              ? 'bg-blue-600 bg-opacity-30 border-blue-400'
              : 'bg-gray-800 bg-opacity-50 border-gray-700 hover:border-blue-500'
          }`}
        >
          <div className="text-center">
            <Sparkles className={`w-8 h-8 mx-auto mb-2 ${
              selected === 'ai' ? 'text-blue-300' : 'text-gray-400'
            }`} />
            <div className="font-semibold text-sm">AI Generation</div>
            <div className="text-xs text-gray-400 mt-1">Create from topic</div>
            {selected === 'ai' && (
              <Check className="w-5 h-5 text-green-400 mx-auto mt-2" />
            )}
          </div>
        </button>

        <button
          onClick={() => onSelect('youtube')}
          className={`p-4 rounded-lg transition border-2 ${
            selected === 'youtube'
              ? 'bg-red-600 bg-opacity-30 border-red-400'
              : 'bg-gray-800 bg-opacity-50 border-gray-700 hover:border-red-500'
          }`}
        >
          <div className="text-center">
            <Youtube className={`w-8 h-8 mx-auto mb-2 ${
              selected === 'youtube' ? 'text-red-300' : 'text-gray-400'
            }`} />
            <div className="font-semibold text-sm">YouTube</div>
            <div className="text-xs text-gray-400 mt-1">From video URL</div>
            {selected === 'youtube' && (
              <Check className="w-5 h-5 text-green-400 mx-auto mt-2" />
            )}
          </div>
        </button>

        <button
          onClick={() => onSelect('web')}
          className={`p-4 rounded-lg transition border-2 ${
            selected === 'web'
              ? 'bg-green-600 bg-opacity-30 border-green-400'
              : 'bg-gray-800 bg-opacity-50 border-gray-700 hover:border-green-500'
          }`}
        >
          <div className="text-center">
            <Globe className={`w-8 h-8 mx-auto mb-2 ${
              selected === 'web' ? 'text-green-300' : 'text-gray-400'
            }`} />
            <div className="font-semibold text-sm">Web Page</div>
            <div className="text-xs text-gray-400 mt-1">From website</div>
            {selected === 'web' && (
              <Check className="w-5 h-5 text-green-400 mx-auto mt-2" />
            )}
          </div>
        </button>

        <button
          onClick={() => onSelect('file')}
          className={`p-4 rounded-lg transition border-2 ${
            selected === 'file'
              ? 'bg-purple-600 bg-opacity-30 border-purple-400'
              : 'bg-gray-800 bg-opacity-50 border-gray-700 hover:border-purple-500'
          }`}
        >
          <div className="text-center">
            <Upload className={`w-8 h-8 mx-auto mb-2 ${
              selected === 'file' ? 'text-purple-300' : 'text-gray-400'
            }`} />
            <div className="font-semibold text-sm">Upload File</div>
            <div className="text-xs text-gray-400 mt-1">Text/Markdown</div>
            {selected === 'file' && (
              <Check className="w-5 h-5 text-green-400 mx-auto mt-2" />
            )}
          </div>
        </button>
      </div>

      {/* Source-Specific Inputs */}
      {selected === 'ai' && (
        <div className="space-y-4 bg-blue-900 bg-opacity-20 rounded-lg p-4 border border-blue-600 border-opacity-30">
          <div>
            <label className="block text-sm font-semibold mb-2">
              Topic / Title <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              value={config.topic}
              onChange={(e) => onChange({ topic: e.target.value })}
              placeholder="e.g., Q3 Sales Review, Product Launch Strategy"
              className="w-full px-4 py-3 bg-gray-900 bg-opacity-70 border border-gray-700 rounded-lg focus:border-blue-500 focus:outline-none transition"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2">
              Brief / Description
            </label>
            <textarea
              value={config.brief}
              onChange={(e) => onChange({ brief: e.target.value })}
              placeholder="Provide context and key points you want to cover..."
              rows={4}
              className="w-full px-4 py-3 bg-gray-900 bg-opacity-70 border border-gray-700 rounded-lg focus:border-blue-500 focus:outline-none transition resize-none"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2">
              Additional Instructions (Optional)
            </label>
            <textarea
              value={config.additionalInstructions}
              onChange={(e) => onChange({ additionalInstructions: e.target.value })}
              placeholder="Any specific requirements, style preferences, or constraints..."
              rows={2}
              className="w-full px-4 py-3 bg-gray-900 bg-opacity-70 border border-gray-700 rounded-lg focus:border-blue-500 focus:outline-none transition resize-none"
            />
          </div>
        </div>
      )}

      {selected === 'youtube' && (
        <div className="space-y-4 bg-red-900 bg-opacity-20 rounded-lg p-4 border border-red-600 border-opacity-30">
          <div>
            <label className="block text-sm font-semibold mb-2">
              YouTube Video URL <span className="text-red-400">*</span>
            </label>
            <input
              type="url"
              value={config.youtubeUrl}
              onChange={(e) => onChange({ youtubeUrl: e.target.value })}
              placeholder="https://www.youtube.com/watch?v=..."
              className="w-full px-4 py-3 bg-gray-900 bg-opacity-70 border border-gray-700 rounded-lg focus:border-red-500 focus:outline-none transition"
            />
            <p className="text-xs text-gray-400 mt-2">
              We'll extract the transcript and generate slides from the video content
            </p>
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2">
              Presentation Title (Optional)
            </label>
            <input
              type="text"
              value={config.topic}
              onChange={(e) => onChange({ topic: e.target.value })}
              placeholder="Auto-generated from video if not provided"
              className="w-full px-4 py-3 bg-gray-900 bg-opacity-70 border border-gray-700 rounded-lg focus:border-red-500 focus:outline-none transition"
            />
          </div>
        </div>
      )}

      {selected === 'web' && (
        <div className="space-y-4 bg-green-900 bg-opacity-20 rounded-lg p-4 border border-green-600 border-opacity-30">
          <div>
            <label className="block text-sm font-semibold mb-2">
              Website URL <span className="text-red-400">*</span>
            </label>
            <input
              type="url"
              value={config.webUrl}
              onChange={(e) => onChange({ webUrl: e.target.value })}
              placeholder="https://example.com/article"
              className="w-full px-4 py-3 bg-gray-900 bg-opacity-70 border border-gray-700 rounded-lg focus:border-green-500 focus:outline-none transition"
            />
            <p className="text-xs text-gray-400 mt-2">
              We'll scrape the content and create slides from the article/page
            </p>
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2">
              Presentation Title (Optional)
            </label>
            <input
              type="text"
              value={config.topic}
              onChange={(e) => onChange({ topic: e.target.value })}
              placeholder="Auto-generated from page if not provided"
              className="w-full px-4 py-3 bg-gray-900 bg-opacity-70 border border-gray-700 rounded-lg focus:border-green-500 focus:outline-none transition"
            />
          </div>
        </div>
      )}

      {selected === 'file' && (
        <div className="space-y-4 bg-purple-900 bg-opacity-20 rounded-lg p-4 border border-purple-600 border-opacity-30">
          <div>
            <label className="block text-sm font-semibold mb-2">
              Upload Content File <span className="text-red-400">*</span>
            </label>
            <div className="border-2 border-dashed border-purple-500 border-opacity-50 rounded-lg p-8 text-center hover:border-purple-400 hover:bg-purple-900 hover:bg-opacity-10 transition">
              <Upload className="w-12 h-12 text-purple-400 mx-auto mb-4" />
              <label className="cursor-pointer">
                <span className="text-purple-300 hover:text-purple-200 font-semibold">
                  Click to upload
                </span>
                <span className="text-gray-400"> or drag and drop</span>
                <input
                  type="file"
                  accept=".txt,.md,.markdown"
                  onChange={(e) => onChange({ uploadedFile: e.target.files?.[0] || null })}
                  className="hidden"
                />
              </label>
              <p className="text-xs text-gray-400 mt-2">
                TXT or Markdown files (max 10MB)
              </p>
              {config.uploadedFile && (
                <div className="mt-4 text-sm text-purple-300">
                  Selected: {config.uploadedFile.name}
                </div>
              )}
            </div>
          </div>

          <div className="bg-purple-800 bg-opacity-20 border border-purple-600 border-opacity-30 rounded p-3 text-xs text-purple-200">
            <div className="font-semibold mb-1">File Format Guidelines:</div>
            <ul className="space-y-1 text-purple-300">
              <li>• Use "# Title" for slide titles</li>
              <li>• Use "-" or "*" for bullet points</li>
              <li>• Separate slides with "---" or blank lines</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default ContentSourceSelector;
