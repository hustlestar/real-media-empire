/**
 * POV Prompt Helper - Generate cinematic POV prompts for AI video/image generation
 *
 * Features:
 * - 8 POV style presets (GoPro, TikTok, Casual Phone, etc.)
 * - Platform-specific recommendations
 * - AI model optimization (Flux, Kling, Minimax, Runway)
 * - Sensory detail enhancement
 */

import React, { useState } from 'react';
import {
  Video,
  Eye,
  Sparkles,
  Copy,
  CheckCircle,
  Settings,
  AlertCircle
} from 'lucide-react';

type POVStyle =
  | 'gopro_action'
  | 'casual_phone'
  | 'desktop_work'
  | 'cinematic_pov'
  | 'tiktok_trending'
  | 'car_driving'
  | 'workout_training'
  | 'cooking_food';

type Platform = 'tiktok' | 'youtube' | 'instagram' | 'linkedin' | 'twitter';
type AIModel = 'flux' | 'kling' | 'minimax' | 'runway';

const POV_STYLES = {
  gopro_action: {
    name: 'GoPro Action',
    icon: '🏃',
    description: 'Fast-paced, first-person action shots',
    example: 'POV mountain biking down a steep trail',
    platforms: ['youtube', 'tiktok', 'instagram']
  },
  casual_phone: {
    name: 'Casual Phone',
    icon: '📱',
    description: 'Personal, selfie-style perspective',
    example: 'POV getting ready in the morning',
    platforms: ['tiktok', 'instagram']
  },
  desktop_work: {
    name: 'Desktop Work',
    icon: '💻',
    description: 'Productivity and work-from-home',
    example: 'POV coding on dual monitors',
    platforms: ['linkedin', 'twitter', 'youtube']
  },
  cinematic_pov: {
    name: 'Cinematic POV',
    icon: '🎬',
    description: 'Professional, movie-like perspective',
    example: 'POV walking through a neon-lit city at night',
    platforms: ['youtube', 'instagram']
  },
  tiktok_trending: {
    name: 'TikTok POV',
    icon: '🎵',
    description: 'Trending, relatable scenarios',
    example: 'POV arriving at your dream job interview',
    platforms: ['tiktok', 'instagram']
  },
  car_driving: {
    name: 'Car Driving',
    icon: '🚗',
    description: 'Dashboard and steering wheel views',
    example: 'POV driving through mountain roads',
    platforms: ['youtube', 'tiktok']
  },
  workout_training: {
    name: 'Workout',
    icon: '💪',
    description: 'Fitness and training perspective',
    example: 'POV doing push-ups in home gym',
    platforms: ['tiktok', 'instagram', 'youtube']
  },
  cooking_food: {
    name: 'Cooking',
    icon: '👨‍🍳',
    description: 'Kitchen and food preparation',
    example: 'POV chopping vegetables for pasta',
    platforms: ['tiktok', 'instagram', 'youtube']
  }
};

