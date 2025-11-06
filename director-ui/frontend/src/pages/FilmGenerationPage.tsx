import React, { useState } from 'react';
import { PlayCircle, Film, Sparkles, Save, Download, Zap } from 'lucide-react';
import StyleSelector from '../components/film/StyleSelector';
import ShotTypeSelector from '../components/film/ShotTypeSelector';
import LightingSelector from '../components/film/LightingSelector';
import EmotionSelector from '../components/film/EmotionSelector';
import PromptBuilder from '../components/film/PromptBuilder';
import SceneSequencer from '../components/film/SceneSequencer';
import PromptPreview from '../components/film/PromptPreview';
import { apiUrl } from '../config/api';

interface PromptConfig {
  subject: string;
  action: string;
  location: string;
  style: string;
  shotType: string;
  lighting: string;
  emotion: string;
  additionalDetails: string;
  characterConsistency: string;
  cameraMotion: string;
}

const FilmGenerationPage: React.FC = () => {
  const [mode, setMode] = useState<'single' | 'scene'>('single');
  const [aiEnhance, setAiEnhance] = useState<boolean>(false);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [promptConfig, setPromptConfig] = useState<PromptConfig>({
    subject: '',
    action: '',
    location: '',
    style: 'hollywood_blockbuster',
    shotType: 'medium_shot',
    lighting: 'three_point_studio',
    emotion: 'contemplation_reflection',
    additionalDetails: '',
    characterConsistency: '',
    cameraMotion: ''
  });

  const [generatedPrompt, setGeneratedPrompt] = useState<any>(null);
  const [sceneShots, setSceneShots] = useState<any[]>([]);

  const handleGenerateSingleShot = async () => {
    try {
      setIsGenerating(true);
      const response = await fetch(apiUrl('/api/film/generate-shot'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...promptConfig,
          aiEnhance
        })
      });
      const result = await response.json();
      setGeneratedPrompt(result);
    } catch (error) {
      console.error('Error generating shot:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleGenerateScene = async () => {
    try {
      setIsGenerating(true);
      const response = await fetch(apiUrl('/api/film/generate-scene'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scene_description: promptConfig.action,
          characters: promptConfig.subject.split(',').map(s => s.trim()),
          location: promptConfig.location,
          num_shots: 5,
          style: promptConfig.style,
          pacing: 'medium',
          aiEnhance
        })
      });
      const result = await response.json();
      setSceneShots(result.shots);
    } catch (error) {
      console.error('Error generating scene:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-black text-white">
      {/* Header */}
      <header className="bg-black bg-opacity-50 backdrop-blur-md border-b border-purple-500">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Film className="w-8 h-8 text-purple-400" />
              <h1 className="text-2xl font-bold">Film Generation Studio</h1>
              <span className="px-3 py-1 bg-purple-500 bg-opacity-20 rounded-full text-sm">
                Professional Cinematic Prompts
              </span>
            </div>

            <div className="flex items-center space-x-4">
              <button className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition flex items-center space-x-2">
                <Save className="w-4 h-4" />
                <span>Save Project</span>
              </button>

              <button className="px-4 py-2 bg-purple-600 hover:bg-purple-500 rounded-lg transition flex items-center space-x-2">
                <Download className="w-4 h-4" />
                <span>Export</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        {/* Mode Selector */}
        <div className="mb-8">
          <div className="flex space-x-4 bg-black bg-opacity-30 p-2 rounded-lg inline-flex">
            <button
              onClick={() => setMode('single')}
              className={`px-6 py-3 rounded-lg transition ${
                mode === 'single'
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <div className="flex items-center space-x-2">
                <Sparkles className="w-5 h-5" />
                <span>Single Shot</span>
              </div>
            </button>

            <button
              onClick={() => setMode('scene')}
              className={`px-6 py-3 rounded-lg transition ${
                mode === 'scene'
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <div className="flex items-center space-x-2">
                <Film className="w-5 h-5" />
                <span>Complete Scene</span>
              </div>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Panel - Configuration */}
          <div className="lg:col-span-2 space-y-6">
            {/* Prompt Builder */}
            <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-6 border border-purple-500 border-opacity-30">
              <h2 className="text-xl font-bold mb-4 flex items-center space-x-2">
                <Sparkles className="w-6 h-6 text-purple-400" />
                <span>Prompt Configuration</span>
              </h2>

              <PromptBuilder
                config={promptConfig}
                onChange={setPromptConfig}
              />
            </div>

            {/* Style Selection */}
            <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-6 border border-purple-500 border-opacity-30">
              <h2 className="text-xl font-bold mb-4">Cinematic Style</h2>
              <StyleSelector
                selected={promptConfig.style}
                onSelect={(style) => setPromptConfig({ ...promptConfig, style })}
              />
            </div>

            {/* Shot Type & Camera */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-6 border border-purple-500 border-opacity-30">
                <h2 className="text-lg font-bold mb-4">Shot Type</h2>
                <ShotTypeSelector
                  selected={promptConfig.shotType}
                  onSelect={(shotType) => setPromptConfig({ ...promptConfig, shotType })}
                />
              </div>

              <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-6 border border-purple-500 border-opacity-30">
                <h2 className="text-lg font-bold mb-4">Lighting Setup</h2>
                <LightingSelector
                  selected={promptConfig.lighting}
                  onSelect={(lighting) => setPromptConfig({ ...promptConfig, lighting })}
                />
              </div>
            </div>

            {/* Emotion */}
            <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-6 border border-purple-500 border-opacity-30">
              <h2 className="text-xl font-bold mb-4">Emotional Beat</h2>
              <EmotionSelector
                selected={promptConfig.emotion}
                onSelect={(emotion) => setPromptConfig({ ...promptConfig, emotion })}
              />
            </div>

            {/* AI Enhancement Toggle */}
            <div className="bg-gradient-to-r from-purple-900 to-pink-900 bg-opacity-30 backdrop-blur-md rounded-xl p-6 border border-purple-400 border-opacity-50">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <Zap className="w-5 h-5 text-yellow-400" />
                    <h3 className="font-bold text-lg">AI Enhancement</h3>
                    <span className="px-2 py-0.5 bg-yellow-500 bg-opacity-20 text-yellow-300 text-xs rounded-full">
                      GPT-4
                    </span>
                  </div>
                  <p className="text-sm text-gray-300">
                    Use AI to enhance prompts with even more cinematic detail, visual poetry, and professional polish.
                    Adds 20-40% more depth and specificity.
                  </p>
                </div>

                <label className="relative inline-flex items-center cursor-pointer ml-4">
                  <input
                    type="checkbox"
                    checked={aiEnhance}
                    onChange={(e) => setAiEnhance(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-14 h-8 bg-gray-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-1 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-gradient-to-r peer-checked:from-purple-600 peer-checked:to-pink-600"></div>
                </label>
              </div>

              {aiEnhance && (
                <div className="mt-4 bg-yellow-900 bg-opacity-20 border border-yellow-600 border-opacity-30 rounded-lg p-3">
                  <div className="flex items-start space-x-2 text-xs text-yellow-200">
                    <Zap className="w-4 h-4 mt-0.5 flex-shrink-0" />
                    <div>
                      <div className="font-semibold mb-1">AI Enhancement Active</div>
                      <div className="text-yellow-300 opacity-80">
                        Prompts will be processed through GPT-4 to add cinematic depth, sensory details,
                        and professional directorial language. This may take a few extra seconds.
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Generate Button */}
            <button
              onClick={mode === 'single' ? handleGenerateSingleShot : handleGenerateScene}
              disabled={isGenerating}
              className={`w-full py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 rounded-xl font-bold text-lg transition flex items-center justify-center space-x-3 ${
                isGenerating ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              {isGenerating ? (
                <>
                  <div className="w-6 h-6 border-4 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>{aiEnhance ? 'Generating & Enhancing...' : 'Generating...'}</span>
                </>
              ) : (
                <>
                  <PlayCircle className="w-6 h-6" />
                  <span>{mode === 'single' ? 'Generate Shot Prompt' : 'Generate Scene Sequence'}</span>
                  {aiEnhance && <Zap className="w-5 h-5 text-yellow-300" />}
                </>
              )}
            </button>
          </div>

          {/* Right Panel - Preview */}
          <div className="space-y-6">
            {mode === 'single' && generatedPrompt && (
              <PromptPreview prompt={generatedPrompt} />
            )}

            {mode === 'scene' && sceneShots.length > 0 && (
              <SceneSequencer shots={sceneShots} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default FilmGenerationPage;
