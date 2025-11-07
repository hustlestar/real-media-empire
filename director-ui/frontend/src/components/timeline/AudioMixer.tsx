import React, { useState, useRef, useEffect } from 'react';
import { Volume2, VolumeX, Volume1, TrendingUp, TrendingDown, Minus, Plus, X } from 'lucide-react';

export interface VolumeKeyframe {
  time: number;      // Time in seconds
  volume: number;    // 0-1
}

export interface AudioTrackConfig {
  id: string;
  name: string;
  type: 'music' | 'dialogue' | 'sfx' | 'ambient';
  volume: number;          // Master volume 0-1
  muted: boolean;
  solo: boolean;
  volumeEnvelope: VolumeKeyframe[];
  ducking?: {
    enabled: boolean;
    targetTrackId: string; // Which track triggers ducking
    amount: number;        // 0-1, how much to reduce volume
    fadeTime: number;      // Fade in/out time in seconds
  };
}

interface AudioMixerProps {
  tracks: AudioTrackConfig[];
  duration: number;
  currentTime: number;
  onTrackUpdate: (trackId: string, config: Partial<AudioTrackConfig>) => void;
  onClose?: () => void;
}

const AudioMixer: React.FC<AudioMixerProps> = ({
  tracks,
  duration,
  currentTime,
  onTrackUpdate,
  onClose
}) => {
  const [selectedTrackId, setSelectedTrackId] = useState<string | null>(tracks[0]?.id || null);
  const [showEnvelopeEditor, setShowEnvelopeEditor] = useState(false);

  const selectedTrack = tracks.find(t => t.id === selectedTrackId);

  // Handle master volume change
  const handleVolumeChange = (trackId: string, volume: number) => {
    onTrackUpdate(trackId, { volume });
  };

  // Handle mute toggle
  const handleMuteToggle = (trackId: string) => {
    const track = tracks.find(t => t.id === trackId);
    if (track) {
      onTrackUpdate(trackId, { muted: !track.muted });
    }
  };

  // Handle solo toggle
  const handleSoloToggle = (trackId: string) => {
    const track = tracks.find(t => t.id === trackId);
    if (track) {
      onTrackUpdate(trackId, { solo: !track.solo });
    }
  };

  // Add volume keyframe at current time
  const handleAddKeyframe = () => {
    if (!selectedTrack) return;

    const newKeyframe: VolumeKeyframe = {
      time: currentTime,
      volume: selectedTrack.volume
    };

    const updatedEnvelope = [...selectedTrack.volumeEnvelope, newKeyframe].sort((a, b) => a.time - b.time);

    onTrackUpdate(selectedTrack.id, { volumeEnvelope: updatedEnvelope });
  };

  // Remove keyframe
  const handleRemoveKeyframe = (index: number) => {
    if (!selectedTrack) return;

    const updatedEnvelope = selectedTrack.volumeEnvelope.filter((_, i) => i !== index);
    onTrackUpdate(selectedTrack.id, { volumeEnvelope: updatedEnvelope });
  };

  // Get track icon
  const getTrackIcon = (type: string) => {
    switch (type) {
      case 'music':
        return '🎵';
      case 'dialogue':
        return '💬';
      case 'sfx':
        return '🔊';
      case 'ambient':
        return '🌊';
      default:
        return '🎧';
    }
  };

  // Calculate current volume based on envelope
  const getCurrentVolumeFromEnvelope = (track: AudioTrackConfig): number => {
    if (track.volumeEnvelope.length === 0) return track.volume;

    // Find keyframes before and after current time
    const before = track.volumeEnvelope.filter(kf => kf.time <= currentTime).sort((a, b) => b.time - a.time)[0];
    const after = track.volumeEnvelope.filter(kf => kf.time > currentTime).sort((a, b) => a.time - b.time)[0];

    if (!before) return after?.volume || track.volume;
    if (!after) return before.volume;

    // Linear interpolation between keyframes
    const t = (currentTime - before.time) / (after.time - before.time);
    return before.volume + (after.volume - before.volume) * t;
  };

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6 max-w-4xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-bold text-white">Audio Mixer</h3>
          <p className="text-sm text-gray-400">Mix and balance audio tracks</p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-700 rounded transition text-gray-400"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Mixer Channels */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {tracks.map(track => {
          const currentVolume = getCurrentVolumeFromEnvelope(track);
          const isSolo = tracks.some(t => t.solo);
          const isAudible = !track.muted && (!isSolo || track.solo);

          return (
            <div
              key={track.id}
              className={`bg-gray-900 rounded-lg p-4 border-2 transition-all ${
                selectedTrackId === track.id
                  ? 'border-blue-500'
                  : 'border-gray-700 hover:border-gray-600'
              }`}
              onClick={() => setSelectedTrackId(track.id)}
            >
              {/* Track Header */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <span className="text-xl">{getTrackIcon(track.type)}</span>
                  <div>
                    <div className="text-sm font-semibold text-white truncate">{track.name}</div>
                    <div className="text-xs text-gray-500 capitalize">{track.type}</div>
                  </div>
                </div>
              </div>

              {/* Volume Fader */}
              <div className="flex flex-col items-center mb-4">
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={track.volume}
                  onChange={(e) => handleVolumeChange(track.id, parseFloat(e.target.value))}
                  className="w-full h-32 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-blue-600 vertical-slider"
                  style={{ writingMode: 'bt-lr', WebkitAppearance: 'slider-vertical' }}
                />
                <div className="mt-2 text-sm font-mono text-white">
                  {Math.round(currentVolume * 100)}%
                </div>
              </div>

              {/* Level Meter */}
              <div className="h-2 bg-gray-800 rounded-full overflow-hidden mb-3">
                <div
                  className={`h-full rounded-full transition-all ${
                    isAudible
                      ? currentVolume > 0.8
                        ? 'bg-red-500'
                        : currentVolume > 0.6
                        ? 'bg-yellow-500'
                        : 'bg-green-500'
                      : 'bg-gray-700'
                  }`}
                  style={{ width: `${currentVolume * 100}%` }}
                ></div>
              </div>

              {/* Controls */}
              <div className="space-y-2">
                {/* Mute */}
                <button
                  onClick={() => handleMuteToggle(track.id)}
                  className={`w-full px-3 py-2 rounded text-sm transition-all ${
                    track.muted
                      ? 'bg-red-600 text-white'
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                  }`}
                >
                  {track.muted ? <VolumeX className="w-4 h-4 inline mr-1" /> : <Volume2 className="w-4 h-4 inline mr-1" />}
                  {track.muted ? 'Muted' : 'Mute'}
                </button>

                {/* Solo */}
                <button
                  onClick={() => handleSoloToggle(track.id)}
                  className={`w-full px-3 py-2 rounded text-sm transition-all ${
                    track.solo
                      ? 'bg-yellow-600 text-white'
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                  }`}
                >
                  Solo
                </button>
              </div>

              {/* Envelope Indicator */}
              {track.volumeEnvelope.length > 0 && (
                <div className="mt-2 text-xs text-blue-400 text-center">
                  {track.volumeEnvelope.length} keyframes
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Selected Track Details */}
      {selectedTrack && (
        <div className="bg-gray-900 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-sm font-semibold text-white">
              {selectedTrack.name} - Advanced Controls
            </h4>
            <button
              onClick={() => setShowEnvelopeEditor(!showEnvelopeEditor)}
              className="px-3 py-1 bg-blue-600 hover:bg-blue-500 rounded text-sm text-white transition"
            >
              {showEnvelopeEditor ? 'Hide' : 'Show'} Envelope
            </button>
          </div>

          {/* Volume Envelope Editor */}
          {showEnvelopeEditor && (
            <div className="mb-4">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm text-gray-400">Volume Automation</span>
                <button
                  onClick={handleAddKeyframe}
                  className="px-3 py-1 bg-gray-800 hover:bg-gray-700 rounded text-sm text-gray-300 transition"
                >
                  <Plus className="w-4 h-4 inline mr-1" />
                  Add Keyframe at {currentTime.toFixed(2)}s
                </button>
              </div>

              {/* Envelope Graph */}
              <div className="bg-gray-800 rounded p-4 h-32 relative">
                {/* Grid lines */}
                <div className="absolute inset-0 flex flex-col justify-between p-4 pointer-events-none">
                  {[0, 0.25, 0.5, 0.75, 1].map(level => (
                    <div key={level} className="w-full h-px bg-gray-700"></div>
                  ))}
                </div>

                {/* Envelope line */}
                {selectedTrack.volumeEnvelope.length > 0 && (
                  <svg className="absolute inset-0 w-full h-full" preserveAspectRatio="none">
                    <polyline
                      points={selectedTrack.volumeEnvelope
                        .map(kf => `${(kf.time / duration) * 100},${(1 - kf.volume) * 100}`)
                        .join(' ')}
                      fill="none"
                      stroke="#3b82f6"
                      strokeWidth="2"
                    />
                  </svg>
                )}

                {/* Keyframe points */}
                {selectedTrack.volumeEnvelope.map((kf, idx) => (
                  <div
                    key={idx}
                    className="absolute w-3 h-3 bg-blue-500 rounded-full cursor-pointer hover:bg-blue-400 group"
                    style={{
                      left: `${(kf.time / duration) * 100}%`,
                      top: `${(1 - kf.volume) * 100}%`,
                      transform: 'translate(-50%, -50%)'
                    }}
                    onClick={() => handleRemoveKeyframe(idx)}
                  >
                    <div className="hidden group-hover:block absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 rounded text-xs text-white whitespace-nowrap">
                      {kf.time.toFixed(2)}s, {Math.round(kf.volume * 100)}%
                      <br />
                      <span className="text-red-400">Click to remove</span>
                    </div>
                  </div>
                ))}

                {/* Current time indicator */}
                <div
                  className="absolute top-0 bottom-0 w-px bg-red-500"
                  style={{ left: `${(currentTime / duration) * 100}%` }}
                ></div>
              </div>

              {/* Keyframe List */}
              {selectedTrack.volumeEnvelope.length > 0 && (
                <div className="mt-3 space-y-1 max-h-32 overflow-y-auto">
                  {selectedTrack.volumeEnvelope.map((kf, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between bg-gray-800 rounded px-3 py-2 text-sm"
                    >
                      <span className="text-gray-400">
                        Keyframe {idx + 1}: {kf.time.toFixed(2)}s
                      </span>
                      <span className="text-white">{Math.round(kf.volume * 100)}%</span>
                      <button
                        onClick={() => handleRemoveKeyframe(idx)}
                        className="p-1 hover:bg-gray-700 rounded transition text-red-400"
                      >
                        <Minus className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Audio Ducking */}
          <div className="mt-4 pt-4 border-t border-gray-700">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-semibold text-gray-300">Audio Ducking</span>
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedTrack.ducking?.enabled || false}
                  onChange={(e) =>
                    onTrackUpdate(selectedTrack.id, {
                      ducking: {
                        ...(selectedTrack.ducking || { targetTrackId: '', amount: 0.5, fadeTime: 0.2 }),
                        enabled: e.target.checked
                      }
                    })
                  }
                  className="w-4 h-4 accent-blue-600"
                />
                <span className="text-sm text-gray-400">Enable</span>
              </label>
            </div>

            {selectedTrack.ducking?.enabled && (
              <div className="space-y-3">
                <div>
                  <label className="block text-xs text-gray-400 mb-1">Duck when this track plays:</label>
                  <select
                    value={selectedTrack.ducking.targetTrackId}
                    onChange={(e) =>
                      onTrackUpdate(selectedTrack.id, {
                        ducking: { ...selectedTrack.ducking!, targetTrackId: e.target.value }
                      })
                    }
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white text-sm"
                  >
                    <option value="">Select track...</option>
                    {tracks
                      .filter(t => t.id !== selectedTrack.id)
                      .map(t => (
                        <option key={t.id} value={t.id}>
                          {t.name}
                        </option>
                      ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs text-gray-400 mb-1">
                    Ducking Amount: {Math.round((selectedTrack.ducking.amount || 0.5) * 100)}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={selectedTrack.ducking.amount || 0.5}
                    onChange={(e) =>
                      onTrackUpdate(selectedTrack.id, {
                        ducking: { ...selectedTrack.ducking!, amount: parseFloat(e.target.value) }
                      })
                    }
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
                  />
                </div>

                <div>
                  <label className="block text-xs text-gray-400 mb-1">
                    Fade Time: {(selectedTrack.ducking.fadeTime || 0.2).toFixed(1)}s
                  </label>
                  <input
                    type="range"
                    min="0.1"
                    max="2"
                    step="0.1"
                    value={selectedTrack.ducking.fadeTime || 0.2}
                    onChange={(e) =>
                      onTrackUpdate(selectedTrack.id, {
                        ducking: { ...selectedTrack.ducking!, fadeTime: parseFloat(e.target.value) }
                      })
                    }
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Master Output */}
      <div className="mt-6 bg-blue-600/10 border border-blue-600/30 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm font-semibold text-white">Master Output</div>
            <div className="text-xs text-gray-400">Final mix level</div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="w-64 h-3 bg-gray-800 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-green-500 via-yellow-500 to-red-500" style={{ width: '75%' }}></div>
            </div>
            <span className="text-lg font-bold text-white">-6 dB</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AudioMixer;
