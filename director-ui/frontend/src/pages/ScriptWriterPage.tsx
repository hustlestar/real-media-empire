import React, { useState, useEffect } from 'react';
import { Film, Sparkles, RefreshCw, Star, Heart, MessageSquare, Clock, ChevronRight, Check } from 'lucide-react';
import { apiUrl } from '../config';

interface Generation {
  id: string;
  generation_type: string;
  version: number;
  parent_id: string | null;
  input_data: {
    idea?: string;
    subject?: string;
    action?: string;
    location?: string;
    style?: string;
    genre?: string;
  };
  output_prompt: string | null;
  output_negative_prompt: string | null;
  output_metadata: any;
  is_active: boolean;
  is_favorite: boolean;
  rating: number | null;
  ai_feedback: string | null;
  created_at: string;
}

const ScriptWriterPage: React.FC = () => {
  const [idea, setIdea] = useState('');
  const [genre, setGenre] = useState('');
  const [style, setStyle] = useState('hollywood_blockbuster');
  const [aiFeedback, setAiFeedback] = useState('');

  const [generations, setGenerations] = useState<Generation[]>([]);
  const [activeGeneration, setActiveGeneration] = useState<Generation | null>(null);
  const [selectedVersionId, setSelectedVersionId] = useState<string | null>(null);

  const [loading, setLoading] = useState(false);
  const [refining, setRefining] = useState(false);
  const [projectId, setProjectId] = useState<string>('demo-project-001');

  // Load generations for project
  const loadGenerations = async () => {
    try {
      const response = await fetch(
        apiUrl(`/api/script/${projectId}/versions?generation_type=script`)
      );
      if (!response.ok) throw new Error('Failed to load versions');

      const data = await response.json();
      setGenerations(data.generations || []);

      // Set active generation
      const active = data.generations?.find((g: Generation) => g.is_active);
      if (active) {
        setActiveGeneration(active);
        setSelectedVersionId(active.id);
      }
    } catch (error) {
      console.error('Error loading generations:', error);
    }
  };

  useEffect(() => {
    if (projectId) {
      loadGenerations();
    }
  }, [projectId]);

  // Generate script from idea
  const handleGenerateScript = async () => {
    if (!idea.trim()) return;

    setLoading(true);
    try {
      const response = await fetch(apiUrl('/api/script/generate-from-idea'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          idea,
          genre: genre || undefined,
          style,
          project_id: projectId,
          ai_feedback: aiFeedback || undefined
        })
      });

      if (!response.ok) throw new Error('Failed to generate script');

      const result = await response.json();

      // Reload generations
      await loadGenerations();

      // Clear input
      setIdea('');
      setAiFeedback('');
    } catch (error) {
      console.error('Error generating script:', error);
      alert('Error generating script. Check console for details.');
    } finally {
      setLoading(false);
    }
  };

  // Refine generation with AI feedback
  const handleRefine = async () => {
    if (!selectedVersionId || !aiFeedback.trim()) return;

    setRefining(true);
    try {
      const response = await fetch(apiUrl(`/api/script/${selectedVersionId}/refine`), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          generation_id: selectedVersionId,
          ai_feedback: aiFeedback
        })
      });

      if (!response.ok) throw new Error('Failed to refine');

      // Reload generations
      await loadGenerations();

      // Clear feedback
      setAiFeedback('');
    } catch (error) {
      console.error('Error refining:', error);
      alert('Error refining generation. Check console for details.');
    } finally {
      setRefining(false);
    }
  };

  // Switch to different version
  const handleSwitchVersion = async (generationId: string) => {
    try {
      const response = await fetch(
        apiUrl(`/api/script/generation/${generationId}/activate`),
        { method: 'PUT' }
      );

      if (!response.ok) throw new Error('Failed to activate version');

      await loadGenerations();
    } catch (error) {
      console.error('Error switching version:', error);
    }
  };

  // Toggle favorite
  const handleToggleFavorite = async (generationId: string, isFavorite: boolean) => {
    try {
      const response = await fetch(
        apiUrl(`/api/script/generation/${generationId}/favorite?is_favorite=${!isFavorite}`),
        { method: 'PUT' }
      );

      if (!response.ok) throw new Error('Failed to toggle favorite');

      await loadGenerations();
    } catch (error) {
      console.error('Error toggling favorite:', error);
    }
  };

  // Rate generation
  const handleRate = async (generationId: string, rating: number) => {
    try {
      const response = await fetch(
        apiUrl(`/api/script/generation/${generationId}/rating?rating=${rating}`),
        { method: 'PUT' }
      );

      if (!response.ok) throw new Error('Failed to rate');

      await loadGenerations();
    } catch (error) {
      console.error('Error rating:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 text-white p-8">
      <div className="max-w-7xl mx-auto">

        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-3">
            <Film className="w-10 h-10 text-purple-400" />
            <h1 className="text-4xl font-bold">AI Script Writer</h1>
          </div>
          <p className="text-gray-300">
            Generate scripts from ideas with AI. All attempts are saved - refine and iterate until perfect.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

          {/* Left Column - Generation Form */}
          <div className="lg:col-span-1 space-y-6">

            {/* New Script Generation */}
            <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-6 border border-purple-500 border-opacity-30">
              <h2 className="text-xl font-bold mb-4 flex items-center">
                <Sparkles className="w-5 h-5 mr-2 text-purple-400" />
                Generate New Script
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Your Idea</label>
                  <textarea
                    value={idea}
                    onChange={(e) => setIdea(e.target.value)}
                    placeholder="A lone astronaut discovers an ancient alien artifact on Mars..."
                    className="w-full h-32 bg-gray-900 bg-opacity-50 border border-gray-700 rounded-lg p-3 text-white placeholder-gray-500 resize-none focus:border-purple-500 focus:outline-none"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium mb-2">Genre</label>
                    <input
                      type="text"
                      value={genre}
                      onChange={(e) => setGenre(e.target.value)}
                      placeholder="Sci-Fi"
                      className="w-full bg-gray-900 bg-opacity-50 border border-gray-700 rounded-lg p-3 text-white placeholder-gray-500 focus:border-purple-500 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Style</label>
                    <select
                      value={style}
                      onChange={(e) => setStyle(e.target.value)}
                      className="w-full bg-gray-900 bg-opacity-50 border border-gray-700 rounded-lg p-3 text-white focus:border-purple-500 focus:outline-none"
                    >
                      <option value="hollywood_blockbuster">Hollywood Blockbuster</option>
                      <option value="indie_film">Indie Film</option>
                      <option value="documentary">Documentary</option>
                      <option value="noir">Film Noir</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">AI Instructions (Optional)</label>
                  <textarea
                    value={aiFeedback}
                    onChange={(e) => setAiFeedback(e.target.value)}
                    placeholder="Make it darker, add more tension, focus on character development..."
                    className="w-full h-24 bg-gray-900 bg-opacity-50 border border-gray-700 rounded-lg p-3 text-white placeholder-gray-500 resize-none focus:border-purple-500 focus:outline-none"
                  />
                </div>

                <button
                  onClick={handleGenerateScript}
                  disabled={loading || !idea.trim()}
                  className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:from-gray-600 disabled:to-gray-600 rounded-lg font-bold transition flex items-center justify-center space-x-2"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="w-5 h-5 animate-spin" />
                      <span>Generating...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5" />
                      <span>Generate Script</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Refine Current Version */}
            {activeGeneration && (
              <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-6 border border-blue-500 border-opacity-30">
                <h2 className="text-xl font-bold mb-4 flex items-center">
                  <RefreshCw className="w-5 h-5 mr-2 text-blue-400" />
                  Refine Version {activeGeneration.version}
                </h2>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Refinement Instructions</label>
                    <textarea
                      value={aiFeedback}
                      onChange={(e) => setAiFeedback(e.target.value)}
                      placeholder="Make it darker, add more tension, change the ending..."
                      className="w-full h-24 bg-gray-900 bg-opacity-50 border border-gray-700 rounded-lg p-3 text-white placeholder-gray-500 resize-none focus:border-blue-500 focus:outline-none"
                    />
                  </div>

                  <button
                    onClick={handleRefine}
                    disabled={refining || !aiFeedback.trim()}
                    className="w-full py-3 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 disabled:from-gray-600 disabled:to-gray-600 rounded-lg font-bold transition flex items-center justify-center space-x-2"
                  >
                    {refining ? (
                      <>
                        <RefreshCw className="w-5 h-5 animate-spin" />
                        <span>Refining...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-5 h-5" />
                        <span>Refine & Create New Version</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Generated Content & Version History */}
          <div className="lg:col-span-2 space-y-6">

            {/* Version Timeline */}
            {generations.length > 0 && (
              <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-6 border border-purple-500 border-opacity-30">
                <h2 className="text-xl font-bold mb-4 flex items-center">
                  <Clock className="w-5 h-5 mr-2 text-purple-400" />
                  Version History ({generations.length} attempts)
                </h2>

                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                  {generations.map((gen) => (
                    <button
                      key={gen.id}
                      onClick={() => {
                        setSelectedVersionId(gen.id);
                        setActiveGeneration(gen);
                      }}
                      className={`relative p-4 rounded-lg border-2 transition ${
                        gen.is_active
                          ? 'border-green-500 bg-green-900 bg-opacity-30'
                          : selectedVersionId === gen.id
                          ? 'border-purple-500 bg-purple-900 bg-opacity-30'
                          : 'border-gray-700 bg-gray-900 bg-opacity-30 hover:border-gray-600'
                      }`}
                    >
                      {/* Active indicator */}
                      {gen.is_active && (
                        <div className="absolute top-2 right-2">
                          <Check className="w-4 h-4 text-green-400" />
                        </div>
                      )}

                      {/* Favorite indicator */}
                      {gen.is_favorite && (
                        <div className="absolute top-2 left-2">
                          <Heart className="w-4 h-4 text-red-400 fill-current" />
                        </div>
                      )}

                      <div className="text-center">
                        <div className="text-2xl font-bold mb-1">v{gen.version}</div>
                        <div className="text-xs text-gray-400">
                          {new Date(gen.created_at).toLocaleDateString()}
                        </div>

                        {/* Rating stars */}
                        {gen.rating && (
                          <div className="flex justify-center mt-2 space-x-1">
                            {[...Array(gen.rating)].map((_, i) => (
                              <Star key={i} className="w-3 h-3 text-yellow-400 fill-current" />
                            ))}
                          </div>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Generated Content Display */}
            {activeGeneration && (
              <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-6 border border-purple-500 border-opacity-30">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold flex items-center">
                    <Film className="w-6 h-6 mr-2 text-purple-400" />
                    Version {activeGeneration.version}
                    {activeGeneration.is_active && (
                      <span className="ml-3 px-3 py-1 bg-green-500 bg-opacity-20 border border-green-500 rounded-full text-sm">
                        Active
                      </span>
                    )}
                  </h2>

                  <div className="flex space-x-2">
                    {/* Favorite toggle */}
                    <button
                      onClick={() => handleToggleFavorite(activeGeneration.id, activeGeneration.is_favorite)}
                      className={`p-2 rounded-lg transition ${
                        activeGeneration.is_favorite
                          ? 'bg-red-500 bg-opacity-20 border border-red-500'
                          : 'bg-gray-700 hover:bg-gray-600'
                      }`}
                    >
                      <Heart className={`w-5 h-5 ${activeGeneration.is_favorite ? 'text-red-400 fill-current' : 'text-gray-400'}`} />
                    </button>

                    {/* Activate button */}
                    {!activeGeneration.is_active && (
                      <button
                        onClick={() => handleSwitchVersion(activeGeneration.id)}
                        className="px-4 py-2 bg-green-600 hover:bg-green-500 rounded-lg font-semibold transition"
                      >
                        Activate This Version
                      </button>
                    )}
                  </div>
                </div>

                {/* Input Data */}
                <div className="mb-6">
                  <h3 className="text-sm font-semibold text-purple-300 mb-3">ORIGINAL IDEA</h3>
                  <div className="bg-gray-900 bg-opacity-50 rounded-lg p-4">
                    <p className="text-gray-300 leading-relaxed">
                      {activeGeneration.input_data.idea || 'No idea provided'}
                    </p>
                    <div className="mt-3 flex space-x-4 text-sm text-gray-400">
                      {activeGeneration.input_data.genre && (
                        <span>Genre: {activeGeneration.input_data.genre}</span>
                      )}
                      {activeGeneration.input_data.style && (
                        <span>Style: {activeGeneration.input_data.style.replace(/_/g, ' ')}</span>
                      )}
                    </div>
                  </div>
                </div>

                {/* AI Feedback (if this was a refinement) */}
                {activeGeneration.ai_feedback && (
                  <div className="mb-6">
                    <h3 className="text-sm font-semibold text-blue-300 mb-3">AI REFINEMENT INSTRUCTIONS</h3>
                    <div className="bg-blue-900 bg-opacity-20 border border-blue-500 rounded-lg p-4">
                      <p className="text-blue-200 italic">{activeGeneration.ai_feedback}</p>
                    </div>
                  </div>
                )}

                {/* Generated Output */}
                <div className="mb-6">
                  <h3 className="text-sm font-semibold text-purple-300 mb-3">GENERATED SCRIPT</h3>
                  <div className="bg-gray-900 bg-opacity-50 rounded-lg p-4">
                    <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">
                      {activeGeneration.output_prompt || 'No output generated yet'}
                    </p>
                  </div>
                </div>

                {/* Rating */}
                <div className="mb-6">
                  <h3 className="text-sm font-semibold text-gray-300 mb-3">RATE THIS VERSION</h3>
                  <div className="flex space-x-2">
                    {[1, 2, 3, 4, 5].map((rating) => (
                      <button
                        key={rating}
                        onClick={() => handleRate(activeGeneration.id, rating)}
                        className="transition hover:scale-110"
                      >
                        <Star
                          className={`w-8 h-8 ${
                            (activeGeneration.rating || 0) >= rating
                              ? 'text-yellow-400 fill-current'
                              : 'text-gray-600'
                          }`}
                        />
                      </button>
                    ))}
                  </div>
                </div>

                {/* Metadata */}
                {activeGeneration.output_metadata && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-300 mb-3">METADATA</h3>
                    <div className="bg-gray-900 bg-opacity-50 rounded-lg p-4">
                      <pre className="text-xs text-gray-400 overflow-auto">
                        {JSON.stringify(activeGeneration.output_metadata, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Empty State */}
            {generations.length === 0 && (
              <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-12 border border-purple-500 border-opacity-30 text-center">
                <Sparkles className="w-16 h-16 text-purple-400 mx-auto mb-4" />
                <h3 className="text-xl font-bold mb-2">No Scripts Yet</h3>
                <p className="text-gray-400 mb-6">
                  Enter your idea on the left and generate your first script with AI
                </p>
                <div className="text-sm text-gray-500">
                  All your attempts will be saved here with full version control
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScriptWriterPage;
