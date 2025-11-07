import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Save, Eye, Upload } from 'lucide-react';
import { apiUrl } from '../config/api';

import StyleMixer, { StyleReference } from '../components/style/StyleMixer';
import ReferenceUpload, { ReferenceImage } from '../components/style/ReferenceUpload';
import ColorPalette, { ColorConfig, ColorGrading } from '../components/style/ColorPalette';
import CameraControls, { CameraSettings } from '../components/style/CameraControls';

const VisualStylePage: React.FC = () => {
  const navigate = useNavigate();

  // Style state
  const [styleReferences, setStyleReferences] = useState<StyleReference[]>([]);
  const [referenceImages, setReferenceImages] = useState<ReferenceImage[]>([]);
  const [colorPalette, setColorPalette] = useState<ColorConfig[]>([]);
  const [colorGrading, setColorGrading] = useState<ColorGrading | undefined>();
  const [cameraSettings, setCameraSettings] = useState<CameraSettings | undefined>();

  // UI state
  const [presetName, setPresetName] = useState('');
  const [generatedPrompt, setGeneratedPrompt] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  // Handle reference image analysis
  const handleAnalyzeImage = async (imageUrl: string): Promise<ReferenceImage['analysis']> => {
    try {
      // Mock analysis - in production, call backend API
      return {
        dominantColors: ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'],
        mood: 'Vibrant and energetic',
        composition: 'Dynamic with strong diagonals',
        lighting: 'High-key with natural light',
        keywords: ['bright', 'colorful', 'energetic', 'modern', 'clean']
      };
    } catch (error) {
      console.error('Analysis error:', error);
      throw error;
    }
  };

  // Generate comprehensive style prompt
  const handleGeneratePrompt = () => {
    const parts: string[] = [];

    // Style references
    if (styleReferences.length > 0) {
      const sorted = [...styleReferences].sort((a, b) => b.weight - a.weight);
      const desc = sorted
        .filter(s => s.weight > 5)
        .map(s => `${Math.round(s.weight)}% ${s.name}`)
        .join(', ');
      parts.push(`Visual style: ${desc}`);
    }

    // Reference images
    if (referenceImages.length > 0) {
      parts.push(`Inspired by ${referenceImages.length} reference image${referenceImages.length > 1 ? 's' : ''}`);

      // Combine keywords from all references
      const allKeywords = referenceImages
        .flatMap(img => img.analysis?.keywords || [])
        .filter((v, i, a) => a.indexOf(v) === i)  // unique
        .slice(0, 5);

      if (allKeywords.length > 0) {
        parts.push(`Visual characteristics: ${allKeywords.join(', ')}`);
      }
    }

    // Color palette
    if (colorPalette.length > 0) {
      const colorNames = colorPalette
        .filter(c => c.weight > 10)
        .map(c => c.name)
        .join(', ');
      parts.push(`Color palette: ${colorNames}`);
    }

    // Color grading
    if (colorGrading) {
      const tempDesc = colorGrading.temperature > 0 ? 'warm' : colorGrading.temperature < 0 ? 'cool' : 'neutral';
      const satDesc = colorGrading.saturation > 110 ? 'saturated' : colorGrading.saturation < 90 ? 'muted' : 'natural';
      const contrastDesc = colorGrading.contrast > 110 ? 'high contrast' : colorGrading.contrast < 90 ? 'low contrast' : 'balanced contrast';

      parts.push(`${tempDesc} color temperature, ${satDesc} colors, ${contrastDesc}`);
    }

    // Camera settings
    if (cameraSettings) {
      parts.push(
        `Shot on ${cameraSettings.sensor} sensor with ${cameraSettings.focalLength}mm lens at f/${cameraSettings.aperture}. ` +
        `${cameraSettings.shotSize.replace(/-/g, ' ')} shot from ${cameraSettings.angle.replace(/-/g, ' ')} angle. ` +
        `${cameraSettings.depthOfField} depth of field. ` +
        `${cameraSettings.composition.replace(/-/g, ' ')} composition.`
      );

      if (cameraSettings.movement !== 'static') {
        parts.push(`${cameraSettings.movementSpeed} ${cameraSettings.movement} camera movement`);
      }
    }

    // Combine
    let prompt = parts.join('. ');
    if (prompt) {
      prompt += '. Professional cinematography, high production value, masterful composition.';
    } else {
      prompt = 'Configure visual style settings to generate a prompt.';
    }

    setGeneratedPrompt(prompt);
  };

  // Save preset
  const handleSavePreset = async () => {
    if (!presetName.trim()) {
      alert('Please enter a preset name');
      return;
    }

    setIsSaving(true);

    try {
      const response = await fetch(apiUrl('/api/style/presets'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: presetName,
          description: generatedPrompt || 'Custom visual style preset',
          style_references: styleReferences,
          color_palette: colorPalette,
          color_grading: colorGrading,
          camera_settings: cameraSettings
        })
      });

      if (!response.ok) {
        throw new Error('Failed to save preset');
      }

      const result = await response.json();

      alert(`Preset "${presetName}" saved successfully!`);
      setPresetName('');

    } catch (error) {
      console.error('Save preset error:', error);
      alert('Failed to save preset. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-4 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate(-1)}
              className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded transition"
            >
              ← Back
            </button>

            <div className="border-l border-gray-700 pl-4">
              <h1 className="text-xl font-bold text-white">Visual Style Mixer</h1>
              <p className="text-sm text-gray-400">Create and blend visual styles for your shots</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={handleGeneratePrompt}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-500 rounded-lg transition flex items-center space-x-2"
            >
              <Sparkles className="w-4 h-4" />
              <span>Generate Prompt</span>
            </button>

            <button
              onClick={handleSavePreset}
              disabled={isSaving}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg transition flex items-center space-x-2"
            >
              <Save className="w-4 h-4" />
              <span>{isSaving ? 'Saving...' : 'Save Preset'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Generated Prompt */}
        {generatedPrompt && (
          <div className="mb-8 bg-gradient-to-r from-purple-600/20 to-blue-600/20 border border-purple-500/30 rounded-lg p-6">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-5 h-5 text-purple-400" />
                <h3 className="text-lg font-bold text-white">Generated Style Prompt</h3>
              </div>
              <button
                onClick={() => navigator.clipboard.writeText(generatedPrompt)}
                className="px-3 py-1 bg-gray-800 hover:bg-gray-700 rounded text-sm transition"
              >
                Copy
              </button>
            </div>
            <p className="text-white leading-relaxed">{generatedPrompt}</p>

            {/* Preset Name Input */}
            {!presetName && (
              <div className="mt-4 flex items-center space-x-3">
                <input
                  type="text"
                  value={presetName}
                  onChange={(e) => setPresetName(e.target.value)}
                  placeholder="Enter preset name to save..."
                  className="flex-1 px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:border-purple-500 focus:outline-none"
                />
              </div>
            )}
          </div>
        )}

        {/* Components Grid */}
        <div className="space-y-8">
          {/* Style Mixer */}
          <StyleMixer
            currentStyles={styleReferences}
            onStylesChange={setStyleReferences}
            onGeneratePrompt={handleGeneratePrompt}
            onSavePreset={(name, styles) => {
              setPresetName(name);
              setStyleReferences(styles);
            }}
          />

          {/* Reference Upload */}
          <ReferenceUpload
            references={referenceImages}
            onReferencesChange={setReferenceImages}
            onAnalyze={handleAnalyzeImage}
            maxReferences={5}
          />

          {/* Color Palette & Grading */}
          <ColorPalette
            colors={colorPalette}
            grading={colorGrading}
            onColorsChange={setColorPalette}
            onGradingChange={setColorGrading}
            onSavePreset={(name, colors, grading) => {
              setPresetName(name);
              setColorPalette(colors);
              setColorGrading(grading);
            }}
          />

          {/* Camera Controls */}
          <CameraControls
            settings={cameraSettings}
            onSettingsChange={setCameraSettings}
            onSavePreset={(name, settings) => {
              setPresetName(name);
              setCameraSettings(settings);
            }}
          />
        </div>

        {/* Help Text */}
        <div className="mt-8 bg-gray-800/50 border border-gray-700 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-white mb-2">💡 How to Use Visual Style Mixer</h4>
          <div className="text-sm text-gray-400 space-y-1">
            <p>1. <strong className="text-gray-300">Add Styles</strong>: Mix cinematographers, directors, genres, and eras with custom weights</p>
            <p>2. <strong className="text-gray-300">Upload References</strong>: Add images that capture the look you want (lighting, color, composition)</p>
            <p>3. <strong className="text-gray-300">Configure Colors</strong>: Build custom color palettes or choose film-inspired presets</p>
            <p>4. <strong className="text-gray-300">Set Camera</strong>: Control focal length, aperture, framing, and camera movement</p>
            <p>5. <strong className="text-gray-300">Generate Prompt</strong>: Create a comprehensive prompt combining all elements</p>
            <p>6. <strong className="text-gray-300">Save Preset</strong>: Store your configuration for future use</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VisualStylePage;
