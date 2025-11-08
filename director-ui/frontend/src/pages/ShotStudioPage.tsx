import React, { useState, useEffect } from 'react';
import { apiUrl } from '../config/api';
import AIEnhancer from '../components/AIEnhancer';
import {
  Sparkles,
  Video,
  RefreshCw,
  Star,
  Check,
  Clock,
  Camera,
  Lightbulb,
  Heart,
  Play,
  Wand2
} from 'lucide-react';

interface ShotVersion {
  id: string;
  version: number;
  parent_id: string | null;
  prompt: string;
  negative_prompt: string | null;
  shot_type: string | null;
  camera_motion: string | null;
  lighting: string | null;
  emotion: string | null;
  duration_seconds: number;
  input_subject: string | null;
  input_action: string | null;
  input_location: string | null;
  ai_feedback: string | null;
  is_active: boolean;
  is_favorite: boolean;
  rating: number | null;
  created_at: string;
}

interface ShotFormData {
  subject: string;
  action: string;
  location: string;
  camera_motion: string;
  shot_type: string;
  lighting: string;
  emotion: string;
  style: string;
  duration_seconds: number;
  ai_feedback: string;
}

export default function ShotStudioPage() {
  const [formData, setFormData] = useState<ShotFormData>({
    subject: '',
    action: '',
    location: '',
    camera_motion: 'static',
    shot_type: 'medium',
    lighting: 'natural',
    emotion: 'neutral',
    style: 'cinematic',
    duration_seconds: 3.0,
    ai_feedback: ''
  });

  const [versions, setVersions] = useState<ShotVersion[]>([]);
  const [selectedVersionId, setSelectedVersionId] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isRefining, setIsRefining] = useState(false);
  const [showRefinementBox, setShowRefinementBox] = useState(false);
  const [refinementFeedback, setRefinementFeedback] = useState('');

  // Load all versions on mount
  useEffect(() => {
    loadVersions();
  }, []);

  // Load form data when version is selected
  useEffect(() => {
    if (selectedVersionId) {
      const selected = versions.find(v => v.id === selectedVersionId);
      if (selected) {
        setFormData({
          subject: selected.input_subject || '',
          action: selected.input_action || '',
          location: selected.input_location || '',
          camera_motion: selected.camera_motion || 'static',
          shot_type: selected.shot_type || 'medium',
          lighting: selected.lighting || 'natural',
          emotion: selected.emotion || 'neutral',
          style: 'cinematic',
          duration_seconds: selected.duration_seconds,
          ai_feedback: selected.ai_feedback || ''
        });
      }
    }
  }, [selectedVersionId, versions]);

  const loadVersions = async () => {
    try {
      const response = await fetch(apiUrl('/api/script/shot/versions'));
      if (response.ok) {
        const data = await response.json();
        setVersions(data.versions || []);
        if (data.active_version_id) {
          setSelectedVersionId(data.active_version_id);
        }
      }
    } catch (error) {
      console.error('Failed to load versions:', error);
    }
  };

  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      const response = await fetch(apiUrl('/api/script/shot/generate'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subject: formData.subject || null,
          action: formData.action || null,
          location: formData.location || null,
          camera_motion: formData.camera_motion,
          shot_type: formData.shot_type,
          lighting: formData.lighting,
          emotion: formData.emotion,
          style: formData.style,
          duration_seconds: formData.duration_seconds,
          ai_feedback: formData.ai_feedback || null
        })
      });

      if (response.ok) {
        const newShot = await response.json();
        await loadVersions();
        setSelectedVersionId(newShot.id);
      } else {
        const error = await response.json();
        alert(`Generation failed: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Generation error:', error);
      alert('Failed to generate shot. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRefine = async () => {
    if (!selectedVersionId || !refinementFeedback.trim()) {
      alert('Please select a version and provide refinement feedback');
      return;
    }

    setIsRefining(true);
    try {
      const response = await fetch(apiUrl(`/api/script/shot/${selectedVersionId}/refine`), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          shot_id: selectedVersionId,
          ai_feedback: refinementFeedback
        })
      });

      if (response.ok) {
        const refinedShot = await response.json();
        await loadVersions();
        setSelectedVersionId(refinedShot.id);
        setRefinementFeedback('');
        setShowRefinementBox(false);
      } else {
        const error = await response.json();
        alert(`Refinement failed: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Refinement error:', error);
      alert('Failed to refine shot. Please try again.');
    } finally {
      setIsRefining(false);
    }
  };

  const handleActivate = async (versionId: string) => {
    try {
      const response = await fetch(apiUrl(`/api/script/shot/${versionId}/activate`), {
        method: 'PUT'
      });

      if (response.ok) {
        await loadVersions();
        setSelectedVersionId(versionId);
      }
    } catch (error) {
      console.error('Activation error:', error);
    }
  };

  const handleToggleFavorite = async (versionId: string) => {
    try {
      const response = await fetch(apiUrl(`/api/script/shot/${versionId}/favorite`), {
        method: 'PUT'
      });

      if (response.ok) {
        await loadVersions();
      }
    } catch (error) {
      console.error('Favorite toggle error:', error);
    }
  };

  const handleRate = async (versionId: string, rating: number) => {
    try {
      const response = await fetch(apiUrl(`/api/script/shot/${versionId}/rating`), {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rating })
      });

      if (response.ok) {
        await loadVersions();
      }
    } catch (error) {
      console.error('Rating error:', error);
    }
  };

  const selectedVersion = versions.find(v => v.id === selectedVersionId);

  const shotTypes = [
    'extreme-close-up', 'close-up', 'medium-close-up', 'medium',
    'medium-wide', 'wide', 'extreme-wide', 'establishing'
  ];

  const cameraMotions = [
    'static', 'pan-left', 'pan-right', 'tilt-up', 'tilt-down',
    'dolly-in', 'dolly-out', 'truck-left', 'truck-right',
    'crane-up', 'crane-down', 'handheld', 'steadicam', 'drone'
  ];

  const lightingOptions = [
    'natural', 'golden-hour', 'blue-hour', 'harsh-sunlight',
    'soft-diffused', 'dramatic', 'low-key', 'high-key',
    'backlit', 'silhouette', 'neon', 'firelight', 'moonlight'
  ];

  const emotionOptions = [
    'neutral', 'happy', 'sad', 'angry', 'fearful', 'surprised',
    'contemplative', 'energetic', 'serene', 'tense', 'mysterious', 'hopeful'
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900 text-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl">
              <Video className="w-8 h-8" />
            </div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              Shot Studio
            </h1>
          </div>
          <p className="text-gray-400">
            AI-powered shot generation with version control
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Shot Input Form */}
          <div className="lg:col-span-2 space-y-6">
            {/* Quick Generation Card */}
            <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6 shadow-xl">
              <div className="flex items-center gap-2 mb-6">
                <Wand2 className="w-5 h-5 text-purple-400" />
                <h2 className="text-xl font-semibold">Shot Details</h2>
              </div>

              <div className="space-y-4">
                {/* Subject with AI */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Subject / Character
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={formData.subject}
                      onChange={(e) => handleChange('subject', e.target.value)}
                      placeholder="e.g., A young woman in her 30s with red hair"
                      className="flex-1 px-4 py-2 bg-gray-900/50 border border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                    <AIEnhancer
                      fieldName="subject"
                      fieldLabel="Subject / Character"
                      formData={formData}
                      onUpdate={handleChange}
                      enhancementPrompt="Generate a detailed character description including age, appearance, clothing, and character traits suitable for film production."
                      variant="compact"
                    />
                  </div>
                </div>

                {/* Action with AI */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Action / What's Happening
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={formData.action}
                      onChange={(e) => handleChange('action', e.target.value)}
                      placeholder="e.g., Walking through a busy street, looking at phone"
                      className="flex-1 px-4 py-2 bg-gray-900/50 border border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                    <AIEnhancer
                      fieldName="action"
                      fieldLabel="Action"
                      formData={formData}
                      onUpdate={handleChange}
                      enhancementPrompt="Generate a detailed action description with movement, gestures, and visual details suitable for film direction."
                      variant="compact"
                    />
                  </div>
                </div>

                {/* Location with AI */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Location / Setting
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={formData.location}
                      onChange={(e) => handleChange('location', e.target.value)}
                      placeholder="e.g., Downtown city street at sunset"
                      className="flex-1 px-4 py-2 bg-gray-900/50 border border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                    <AIEnhancer
                      fieldName="location"
                      fieldLabel="Location / Setting"
                      formData={formData}
                      onUpdate={handleChange}
                      enhancementPrompt="Generate a detailed location description including environment, atmosphere, time of day, and visual elements."
                      variant="compact"
                    />
                  </div>
                </div>

                {/* Technical Settings Grid */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      <Camera className="w-4 h-4 inline mr-1" />
                      Shot Type
                    </label>
                    <select
                      value={formData.shot_type}
                      onChange={(e) => handleChange('shot_type', e.target.value)}
                      className="w-full px-4 py-2 bg-gray-900/50 border border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    >
                      {shotTypes.map(type => (
                        <option key={type} value={type}>
                          {type.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      <Video className="w-4 h-4 inline mr-1" />
                      Camera Motion
                    </label>
                    <select
                      value={formData.camera_motion}
                      onChange={(e) => handleChange('camera_motion', e.target.value)}
                      className="w-full px-4 py-2 bg-gray-900/50 border border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    >
                      {cameraMotions.map(motion => (
                        <option key={motion} value={motion}>
                          {motion.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      <Lightbulb className="w-4 h-4 inline mr-1" />
                      Lighting
                    </label>
                    <select
                      value={formData.lighting}
                      onChange={(e) => handleChange('lighting', e.target.value)}
                      className="w-full px-4 py-2 bg-gray-900/50 border border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    >
                      {lightingOptions.map(light => (
                        <option key={light} value={light}>
                          {light.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      <Heart className="w-4 h-4 inline mr-1" />
                      Emotion / Mood
                    </label>
                    <select
                      value={formData.emotion}
                      onChange={(e) => handleChange('emotion', e.target.value)}
                      className="w-full px-4 py-2 bg-gray-900/50 border border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    >
                      {emotionOptions.map(emotion => (
                        <option key={emotion} value={emotion}>
                          {emotion.charAt(0).toUpperCase() + emotion.slice(1)}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Duration */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    <Clock className="w-4 h-4 inline mr-1" />
                    Duration (seconds)
                  </label>
                  <input
                    type="number"
                    value={formData.duration_seconds}
                    onChange={(e) => handleChange('duration_seconds', parseFloat(e.target.value))}
                    min="1"
                    max="30"
                    step="0.5"
                    className="w-full px-4 py-2 bg-gray-900/50 border border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>

                {/* Generate Button */}
                <button
                  onClick={handleGenerate}
                  disabled={isGenerating}
                  className="w-full py-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 disabled:from-gray-600 disabled:to-gray-600 rounded-lg font-semibold transition-all duration-200 flex items-center justify-center gap-2 shadow-lg hover:shadow-purple-500/50"
                >
                  {isGenerating ? (
                    <>
                      <RefreshCw className="w-5 h-5 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5" />
                      Generate Shot
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Current Shot Preview */}
            {selectedVersion && (
              <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6 shadow-xl">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Play className="w-5 h-5 text-green-400" />
                    <h2 className="text-xl font-semibold">
                      Current Shot (v{selectedVersion.version})
                    </h2>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleToggleFavorite(selectedVersion.id)}
                      className={`p-2 rounded-lg transition-colors ${
                        selectedVersion.is_favorite
                          ? 'bg-pink-500 text-white'
                          : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                      }`}
                    >
                      <Star className="w-4 h-4" fill={selectedVersion.is_favorite ? 'currentColor' : 'none'} />
                    </button>
                  </div>
                </div>

                {/* Prompt Display */}
                <div className="bg-gray-900/50 rounded-lg p-4 mb-4">
                  <div className="text-sm font-medium text-gray-400 mb-2">Generated Prompt:</div>
                  <div className="text-gray-200">{selectedVersion.prompt}</div>
                </div>

                {/* Rating */}
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-sm text-gray-400">Rate this shot:</span>
                  {[1, 2, 3, 4, 5].map((rating) => (
                    <button
                      key={rating}
                      onClick={() => handleRate(selectedVersion.id, rating)}
                      className="transition-transform hover:scale-110"
                    >
                      <Star
                        className={`w-5 h-5 ${
                          selectedVersion.rating && rating <= selectedVersion.rating
                            ? 'text-yellow-400 fill-yellow-400'
                            : 'text-gray-600'
                        }`}
                      />
                    </button>
                  ))}
                </div>

                {/* Refinement Section */}
                <div>
                  {!showRefinementBox ? (
                    <button
                      onClick={() => setShowRefinementBox(true)}
                      className="w-full py-2 bg-gray-700 hover:bg-gray-600 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                    >
                      <RefreshCw className="w-4 h-4" />
                      Refine with AI
                    </button>
                  ) : (
                    <div className="space-y-3">
                      <textarea
                        value={refinementFeedback}
                        onChange={(e) => setRefinementFeedback(e.target.value)}
                        placeholder="Describe how to improve this shot... (e.g., 'Make it more dramatic', 'Add more detail to the subject', 'Change lighting to golden hour')"
                        className="w-full px-4 py-3 bg-gray-900/50 border border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                        rows={3}
                      />
                      <div className="flex gap-2">
                        <button
                          onClick={handleRefine}
                          disabled={isRefining || !refinementFeedback.trim()}
                          className="flex-1 py-2 bg-purple-500 hover:bg-purple-600 disabled:bg-gray-600 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                        >
                          {isRefining ? (
                            <>
                              <RefreshCw className="w-4 h-4 animate-spin" />
                              Refining...
                            </>
                          ) : (
                            <>
                              <Sparkles className="w-4 h-4" />
                              Apply Refinement
                            </>
                          )}
                        </button>
                        <button
                          onClick={() => {
                            setShowRefinementBox(false);
                            setRefinementFeedback('');
                          }}
                          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg font-medium transition-colors"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Right: Version History */}
          <div className="lg:col-span-1">
            <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6 shadow-xl sticky top-4">
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <Clock className="w-5 h-5 text-purple-400" />
                Version History
              </h2>

              {versions.length === 0 ? (
                <div className="text-center py-12 text-gray-400">
                  <Video className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>No shots yet</p>
                  <p className="text-sm mt-1">Generate your first shot!</p>
                </div>
              ) : (
                <div className="space-y-2 max-h-[calc(100vh-200px)] overflow-y-auto pr-2">
                  {versions.map((version) => (
                    <div
                      key={version.id}
                      onClick={() => setSelectedVersionId(version.id)}
                      className={`p-4 rounded-lg border-2 cursor-pointer transition-all duration-200 ${
                        version.id === selectedVersionId
                          ? 'border-purple-500 bg-purple-500/10'
                          : 'border-gray-700 bg-gray-900/30 hover:border-gray-600'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-lg">v{version.version}</span>
                          {version.is_active && (
                            <span className="px-2 py-0.5 bg-green-500 text-xs rounded-full flex items-center gap-1">
                              <Check className="w-3 h-3" />
                              Active
                            </span>
                          )}
                          {version.is_favorite && (
                            <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                          )}
                        </div>
                        {version.rating && (
                          <div className="flex items-center gap-1">
                            <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                            <span className="text-sm text-yellow-400">{version.rating}</span>
                          </div>
                        )}
                      </div>

                      <div className="text-xs text-gray-400 mb-2">
                        {new Date(version.created_at).toLocaleString()}
                      </div>

                      {version.prompt && (
                        <div className="text-sm text-gray-300 line-clamp-2">
                          {version.prompt}
                        </div>
                      )}

                      {!version.is_active && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleActivate(version.id);
                          }}
                          className="mt-3 w-full py-1.5 bg-gray-700 hover:bg-gray-600 rounded text-sm font-medium transition-colors"
                        >
                          Activate
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
