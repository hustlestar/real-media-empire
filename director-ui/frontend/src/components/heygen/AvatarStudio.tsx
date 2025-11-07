/**
 * HeyGen Avatar Studio - Main component for AI avatar video generation
 *
 * Features:
 * - Avatar selection with preview
 * - Voice selection with audio samples
 * - Script editing with character count
 * - Background customization (color/image/video)
 * - Aspect ratio selection for platform-specific content
 * - Voice settings (speed, pitch, emotion)
 * - Character positioning and scaling
 * - Real-time generation status tracking
 * - Video preview and download
 */

import React, { useState, useEffect } from 'react';
import {
  Video,
  Mic,
  Settings,
  Play,
  Download,
  Loader2,
  AlertCircle,
  CheckCircle,
  Image as ImageIcon,
  Palette,
  Film
} from 'lucide-react';
import AvatarSelector from './AvatarSelector';
import VoiceSelector from './VoiceSelector';
import ScriptEditor from './ScriptEditor';
import BackgroundConfig from './BackgroundConfig';
import VideoSettings from './VideoSettings';
import GenerationStatus from './GenerationStatus';

export interface Avatar {
  id: string;
  name: string;
  previewImageUrl?: string;
  previewVideoUrl?: string;
  gender?: string;
  isGreenScreen: boolean;
}

export interface Voice {
  id: string;
  name: string;
  language: string;
  gender?: string;
  previewAudioUrl?: string;
}

export interface BackgroundSettings {
  type: 'color' | 'image' | 'video';
  value: string; // Hex color or URL
}

export interface VideoConfig {
  aspectRatio: '9:16' | '16:9' | '1:1' | '4:5';
  voiceSpeed: number;
  voicePitch: number;
  voiceEmotion: string;
  avatarScale: number;
  hasGreenScreen: boolean;
  avatarOffsetX: number;
  avatarOffsetY: number;
  caption: boolean;
  test: boolean;
}

export interface GenerationResult {
  videoId: string;
  videoUrl: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  cost: number;
  duration: number;
  metadata: Record<string, any>;
  error?: string;
}

type Tab = 'avatar' | 'voice' | 'script' | 'background' | 'settings' | 'preview';

const ASPECT_RATIO_INFO = {
  '9:16': { name: 'Vertical', platforms: ['TikTok', 'Instagram Reels', 'YouTube Shorts'], icon: '📱' },
  '16:9': { name: 'Landscape', platforms: ['YouTube', 'LinkedIn', 'Twitter'], icon: '🖥️' },
  '1:1': { name: 'Square', platforms: ['Instagram Feed', 'Facebook Feed'], icon: '⬜' },
  '4:5': { name: 'Portrait', platforms: ['Instagram Feed', 'Facebook Feed'], icon: '📄' }
};

