import React, { useState, useEffect } from 'react';
import { PlayCircle, Film, Sparkles, Save, Download, Zap, Users, Upload, Camera, Grid } from 'lucide-react';
import StyleSelector from '../components/film/StyleSelector';
import ShotTypeSelector from '../components/film/ShotTypeSelector';
import LightingSelector from '../components/film/LightingSelector';
import EmotionSelector from '../components/film/EmotionSelector';
import PromptBuilder from '../components/film/PromptBuilder';
import SceneSequencer from '../components/film/SceneSequencer';
import PromptPreview from '../components/film/PromptPreview';
import CharacterPickerModal from '../components/CharacterPickerModal';
import WorkspaceSelector from '../components/WorkspaceSelector';
import { useWorkspace } from '../contexts/WorkspaceContext';
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
  selectedCharacters: any[];
}

const FilmGenerationPage: React.FC = () => {
  const { currentWorkspace } = useWorkspace();
  const [mode, setMode] = useState<'single' | 'scene'>('single');
  const [aiEnhance, setAiEnhance] = useState<boolean>(false);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [isPublishing, setIsPublishing] = useState<boolean>(false);
  const [showCharacterPicker, setShowCharacterPicker] = useState<boolean>(false);
  const [currentFilmProjectId, setCurrentFilmProjectId] = useState<string | null>(null);
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
    cameraMotion: '',
    selectedCharacters: []
  });

  const [generatedPrompt, setGeneratedPrompt] = useState<any>(null);
  const [sceneShots, setSceneShots] = useState<any[]>([]);
  const [availableShots, setAvailableShots] = useState<any[]>([]);
  const [selectedShots, setSelectedShots] = useState<any[]>([]);
  const [showShotSelector, setShowShotSelector] = useState<boolean>(false);

  // Load available shots when workspace changes
  useEffect(() => {
    if (currentWorkspace) {
      loadAvailableShots();
    }
  }, [currentWorkspace]);

  const loadAvailableShots = async () => {
    if (!currentWorkspace) return;

    try {
      const response = await fetch(apiUrl(`/api/storyboard/shots/by-workspace/${currentWorkspace.id}`));
      if (response.ok) {
        const shots = await response.json();
        setAvailableShots(shots);
      }
    } catch (error) {
      console.error('Failed to load shots:', error);
    }
  };

  const handleShotSelect = (shot: any) => {
    // Check if shot is already selected
    if (selectedShots.find(s => s.id === shot.id)) {
      return;
    }

    // Add shot to selection
    setSelectedShots([...selectedShots, shot]);

    // Pre-populate prompt config from shot metadata
    setPromptConfig({
      ...promptConfig,
      subject: shot.input_subject || promptConfig.subject,
      action: shot.input_action || promptConfig.action,
      location: shot.input_location || promptConfig.location,
      shotType: shot.shot_type || promptConfig.shotType,
      lighting: shot.lighting || promptConfig.lighting,
      emotion: shot.emotion || promptConfig.emotion,
      cameraMotion: shot.camera_motion || promptConfig.cameraMotion
    });

    setShowShotSelector(false);
  };

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

  const handlePublish = async () => {
    if (!currentFilmProjectId) {
      alert('Please generate a film first before publishing');
      return;
    }

    if (!currentWorkspace) {
      alert('Please select a workspace first');
      return;
    }

    try {
      setIsPublishing(true);

      // For now, this is a placeholder - would need actual video path
      // In production, this would be called after film generation completes
      const response = await fetch(apiUrl('/api/publishing/publish/immediate'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          account_id: 'default', // Would come from account selector
          platforms: ['tiktok', 'instagram'], // Would come from platform selector
          video_path: '/path/to/generated/video.mp4', // Would be actual film output
          title: promptConfig.subject,
          description: promptConfig.action,
          film_project_id: currentFilmProjectId,
          film_variant_id: null // Could specify variant if platform-specific
        })
      });

      if (response.ok) {
        alert('Successfully published to selected platforms!');
      } else {
        throw new Error('Publishing failed');
      }
    } catch (error) {
      console.error('Error publishing:', error);
      alert('Failed to publish. Please try again.');
    } finally {
      setIsPublishing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-black text-white">
      {/* Header */}
      <header className="bg-black bg-opacity-50 backdrop-blur-md border-b border-purple-500">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Film className="w-8 h-8 text-purple-400" />
              <h1 className="text-2xl font-bold">Film Generation Studio</h1>
              <span className="px-3 py-1 bg-purple-500 bg-opacity-20 rounded-full text-sm">
                Professional Cinematic Prompts
              </span>
              <WorkspaceSelector />
            </div>

            <div className="flex items-center space-x-3">
              <button className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition flex items-center space-x-2">
                <Save className="w-4 h-4" />
                <span>Save Project</span>
              </button>

              <button
                onClick={handlePublish}
                disabled={!currentFilmProjectId || isPublishing}
                className="px-4 py-2 bg-green-600 hover:bg-green-500 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg transition flex items-center space-x-2"
              >
                <Upload className="w-4 h-4" />
                <span>{isPublishing ? 'Publishing...' : 'Publish'}</span>
              </button>

              <button className="px-4 py-2 bg-purple-600 hover:bg-purple-500 rounded-lg transition flex items-center space-x-2">
                <Download className="w-4 h-4" />
                <span>Export</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8 max-w-screen-2xl">
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

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          {/* Left Panel - Configuration */}
          <div className="xl:col-span-2 space-y-6">
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

              {/* Character Selection */}
              <div className="mt-6 pt-6 border-t border-purple-500 border-opacity-30">
                <h3 className="text-lg font-semibold mb-3 flex items-center space-x-2">
                  <Users className="w-5 h-5 text-purple-400" />
                  <span>Characters</span>
                </h3>

                {promptConfig.selectedCharacters.length > 0 ? (
                  <div className="space-y-2">
                    {promptConfig.selectedCharacters.map((char: any, idx: number) => (
                      <div key={idx} className="flex items-center justify-between p-3 bg-purple-900 bg-opacity-30 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className="w-12 h-12 bg-gray-700 rounded-full flex items-center justify-center">
                            {char.reference_images && char.reference_images[0] ? (
                              <img src={char.reference_images[0]} alt={char.name} className="w-full h-full rounded-full object-cover" />
                            ) : (
                              <User className="w-6 h-6 text-gray-400" />
                            )}
                          </div>
                          <div>
                            <div className="font-semibold">{char.name}</div>
                            <div className="text-sm text-gray-400">{char.description}</div>
                          </div>
                        </div>
                        <button
                          onClick={() => {
                            setPromptConfig({
                              ...promptConfig,
                              selectedCharacters: promptConfig.selectedCharacters.filter((_, i) => i !== idx)
                            });
                          }}
                          className="px-3 py-1 bg-red-600 bg-opacity-50 hover:bg-opacity-70 rounded text-sm"
                        >
                          Remove
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-6 text-gray-400 bg-gray-900 bg-opacity-30 rounded-lg">
                    <Users className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>No characters selected</p>
                    <p className="text-sm mt-1">Add characters for consistent visual identity</p>
                  </div>
                )}

                <button
                  onClick={() => setShowCharacterPicker(true)}
                  className="mt-4 w-full px-4 py-3 bg-purple-600 hover:bg-purple-500 rounded-lg font-semibold flex items-center justify-center space-x-2"
                >
                  <Users className="w-5 h-5" />
                  <span>Add Character</span>
                </button>
              </div>
            </div>

            {/* Character Picker Modal */}
            {showCharacterPicker && (
              <CharacterPickerModal
                isOpen={showCharacterPicker}
                onClose={() => setShowCharacterPicker(false)}
                onSelect={(character) => {
                  setPromptConfig({
                    ...promptConfig,
                    selectedCharacters: [...promptConfig.selectedCharacters, character],
                    characterConsistency: character.consistency_prompt,
                    subject: character.name
                  });
                  setShowCharacterPicker(false);
                }}
                title="Select Character for Film"
              />
            )}

            {/* Shot Selection from Shot Studio */}
            <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-6 border border-purple-500 border-opacity-30">
              <h3 className="text-lg font-semibold mb-3 flex items-center space-x-2">
                <Camera className="w-5 h-5 text-purple-400" />
                <span>Shots from Shot Studio</span>
              </h3>

              {selectedShots.length > 0 ? (
                <div className="space-y-2">
                  {selectedShots.map((shot: any, idx: number) => (
                    <div key={shot.id} className="p-3 bg-purple-900 bg-opacity-30 rounded-lg border border-purple-500 border-opacity-30">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <div className="font-semibold text-sm">Shot #{shot.sequence_order || idx + 1} - v{shot.version}</div>
                          <div className="text-xs text-gray-400 mt-1">
                            {shot.shot_type && <span className="mr-2">📷 {shot.shot_type}</span>}
                            {shot.camera_motion && <span className="mr-2">🎬 {shot.camera_motion}</span>}
                            {shot.duration_seconds && <span>⏱️ {shot.duration_seconds}s</span>}
                          </div>
                        </div>
                        <button
                          onClick={() => {
                            setSelectedShots(selectedShots.filter((_, i) => i !== idx));
                          }}
                          className="px-2 py-1 bg-red-600 bg-opacity-50 hover:bg-opacity-70 rounded text-xs"
                        >
                          Remove
                        </button>
                      </div>
                      <div className="text-sm text-gray-300 line-clamp-2">
                        {shot.prompt}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-6 text-gray-400 bg-gray-900 bg-opacity-30 rounded-lg">
                  <Camera className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>No shots selected</p>
                  <p className="text-sm mt-1">Add shots from your Shot Studio library</p>
                </div>
              )}

              <button
                onClick={() => setShowShotSelector(true)}
                className="mt-4 w-full px-4 py-3 bg-purple-600 hover:bg-purple-500 rounded-lg font-semibold flex items-center justify-center space-x-2"
              >
                <Grid className="w-5 h-5" />
                <span>Browse Shots ({availableShots.length} available)</span>
              </button>
            </div>

            {/* Shot Selector Modal */}
            {showShotSelector && (
              <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-75 backdrop-blur-sm">
                <div className="bg-gray-900 rounded-xl shadow-2xl border border-purple-500 max-w-4xl w-full max-h-[80vh] overflow-hidden">
                  <div className="p-6 border-b border-purple-500 border-opacity-30">
                    <div className="flex items-center justify-between">
                      <h2 className="text-2xl font-bold flex items-center space-x-2">
                        <Camera className="w-6 h-6 text-purple-400" />
                        <span>Select Shot from Shot Studio</span>
                      </h2>
                      <button
                        onClick={() => setShowShotSelector(false)}
                        className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition"
                      >
                        Close
                      </button>
                    </div>
                  </div>

                  <div className="p-6 overflow-y-auto max-h-[60vh]">
                    {availableShots.length === 0 ? (
                      <div className="text-center py-12 text-gray-400">
                        <Camera className="w-16 h-16 mx-auto mb-4 opacity-50" />
                        <p className="text-lg">No shots available in this workspace</p>
                        <p className="text-sm mt-2">Create shots in Shot Studio first</p>
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {availableShots.map((shot: any) => (
                          <div
                            key={shot.id}
                            onClick={() => handleShotSelect(shot)}
                            className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                              selectedShots.find(s => s.id === shot.id)
                                ? 'border-purple-500 bg-purple-900 bg-opacity-30'
                                : 'border-gray-700 bg-gray-800 bg-opacity-50 hover:border-purple-400'
                            }`}
                          >
                            <div className="flex items-center justify-between mb-2">
                              <div className="flex items-center gap-2">
                                <span className="font-bold">#{shot.sequence_order || '?'}</span>
                                <span className="text-sm text-gray-400">v{shot.version}</span>
                                {shot.is_favorite && (
                                  <span className="text-yellow-400">⭐</span>
                                )}
                              </div>
                              {shot.duration_seconds && (
                                <span className="text-xs text-gray-400">{shot.duration_seconds}s</span>
                              )}
                            </div>

                            <div className="text-sm text-gray-300 mb-3 line-clamp-3">
                              {shot.prompt}
                            </div>

                            <div className="flex flex-wrap gap-1">
                              {shot.shot_type && (
                                <span className="px-2 py-1 bg-blue-900 bg-opacity-50 text-blue-300 text-xs rounded">
                                  {shot.shot_type}
                                </span>
                              )}
                              {shot.camera_motion && (
                                <span className="px-2 py-1 bg-green-900 bg-opacity-50 text-green-300 text-xs rounded">
                                  {shot.camera_motion}
                                </span>
                              )}
                              {shot.lighting && (
                                <span className="px-2 py-1 bg-yellow-900 bg-opacity-50 text-yellow-300 text-xs rounded">
                                  {shot.lighting}
                                </span>
                              )}
                              {shot.emotion && (
                                <span className="px-2 py-1 bg-pink-900 bg-opacity-50 text-pink-300 text-xs rounded">
                                  {shot.emotion}
                                </span>
                              )}
                            </div>

                            {selectedShots.find(s => s.id === shot.id) && (
                              <div className="mt-3 text-center text-sm text-purple-300 font-semibold">
                                ✓ Selected
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

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