export default function POVPromptHelper() {
  const [sceneDescription, setSceneDescription] = useState('');
  const [selectedStyle, setSelectedStyle] = useState<POVStyle>('gopro_action');
  const [environment, setEnvironment] = useState('');
  const [addSensory, setAddSensory] = useState(true);
  const [aiModel, setAiModel] = useState<AIModel>('flux');
  const [generatedPrompt, setGeneratedPrompt] = useState('');
  const [copied, setCopied] = useState(false);

  const generatePrompt = () => {
    if (!sceneDescription.trim()) {
      alert('Please describe your scene');
      return;
    }

    const style = POV_STYLES[selectedStyle];

    // Build prompt structure
    let prompt = `First person view POV ${selectedStyle.replace(/_/g, ' ')} shot of ${sceneDescription}`;

    // Add visible body parts
    if (!sceneDescription.toLowerCase().includes('hand') &&
        !sceneDescription.toLowerCase().includes('arm') &&
        !sceneDescription.toLowerCase().includes('feet')) {
      prompt += ', hands visible in frame';
    }

    // Add environment
    if (environment.trim()) {
      prompt += `; in the background, ${environment}`;
    } else {
      prompt += '; in the background, detailed environment';
    }

    // Add sensory details
    if (addSensory) {
      if (selectedStyle === 'cooking_food') {
        prompt += '; aroma of fresh ingredients, sound of sizzling';
      } else if (selectedStyle === 'workout_training') {
        prompt += '; sound of breathing, feel of effort';
      } else if (selectedStyle === 'car_driving') {
        prompt += '; engine sound, feel of acceleration';
      } else if (selectedStyle === 'gopro_action') {
        prompt += '; adrenaline rush, wind rushing past';
      }
    }

    // Optimize for AI model
    if (aiModel === 'flux') {
      prompt += '. Photorealistic, high detail, DSLR quality';
    } else if (aiModel === 'kling') {
      prompt += '. Smooth camera movement, cinematic motion blur';
    } else if (aiModel === 'minimax') {
      prompt += '. Dynamic camera zoom, professional cinematography';
    } else if (aiModel === 'runway') {
      prompt += '. Cinematic color grading, artistic composition';
    }

    setGeneratedPrompt(prompt);
  };

  const copyPrompt = () => {
    navigator.clipboard.writeText(generatedPrompt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-3 mb-2">
          <Eye className="w-8 h-8 text-purple-600" />
          <h1 className="text-2xl font-bold">POV Prompt Helper</h1>
        </div>
        <p className="text-gray-600">
          Generate cinematic point-of-view prompts for AI video and image generation
        </p>
      </div>

      {/* Style Selection */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Choose POV Style</h2>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {(Object.keys(POV_STYLES) as POVStyle[]).map((styleKey) => {
            const style = POV_STYLES[styleKey];
            const isSelected = selectedStyle === styleKey;

            return (
              <button
                key={styleKey}
                onClick={() => setSelectedStyle(styleKey)}
                className={`p-4 border-2 rounded-lg text-left transition-all ${
                  isSelected
                    ? 'border-purple-600 bg-purple-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="text-3xl mb-2">{style.icon}</div>
                <div className="font-semibold text-sm">{style.name}</div>
                <div className="text-xs text-gray-600 mt-1">{style.description}</div>
              </button>
            );
          })}
        </div>

        <div className="mt-4 p-4 bg-blue-50 rounded-lg">
          <div className="flex items-start gap-2">
            <Sparkles className="w-5 h-5 text-blue-600 mt-0.5" />
            <div>
              <div className="font-medium text-blue-900">Example:</div>
              <div className="text-sm text-blue-700 mt-1">
                {POV_STYLES[selectedStyle].example}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Input Fields */}
      <div className="bg-white rounded-lg shadow p-6 space-y-4">
        <h2 className="text-lg font-semibold mb-4">Scene Details</h2>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Scene Description *
          </label>
          <textarea
            value={sceneDescription}
            onChange={(e) => setSceneDescription(e.target.value)}
            placeholder="e.g., unboxing a new iPhone 15 Pro on my desk"
            rows={3}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Environment (Optional)
          </label>
          <input
            type="text"
            value={environment}
            onChange={(e) => setEnvironment(e.target.value)}
            placeholder="e.g., modern minimalist office with plants"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="sensory"
            checked={addSensory}
            onChange={(e) => setAddSensory(e.target.checked)}
            className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
          />
          <label htmlFor="sensory" className="text-sm font-medium text-gray-700">
            Add sensory details (smell, sound, feel)
          </label>
        </div>
      </div>

      {/* AI Model Selection */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-4">
          <Settings className="w-5 h-5 text-gray-600" />
          <h2 className="text-lg font-semibold">AI Model Optimization</h2>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {(['flux', 'kling', 'minimax', 'runway'] as AIModel[]).map((model) => (
            <button
              key={model}
              onClick={() => setAiModel(model)}
              className={`p-3 border-2 rounded-lg transition-all ${
                aiModel === model
                  ? 'border-blue-600 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="font-semibold capitalize">{model}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Generate Button */}
      <button
        onClick={generatePrompt}
        disabled={!sceneDescription.trim()}
        className={`w-full py-4 rounded-lg font-semibold text-white transition-all flex items-center justify-center gap-2 ${
          !sceneDescription.trim()
            ? 'bg-gray-300 cursor-not-allowed'
            : 'bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700'
        }`}
      >
        <Sparkles className="w-5 h-5" />
        Generate POV Prompt
      </button>

      {/* Generated Prompt */}
      {generatedPrompt && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Generated Prompt</h2>
            <button
              onClick={copyPrompt}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg flex items-center gap-2 transition-colors"
            >
              {copied ? (
                <>
                  <CheckCircle className="w-4 h-4" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  Copy
                </>
              )}
            </button>
          </div>

          <div className="p-5 bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg border border-purple-200">
            <p className="text-gray-900 leading-relaxed">{generatedPrompt}</p>
          </div>

          <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5" />
              <div className="text-sm text-yellow-800">
                <div className="font-medium mb-1">Tips for best results:</div>
                <ul className="space-y-1 ml-4 list-disc">
                  <li>Use this prompt with {aiModel.toUpperCase()} for optimal quality</li>
                  <li>Recommended platforms: {POV_STYLES[selectedStyle].platforms.join(', ')}</li>
                  <li>POV style works best with visible hands/arms in frame</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
