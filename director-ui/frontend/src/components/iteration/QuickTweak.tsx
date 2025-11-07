import React, { useState } from 'react';
import { Zap, Sun, Moon, Thermometer, Droplets, Maximize2, Minimize2, Camera, Palette, Sparkles } from 'lucide-react';

export interface TweakPreset {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  category: 'lighting' | 'color' | 'composition' | 'style';
  promptModifier: string;
  parameterChanges?: {
    brightness?: number;
    contrast?: number;
    saturation?: number;
    temperature?: number;
    [key: string]: any;
  };
}

interface QuickTweakProps {
  currentShot?: {
    id: string;
    prompt: string;
    thumbnailUrl?: string;
  };
  onApplyTweak?: (tweak: TweakPreset) => void;
  onGenerateWithTweak?: (tweak: TweakPreset) => void;
}

const QuickTweak: React.FC<QuickTweakProps> = ({
  currentShot,
  onApplyTweak,
  onGenerateWithTweak
}) => {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedTweaks, setSelectedTweaks] = useState<string[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);

  // Predefined quick tweaks
  const tweakPresets: TweakPreset[] = [
    // Lighting tweaks
    {
      id: 'brighter',
      name: 'Brighter',
      description: 'Increase overall brightness and exposure',
      icon: <Sun className="w-5 h-5" />,
      category: 'lighting',
      promptModifier: 'brighter lighting, increased exposure, well-lit',
      parameterChanges: { brightness: 20, contrast: -5 }
    },
    {
      id: 'darker',
      name: 'Darker',
      description: 'Reduce lighting for moodier atmosphere',
      icon: <Moon className="w-5 h-5" />,
      category: 'lighting',
      promptModifier: 'darker lighting, low-key, moody shadows',
      parameterChanges: { brightness: -20, contrast: 10 }
    },
    {
      id: 'dramatic-lighting',
      name: 'More Dramatic',
      description: 'Increase lighting contrast and drama',
      icon: <Zap className="w-5 h-5" />,
      category: 'lighting',
      promptModifier: 'dramatic lighting, high contrast, chiaroscuro, rim lighting',
      parameterChanges: { contrast: 30, brightness: -5 }
    },
    {
      id: 'soft-lighting',
      name: 'Softer Light',
      description: 'Diffused, gentle lighting',
      icon: <Droplets className="w-5 h-5" />,
      category: 'lighting',
      promptModifier: 'soft diffused lighting, gentle shadows, even illumination',
      parameterChanges: { contrast: -15, brightness: 5 }
    },

    // Color tweaks
    {
      id: 'warmer',
      name: 'Warmer',
      description: 'Add warmth with orange/yellow tones',
      icon: <Thermometer className="w-5 h-5" />,
      category: 'color',
      promptModifier: 'warm color temperature, golden hour, amber tones',
      parameterChanges: { temperature: 30 }
    },
    {
      id: 'cooler',
      name: 'Cooler',
      description: 'Add cool blue tones',
      icon: <Thermometer className="w-5 h-5" />,
      category: 'color',
      promptModifier: 'cool color temperature, blue hour, cyan tones',
      parameterChanges: { temperature: -30 }
    },
    {
      id: 'more-saturated',
      name: 'More Vibrant',
      description: 'Boost color saturation',
      icon: <Palette className="w-5 h-5" />,
      category: 'color',
      promptModifier: 'vibrant colors, saturated, rich color palette',
      parameterChanges: { saturation: 30 }
    },
    {
      id: 'desaturated',
      name: 'Muted Colors',
      description: 'Reduce saturation for subtle look',
      icon: <Palette className="w-5 h-5" />,
      category: 'color',
      promptModifier: 'muted colors, desaturated, subtle color palette',
      parameterChanges: { saturation: -30 }
    },

    // Composition tweaks
    {
      id: 'closer',
      name: 'Closer',
      description: 'Tighter framing, move camera closer',
      icon: <Maximize2 className="w-5 h-5" />,
      category: 'composition',
      promptModifier: 'closer framing, tighter shot, intimate composition',
      parameterChanges: { focalLength: 85 }
    },
    {
      id: 'wider',
      name: 'Wider',
      description: 'Pull back for wider view',
      icon: <Minimize2 className="w-5 h-5" />,
      category: 'composition',
      promptModifier: 'wider framing, establishing shot, more context',
      parameterChanges: { focalLength: 24 }
    },
    {
      id: 'lower-angle',
      name: 'Lower Angle',
      description: 'Camera angle from below',
      icon: <Camera className="w-5 h-5" />,
      category: 'composition',
      promptModifier: 'low camera angle, looking up, heroic perspective',
      parameterChanges: {}
    },
    {
      id: 'higher-angle',
      name: 'Higher Angle',
      description: 'Camera angle from above',
      icon: <Camera className="w-5 h-5" />,
      category: 'composition',
      promptModifier: 'high camera angle, looking down, overhead perspective',
      parameterChanges: {}
    },

    // Style tweaks
    {
      id: 'more-cinematic',
      name: 'More Cinematic',
      description: 'Enhance film-like quality',
      icon: <Sparkles className="w-5 h-5" />,
      category: 'style',
      promptModifier: 'cinematic, film grain, anamorphic lens, 2.39:1 aspect ratio',
      parameterChanges: { contrast: 10, saturation: 5 }
    },
    {
      id: 'more-realistic',
      name: 'More Realistic',
      description: 'Natural, photographic look',
      icon: <Camera className="w-5 h-5" />,
      category: 'style',
      promptModifier: 'photorealistic, natural lighting, documentary style',
      parameterChanges: { contrast: -5, saturation: -10 }
    },
    {
      id: 'more-stylized',
      name: 'More Stylized',
      description: 'Artistic, heightened visuals',
      icon: <Palette className="w-5 h-5" />,
      category: 'style',
      promptModifier: 'stylized, artistic, heightened reality, bold visuals',
      parameterChanges: { contrast: 20, saturation: 20 }
    },
    {
      id: 'film-noir',
      name: 'Film Noir',
      description: 'High contrast black and white aesthetic',
      icon: <Moon className="w-5 h-5" />,
      category: 'style',
      promptModifier: 'film noir, high contrast, dramatic shadows, black and white',
      parameterChanges: { contrast: 40, saturation: -80 }
    }
  ];

  // Filter tweaks by category
  const filteredTweaks = selectedCategory === 'all'
    ? tweakPresets
    : tweakPresets.filter(t => t.category === selectedCategory);

  // Group tweaks by category
  const groupedTweaks = filteredTweaks.reduce((acc, tweak) => {
    if (!acc[tweak.category]) {
      acc[tweak.category] = [];
    }
    acc[tweak.category].push(tweak);
    return acc;
  }, {} as Record<string, TweakPreset[]>);

  // Toggle tweak selection
  const handleTweakClick = (tweak: TweakPreset) => {
    if (selectedTweaks.includes(tweak.id)) {
      setSelectedTweaks(selectedTweaks.filter(id => id !== tweak.id));
    } else {
      setSelectedTweaks([...selectedTweaks, tweak.id]);
    }
  };

  // Apply selected tweaks
  const handleApplyTweaks = async () => {
    if (selectedTweaks.length === 0) return;

    setIsGenerating(true);

    try {
      // Apply each selected tweak
      for (const tweakId of selectedTweaks) {
        const tweak = tweakPresets.find(t => t.id === tweakId);
        if (tweak) {
          await onGenerateWithTweak?.(tweak);
        }
      }

      setSelectedTweaks([]);
    } catch (error) {
      console.error('Apply tweaks error:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  // Get category icon
  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'lighting': return '💡';
      case 'color': return '🎨';
      case 'composition': return '📐';
      case 'style': return '✨';
      default: return '⚡';
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Zap className="w-6 h-6 text-yellow-400" />
          <div>
            <h3 className="text-lg font-bold text-white">Quick Tweaks</h3>
            <p className="text-sm text-gray-400">One-click adjustments for rapid iteration</p>
          </div>
        </div>

        {selectedTweaks.length > 0 && (
          <button
            onClick={handleApplyTweaks}
            disabled={isGenerating}
            className="px-4 py-2 bg-yellow-600 hover:bg-yellow-500 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg transition flex items-center space-x-2"
          >
            <Zap className="w-4 h-4" />
            <span>{isGenerating ? 'Generating...' : `Apply ${selectedTweaks.length} Tweak${selectedTweaks.length > 1 ? 's' : ''}`}</span>
          </button>
        )}
      </div>

      {/* Current Shot Preview */}
      {currentShot && (
        <div className="mb-6 bg-gray-900 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center space-x-4">
            {currentShot.thumbnailUrl && (
              <img
                src={currentShot.thumbnailUrl}
                alt="Current shot"
                className="w-32 h-20 object-cover rounded border border-gray-600"
              />
            )}
            <div className="flex-1">
              <h4 className="text-white font-semibold mb-1">Current Shot</h4>
              <p className="text-sm text-gray-400 line-clamp-2">{currentShot.prompt}</p>
            </div>
          </div>
        </div>
      )}

      {/* Category Filter */}
      <div className="flex items-center space-x-2 mb-6 overflow-x-auto">
        {['all', 'lighting', 'color', 'composition', 'style'].map(category => (
          <button
            key={category}
            onClick={() => setSelectedCategory(category)}
            className={`px-4 py-2 rounded-lg text-sm transition whitespace-nowrap ${
              selectedCategory === category
                ? 'bg-yellow-600 text-white'
                : 'bg-gray-900 text-gray-400 hover:bg-gray-700'
            }`}
          >
            {category === 'all' ? 'All' : `${getCategoryIcon(category)} ${category.charAt(0).toUpperCase() + category.slice(1)}`}
          </button>
        ))}
      </div>

      {/* Tweak Grid */}
      <div className="space-y-6">
        {Object.entries(groupedTweaks).map(([category, tweaks]) => (
          <div key={category}>
            <h4 className="text-sm font-semibold text-gray-400 mb-3 capitalize flex items-center space-x-2">
              <span>{getCategoryIcon(category)}</span>
              <span>{category}</span>
            </h4>

            <div className="grid grid-cols-2 gap-3">
              {tweaks.map(tweak => {
                const isSelected = selectedTweaks.includes(tweak.id);

                return (
                  <button
                    key={tweak.id}
                    onClick={() => handleTweakClick(tweak)}
                    className={`bg-gray-900 rounded-lg p-4 border-2 transition-all text-left ${
                      isSelected
                        ? 'border-yellow-500 bg-yellow-500/10'
                        : 'border-gray-700 hover:border-gray-600'
                    }`}
                  >
                    <div className="flex items-start space-x-3 mb-2">
                      <div className={`p-2 rounded-lg ${
                        isSelected ? 'bg-yellow-600 text-white' : 'bg-gray-800 text-gray-400'
                      }`}>
                        {tweak.icon}
                      </div>

                      <div className="flex-1">
                        <h5 className="text-white font-semibold mb-1">{tweak.name}</h5>
                        <p className="text-xs text-gray-400">{tweak.description}</p>
                      </div>
                    </div>

                    {/* Parameter changes preview */}
                    {tweak.parameterChanges && Object.keys(tweak.parameterChanges).length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {Object.entries(tweak.parameterChanges).map(([key, value]) => (
                          <span key={key} className="text-xs px-2 py-0.5 bg-gray-800 text-gray-500 rounded">
                            {key}: {value > 0 ? '+' : ''}{value}
                          </span>
                        ))}
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Tips */}
      <div className="mt-6 bg-yellow-600/10 border border-yellow-600/30 rounded-lg p-3">
        <p className="text-xs text-yellow-400">
          <strong>💡 Pro Tip:</strong> Select multiple tweaks to combine effects (e.g., "Brighter" + "Warmer" + "More Cinematic").
          The system will apply all selected adjustments in a single generation.
        </p>
      </div>
    </div>
  );
};

export default QuickTweak;
