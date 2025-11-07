/**
 * VEED Talking Avatar - Simple photo + audio → talking video
 *
 * Features:
 * - Image URL input with preview
 * - Audio URL input with player
 * - Resolution selection
 * - Generation and status tracking
 */

import React, { useState } from 'react';
import {
  Image as ImageIcon,
  Mic,
  Video,
  Upload,
  Loader2,
  CheckCircle,
  AlertCircle,
  Download,
  DollarSign
} from 'lucide-react';

interface GenerationStatus {
  requestId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  videoUrl?: string;
  cost?: number;
  error?: string;
}

type Resolution = '480p' | '720p' | '1080p';

export default function VeedTalkingAvatar() {
  const [imageUrl, setImageUrl] = useState('');
  const [audioUrl, setAudioUrl] = useState('');
  const [resolution, setResolution] = useState<Resolution>('720p');
  const [isGenerating, setIsGenerating] = useState(false);
  const [status, setStatus] = useState<GenerationStatus | null>(null);

  const handleGenerate = async () => {
    if (!imageUrl || !audioUrl) {
      alert('Please provide both image and audio URLs');
      return;
    }

    setIsGenerating(true);
    setStatus({ requestId: '', status: 'pending' });

    try {
      const response = await fetch('/api/veed/generate-talking-avatar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image_url: imageUrl,
          audio_url: audioUrl,
          resolution
        })
      });

      if (!response.ok) {
        throw new Error(`Generation failed: ${response.statusText}`);
      }

      const result = await response.json();

      setStatus({
        requestId: result.request_id,
        status: result.status,
        videoUrl: result.video_url,
        cost: result.cost
      });
    } catch (error) {
      setStatus({
        requestId: '',
        status: 'failed',
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Info Banner */}
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <Video className="w-5 h-5 text-purple-600 mt-0.5" />
          <div>
            <h3 className="font-semibold text-purple-900">VEED Talking Avatar</h3>
            <p className="text-sm text-purple-700 mt-1">
              Transform any photo into a talking avatar with automatic lip-sync. Perfect for faceless content creation.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Image Input */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center gap-2 mb-4">
            <ImageIcon className="w-5 h-5 text-blue-600" />
            <h3 className="font-semibold">Source Photo</h3>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Image URL
              </label>
              <input
                type="text"
                value={imageUrl}
                onChange={(e) => setImageUrl(e.target.value)}
                placeholder="https://example.com/photo.jpg"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {imageUrl && (
              <div className="relative w-full aspect-[4/5] bg-gray-100 rounded-lg overflow-hidden">
                <img
                  src={imageUrl}
                  alt="Source"
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    e.currentTarget.src = '';
                    e.currentTarget.alt = 'Failed to load image';
                  }}
                />
              </div>
            )}

            <p className="text-xs text-gray-500">
              Use a clear frontal portrait photo with good lighting
            </p>
          </div>
        </div>

        {/* Audio Input */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center gap-2 mb-4">
            <Mic className="w-5 h-5 text-purple-600" />
            <h3 className="font-semibold">Voiceover Audio</h3>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Audio URL
              </label>
              <input
                type="text"
                value={audioUrl}
                onChange={(e) => setAudioUrl(e.target.value)}
                placeholder="https://example.com/audio.mp3"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            {audioUrl && (
              <div className="p-4 bg-gray-50 rounded-lg">
                <audio controls className="w-full">
                  <source src={audioUrl} />
                  Your browser does not support the audio element.
                </audio>
              </div>
            )}

            <p className="text-xs text-gray-500">
              Clear voice audio with minimal background noise
            </p>
          </div>
        </div>
      </div>

      {/* Resolution Selection */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Resolution
        </label>
        <div className="grid grid-cols-3 gap-4">
          {[
            { value: '480p', label: '480p', desc: 'Fast generation' },
            { value: '720p', label: '720p', desc: 'Balanced (recommended)' },
            { value: '1080p', label: '1080p', desc: 'High quality' }
          ].map((option) => (
            <button
              key={option.value}
              onClick={() => setResolution(option.value as Resolution)}
              className={`p-3 border-2 rounded-lg text-left transition-all ${
                resolution === option.value
                  ? 'border-purple-600 bg-purple-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="font-semibold">{option.label}</div>
              <div className="text-xs text-gray-600 mt-1">{option.desc}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Generate Button */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <button
          onClick={handleGenerate}
          disabled={isGenerating || !imageUrl || !audioUrl}
          className={`w-full py-3 rounded-lg font-semibold text-white transition-all flex items-center justify-center gap-2 ${
            isGenerating || !imageUrl || !audioUrl
              ? 'bg-gray-300 cursor-not-allowed'
              : 'bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700'
          }`}
        >
          {isGenerating ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Video className="w-5 h-5" />
              Generate Talking Avatar
            </>
          )}
        </button>

        <div className="mt-3 flex items-center justify-center gap-2 text-sm text-gray-600">
          <DollarSign className="w-4 h-4" />
          <span>Cost: ~$0.10 per video</span>
        </div>
      </div>

      {/* Status & Result */}
      {status && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="font-semibold mb-4">Status</h3>

          {status.status === 'pending' && (
            <div className="flex items-center gap-3 text-yellow-600">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Initializing...</span>
            </div>
          )}

          {status.status === 'processing' && (
            <div className="flex items-center gap-3 text-blue-600">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Creating talking avatar with lip-sync...</span>
            </div>
          )}

          {status.status === 'completed' && status.videoUrl && (
            <div className="space-y-4">
              <div className="flex items-center gap-3 text-green-600">
                <CheckCircle className="w-5 h-5" />
                <span className="font-medium">Generation completed!</span>
              </div>

              <div className="relative w-full aspect-video bg-gray-900 rounded-lg overflow-hidden">
                <video controls className="w-full h-full">
                  <source src={status.videoUrl} />
                  Your browser does not support the video element.
                </video>
              </div>

              <a
                href={status.videoUrl}
                download
                className="w-full py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium flex items-center justify-center gap-2 transition-colors"
              >
                <Download className="w-5 h-5" />
                Download Video
              </a>

              {status.cost && (
                <div className="text-sm text-gray-600 text-center">
                  Cost: ${status.cost.toFixed(2)}
                </div>
              )}
            </div>
          )}

          {status.status === 'failed' && (
            <div className="flex items-center gap-3 text-red-600">
              <AlertCircle className="w-5 h-5" />
              <span>{status.error || 'Generation failed'}</span>
            </div>
          )}
        </div>
      )}

      {/* Use Cases */}
      <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg border border-purple-200 p-6">
        <h3 className="font-semibold mb-3">Perfect For</h3>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-purple-600 rounded-full"></div>
            <span>Faceless content</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-purple-600 rounded-full"></div>
            <span>Educational tutorials</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-purple-600 rounded-full"></div>
            <span>Product demos</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-purple-600 rounded-full"></div>
            <span>Social media shorts</span>
          </div>
        </div>
      </div>
    </div>
  );
}
