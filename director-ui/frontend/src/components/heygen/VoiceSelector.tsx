/**
 * Voice Selector - Browse and select HeyGen voices
 *
 * Features:
 * - List view with voice details
 * - Audio preview playback
 * - Language filter
 * - Gender filter
 * - Search by name
 */

import React, { useState, useEffect, useRef } from 'react';
import { Mic, Search, Play, Pause, Volume2, Check, Filter, Globe } from 'lucide-react';
import { Voice } from './AvatarStudio';

interface VoiceSelectorProps {
  selectedVoice: Voice | null;
  onSelectVoice: (voice: Voice) => void;
}

export default function VoiceSelector({ selectedVoice, onSelectVoice }: VoiceSelectorProps) {
  const [voices, setVoices] = useState<Voice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [languageFilter, setLanguageFilter] = useState<string | null>(null);
  const [genderFilter, setGenderFilter] = useState<string | null>(null);
  const [playingVoice, setPlayingVoice] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    fetchVoices();
  }, [languageFilter]);

  useEffect(() => {
    // Cleanup audio when component unmounts
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

  const fetchVoices = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (languageFilter) {
        params.append('language', languageFilter);
      }

      const response = await fetch(`/api/heygen/voices?${params}`);
      if (!response.ok) throw new Error('Failed to fetch voices');

      const data = await response.json();
      setVoices(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const handlePlayPreview = (voice: Voice) => {
    if (!voice.previewAudioUrl) return;

    // Stop current audio
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }

    // If clicking the same voice, just stop
    if (playingVoice === voice.id) {
      setPlayingVoice(null);
      return;
    }

    // Play new audio
    const audio = new Audio(voice.previewAudioUrl);
    audio.onended = () => setPlayingVoice(null);
    audio.onerror = () => {
      setPlayingVoice(null);
      console.error('Failed to play audio preview');
    };

    audio.play();
    audioRef.current = audio;
    setPlayingVoice(voice.id);
  };

  // Filter voices
  const filteredVoices = voices.filter(voice => {
    if (searchQuery && !voice.name.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    if (genderFilter && voice.gender !== genderFilter) {
      return false;
    }
    return true;
  });

  // Extract unique languages and genders
  const uniqueLanguages = Array.from(new Set(voices.map(v => v.language)));
  const uniqueGenders = Array.from(new Set(voices.map(v => v.gender).filter(Boolean)));

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-500">Loading voices...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <p className="text-red-600">{error}</p>
        <button
          onClick={fetchVoices}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-2">Select Voice</h2>
        <p className="text-gray-600">Choose a voice for your avatar to speak with</p>
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
              placeholder="Search voices by name..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
            />
          </div>

          {/* Language filter */}
          <div className="flex items-center gap-2">
            <Globe className="w-4 h-4 text-gray-400" />
            <select
              value={languageFilter || ''}
              onChange={(e) => setLanguageFilter(e.target.value || null)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
            >
              <option value="">All Languages</option>
              {uniqueLanguages.map(lang => (
                <option key={lang} value={lang}>{lang}</option>
              ))}
            </select>
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
        </div>

        <div className="mt-2 text-sm text-gray-500">
          Showing {filteredVoices.length} of {voices.length} voices
        </div>
      </div>

      {/* Voice list */}
      <div className="space-y-3">
        {filteredVoices.map(voice => (
          <div
            key={voice.id}
            onClick={() => onSelectVoice(voice)}
            className={`
              bg-white rounded-lg border-2 p-4 cursor-pointer transition-all
              ${selectedVoice?.id === voice.id
                ? 'border-purple-600 ring-2 ring-purple-600 ring-offset-2'
                : 'border-gray-200 hover:border-purple-400'
              }
            `}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4 flex-1">
                {/* Voice icon */}
                <div className={`
                  w-12 h-12 rounded-full flex items-center justify-center
                  ${selectedVoice?.id === voice.id ? 'bg-purple-600' : 'bg-gray-200'}
                `}>
                  {selectedVoice?.id === voice.id ? (
                    <Check className="w-6 h-6 text-white" />
                  ) : (
                    <Mic className="w-6 h-6 text-gray-600" />
                  )}
                </div>

                {/* Voice info */}
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900">{voice.name}</h3>
                  <div className="flex items-center gap-3 mt-1 text-sm text-gray-500">
                    <span className="flex items-center gap-1">
                      <Globe className="w-3 h-3" />
                      {voice.language}
                    </span>
                    {voice.gender && (
                      <span>{voice.gender}</span>
                    )}
                  </div>
                </div>

                {/* Preview button */}
                {voice.previewAudioUrl && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handlePlayPreview(voice);
                    }}
                    className={`
                      px-4 py-2 rounded-lg flex items-center gap-2 transition-colors
                      ${playingVoice === voice.id
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }
                    `}
                  >
                    {playingVoice === voice.id ? (
                      <>
                        <Pause className="w-4 h-4" />
                        Playing
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4" />
                        Preview
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredVoices.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <Volume2 className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No voices found matching your filters</p>
        </div>
      )}
    </div>
  );
}
