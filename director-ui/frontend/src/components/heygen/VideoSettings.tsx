/**
 * Video Settings - Configure video and voice parameters
 *
 * Features:
 * - Aspect ratio selection
 * - Voice speed control
 * - Voice pitch control
 * - Emotion selection
 * - Avatar scale and positioning
 * - Caption toggle
 * - Test mode toggle
 */

import React from 'react';
import {
  Smartphone,
  Monitor,
  Square,
  FileText,
  Gauge,
  TrendingUp,
  Smile,
  Move,
  TestTube,
  Captions
} from 'lucide-react';
import { VideoConfig } from './AvatarStudio';

interface VideoSettingsProps {
  config: VideoConfig;
  onConfigChange: (config: VideoConfig) => void;
  avatarIsGreenScreen: boolean;
}

const ASPECT_RATIOS = [
  {
    value: '9:16' as const,
    name: 'Vertical (9:16)',
    icon: Smartphone,
    description: 'TikTok, Instagram Reels, YouTube Shorts',
    dimensions: '720 x 1280'
  },
  {
    value: '16:9' as const,
    name: 'Landscape (16:9)',
    icon: Monitor,
    description: 'YouTube, LinkedIn, Twitter',
    dimensions: '1280 x 720'
  },
  {
    value: '1:1' as const,
    name: 'Square (1:1)',
    icon: Square,
    description: 'Instagram Feed, Facebook',
    dimensions: '1080 x 1080'
  },
  {
    value: '4:5' as const,
    name: 'Portrait (4:5)',
    icon: FileText,
    description: 'Instagram Feed, Facebook',
    dimensions: '1080 x 1350'
  }
];

const EMOTIONS = [
  'Excited',
  'Friendly',
  'Professional',
  'Serious',
  'Calm',
  'Cheerful',
  'Empathetic',
  'Authoritative'
];

