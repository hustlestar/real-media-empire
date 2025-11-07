/**
 * Avatar Selector - Browse and select HeyGen avatars
 *
 * Features:
 * - Grid view with avatar previews
 * - Video preview on hover
 * - Gender filter
 * - Green screen filter
 * - Search by name
 */

import React, { useState, useEffect } from 'react';
import { Video, User, Search, Play, Check, Filter } from 'lucide-react';
import { Avatar } from './AvatarStudio';

interface AvatarSelectorProps {
  selectedAvatar: Avatar | null;
  onSelectAvatar: (avatar: Avatar) => void;
}

export default function AvatarSelector({ selectedAvatar, onSelectAvatar }: AvatarSelectorProps) {
  const [avatars, setAvatars] = useState<Avatar[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [genderFilter, setGenderFilter] = useState<string | null>(null);
  const [greenScreenOnly, setGreenScreenOnly] = useState(false);
  const [hoveredAvatar, setHoveredAvatar] = useState<string | null>(null);

  useEffect(() => {
    fetchAvatars();
  }, []);

  const fetchAvatars = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/heygen/avatars');
      if (!response.ok) throw new Error('Failed to fetch avatars');

      const data = await response.json();
      setAvatars(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  // Filter avatars
  const filteredAvatars = avatars.filter(avatar => {
    if (searchQuery && !avatar.name.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    if (genderFilter && avatar.gender !== genderFilter) {
      return false;
    }
    if (greenScreenOnly && !avatar.isGreenScreen) {
      return false;
    }
    return true;
  });

  const uniqueGenders = Array.from(new Set(avatars.map(a => a.gender).filter(Boolean)));

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-500">Loading avatars...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <p className="text-red-600">{error}</p>
        <button
          onClick={fetchAvatars}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-2">Select Avatar</h2>
        <p className="text-gray-600">Choose an AI avatar to present your content</p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
        <div className="flex items-center gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search avatars by name..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
            />
          </div>

          {/* Gender filter */}
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <select
              value={genderFilter || ''}
              onChange={(e) => setGenderFilter(e.target.value || null)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
            >
              <option value="">All Genders</option>
              {uniqueGenders.map(gender => (
                <option key={gender} value={gender}>{gender}</option>
              ))}
            </select>
          </div>

          {/* Green screen filter */}
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={greenScreenOnly}
              onChange={(e) => setGreenScreenOnly(e.target.checked)}
              className="rounded border-gray-300 text-purple-600 focus:ring-purple-600"
            />
            <span className="text-sm text-gray-700">Green screen only</span>
          </label>
        </div>

        <div className="mt-2 text-sm text-gray-500">
          Showing {filteredAvatars.length} of {avatars.length} avatars
        </div>
      </div>

      {/* Avatar grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {filteredAvatars.map(avatar => (
          <div
            key={avatar.id}
            onClick={() => onSelectAvatar(avatar)}
            onMouseEnter={() => setHoveredAvatar(avatar.id)}
            onMouseLeave={() => setHoveredAvatar(null)}
            className={`
              relative bg-white rounded-lg border-2 overflow-hidden cursor-pointer transition-all
              ${selectedAvatar?.id === avatar.id
                ? 'border-purple-600 ring-2 ring-purple-600 ring-offset-2'
                : 'border-gray-200 hover:border-purple-400'
              }
            `}
          >
            {/* Selected checkmark */}
            {selectedAvatar?.id === avatar.id && (
              <div className="absolute top-2 right-2 z-10 bg-purple-600 rounded-full p-1">
                <Check className="w-4 h-4 text-white" />
              </div>
            )}

            {/* Avatar preview */}
            <div className="aspect-[3/4] bg-gray-100 relative overflow-hidden">
              {/* Image preview */}
              {avatar.previewImageUrl && (
                <img
                  src={avatar.previewImageUrl}
                  alt={avatar.name}
                  className="w-full h-full object-cover"
                />
              )}

              {/* Video preview on hover */}
              {hoveredAvatar === avatar.id && avatar.previewVideoUrl && (
                <video
                  src={avatar.previewVideoUrl}
                  autoPlay
                  loop
                  muted
                  className="absolute inset-0 w-full h-full object-cover"
                />
              )}

              {/* Play indicator */}
              {avatar.previewVideoUrl && hoveredAvatar !== avatar.id && (
                <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-0 hover:bg-opacity-20 transition-all">
                  <Play className="w-8 h-8 text-white opacity-0 hover:opacity-100 transition-opacity" />
                </div>
              )}

              {/* Green screen badge */}
              {avatar.isGreenScreen && (
                <div className="absolute bottom-2 left-2 bg-green-600 text-white text-xs px-2 py-1 rounded">
                  Green Screen
                </div>
              )}
            </div>

            {/* Avatar info */}
            <div className="p-3">
              <h3 className="font-medium text-gray-900 truncate">{avatar.name}</h3>
              <div className="flex items-center gap-2 mt-1 text-sm text-gray-500">
                <User className="w-3 h-3" />
                <span>{avatar.gender || 'Unknown'}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredAvatars.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <Video className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No avatars found matching your filters</p>
        </div>
      )}
    </div>
  );
}
