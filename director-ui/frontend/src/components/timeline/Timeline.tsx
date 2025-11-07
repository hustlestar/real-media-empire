import React, { useState, useRef, useEffect } from 'react';
import { ZoomIn, ZoomOut, Play, Pause, SkipBack, SkipForward } from 'lucide-react';

export interface TimelineClip {
  id: string;
  trackId: string;
  startTime: number;
  duration: number;
  type: 'video' | 'audio' | 'text' | 'image';
  name: string;
  thumbnailUrl?: string;
  audioUrl?: string;
  color?: string;
  trimIn?: number;  // Trim start offset
  trimOut?: number; // Trim end offset
}

export interface TimelineTrack {
  id: string;
  type: 'video' | 'audio' | 'text';
  name: string;
  clips: TimelineClip[];
  volume?: number;
  muted?: boolean;
  locked?: boolean;
}

interface TimelineProps {
  tracks: TimelineTrack[];
  duration: number; // Total timeline duration in seconds
  currentTime: number;
  onTimeChange?: (time: number) => void;
  onClipMove?: (clipId: string, newStartTime: number, newTrackId: string) => void;
  onClipResize?: (clipId: string, newStartTime: number, newDuration: number) => void;
  onClipSelect?: (clipId: string) => void;
  onPlayPause?: () => void;
  isPlaying?: boolean;
}