export default function VideoSettings({ config, onConfigChange, avatarIsGreenScreen }: VideoSettingsProps) {
  const updateConfig = (updates: Partial<VideoConfig>) => {
    onConfigChange({ ...config, ...updates });
  };

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-2">Video Settings</h2>
        <p className="text-gray-600">Fine-tune your video generation parameters</p>
      </div>

      <div className="space-y-6">
        {/* Aspect ratio selection */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-medium mb-4 flex items-center gap-2">
            <Monitor className="w-5 h-5 text-purple-600" />
            Aspect Ratio
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {ASPECT_RATIOS.map(ratio => {
              const Icon = ratio.icon;
              return (
                <button
                  key={ratio.value}
                  onClick={() => updateConfig({ aspectRatio: ratio.value })}
                  className={`
                    p-4 rounded-lg border-2 transition-all text-left
                    ${config.aspectRatio === ratio.value
                      ? 'border-purple-600 bg-purple-50'
                      : 'border-gray-200 hover:border-purple-400 hover:bg-gray-50'
                    }
                  `}
                >
                  <div className="flex items-start gap-3">
                    <Icon className={`w-5 h-5 flex-shrink-0 ${
                      config.aspectRatio === ratio.value ? 'text-purple-600' : 'text-gray-400'
                    }`} />
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{ratio.name}</h4>
                      <p className="text-sm text-gray-500 mt-1">{ratio.description}</p>
                      <p className="text-xs text-gray-400 mt-1">{ratio.dimensions}</p>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Voice settings */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-medium mb-4 flex items-center gap-2">
            <Gauge className="w-5 h-5 text-purple-600" />
            Voice Settings
          </h3>

          <div className="space-y-6">
            {/* Voice speed */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-gray-700 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4" />
                  Voice Speed
                </label>
                <span className="text-sm text-gray-600">{config.voiceSpeed.toFixed(1)}x</span>
              </div>
              <input
                type="range"
                min="0.5"
                max="2.0"
                step="0.1"
                value={config.voiceSpeed}
                onChange={(e) => updateConfig({ voiceSpeed: parseFloat(e.target.value) })}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>Slower (0.5x)</span>
                <span>Normal (1.0x)</span>
                <span>Faster (2.0x)</span>
              </div>
            </div>

            {/* Voice pitch */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-gray-700 flex items-center gap-2">
                  <Gauge className="w-4 h-4" />
                  Voice Pitch
                </label>
                <span className="text-sm text-gray-600">{config.voicePitch}</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="1"
                value={config.voicePitch}
                onChange={(e) => updateConfig({ voicePitch: parseInt(e.target.value) })}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>Lower (0)</span>
                <span>Normal (50)</span>
                <span>Higher (100)</span>
              </div>
            </div>

            {/* Emotion */}
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                <Smile className="w-4 h-4" />
                Voice Emotion
              </label>
              <select
                value={config.voiceEmotion}
                onChange={(e) => updateConfig({ voiceEmotion: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
              >
                {EMOTIONS.map(emotion => (
                  <option key={emotion} value={emotion}>{emotion}</option>
                ))}
              </select>
              <p className="text-xs text-gray-500 mt-1">
                Choose the emotional tone for voice delivery
              </p>
            </div>
          </div>
        </div>

        {/* Avatar positioning (only for green screen avatars) */}
        {avatarIsGreenScreen && (
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-medium mb-4 flex items-center gap-2">
              <Move className="w-5 h-5 text-purple-600" />
              Avatar Positioning
            </h3>

            <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-4 text-sm text-green-800">
              Green screen avatar detected - customize positioning and scale
            </div>

            <div className="space-y-6">
              {/* Avatar scale */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-medium text-gray-700">
                    Avatar Scale
                  </label>
                  <span className="text-sm text-gray-600">{config.avatarScale.toFixed(1)}x</span>
                </div>
                <input
                  type="range"
                  min="0.5"
                  max="2.0"
                  step="0.1"
                  value={config.avatarScale}
                  onChange={(e) => updateConfig({ avatarScale: parseFloat(e.target.value) })}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
                />
              </div>

              {/* Enable green screen */}
              <div>
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={config.hasGreenScreen}
                    onChange={(e) => updateConfig({ hasGreenScreen: e.target.checked })}
                    className="w-4 h-4 rounded border-gray-300 text-purple-600 focus:ring-purple-600"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Remove background (green screen)
                  </span>
                </label>
              </div>

              {/* Offset controls (only when green screen enabled) */}
              {config.hasGreenScreen && (
                <>
                  {/* Horizontal offset */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-sm font-medium text-gray-700">
                        Horizontal Offset
                      </label>
                      <span className="text-sm text-gray-600">{config.avatarOffsetX.toFixed(1)}</span>
                    </div>
                    <input
                      type="range"
                      min="-1"
                      max="1"
                      step="0.1"
                      value={config.avatarOffsetX}
                      onChange={(e) => updateConfig({ avatarOffsetX: parseFloat(e.target.value) })}
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>Left</span>
                      <span>Center</span>
                      <span>Right</span>
                    </div>
                  </div>

                  {/* Vertical offset */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-sm font-medium text-gray-700">
                        Vertical Offset
                      </label>
                      <span className="text-sm text-gray-600">{config.avatarOffsetY.toFixed(1)}</span>
                    </div>
                    <input
                      type="range"
                      min="-1"
                      max="1"
                      step="0.1"
                      value={config.avatarOffsetY}
                      onChange={(e) => updateConfig({ avatarOffsetY: parseFloat(e.target.value) })}
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>Top</span>
                      <span>Center</span>
                      <span>Bottom</span>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        )}

        {/* Additional options */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-medium mb-4">Additional Options</h3>

          <div className="space-y-4">
            {/* Captions */}
            <label className="flex items-center gap-3 cursor-pointer p-3 rounded-lg hover:bg-gray-50 transition-colors">
              <input
                type="checkbox"
                checked={config.caption}
                onChange={(e) => updateConfig({ caption: e.target.checked })}
                className="w-4 h-4 rounded border-gray-300 text-purple-600 focus:ring-purple-600"
              />
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <Captions className="w-4 h-4 text-gray-600" />
                  <span className="font-medium text-gray-900">Generate Captions</span>
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  Add auto-generated subtitles to your video
                </p>
              </div>
            </label>

            {/* Test mode */}
            <label className="flex items-center gap-3 cursor-pointer p-3 rounded-lg hover:bg-gray-50 transition-colors">
              <input
                type="checkbox"
                checked={config.test}
                onChange={(e) => updateConfig({ test: e.target.checked })}
                className="w-4 h-4 rounded border-gray-300 text-purple-600 focus:ring-purple-600"
              />
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <TestTube className="w-4 h-4 text-gray-600" />
                  <span className="font-medium text-gray-900">Test Mode</span>
                  <span className="px-2 py-0.5 bg-yellow-100 text-yellow-800 text-xs rounded-full">
                    No credits charged
                  </span>
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  Preview video without consuming credits (watermarked)
                </p>
              </div>
            </label>
          </div>
        </div>
      </div>
    </div>
  );
}
