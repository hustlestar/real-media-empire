import React from 'react';
import { Smile, Frown, Zap, Heart, CloudRain, Flame, Wind } from 'lucide-react';

interface EmotionPreset {
  id: string;
  name: string;
  icon: React.ReactNode;
  color: string;
  description: string;
  config: {
    speed: number;
    pitch?: number;
    emphasis_words?: string[];
    pauses?: Array<{ after_word: string, duration_ms: number }>;
    ssml_additions?: string;
  };
}

interface EmotionPresetsProps {
  provider: 'google' | 'elevenlabs' | 'openai';
  onPresetSelect: (preset: EmotionPreset) => void;
  selectedPreset?: string;
}

const EmotionPresets: React.FC<EmotionPresetsProps> = ({
  provider,
  onPresetSelect,
  selectedPreset
}) => {
  // Provider-specific emotion presets
  const getPresets = (): EmotionPreset[] => {
    const basePresets: EmotionPreset[] = [
      {
        id: 'neutral',
        name: 'Neutral',
        icon: <Wind className="w-5 h-5" />,
        color: 'bg-gray-600',
        description: 'Clear, professional tone',
        config: { speed: 1.0, pitch: 0 }
      },
      {
        id: 'excited',
        name: 'Excited',
        icon: <Zap className="w-5 h-5" />,
        color: 'bg-yellow-600',
        description: 'High energy and enthusiasm',
        config: { speed: 1.15, pitch: 2 }
      },
      {
        id: 'calm',
        name: 'Calm',
        icon: <CloudRain className="w-5 h-5" />,
        color: 'bg-blue-600',
        description: 'Soothing and relaxed',
        config: { speed: 0.9, pitch: -1 }
      },
      {
        id: 'dramatic',
        name: 'Dramatic',
        icon: <Flame className="w-5 h-5" />,
        color: 'bg-red-600',
        description: 'Intense and powerful',
        config: { speed: 0.95, pitch: 1 }
      },
      {
        id: 'happy',
        name: 'Happy',
        icon: <Smile className="w-5 h-5" />,
        color: 'bg-green-600',
        description: 'Upbeat and cheerful',
        config: { speed: 1.05, pitch: 1 }
      },
      {
        id: 'sad',
        name: 'Sad',
        icon: <Frown className="w-5 h-5" />,
        color: 'bg-purple-600',
        description: 'Somber and melancholic',
        config: { speed: 0.85, pitch: -2 }
      },
      {
        id: 'romantic',
        name: 'Romantic',
        icon: <Heart className="w-5 h-5" />,
        color: 'bg-pink-600',
        description: 'Warm and intimate',
        config: { speed: 0.95, pitch: -0.5 }
      }
    ];

    // Add provider-specific optimizations
    if (provider === 'elevenlabs') {
      return basePresets.map(preset => ({
        ...preset,
        description: `${preset.description} (ElevenLabs optimized)`
      }));
    } else if (provider === 'google') {
      return basePresets.map(preset => ({
        ...preset,
        description: `${preset.description} (SSML prosody)`,
        config: {
          ...preset.config,
          ssml_additions: `<prosody rate="${preset.config.speed > 1 ? 'fast' : preset.config.speed < 1 ? 'slow' : 'medium'}" pitch="${preset.config.pitch || 0}st">`
        }
      }));
    } else if (provider === 'openai') {
      return basePresets.map(preset => ({
        ...preset,
        description: `${preset.description} (OpenAI optimized)`,
        config: {
          ...preset.config,
          pitch: undefined // OpenAI doesn't support pitch
        }
      }));
    }

    return basePresets;
  };

  const presets = getPresets();

  return (
    <div className="space-y-4">
      <div>
        <h4 className="text-sm font-semibold text-gray-300 mb-3">Quick Emotion Presets</h4>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {presets.map(preset => (
            <button
              key={preset.id}
              onClick={() => onPresetSelect(preset)}
              className={`p-4 rounded-lg transition-all ${
                selectedPreset === preset.id
                  ? `${preset.color} text-white ring-2 ring-white/50`
                  : 'bg-gray-800 hover:bg-gray-700 text-gray-300'
              }`}
            >
              <div className="flex flex-col items-center space-y-2">
                {preset.icon}
                <span className="text-sm font-medium">{preset.name}</span>
                <span className="text-xs opacity-75 text-center">{preset.description}</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Provider-Specific Tips */}
      <div className="bg-gray-800 rounded-lg p-3">
        <div className="text-xs text-gray-400">
          {provider === 'elevenlabs' && (
            <>
              <strong className="text-white">ElevenLabs:</strong> Supports natural emotion control through voice model selection and prosody.
            </>
          )}
          {provider === 'google' && (
            <>
              <strong className="text-white">Google TTS:</strong> Uses SSML prosody tags for precise emotional control.
            </>
          )}
          {provider === 'openai' && (
            <>
              <strong className="text-white">OpenAI TTS:</strong> Best results with punctuation and capitalization for emphasis.
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default EmotionPresets;
