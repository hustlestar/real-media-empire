import React, { useState } from 'react';
import { Palette, Plus, X, Sparkles, Eye, Save, Upload } from 'lucide-react';

export interface StyleReference {
  id: string;
  name: string;
  category: 'cinematographer' | 'director' | 'genre' | 'era' | 'artist' | 'custom';
  weight: number; // 0-100 percentage
  description?: string;
  imageUrl?: string;
  keywords?: string[];
}

interface StyleMixerProps {
  currentStyles?: StyleReference[];
  onStylesChange?: (styles: StyleReference[]) => void;
  onGeneratePrompt?: () => void;
  onSavePreset?: (name: string, styles: StyleReference[]) => void;
}

const StyleMixer: React.FC<StyleMixerProps> = ({
  currentStyles = [],
  onStylesChange,
  onGeneratePrompt,
  onSavePreset
}) => {
  const [styles, setStyles] = useState<StyleReference[]>(currentStyles);
  const [showStyleLibrary, setShowStyleLibrary] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [generatedPrompt, setGeneratedPrompt] = useState('');
  const [presetName, setPresetName] = useState('');

  // Style library with famous references
  const styleLibrary: Omit<StyleReference, 'id' | 'weight'>[] = [
    // Cinematographers
    {
      name: 'Roger Deakins',
      category: 'cinematographer',
      description: 'Natural lighting, wide shots, moody atmospheres',
      keywords: ['naturalistic', 'wide-angle', 'atmospheric', 'high-contrast']
    },
    {
      name: 'Emmanuel Lubezki',
      category: 'cinematographer',
      description: 'Natural light, long takes, fluid camera movement',
      keywords: ['natural-light', 'long-takes', 'fluid', 'immersive']
    },
    {
      name: 'Greig Fraser',
      category: 'cinematographer',
      description: 'Dramatic lighting, rich colors, epic scale',
      keywords: ['dramatic', 'epic', 'rich-colors', 'wide-format']
    },
    {
      name: 'Hoyte van Hoytema',
      category: 'cinematographer',
      description: 'IMAX, practical effects, bold compositions',
      keywords: ['IMAX', 'large-format', 'practical', 'bold']
    },

    // Directors
    {
      name: 'Christopher Nolan',
      category: 'director',
      description: 'Practical effects, complex narratives, epic scope',
      keywords: ['practical', 'epic', 'complex', 'ambitious']
    },
    {
      name: 'Wes Anderson',
      category: 'director',
      description: 'Symmetrical framing, pastel colors, whimsical',
      keywords: ['symmetrical', 'pastel', 'centered', 'whimsical']
    },
    {
      name: 'Denis Villeneuve',
      category: 'director',
      description: 'Minimalist, atmospheric, slow-burn tension',
      keywords: ['minimalist', 'atmospheric', 'tense', 'deliberate']
    },
    {
      name: 'Quentin Tarantino',
      category: 'director',
      description: 'Bold colors, dynamic angles, stylized violence',
      keywords: ['bold', 'dynamic', 'stylized', 'saturated']
    },
    {
      name: 'Ridley Scott',
      category: 'director',
      description: 'Dark, moody, dystopian, detailed worlds',
      keywords: ['dark', 'moody', 'dystopian', 'detailed']
    },

    // Genres
    {
      name: 'Film Noir',
      category: 'genre',
      description: 'High contrast, dramatic shadows, venetian blinds',
      keywords: ['high-contrast', 'shadows', 'black-and-white', 'dramatic']
    },
    {
      name: 'Cyberpunk',
      category: 'genre',
      description: 'Neon lights, rain, urban dystopia, tech noir',
      keywords: ['neon', 'rain', 'urban', 'tech', 'dystopian']
    },
    {
      name: 'Western',
      category: 'genre',
      description: 'Golden hour, wide vistas, dust, warm tones',
      keywords: ['golden-hour', 'wide', 'warm', 'dusty', 'vast']
    },
    {
      name: 'Sci-Fi Epic',
      category: 'genre',
      description: 'Vast scale, futuristic, clean lines, cool tones',
      keywords: ['epic', 'futuristic', 'clean', 'cool-tones', 'vast']
    },

    // Eras
    {
      name: '1970s Cinema',
      category: 'era',
      description: 'Warm grain, natural lighting, earthy tones',
      keywords: ['grainy', 'warm', 'natural', 'earthy', 'organic']
    },
    {
      name: '1990s Action',
      category: 'era',
      description: 'Saturated colors, fast cuts, dynamic movement',
      keywords: ['saturated', 'dynamic', 'energetic', 'bold']
    },

    // Artists
    {
      name: 'Caravaggio',
      category: 'artist',
      description: 'Dramatic chiaroscuro, theatrical lighting',
      keywords: ['chiaroscuro', 'dramatic', 'theatrical', 'painterly']
    },
    {
      name: 'Edward Hopper',
      category: 'artist',
      description: 'Isolation, geometric compositions, American realism',
      keywords: ['geometric', 'isolated', 'realism', 'contemplative']
    }
  ];

  // Add style to mixer
  const handleAddStyle = (style: Omit<StyleReference, 'id' | 'weight'>) => {
    const newStyle: StyleReference = {
      ...style,
      id: `style_${Date.now()}_${Math.random()}`,
      weight: 100 / (styles.length + 1) // Distribute evenly
    };

    // Redistribute weights
    const redistributedStyles = styles.map(s => ({
      ...s,
      weight: 100 / (styles.length + 1)
    }));

    const updatedStyles = [...redistributedStyles, newStyle];
    setStyles(updatedStyles);
    onStylesChange?.(updatedStyles);
    setShowStyleLibrary(false);
  };

  // Remove style
  const handleRemoveStyle = (id: string) => {
    const updatedStyles = styles.filter(s => s.id !== id);

    // Redistribute weights
    if (updatedStyles.length > 0) {
      const redistributed = updatedStyles.map(s => ({
        ...s,
        weight: 100 / updatedStyles.length
      }));
      setStyles(redistributed);
      onStylesChange?.(redistributed);
    } else {
      setStyles([]);
      onStylesChange?.([]);
    }
  };

  // Update style weight
  const handleWeightChange = (id: string, newWeight: number) => {
    const updatedStyles = styles.map(s =>
      s.id === id ? { ...s, weight: newWeight } : s
    );

    // Normalize weights to sum to 100
    const totalWeight = updatedStyles.reduce((sum, s) => sum + s.weight, 0);
    if (totalWeight > 0) {
      const normalized = updatedStyles.map(s => ({
        ...s,
        weight: (s.weight / totalWeight) * 100
      }));
      setStyles(normalized);
      onStylesChange?.(normalized);
    }
  };

  // Generate style prompt
  const handleGeneratePrompt = () => {
    if (styles.length === 0) {
      setGeneratedPrompt('No styles selected. Add styles to generate a prompt.');
      return;
    }

    // Sort by weight descending
    const sortedStyles = [...styles].sort((a, b) => b.weight - a.weight);

    // Build prompt
    let prompt = 'Cinematic shot with ';

    sortedStyles.forEach((style, idx) => {
      const percentage = Math.round(style.weight);
      if (idx === 0) {
        prompt += `${percentage}% ${style.name} style`;
      } else if (idx === sortedStyles.length - 1) {
        prompt += `, and ${percentage}% ${style.name}`;
      } else {
        prompt += `, ${percentage}% ${style.name}`;
      }
    });

    // Add combined keywords
    const allKeywords = styles.flatMap(s => s.keywords || []);
    const uniqueKeywords = Array.from(new Set(allKeywords)).slice(0, 8);

    if (uniqueKeywords.length > 0) {
      prompt += `. Visual characteristics: ${uniqueKeywords.join(', ')}`;
    }

    prompt += '. Professional cinematography, high production value, masterful composition.';

    setGeneratedPrompt(prompt);
    onGeneratePrompt?.();
  };

  // Save as preset
  const handleSavePreset = () => {
    if (!presetName.trim()) {
      alert('Please enter a preset name');
      return;
    }

    onSavePreset?.(presetName, styles);
    setPresetName('');
    alert(`Preset "${presetName}" saved!`);
  };

  // Filter library by category
  const filteredLibrary = selectedCategory === 'all'
    ? styleLibrary
    : styleLibrary.filter(s => s.category === selectedCategory);

  // Get category icon
  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'cinematographer': return '🎥';
      case 'director': return '🎬';
      case 'genre': return '🎭';
      case 'era': return '📅';
      case 'artist': return '🎨';
      default: return '✨';
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Palette className="w-6 h-6 text-purple-400" />
          <div>
            <h3 className="text-lg font-bold text-white">Style Mixer</h3>
            <p className="text-sm text-gray-400">Blend visual references to create unique looks</p>
          </div>
        </div>

        <button
          onClick={() => setShowStyleLibrary(!showStyleLibrary)}
          className="px-4 py-2 bg-purple-600 hover:bg-purple-500 rounded-lg transition flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>Add Style</span>
        </button>
      </div>

      {/* Current Styles */}
      {styles.length > 0 ? (
        <div className="mb-6 space-y-3">
          {styles.map(style => (
            <div
              key={style.id}
              className="bg-gray-900 rounded-lg p-4 border border-gray-700"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-lg">{getCategoryIcon(style.category)}</span>
                    <h4 className="text-white font-semibold">{style.name}</h4>
                    <span className="text-xs px-2 py-1 bg-purple-600/20 text-purple-400 rounded capitalize">
                      {style.category}
                    </span>
                  </div>
                  {style.description && (
                    <p className="text-sm text-gray-400">{style.description}</p>
                  )}
                  {style.keywords && style.keywords.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {style.keywords.map((keyword, idx) => (
                        <span
                          key={idx}
                          className="text-xs px-2 py-0.5 bg-gray-800 text-gray-400 rounded"
                        >
                          {keyword}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <button
                  onClick={() => handleRemoveStyle(style.id)}
                  className="p-1 hover:bg-gray-800 rounded transition text-gray-400 hover:text-red-400"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Weight Slider */}
              <div className="flex items-center space-x-4">
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="1"
                  value={style.weight}
                  onChange={(e) => handleWeightChange(style.id, parseFloat(e.target.value))}
                  className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-600"
                />
                <div className="w-16 text-center">
                  <span className="text-lg font-bold text-white">{Math.round(style.weight)}%</span>
                </div>
              </div>

              {/* Weight bar visualization */}
              <div className="mt-2 h-2 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all"
                  style={{ width: `${style.weight}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="mb-6 bg-gray-900 rounded-lg p-8 border border-gray-700 text-center">
          <Sparkles className="w-12 h-12 text-gray-600 mx-auto mb-3" />
          <p className="text-gray-400 mb-2">No styles added yet</p>
          <p className="text-sm text-gray-500">Click "Add Style" to start mixing visual references</p>
        </div>
      )}

      {/* Style Library Modal */}
      {showStyleLibrary && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-8">
          <div className="bg-gray-800 rounded-lg border border-gray-700 max-w-4xl w-full max-h-[80vh] overflow-hidden flex flex-col">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-700">
              <div>
                <h3 className="text-lg font-bold text-white">Style Library</h3>
                <p className="text-sm text-gray-400">Choose styles to add to your mix</p>
              </div>
              <button
                onClick={() => setShowStyleLibrary(false)}
                className="p-2 hover:bg-gray-700 rounded transition text-gray-400"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Category Filters */}
            <div className="flex items-center space-x-2 px-6 py-3 border-b border-gray-700 overflow-x-auto">
              {['all', 'cinematographer', 'director', 'genre', 'era', 'artist'].map(category => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`px-4 py-2 rounded-lg text-sm transition whitespace-nowrap ${
                    selectedCategory === category
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-900 text-gray-400 hover:bg-gray-700'
                  }`}
                >
                  {category === 'all' ? 'All' : category.charAt(0).toUpperCase() + category.slice(1)}
                </button>
              ))}
            </div>

            {/* Style Grid */}
            <div className="flex-1 overflow-y-auto p-6">
              <div className="grid grid-cols-2 gap-4">
                {filteredLibrary.map((style, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleAddStyle(style)}
                    className="bg-gray-900 rounded-lg p-4 border border-gray-700 hover:border-purple-500 transition text-left"
                  >
                    <div className="flex items-start space-x-3 mb-2">
                      <span className="text-2xl">{getCategoryIcon(style.category)}</span>
                      <div className="flex-1">
                        <h4 className="text-white font-semibold mb-1">{style.name}</h4>
                        <p className="text-xs text-gray-400">{style.description}</p>
                      </div>
                    </div>
                    {style.keywords && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {style.keywords.slice(0, 4).map((keyword, kidx) => (
                          <span
                            key={kidx}
                            className="text-xs px-2 py-0.5 bg-gray-800 text-gray-500 rounded"
                          >
                            {keyword}
                          </span>
                        ))}
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center space-x-3">
        <button
          onClick={handleGeneratePrompt}
          disabled={styles.length === 0}
          className="flex-1 px-4 py-3 bg-purple-600 hover:bg-purple-500 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg transition flex items-center justify-center space-x-2"
        >
          <Sparkles className="w-5 h-5" />
          <span>Generate Style Prompt</span>
        </button>

        <button
          onClick={() => {}}
          disabled={styles.length === 0}
          className="px-4 py-3 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:cursor-not-allowed rounded-lg transition"
          title="Preview Style"
        >
          <Eye className="w-5 h-5" />
        </button>
      </div>

      {/* Generated Prompt */}
      {generatedPrompt && (
        <div className="mt-4 bg-gray-900 rounded-lg p-4 border border-purple-500/30">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-semibold text-purple-400">Generated Style Prompt</h4>
            <button
              onClick={() => navigator.clipboard.writeText(generatedPrompt)}
              className="text-xs px-2 py-1 bg-gray-800 hover:bg-gray-700 rounded text-gray-400 transition"
            >
              Copy
            </button>
          </div>
          <p className="text-sm text-gray-300 leading-relaxed">{generatedPrompt}</p>
        </div>
      )}

      {/* Save Preset */}
      {styles.length > 0 && (
        <div className="mt-4 flex items-center space-x-3">
          <input
            type="text"
            value={presetName}
            onChange={(e) => setPresetName(e.target.value)}
            placeholder="Preset name (e.g., 'Neo-Noir Mix')"
            className="flex-1 px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:border-purple-500 focus:outline-none"
          />
          <button
            onClick={handleSavePreset}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition flex items-center space-x-2"
          >
            <Save className="w-4 h-4" />
            <span>Save Preset</span>
          </button>
        </div>
      )}
    </div>
  );
};

export default StyleMixer;
