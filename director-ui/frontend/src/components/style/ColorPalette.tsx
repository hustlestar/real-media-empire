import React, { useState } from 'react';
import { Palette, Plus, X, Copy, Eye, Sparkles, Save, RefreshCw } from 'lucide-react';

export interface ColorConfig {
  id: string;
  name: string;
  hex: string;
  role: 'primary' | 'secondary' | 'accent' | 'background' | 'highlight';
  weight: number; // 0-100 prominence
}

export interface ColorGrading {
  temperature: number; // -100 to 100 (cool to warm)
  tint: number; // -100 to 100 (green to magenta)
  saturation: number; // 0-200 (0=grayscale, 100=normal, 200=hyper-saturated)
  contrast: number; // 0-200
  brightness: number; // -100 to 100
  shadows: string; // hex color for shadow tint
  midtones: string; // hex color for midtone tint
  highlights: string; // hex color for highlight tint
}

interface ColorPaletteProps {
  colors?: ColorConfig[];
  grading?: ColorGrading;
  onColorsChange?: (colors: ColorConfig[]) => void;
  onGradingChange?: (grading: ColorGrading) => void;
  onSavePreset?: (name: string, colors: ColorConfig[], grading: ColorGrading) => void;
}

const ColorPalette: React.FC<ColorPaletteProps> = ({
  colors = [],
  grading,
  onColorsChange,
  onGradingChange,
  onSavePreset
}) => {
  const [palette, setPalette] = useState<ColorConfig[]>(colors);
  const [colorGrading, setColorGrading] = useState<ColorGrading>(
    grading || {
      temperature: 0,
      tint: 0,
      saturation: 100,
      contrast: 100,
      brightness: 0,
      shadows: '#000000',
      midtones: '#808080',
      highlights: '#ffffff'
    }
  );
  const [showPresets, setShowPresets] = useState(false);
  const [presetName, setPresetName] = useState('');

  // Preset palettes inspired by famous films
  const presetPalettes: Array<{
    name: string;
    description: string;
    colors: Omit<ColorConfig, 'id'>[];
    grading: Partial<ColorGrading>;
  }> = [
    {
      name: 'Blade Runner 2049',
      description: 'Orange and teal neo-noir',
      colors: [
        { name: 'Desert Orange', hex: '#FF8C42', role: 'primary', weight: 40 },
        { name: 'Neon Teal', hex: '#00D9FF', role: 'secondary', weight: 35 },
        { name: 'Deep Purple', hex: '#6B2D5C', role: 'accent', weight: 15 },
        { name: 'Dark Gray', hex: '#1A1A1A', role: 'background', weight: 10 }
      ],
      grading: { temperature: 10, saturation: 130, contrast: 120, brightness: -5 }
    },
    {
      name: 'The Grand Budapest Hotel',
      description: 'Wes Anderson pastels',
      colors: [
        { name: 'Pink', hex: '#F4C7D8', role: 'primary', weight: 30 },
        { name: 'Lavender', hex: '#B4A7D6', role: 'secondary', weight: 25 },
        { name: 'Mustard', hex: '#F3D250', role: 'accent', weight: 20 },
        { name: 'Mint', hex: '#90D7CE', role: 'highlight', weight: 15 },
        { name: 'Beige', hex: '#E8D4B2', role: 'background', weight: 10 }
      ],
      grading: { temperature: 5, saturation: 95, contrast: 90, brightness: 5 }
    },
    {
      name: 'The Matrix',
      description: 'Green-tinted cyberpunk',
      colors: [
        { name: 'Matrix Green', hex: '#00FF41', role: 'primary', weight: 50 },
        { name: 'Dark Green', hex: '#003B00', role: 'secondary', weight: 30 },
        { name: 'Black', hex: '#000000', role: 'background', weight: 20 }
      ],
      grading: { temperature: -10, tint: 20, saturation: 110, contrast: 130, brightness: -10 }
    },
    {
      name: 'Mad Max: Fury Road',
      description: 'Desert orange and blue',
      colors: [
        { name: 'Desert Sand', hex: '#E8AA42', role: 'primary', weight: 40 },
        { name: 'Sky Blue', hex: '#00A8CC', role: 'secondary', weight: 35 },
        { name: 'Blood Red', hex: '#B83B5E', role: 'accent', weight: 15 },
        { name: 'Storm Gray', hex: '#3B4252', role: 'background', weight: 10 }
      ],
      grading: { temperature: 20, saturation: 150, contrast: 130, brightness: 0 }
    },
    {
      name: 'Moonlight',
      description: 'Blue and violet intimacy',
      colors: [
        { name: 'Ocean Blue', hex: '#2E5266', role: 'primary', weight: 40 },
        { name: 'Violet', hex: '#6E44FF', role: 'secondary', weight: 30 },
        { name: 'Pink', hex: '#D891EF', role: 'accent', weight: 20 },
        { name: 'Navy', hex: '#0F1B2E', role: 'background', weight: 10 }
      ],
      grading: { temperature: -15, saturation: 115, contrast: 105, brightness: -5 }
    },
    {
      name: 'Her',
      description: 'Warm nostalgic pastels',
      colors: [
        { name: 'Peach', hex: '#FFA07A', role: 'primary', weight: 35 },
        { name: 'Cream', hex: '#FFF5E1', role: 'secondary', weight: 30 },
        { name: 'Coral', hex: '#FF6B6B', role: 'accent', weight: 20 },
        { name: 'Beige', hex: '#D4C5A9', role: 'background', weight: 15 }
      ],
      grading: { temperature: 15, saturation: 85, contrast: 95, brightness: 10 }
    }
  ];

  // Apply preset
  const handleApplyPreset = (preset: typeof presetPalettes[0]) => {
    const newPalette: ColorConfig[] = preset.colors.map((color, idx) => ({
      ...color,
      id: `color_${Date.now()}_${idx}`
    }));

    setPalette(newPalette);
    onColorsChange?.(newPalette);

    const newGrading = { ...colorGrading, ...preset.grading };
    setColorGrading(newGrading);
    onGradingChange?.(newGrading);

    setShowPresets(false);
  };

  // Add custom color
  const handleAddColor = () => {
    const newColor: ColorConfig = {
      id: `color_${Date.now()}`,
      name: 'Custom Color',
      hex: '#' + Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0'),
      role: 'accent',
      weight: 100 / (palette.length + 1)
    };

    const redistributed = palette.map(c => ({
      ...c,
      weight: 100 / (palette.length + 1)
    }));

    const updated = [...redistributed, newColor];
    setPalette(updated);
    onColorsChange?.(updated);
  };

  // Remove color
  const handleRemoveColor = (id: string) => {
    const updated = palette.filter(c => c.id !== id);
    const redistributed = updated.map(c => ({
      ...c,
      weight: updated.length > 0 ? 100 / updated.length : 0
    }));

    setPalette(redistributed);
    onColorsChange?.(redistributed);
  };

  // Update color
  const handleUpdateColor = (id: string, updates: Partial<ColorConfig>) => {
    const updated = palette.map(c => (c.id === id ? { ...c, ...updates } : c));
    setPalette(updated);
    onColorsChange?.(updated);
  };

  // Update grading
  const handleGradingUpdate = (updates: Partial<ColorGrading>) => {
    const updated = { ...colorGrading, ...updates };
    setColorGrading(updated);
    onGradingChange?.(updated);
  };

  // Save preset
  const handleSavePreset = () => {
    if (!presetName.trim()) {
      alert('Please enter a preset name');
      return;
    }

    onSavePreset?.(presetName, palette, colorGrading);
    setPresetName('');
    alert(`Preset "${presetName}" saved!`);
  };

  // Copy palette as prompt
  const handleCopyPrompt = () => {
    const colorNames = palette.map(c => c.name).join(', ');
    const prompt = `Color palette: ${colorNames}. Temperature ${colorGrading.temperature > 0 ? 'warm' : 'cool'}, ${colorGrading.saturation > 100 ? 'saturated' : 'muted'} colors, ${colorGrading.contrast > 100 ? 'high' : 'low'} contrast.`;

    navigator.clipboard.writeText(prompt);
    alert('Color prompt copied to clipboard!');
  };

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Palette className="w-6 h-6 text-pink-400" />
          <div>
            <h3 className="text-lg font-bold text-white">Color Palette & Grading</h3>
            <p className="text-sm text-gray-400">Control colors and color grading</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowPresets(true)}
            className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition flex items-center space-x-2"
          >
            <Eye className="w-4 h-4" />
            <span>Presets</span>
          </button>

          <button
            onClick={handleAddColor}
            className="px-3 py-2 bg-pink-600 hover:bg-pink-500 rounded-lg transition flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Add Color</span>
          </button>
        </div>
      </div>

      {/* Current Palette */}
      {palette.length > 0 ? (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-semibold text-white">Current Palette</h4>
            <button
              onClick={handleCopyPrompt}
              className="text-xs px-2 py-1 bg-gray-700 hover:bg-gray-600 rounded transition flex items-center space-x-1"
            >
              <Copy className="w-3 h-3" />
              <span>Copy Prompt</span>
            </button>
          </div>

          {/* Color Swatches */}
          <div className="flex items-center space-x-2 mb-4">
            {palette.map(color => (
              <div
                key={color.id}
                className="flex-1 h-20 rounded-lg border-2 border-gray-700 relative group cursor-pointer"
                style={{ backgroundColor: color.hex }}
              >
                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition flex items-center justify-center">
                  <button
                    onClick={() => handleRemoveColor(color.id)}
                    className="p-1 bg-red-600 rounded hover:bg-red-500"
                  >
                    <X className="w-4 h-4 text-white" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Color Details */}
          <div className="space-y-3">
            {palette.map(color => (
              <div key={color.id} className="bg-gray-900 rounded-lg p-3 border border-gray-700">
                <div className="flex items-center space-x-3 mb-2">
                  <div
                    className="w-8 h-8 rounded border border-gray-600"
                    style={{ backgroundColor: color.hex }}
                  ></div>

                  <input
                    type="text"
                    value={color.name}
                    onChange={(e) => handleUpdateColor(color.id, { name: e.target.value })}
                    className="flex-1 px-2 py-1 bg-gray-800 border border-gray-700 rounded text-white text-sm focus:border-pink-500 focus:outline-none"
                  />

                  <input
                    type="color"
                    value={color.hex}
                    onChange={(e) => handleUpdateColor(color.id, { hex: e.target.value })}
                    className="w-10 h-8 rounded cursor-pointer"
                  />

                  <select
                    value={color.role}
                    onChange={(e) => handleUpdateColor(color.id, { role: e.target.value as ColorConfig['role'] })}
                    className="px-2 py-1 bg-gray-800 border border-gray-700 rounded text-white text-sm focus:border-pink-500 focus:outline-none"
                  >
                    <option value="primary">Primary</option>
                    <option value="secondary">Secondary</option>
                    <option value="accent">Accent</option>
                    <option value="background">Background</option>
                    <option value="highlight">Highlight</option>
                  </select>
                </div>

                {/* Weight Slider */}
                <div className="flex items-center space-x-3">
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={color.weight}
                    onChange={(e) => handleUpdateColor(color.id, { weight: parseFloat(e.target.value) })}
                    className="flex-1 h-1 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-pink-600"
                  />
                  <span className="text-sm text-gray-400 w-12">{Math.round(color.weight)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="mb-6 bg-gray-900 rounded-lg p-8 border border-gray-700 text-center">
          <Palette className="w-12 h-12 text-gray-600 mx-auto mb-3" />
          <p className="text-gray-400 mb-2">No colors in palette</p>
          <p className="text-sm text-gray-500">Add colors or choose a preset</p>
        </div>
      )}

      {/* Color Grading Controls */}
      <div className="bg-gray-900 rounded-lg p-4 border border-gray-700">
        <h4 className="text-sm font-semibold text-white mb-4">Color Grading</h4>

        <div className="space-y-4">
          {/* Temperature */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm text-gray-400">Temperature</label>
              <span className="text-sm text-white">{colorGrading.temperature}</span>
            </div>
            <input
              type="range"
              min="-100"
              max="100"
              value={colorGrading.temperature}
              onChange={(e) => handleGradingUpdate({ temperature: parseFloat(e.target.value) })}
              className="w-full h-2 bg-gradient-to-r from-blue-500 via-gray-500 to-orange-500 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Cool</span>
              <span>Warm</span>
            </div>
          </div>

          {/* Tint */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm text-gray-400">Tint</label>
              <span className="text-sm text-white">{colorGrading.tint}</span>
            </div>
            <input
              type="range"
              min="-100"
              max="100"
              value={colorGrading.tint}
              onChange={(e) => handleGradingUpdate({ tint: parseFloat(e.target.value) })}
              className="w-full h-2 bg-gradient-to-r from-green-500 via-gray-500 to-pink-500 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Green</span>
              <span>Magenta</span>
            </div>
          </div>

          {/* Saturation */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm text-gray-400">Saturation</label>
              <span className="text-sm text-white">{colorGrading.saturation}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="200"
              value={colorGrading.saturation}
              onChange={(e) => handleGradingUpdate({ saturation: parseFloat(e.target.value) })}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-pink-600"
            />
          </div>

          {/* Contrast */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm text-gray-400">Contrast</label>
              <span className="text-sm text-white">{colorGrading.contrast}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="200"
              value={colorGrading.contrast}
              onChange={(e) => handleGradingUpdate({ contrast: parseFloat(e.target.value) })}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-pink-600"
            />
          </div>

          {/* Brightness */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm text-gray-400">Brightness</label>
              <span className="text-sm text-white">{colorGrading.brightness}</span>
            </div>
            <input
              type="range"
              min="-100"
              max="100"
              value={colorGrading.brightness}
              onChange={(e) => handleGradingUpdate({ brightness: parseFloat(e.target.value) })}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-pink-600"
            />
          </div>
        </div>
      </div>

      {/* Save Preset */}
      {palette.length > 0 && (
        <div className="mt-4 flex items-center space-x-3">
          <input
            type="text"
            value={presetName}
            onChange={(e) => setPresetName(e.target.value)}
            placeholder="Preset name (e.g., 'Cyberpunk Neon')"
            className="flex-1 px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:border-pink-500 focus:outline-none"
          />
          <button
            onClick={handleSavePreset}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition flex items-center space-x-2"
          >
            <Save className="w-4 h-4" />
            <span>Save</span>
          </button>
        </div>
      )}

      {/* Presets Modal */}
      {showPresets && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-8">
          <div className="bg-gray-800 rounded-lg border border-gray-700 max-w-4xl w-full max-h-[80vh] overflow-hidden flex flex-col">
            <div className="flex items-center justify-between p-6 border-b border-gray-700">
              <div>
                <h3 className="text-lg font-bold text-white">Color Presets</h3>
                <p className="text-sm text-gray-400">Inspired by famous films</p>
              </div>
              <button
                onClick={() => setShowPresets(false)}
                className="p-2 hover:bg-gray-700 rounded transition text-gray-400"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
              <div className="grid grid-cols-2 gap-4">
                {presetPalettes.map((preset, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleApplyPreset(preset)}
                    className="bg-gray-900 rounded-lg p-4 border border-gray-700 hover:border-pink-500 transition text-left"
                  >
                    <h4 className="text-white font-semibold mb-1">{preset.name}</h4>
                    <p className="text-xs text-gray-400 mb-3">{preset.description}</p>

                    {/* Color Swatches */}
                    <div className="flex items-center space-x-1">
                      {preset.colors.map((color, cidx) => (
                        <div
                          key={cidx}
                          className="flex-1 h-8 rounded"
                          style={{ backgroundColor: color.hex }}
                        ></div>
                      ))}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ColorPalette;
