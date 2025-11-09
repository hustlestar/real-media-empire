import React, { useState, useEffect } from 'react';
import { apiUrl } from '../config/api';
import {
  Film,
  Briefcase,
  Grid,
  List,
  Star,
  Clock,
  Camera,
  GripVertical,
  Play,
  Copy
} from 'lucide-react';

interface Shot {
  id: string;
  workspace_id: string | null;
  film_id: string | null;
  sequence_order: number | null;
  version: number;
  prompt: string;
  shot_type: string | null;
  camera_motion: string | null;
  lighting: string | null;
  emotion: string | null;
  duration_seconds: number;
  is_active: boolean;
  is_favorite: boolean;
  rating: number | null;
  created_at: string;
}

interface Film {
  id: string;
  name: string;
  description: string;
  workspace_id: string;
}

interface Workspace {
  id: string;
  name: string;
  slug: string;
}

export default function StoryboardPage() {
  const [shots, setShots] = useState<Shot[]>([]);
  const [films, setFilms] = useState<Film[]>([]);
  const [selectedFilmId, setSelectedFilmId] = useState<string>('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadFilms();
  }, []);

  useEffect(() => {
    if (selectedFilmId) {
      loadShots();
    }
  }, [selectedFilmId]);

  const loadFilms = async () => {
    try {
      const response = await fetch(apiUrl('/api/workspaces/projects'));
      if (response.ok) {
        const data = await response.json();
        setFilms(data.projects || []);
      }
    } catch (error) {
      console.error('Failed to load films:', error);
    }
  };

  const loadShots = async () => {
    if (!selectedFilmId) return;

    setIsLoading(true);
    try {
      const response = await fetch(apiUrl(`/api/storyboard/shots/by-film/${selectedFilmId}`));
      if (response.ok) {
        const data = await response.json();
        setShots(data);
      }
    } catch (error) {
      console.error('Failed to load shots:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDragStart = (index: number) => {
    setDraggedIndex(index);
  };

  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault();

    if (draggedIndex === null || draggedIndex === index) return;

    const newShots = [...shots];
    const draggedShot = newShots[draggedIndex];

    // Remove from old position
    newShots.splice(draggedIndex, 1);
    // Insert at new position
    newShots.splice(index, 0, draggedShot);

    setShots(newShots);
    setDraggedIndex(index);
  };

  const handleDragEnd = async () => {
    if (draggedIndex === null) return;

    // Update sequence orders based on new positions
    const updates = shots.map((shot, index) => ({
      shot_id: shot.id,
      sequence_order: index + 1
    }));

    try {
      const response = await fetch(apiUrl('/api/storyboard/shots/batch-sequence'), {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ updates })
      });

      if (response.ok) {
        // Reload to get fresh data
        await loadShots();
      }
    } catch (error) {
      console.error('Failed to update sequence:', error);
    }

    setDraggedIndex(null);
  };

  const copyToClipboard = (shot: Shot) => {
    const text = `Shot: ${shot.prompt}\nType: ${shot.shot_type || 'N/A'}\nCamera: ${shot.camera_motion || 'N/A'}\nLighting: ${shot.lighting || 'N/A'}\nEmotion: ${shot.emotion || 'N/A'}`;
    navigator.clipboard.writeText(text);
    alert('Shot details copied to clipboard!');
  };

  const selectedFilm = films.find(f => f.id === selectedFilmId);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900/20 to-gray-900 text-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl">
                <Grid className="w-8 h-8" />
              </div>
              <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  Storyboard
                </h1>
                <p className="text-gray-400">Organize and sequence your shots</p>
              </div>
            </div>

            {/* View Toggle */}
            <div className="flex gap-2 bg-gray-800 rounded-lg p-1">
              <button
                onClick={() => setViewMode('grid')}
                className={`px-4 py-2 rounded-md transition-colors ${
                  viewMode === 'grid' ? 'bg-purple-600 text-white' : 'text-gray-400 hover:text-white'
                }`}
              >
                <Grid className="w-5 h-5" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`px-4 py-2 rounded-md transition-colors ${
                  viewMode === 'list' ? 'bg-purple-600 text-white' : 'text-gray-400 hover:text-white'
                }`}
              >
                <List className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Film Selector */}
          <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6">
            <label className="block text-sm font-medium text-gray-300 mb-3 flex items-center gap-2">
              <Film className="w-4 h-4 text-blue-400" />
              Select Film/Project
            </label>
            <select
              value={selectedFilmId}
              onChange={(e) => setSelectedFilmId(e.target.value)}
              className="w-full px-4 py-3 bg-gray-900/50 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
            >
              <option value="">-- Choose a Film --</option>
              {films.map(film => (
                <option key={film.id} value={film.id}>
                  {film.name} {film.description && `- ${film.description.substring(0, 50)}...`}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Shots Display */}
        {selectedFilmId && (
          <div>
            {/* Stats Bar */}
            <div className="mb-6 flex items-center gap-4 text-sm text-gray-400">
              <div className="flex items-center gap-2">
                <Camera className="w-4 h-4" />
                <span>{shots.length} shots</span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                <span>{shots.reduce((sum, s) => sum + s.duration_seconds, 0).toFixed(1)}s total</span>
              </div>
              <div className="flex items-center gap-2">
                <Star className="w-4 h-4" />
                <span>{shots.filter(s => s.is_favorite).length} favorites</span>
              </div>
            </div>

            {isLoading ? (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
                <p className="mt-4 text-gray-400">Loading shots...</p>
              </div>
            ) : shots.length === 0 ? (
              <div className="text-center py-12 bg-gray-800/30 rounded-xl border border-gray-700">
                <Camera className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                <p className="text-xl text-gray-400">No shots in this film yet</p>
                <p className="text-sm text-gray-500 mt-2">Create shots in Shot Studio and link them to this film</p>
              </div>
            ) : (
              <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4' : 'space-y-3'}>
                {shots.map((shot, index) => (
                  <div
                    key={shot.id}
                    draggable
                    onDragStart={() => handleDragStart(index)}
                    onDragOver={(e) => handleDragOver(e, index)}
                    onDragEnd={handleDragEnd}
                    className={`bg-gray-800/50 backdrop-blur-sm border-2 rounded-xl p-4 transition-all duration-200 cursor-move hover:border-blue-500 ${
                      draggedIndex === index ? 'opacity-50 scale-95' : 'opacity-100'
                    } ${shot.is_favorite ? 'border-yellow-500' : 'border-gray-700'}`}
                  >
                    {/* Shot Number & Controls */}
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <GripVertical className="w-4 h-4 text-gray-500" />
                        <span className="font-bold text-lg">
                          #{(shot.sequence_order !== null && shot.sequence_order !== undefined) ? shot.sequence_order : index + 1}
                        </span>
                        {shot.is_favorite && <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />}
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => copyToClipboard(shot)}
                          className="p-1.5 bg-gray-700 hover:bg-gray-600 rounded-md transition-colors"
                          title="Copy shot details"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                        {shot.rating && (
                          <div className="flex items-center gap-1 px-2 py-1 bg-gray-700 rounded-md">
                            <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                            <span className="text-xs">{shot.rating}</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Prompt */}
                    <div className="mb-3">
                      <p className="text-sm text-gray-300 line-clamp-3">{shot.prompt}</p>
                    </div>

                    {/* Technical Details */}
                    <div className="space-y-2 text-xs">
                      {shot.shot_type && (
                        <div className="flex items-center gap-2">
                          <Camera className="w-3 h-3 text-blue-400" />
                          <span className="text-gray-400">{shot.shot_type}</span>
                        </div>
                      )}
                      {shot.camera_motion && (
                        <div className="flex items-center gap-2">
                          <Play className="w-3 h-3 text-green-400" />
                          <span className="text-gray-400">{shot.camera_motion}</span>
                        </div>
                      )}
                      {shot.lighting && (
                        <div className="flex items-center gap-2">
                          <span className="w-3 h-3 flex items-center justify-center">💡</span>
                          <span className="text-gray-400">{shot.lighting}</span>
                        </div>
                      )}
                      <div className="flex items-center gap-2">
                        <Clock className="w-3 h-3 text-purple-400" />
                        <span className="text-gray-400">{shot.duration_seconds}s</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {!selectedFilmId && (
          <div className="text-center py-16">
            <Film className="w-20 h-20 mx-auto mb-4 text-gray-600" />
            <p className="text-xl text-gray-400">Select a film to view its storyboard</p>
          </div>
        )}
      </div>
    </div>
  );
}
