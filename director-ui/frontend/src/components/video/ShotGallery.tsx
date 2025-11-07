import React, { useState, useEffect } from 'react';
import { Play, CheckCircle, XCircle, Clock, AlertCircle, RefreshCw, Trash2, Eye } from 'lucide-react';
import { apiUrl } from '../../config/api';

export interface Shot {
  id: string;
  shot_id: string;
  film_project_id: string;
  video_url: string;
  thumbnail_url?: string;
  image_url?: string;
  audio_url?: string;
  prompt: string;
  duration: number;
  status: 'pending' | 'generating' | 'completed' | 'approved' | 'rejected' | 'needs_revision';
  created_at: string;
  updated_at: string;
  review?: {
    status: string;
    notes?: string;
    reviewer?: string;
    reviewed_at?: string;
  };
}

interface ShotGalleryProps {
  filmProjectId?: string;
  onShotSelect?: (shot: Shot) => void;
  selectedShotId?: string;
  viewMode?: 'grid' | 'list';
}

const ShotGallery: React.FC<ShotGalleryProps> = ({
  filmProjectId,
  onShotSelect,
  selectedShotId,
  viewMode = 'grid'
}) => {
  const [shots, setShots] = useState<Shot[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    fetchShots();
  }, [filmProjectId]);

  const fetchShots = async () => {
    try {
      setLoading(true);
      const url = filmProjectId
        ? apiUrl(`/api/film/projects/${filmProjectId}/shots`)
        : apiUrl('/api/film/shots');
      const response = await fetch(url);
      const data = await response.json();
      setShots(data.shots || []);
    } catch (error) {
      console.error('Error fetching shots:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredShots = shots.filter(shot => {
    if (filter === 'all') return true;
    if (filter === 'review') return shot.status === 'completed';
    if (filter === 'approved') return shot.status === 'approved';
    if (filter === 'rejected') return shot.status === 'rejected';
    return true;
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'rejected':
        return <XCircle className="w-5 h-5 text-red-400" />;
      case 'needs_revision':
        return <AlertCircle className="w-5 h-5 text-yellow-400" />;
      case 'generating':
        return <RefreshCw className="w-5 h-5 text-blue-400 animate-spin" />;
      case 'completed':
        return <Clock className="w-5 h-5 text-purple-400" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'bg-green-500/20 border-green-500 text-green-300';
      case 'rejected':
        return 'bg-red-500/20 border-red-500 text-red-300';
      case 'needs_revision':
        return 'bg-yellow-500/20 border-yellow-500 text-yellow-300';
      case 'generating':
        return 'bg-blue-500/20 border-blue-500 text-blue-300';
      case 'completed':
        return 'bg-purple-500/20 border-purple-500 text-purple-300';
      default:
        return 'bg-gray-500/20 border-gray-500 text-gray-300';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <span className="ml-4 text-gray-400">Loading shots...</span>
      </div>
    );
  }

  if (shots.length === 0) {
    return (
      <div className="text-center py-20 text-gray-400">
        <Play className="w-16 h-16 mx-auto mb-4 opacity-50" />
        <p>No shots generated yet</p>
        <p className="text-sm mt-2">Generate your first shot to see it here</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filter Bar */}
      <div className="flex items-center justify-between bg-gray-800 rounded-lg p-4">
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-400">Filter:</span>
          <div className="flex space-x-2">
            {['all', 'review', 'approved', 'rejected'].map(filterOption => (
              <button
                key={filterOption}
                onClick={() => setFilter(filterOption)}
                className={`px-3 py-1 rounded-lg text-sm transition ${
                  filter === filterOption
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {filterOption.charAt(0).toUpperCase() + filterOption.slice(1)}
              </button>
            ))}
          </div>
        </div>
        <div className="text-sm text-gray-400">
          {filteredShots.length} shot{filteredShots.length !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Gallery Grid */}
      {viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filteredShots.map(shot => (
            <div
              key={shot.id}
              onClick={() => onShotSelect?.(shot)}
              className={`relative group cursor-pointer rounded-lg overflow-hidden bg-gray-800 border-2 transition-all ${
                selectedShotId === shot.id
                  ? 'border-blue-500 ring-2 ring-blue-500/50'
                  : 'border-gray-700 hover:border-gray-600'
              }`}
            >
              {/* Thumbnail */}
              <div className="relative aspect-video bg-gray-900">
                {shot.thumbnail_url || shot.image_url ? (
                  <img
                    src={shot.thumbnail_url || shot.image_url}
                    alt={shot.shot_id}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <Play className="w-12 h-12 text-gray-600" />
                  </div>
                )}

                {/* Play Overlay */}
                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <Play className="w-12 h-12 text-white" />
                </div>

                {/* Status Badge */}
                <div className="absolute top-2 right-2">
                  <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs border ${getStatusColor(shot.status)}`}>
                    {getStatusIcon(shot.status)}
                    <span className="capitalize">{shot.status}</span>
                  </div>
                </div>

                {/* Duration */}
                <div className="absolute bottom-2 right-2 bg-black/80 px-2 py-1 rounded text-xs text-white">
                  {shot.duration}s
                </div>
              </div>

              {/* Info */}
              <div className="p-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-white truncate">{shot.shot_id}</h3>
                    <p className="text-xs text-gray-400 line-clamp-2 mt-1">{shot.prompt}</p>
                  </div>
                </div>

                {shot.review?.notes && (
                  <div className="mt-2 p-2 bg-gray-900 rounded text-xs text-gray-400">
                    <p className="line-clamp-2">{shot.review.notes}</p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* List View */
        <div className="space-y-2">
          {filteredShots.map(shot => (
            <div
              key={shot.id}
              onClick={() => onShotSelect?.(shot)}
              className={`flex items-center p-4 rounded-lg bg-gray-800 border-2 cursor-pointer transition-all ${
                selectedShotId === shot.id
                  ? 'border-blue-500 ring-2 ring-blue-500/50'
                  : 'border-gray-700 hover:border-gray-600'
              }`}
            >
              {/* Thumbnail */}
              <div className="relative w-32 h-18 bg-gray-900 rounded overflow-hidden flex-shrink-0">
                {shot.thumbnail_url || shot.image_url ? (
                  <img
                    src={shot.thumbnail_url || shot.image_url}
                    alt={shot.shot_id}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <Play className="w-8 h-8 text-gray-600" />
                  </div>
                )}
              </div>

              {/* Info */}
              <div className="flex-1 ml-4 min-w-0">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-white">{shot.shot_id}</h3>
                    <p className="text-sm text-gray-400 line-clamp-1 mt-1">{shot.prompt}</p>
                  </div>
                  <div className="flex items-center space-x-2 ml-4">
                    <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs border ${getStatusColor(shot.status)}`}>
                      {getStatusIcon(shot.status)}
                      <span className="capitalize">{shot.status}</span>
                    </div>
                    <span className="text-xs text-gray-400">{shot.duration}s</span>
                  </div>
                </div>

                {shot.review?.notes && (
                  <div className="mt-2 p-2 bg-gray-900 rounded text-xs text-gray-400">
                    {shot.review.notes}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ShotGallery;