const Timeline: React.FC<TimelineProps> = ({
  tracks,
  duration,
  currentTime,
  onTimeChange,
  onClipMove,
  onClipResize,
  onClipSelect,
  onPlayPause,
  isPlaying = false
}) => {
  const [zoom, setZoom] = useState(1); // Pixels per second
  const [scrollLeft, setScrollLeft] = useState(0);
  const [isDraggingPlayhead, setIsDraggingPlayhead] = useState(false);
  const [selectedClipId, setSelectedClipId] = useState<string | null>(null);

  const timelineRef = useRef<HTMLDivElement>(null);
  const rulerRef = useRef<HTMLDivElement>(null);

  // Calculate timeline width in pixels
  const timelineWidth = duration * zoom * 50; // 50 pixels per second at zoom=1

  // Zoom controls
  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev * 1.5, 10));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev / 1.5, 0.1));
  };

  // Playhead dragging
  const handlePlayheadMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDraggingPlayhead(true);
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (!isDraggingPlayhead || !timelineRef.current) return;

    const rect = timelineRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left + scrollLeft;
    const time = Math.max(0, Math.min((x / timelineWidth) * duration, duration));

    onTimeChange?.(time);
  };

  const handleMouseUp = () => {
    setIsDraggingPlayhead(false);
  };

  useEffect(() => {
    if (isDraggingPlayhead) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDraggingPlayhead, scrollLeft, timelineWidth, duration]);

  // Click on ruler to jump to time
  const handleRulerClick = (e: React.MouseEvent) => {
    if (!rulerRef.current) return;

    const rect = rulerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left + scrollLeft;
    const time = Math.max(0, Math.min((x / timelineWidth) * duration, duration));

    onTimeChange?.(time);
  };

  // Format time as MM:SS or HH:MM:SS
  const formatTime = (seconds: number): string => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    if (hrs > 0) {
      return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Generate time markers for ruler
  const generateTimeMarkers = () => {
    const markers: { time: number; label: string }[] = [];
    const interval = zoom > 2 ? 1 : zoom > 0.5 ? 5 : 10; // Adaptive interval based on zoom

    for (let t = 0; t <= duration; t += interval) {
      markers.push({ time: t, label: formatTime(t) });
    }

    return markers;
  };

  const timeMarkers = generateTimeMarkers();

  // Calculate playhead position
  const playheadPosition = (currentTime / duration) * timelineWidth;

  // Skip forward/backward
  const handleSkipForward = () => {
    const newTime = Math.min(currentTime + 5, duration);
    onTimeChange?.(newTime);
  };

  const handleSkipBack = () => {
    const newTime = Math.max(currentTime - 5, 0);
    onTimeChange?.(newTime);
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 text-white">
      {/* Toolbar */}
      <div className="flex items-center justify-between bg-gray-800 border-b border-gray-700 px-4 py-2">
        {/* Playback Controls */}
        <div className="flex items-center space-x-2">
          <button
            onClick={handleSkipBack}
            className="p-2 hover:bg-gray-700 rounded transition"
            title="Skip Back 5s"
          >
            <SkipBack className="w-5 h-5" />
          </button>

          <button
            onClick={onPlayPause}
            className="p-2 bg-blue-600 hover:bg-blue-500 rounded transition"
            title={isPlaying ? 'Pause' : 'Play'}
          >
            {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
          </button>

          <button
            onClick={handleSkipForward}
            className="p-2 hover:bg-gray-700 rounded transition"
            title="Skip Forward 5s"
          >
            <SkipForward className="w-5 h-5" />
          </button>

          <div className="ml-4 text-sm font-mono">
            <span className="text-blue-400">{formatTime(currentTime)}</span>
            <span className="text-gray-500"> / </span>
            <span className="text-gray-400">{formatTime(duration)}</span>
          </div>
        </div>

        {/* Zoom Controls */}
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-400">Zoom:</span>
          <button
            onClick={handleZoomOut}
            className="p-2 hover:bg-gray-700 rounded transition"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>

          <div className="w-20 text-center text-sm">
            {Math.round(zoom * 100)}%
          </div>

          <button
            onClick={handleZoomIn}
            className="p-2 hover:bg-gray-700 rounded transition"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Timeline Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Track Headers */}
        <div className="w-40 bg-gray-800 border-r border-gray-700 flex-shrink-0">
          <div className="h-12 border-b border-gray-700"></div> {/* Spacer for ruler */}
          {tracks.map(track => (
            <div
              key={track.id}
              className="h-20 border-b border-gray-700 px-3 py-2 flex flex-col justify-center"
            >
              <div className="text-sm font-semibold truncate">{track.name}</div>
              <div className="text-xs text-gray-400 capitalize">{track.type}</div>
            </div>
          ))}
        </div>

        {/* Timeline Content */}
        <div className="flex-1 overflow-auto" ref={timelineRef} onScroll={(e) => setScrollLeft(e.currentTarget.scrollLeft)}>
          <div style={{ width: `${timelineWidth}px` }}>
            {/* Time Ruler */}
            <div
              ref={rulerRef}
              className="h-12 bg-gray-800 border-b border-gray-700 relative cursor-pointer"
              onClick={handleRulerClick}
            >
              {timeMarkers.map((marker, idx) => {
                const x = (marker.time / duration) * timelineWidth;
                return (
                  <div
                    key={idx}
                    className="absolute"
                    style={{ left: `${x}px`, top: 0 }}
                  >
                    <div className="w-px h-3 bg-gray-600"></div>
                    <div className="text-xs text-gray-400 mt-1 -translate-x-1/2">
                      {marker.label}
                    </div>
                  </div>
                );
              })}

              {/* Playhead */}
              <div
                className="absolute top-0 bottom-0 w-0.5 bg-red-500 cursor-ew-resize z-20"
                style={{ left: `${playheadPosition}px` }}
                onMouseDown={handlePlayheadMouseDown}
              >
                <div className="absolute -top-1 -left-2 w-4 h-4 bg-red-500 rounded-sm"></div>
              </div>
            </div>

            {/* Tracks */}
            {tracks.map(track => (
              <div
                key={track.id}
                className="h-20 bg-gray-900 border-b border-gray-700 relative"
              >
                {/* Track clips will be rendered here by TimelineTrack component */}
                {track.clips.map(clip => {
                  const clipX = (clip.startTime / duration) * timelineWidth;
                  const clipWidth = (clip.duration / duration) * timelineWidth;
                  const isSelected = selectedClipId === clip.id;

                  return (
                    <div
                      key={clip.id}
                      className={`absolute top-2 bottom-2 rounded cursor-move transition-all ${
                        isSelected ? 'ring-2 ring-blue-400' : ''
                      }`}
                      style={{
                        left: `${clipX}px`,
                        width: `${clipWidth}px`,
                        backgroundColor: clip.color || '#3b82f6'
                      }}
                      onClick={() => {
                        setSelectedClipId(clip.id);
                        onClipSelect?.(clip.id);
                      }}
                    >
                      {/* Clip thumbnail or waveform */}
                      {clip.type === 'video' && clip.thumbnailUrl && (
                        <img
                          src={clip.thumbnailUrl}
                          alt={clip.name}
                          className="w-full h-full object-cover rounded opacity-60"
                        />
                      )}

                      {/* Clip name */}
                      <div className="absolute inset-0 flex items-center px-2">
                        <span className="text-xs font-medium text-white truncate drop-shadow">
                          {clip.name}
                        </span>
                      </div>

                      {/* Trim handles (left and right edges) */}
                      <div className="absolute left-0 top-0 bottom-0 w-1 bg-white/50 cursor-ew-resize hover:bg-white"></div>
                      <div className="absolute right-0 top-0 bottom-0 w-1 bg-white/50 cursor-ew-resize hover:bg-white"></div>
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="bg-gray-800 border-t border-gray-700 px-4 py-2 flex items-center justify-between text-xs text-gray-400">
        <div>
          {selectedClipId ? `Selected: ${tracks.flatMap(t => t.clips).find(c => c.id === selectedClipId)?.name}` : 'No clip selected'}
        </div>
        <div>
          {tracks.length} tracks • {tracks.flatMap(t => t.clips).length} clips
        </div>
      </div>
    </div>
  );
};

export default Timeline;