export default function AvatarStudio() {
  const [activeTab, setActiveTab] = useState<Tab>('avatar');
  const [selectedAvatar, setSelectedAvatar] = useState<Avatar | null>(null);
  const [selectedVoice, setSelectedVoice] = useState<Voice | null>(null);
  const [script, setScript] = useState('');
  const [title, setTitle] = useState('');
  const [background, setBackground] = useState<BackgroundSettings>({
    type: 'color',
    value: '#000000'
  });
  const [videoConfig, setVideoConfig] = useState<VideoConfig>({
    aspectRatio: '9:16',
    voiceSpeed: 1.1,
    voicePitch: 50,
    voiceEmotion: 'Excited',
    avatarScale: 1.0,
    hasGreenScreen: false,
    avatarOffsetX: 0.0,
    avatarOffsetY: 0.0,
    caption: false,
    test: false
  });

  const [isGenerating, setIsGenerating] = useState(false);
  const [generationResult, setGenerationResult] = useState<GenerationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Validate if we can generate
  const canGenerate = selectedAvatar && selectedVoice && script.trim().length > 0;

  // Calculate estimated cost
  const estimatedCost = videoConfig.test ? 0 : (script.length / 1000) * 0.15; // Rough estimate

  const handleGenerate = async () => {
    if (!canGenerate) return;

    setIsGenerating(true);
    setError(null);
    setGenerationResult(null);

    try {
      const response = await fetch('/api/heygen/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          script,
          avatar_id: selectedAvatar!.id,
          voice_id: selectedVoice!.id,
          title,
          aspect_ratio: videoConfig.aspectRatio,
          background_type: background.type,
          background_value: background.value,
          voice_speed: videoConfig.voiceSpeed,
          voice_pitch: videoConfig.voicePitch,
          voice_emotion: videoConfig.voiceEmotion,
          avatar_scale: videoConfig.avatarScale,
          has_green_screen: videoConfig.hasGreenScreen,
          avatar_offset_x: videoConfig.avatarOffsetX,
          avatar_offset_y: videoConfig.avatarOffsetY,
          caption: videoConfig.caption,
          test: videoConfig.test
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Generation failed');
      }

      const result = await response.json();
      setGenerationResult(result);
      setActiveTab('preview');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = () => {
    if (generationResult?.videoUrl) {
      window.open(generationResult.videoUrl, '_blank');
    }
  };

  const tabs: Array<{ id: Tab; label: string; icon: React.ReactNode }> = [
    { id: 'avatar', label: 'Avatar', icon: <Video className="w-4 h-4" /> },
    { id: 'voice', label: 'Voice', icon: <Mic className="w-4 h-4" /> },
    { id: 'script', label: 'Script', icon: <Film className="w-4 h-4" /> },
    { id: 'background', label: 'Background', icon: <Palette className="w-4 h-4" /> },
    { id: 'settings', label: 'Settings', icon: <Settings className="w-4 h-4" /> },
    { id: 'preview', label: 'Preview', icon: <Play className="w-4 h-4" /> }
  ];

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <Video className="w-6 h-6 text-purple-600" />
              HeyGen Avatar Studio
            </h1>
            <p className="text-sm text-gray-500 mt-1">
              Generate AI avatar videos with custom voices and backgrounds
            </p>
          </div>

          {/* Platform badges */}
          <div className="flex items-center gap-2">
            <div className="text-xs text-gray-500">
              {ASPECT_RATIO_INFO[videoConfig.aspectRatio].icon} {ASPECT_RATIO_INFO[videoConfig.aspectRatio].name}
            </div>
            <div className="flex flex-wrap gap-1">
              {ASPECT_RATIO_INFO[videoConfig.aspectRatio].platforms.slice(0, 2).map(platform => (
                <span key={platform} className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs">
                  {platform}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Tab navigation */}
      <div className="bg-white border-b border-gray-200">
        <div className="flex space-x-1 px-6">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                px-4 py-3 flex items-center gap-2 border-b-2 transition-colors
                ${activeTab === tab.id
                  ? 'border-purple-600 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
                }
              `}
            >
              {tab.icon}
              <span className="font-medium">{tab.label}</span>
              {/* Checkmark for completed sections */}
              {tab.id === 'avatar' && selectedAvatar && (
                <CheckCircle className="w-4 h-4 text-green-500" />
              )}
              {tab.id === 'voice' && selectedVoice && (
                <CheckCircle className="w-4 h-4 text-green-500" />
              )}
              {tab.id === 'script' && script.trim().length > 0 && (
                <CheckCircle className="w-4 h-4 text-green-500" />
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Content area */}
      <div className="flex-1 overflow-auto p-6">
        {activeTab === 'avatar' && (
          <AvatarSelector
            selectedAvatar={selectedAvatar}
            onSelectAvatar={setSelectedAvatar}
          />
        )}

        {activeTab === 'voice' && (
          <VoiceSelector
            selectedVoice={selectedVoice}
            onSelectVoice={setSelectedVoice}
          />
        )}

        {activeTab === 'script' && (
          <ScriptEditor
            script={script}
            title={title}
            onScriptChange={setScript}
            onTitleChange={setTitle}
          />
        )}

        {activeTab === 'background' && (
          <BackgroundConfig
            background={background}
            onBackgroundChange={setBackground}
          />
        )}

        {activeTab === 'settings' && (
          <VideoSettings
            config={videoConfig}
            onConfigChange={setVideoConfig}
            avatarIsGreenScreen={selectedAvatar?.isGreenScreen || false}
          />
        )}

        {activeTab === 'preview' && (
          <div className="max-w-4xl mx-auto">
            {/* Summary card */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
              <h2 className="text-lg font-semibold mb-4">Generation Summary</h2>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Avatar:</span>
                  <span className="ml-2 font-medium">{selectedAvatar?.name || 'Not selected'}</span>
                </div>
                <div>
                  <span className="text-gray-500">Voice:</span>
                  <span className="ml-2 font-medium">{selectedVoice?.name || 'Not selected'}</span>
                </div>
                <div>
                  <span className="text-gray-500">Script length:</span>
                  <span className="ml-2 font-medium">{script.length} characters</span>
                </div>
                <div>
                  <span className="text-gray-500">Aspect ratio:</span>
                  <span className="ml-2 font-medium">{videoConfig.aspectRatio}</span>
                </div>
                <div>
                  <span className="text-gray-500">Background:</span>
                  <span className="ml-2 font-medium capitalize">{background.type}</span>
                </div>
                <div>
                  <span className="text-gray-500">Estimated cost:</span>
                  <span className="ml-2 font-medium">${estimatedCost.toFixed(2)}</span>
                </div>
              </div>
            </div>

            {/* Generation status */}
            {generationResult && (
              <GenerationStatus result={generationResult} />
            )}

            {/* Error display */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-medium text-red-900">Generation Failed</h3>
                  <p className="text-sm text-red-700 mt-1">{error}</p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer with action buttons */}
      <div className="bg-white border-t border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-500">
            {videoConfig.test && (
              <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-xs font-medium">
                TEST MODE - No credits charged
              </span>
            )}
            {!videoConfig.test && (
              <span>Estimated cost: <span className="font-semibold">${estimatedCost.toFixed(2)}</span></span>
            )}
          </div>

          <div className="flex items-center gap-3">
            {generationResult?.status === 'completed' && (
              <button
                onClick={handleDownload}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Download Video
              </button>
            )}

            <button
              onClick={handleGenerate}
              disabled={!canGenerate || isGenerating}
              className={`
                px-6 py-2 rounded-lg font-medium transition-colors flex items-center gap-2
                ${canGenerate && !isGenerating
                  ? 'bg-purple-600 text-white hover:bg-purple-700'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }
              `}
            >
              {isGenerating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  Generate Video
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
