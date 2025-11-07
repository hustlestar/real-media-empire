import React, { useState } from 'react';
import { Volume2, VolumeX, Lock, Unlock, Eye, EyeOff, MoreVertical } from 'lucide-react';
import TimelineClip, { Clip } from './TimelineClip';

export interface Track {
  id: string;
  type: 'video' | 'audio' | 'text';
  name: string;
  clips: Clip[];
  volume: number;      // 0-1
  muted: boolean;
  locked: boolean;
  visible: boolean;
  color?: string;
}

interface TimelineTrackProps {
  track: Track;
  timelineWidth: number;
  duration: number;
  selectedClipId: string | null;
  zoom: number;
  onClipSelect: (clipId: string) => void;
  onClipMove?: (clipId: string, newStartTime: number) => void;
  onClipTrimStart?: (clipId: string, newStartTime: number, newDuration: number) => void;
  onClipTrimEnd?: (clipId: string, newDuration: number) => void;
  onClipDoubleClick?: (clipId: string) => void;
  onTrackVolumeChange?: (trackId: string, volume: number) => void;
  onTrackMuteToggle?: (trackId: string) => void;
  onTrackLockToggle?: (trackId: string) => void;
  onTrackVisibilityToggle?: (trackId: string) => void;
}

const TimelineTrack: React.FC<TimelineTrackProps> = ({
  track,
  timelineWidth,
  duration,
  selectedClipId,
  zoom,
  onClipSelect,
  onClipMove,
  onClipTrimStart,
  onClipTrimEnd,
  onClipDoubleClick,
  onTrackVolumeChange,
  onTrackMuteToggle,
  onTrackLockToggle,
  onTrackVisibilityToggle
}) => {
  const [showVolumeSlider, setShowVolumeSlider] = useState(false);

  // Handle volume change
  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value);
    onTrackVolumeChange?.(track.id, newVolume);
  };

  // Get track background color
  const getTrackBgColor = () => {
    if (!track.visible) return 'bg-gray-800/50';
    return track.locked ? 'bg-gray-900/80' : 'bg-gray-900';
  };

  return (
    <div className="flex border-b border-gray-700">
      {/* Track Header */}
      <div className="w-40 bg-gray-800 border-r border-gray-700 px-3 py-2 flex-shrink-0 flex flex-col justify-between">
        {/* Track Name and Type */}
        <div>
          <div className="text-sm font-semibold truncate text-white">{track.name}</div>
          <div className="text-xs text-gray-400 capitalize">{track.type}</div>
        </div>

        {/* Track Controls */}
        <div className="flex items-center justify-between mt-2">
          <div className="flex items-center space-x-1">
            {/* Visibility Toggle */}
            <button
              onClick={() => onTrackVisibilityToggle?.(track.id)}
              className={`p-1 rounded transition ${
                track.visible ? 'hover:bg-gray-700 text-gray-400' : 'bg-gray-700 text-gray-500'
              }`}
              title={track.visible ? 'Hide track' : 'Show track'}
            >
              {track.visible ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
            </button>

            {/* Lock Toggle */}
            <button
              onClick={() => onTrackLockToggle?.(track.id)}
              className={`p-1 rounded transition ${
                track.locked ? 'bg-red-600/20 text-red-400' : 'hover:bg-gray-700 text-gray-400'
              }`}
              title={track.locked ? 'Unlock track' : 'Lock track'}
            >
              {track.locked ? <Lock className="w-4 h-4" /> : <Unlock className="w-4 h-4" />}
            </button>

            {/* Mute Toggle (for audio tracks) */}
            {(track.type === 'audio' || track.type === 'video') && (
              <button
                onClick={() => onTrackMuteToggle?.(track.id)}
                className={`p-1 rounded transition ${
                  track.muted ? 'bg-yellow-600/20 text-yellow-400' : 'hover:bg-gray-700 text-gray-400'
                }`}
                title={track.muted ? 'Unmute' : 'Mute'}
              >
                {track.muted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
              </button>
            )}
          </div>

          {/* More Options */}
          <button className="p-1 hover:bg-gray-700 rounded transition text-gray-400">
            <MoreVertical className="w-4 h-4" />
          </button>
        </div>

        {/* Volume Slider (for audio/video tracks) */}
        {(track.type === 'audio' || track.type === 'video') && !track.muted && (
          <div className="mt-2">
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={track.volume}
              onChange={handleVolumeChange}
              className="w-full h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
            />
            <div className="text-xs text-gray-500 text-center mt-1">
              {Math.round(track.volume * 100)}%
            </div>
          </div>
        )}
      </div>

      {/* Track Timeline Area */}
      <div className={`flex-1 h-20 ${getTrackBgColor()} relative`}>
        {/* Render clips */}
        {track.clips.map(clip => (
          <TimelineClip
            key={clip.id}
            clip={clip}
            timelineWidth={timelineWidth}
            duration={duration}
            isSelected={selectedClipId === clip.id}
            zoom={zoom}
            onSelect={onClipSelect}
            onMove={onClipMove}
            onTrimStart={onClipTrimStart}
            onTrimEnd={onClipTrimEnd}
            onDoubleClick={onClipDoubleClick}
          />
        ))}

        {/* Drop zone indicator (when dragging clips) */}
        {track.clips.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center text-gray-600 text-xs">
            Drop clips here
          </div>
        )}
      </div>
    </div>
  );
};

export default TimelineTrack;
