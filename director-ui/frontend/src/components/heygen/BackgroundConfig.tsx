/**
 * Background Configuration - Customize video background
 *
 * Features:
 * - Color picker
 * - Image upload/URL
 * - Video background URL
 * - Preset backgrounds
 * - Background preview
 */

import React, { useState } from 'react';
import { Palette, Image, Video, Link, Upload } from 'lucide-react';
import { BackgroundSettings } from './AvatarStudio';

interface BackgroundConfigProps {
  background: BackgroundSettings;
  onBackgroundChange: (background: BackgroundSettings) => void;
}

const PRESET_COLORS = [
  { name: 'Black', value: '#000000' },
  { name: 'White', value: '#FFFFFF' },
  { name: 'Navy Blue', value: '#1E3A8A' },
  { name: 'Royal Purple', value: '#7C3AED' },
  { name: 'Emerald', value: '#059669' },
  { name: 'Orange', value: '#EA580C' },
  { name: 'Rose', value: '#E11D48' },
  { name: 'Gray', value: '#6B7280' },
  { name: 'Gradient Blue', value: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
  { name: 'Gradient Sunset', value: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
  { name: 'Gradient Ocean', value: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' },
  { name: 'Gradient Forest', value: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' }
];

const PRESET_IMAGES = [
  'https://images.unsplash.com/photo-1557683316-973673baf926?w=800&h=1200&fit=crop',
  'https://images.unsplash.com/photo-1579546929518-9e396f3cc809?w=800&h=1200&fit=crop',
  'https://images.unsplash.com/photo-1557682250-33bd709cbe85?w=800&h=1200&fit=crop',
  'https://images.unsplash.com/photo-1557682224-5b8590cd9ec5?w=800&h=1200&fit=crop',
  'https://images.unsplash.com/photo-1557682268-e3955ed5d83f?w=800&h=1200&fit=crop',
  'https://images.unsplash.com/photo-1557683311-eac922347aa1?w=800&h=1200&fit=crop'
];

export default function BackgroundConfig({ background, onBackgroundChange }: BackgroundConfigProps) {
  const [urlInput, setUrlInput] = useState('');

  const handleColorChange = (color: string) => {
    onBackgroundChange({
      type: 'color',
      value: color
    });
  };

  const handleImageUrl = () => {
    if (urlInput.trim()) {
      onBackgroundChange({
        type: 'image',
        value: urlInput.trim()
      });
    }
  };

  const handleVideoUrl = () => {
    if (urlInput.trim()) {
      onBackgroundChange({
        type: 'video',
        value: urlInput.trim()
      });
    }
  };

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-2">Background Settings</h2>
        <p className="text-gray-600">Customize the background for your avatar video</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Preview */}
        <div className="lg:col-span-1">
          <div className="sticky top-6">
            <h3 className="text-sm font-medium text-gray-700 mb-3">Preview</h3>
            <div className="aspect-[9/16] rounded-lg border-2 border-gray-300 overflow-hidden">
              {background.type === 'color' && (
                <div
                  className="w-full h-full"
                  style={{
                    background: background.value.startsWith('linear-gradient')
                      ? background.value
                      : background.value
                  }}
                />
              )}
              {background.type === 'image' && background.value && (
                <img
                  src={background.value}
                  alt="Background"
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    e.currentTarget.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="%23f3f4f6"/></svg>';
                  }}
                />
              )}
              {background.type === 'video' && background.value && (
                <video
                  src={background.value}
                  autoPlay
                  loop
                  muted
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    console.error('Video load error');
                  }}
                />
              )}
            </div>

            {/* Current selection info */}
            <div className="mt-3 text-sm text-gray-600">
              <div className="flex items-center gap-2">
                {background.type === 'color' && <Palette className="w-4 h-4" />}
                {background.type === 'image' && <Image className="w-4 h-4" />}
                {background.type === 'video' && <Video className="w-4 h-4" />}
                <span className="capitalize">{background.type} background</span>
              </div>
              {(background.type === 'image' || background.type === 'video') && (
                <p className="text-xs text-gray-500 mt-1 truncate">{background.value}</p>
              )}
            </div>
          </div>
        </div>

        {/* Configuration options */}
        <div className="lg:col-span-2 space-y-6">
          {/* Color backgrounds */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center gap-2 mb-4">
              <Palette className="w-5 h-5 text-purple-600" />
              <h3 className="text-lg font-medium">Solid Colors & Gradients</h3>
            </div>

            {/* Color presets */}
            <div className="grid grid-cols-4 gap-3 mb-4">
              {PRESET_COLORS.map(preset => (
                <button
                  key={preset.name}
                  onClick={() => handleColorChange(preset.value)}
                  className={`
                    aspect-square rounded-lg border-2 transition-all overflow-hidden
                    ${background.type === 'color' && background.value === preset.value
                      ? 'border-purple-600 ring-2 ring-purple-600 ring-offset-2'
                      : 'border-gray-300 hover:border-purple-400'
                    }
                  `}
                  title={preset.name}
                >
                  <div
                    className="w-full h-full"
                    style={{
                      background: preset.value
                    }}
                  />
                </button>
              ))}
            </div>

            {/* Custom color picker */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Custom Color
              </label>
              <div className="flex gap-2">
                <input
                  type="color"
                  value={background.type === 'color' && !background.value.startsWith('linear-gradient')
                    ? background.value
                    : '#000000'
                  }
                  onChange={(e) => handleColorChange(e.target.value)}
                  className="w-16 h-10 rounded border border-gray-300 cursor-pointer"
                />
                <input
                  type="text"
                  value={background.type === 'color' && !background.value.startsWith('linear-gradient')
                    ? background.value
                    : ''
                  }
                  onChange={(e) => handleColorChange(e.target.value)}
                  placeholder="#000000"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
                />
              </div>
            </div>
          </div>

          {/* Image backgrounds */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center gap-2 mb-4">
              <Image className="w-5 h-5 text-purple-600" />
              <h3 className="text-lg font-medium">Image Background</h3>
            </div>

            {/* Image presets */}
            <div className="grid grid-cols-3 gap-3 mb-4">
              {PRESET_IMAGES.map((url, idx) => (
                <button
                  key={idx}
                  onClick={() => onBackgroundChange({ type: 'image', value: url })}
                  className={`
                    aspect-video rounded-lg border-2 overflow-hidden transition-all
                    ${background.type === 'image' && background.value === url
                      ? 'border-purple-600 ring-2 ring-purple-600 ring-offset-2'
                      : 'border-gray-300 hover:border-purple-400'
                    }
                  `}
                >
                  <img
                    src={url}
                    alt={`Preset ${idx + 1}`}
                    className="w-full h-full object-cover"
                  />
                </button>
              ))}
            </div>

            {/* Custom image URL */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Image URL
              </label>
              <div className="flex gap-2">
                <div className="flex-1 relative">
                  <Link className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    value={urlInput}
                    onChange={(e) => setUrlInput(e.target.value)}
                    placeholder="https://example.com/image.jpg"
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
                  />
                </div>
                <button
                  onClick={handleImageUrl}
                  disabled={!urlInput.trim()}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                >
                  Apply
                </button>
              </div>
            </div>
          </div>

          {/* Video backgrounds */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center gap-2 mb-4">
              <Video className="w-5 h-5 text-purple-600" />
              <h3 className="text-lg font-medium">Video Background</h3>
            </div>

            <p className="text-sm text-gray-600 mb-4">
              Add a looping video background for dynamic content
            </p>

            {/* Video URL input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Video URL
              </label>
              <div className="flex gap-2">
                <div className="flex-1 relative">
                  <Link className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    value={urlInput}
                    onChange={(e) => setUrlInput(e.target.value)}
                    placeholder="https://example.com/video.mp4"
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
                  />
                </div>
                <button
                  onClick={handleVideoUrl}
                  disabled={!urlInput.trim()}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                >
                  Apply
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Supported formats: MP4, WebM. Video will loop automatically.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
