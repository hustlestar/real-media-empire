import React, { useState, useRef, useEffect } from 'react';
import { Volume2, VolumeX, Lock, Image as ImageIcon, Type, Film } from 'lucide-react';

export interface Clip {
  id: string;
  trackId: string;
  startTime: number;
  duration: number;
  type: 'video' | 'audio' | 'text' | 'image';
  name: string;
  thumbnailUrl?: string;
  audioUrl?: string;
  color?: string;
  trimIn?: number;  // Trim start offset in seconds
  trimOut?: number; // Trim end offset in seconds
  volume?: number;  // 0-1
  locked?: boolean;
  transition?: {
    type: 'fade' | 'dissolve' | 'wipe';
    duration: number; // in seconds
  };
}

interface TimelineClipProps {
  clip: Clip;
  timelineWidth: number;
  duration: number;
  isSelected: boolean;
  zoom: number;
  onSelect: (clipId: string) => void;
  onMove?: (clipId: string, newStartTime: number) => void;
  onTrimStart?: (clipId: string, newStartTime: number, newDuration: number) => void;
  onTrimEnd?: (clipId: string, newDuration: number) => void;
  onDoubleClick?: (clipId: string) => void;
}

const TimelineClip: React.FC<TimelineClipProps> = ({
  clip,
  timelineWidth,
  duration,
  isSelected,
  zoom,
  onSelect,
  onMove,
  onTrimStart,
  onTrimEnd,
  onDoubleClick
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isTrimming, setIsTrimming] = useState<'start' | 'end' | null>(null);
  const [dragStartX, setDragStartX] = useState(0);
  const [dragStartTime, setDragStartTime] = useState(0);

  const clipRef = useRef<HTMLDivElement>(null);

  // Calculate clip position and width
  const clipX = (clip.startTime / duration) * timelineWidth;
  const clipWidth = (clip.duration / duration) * timelineWidth;

  // Handle clip dragging (move)
  const handleMouseDown = (e: React.MouseEvent) => {
    if (clip.locked) return;

    e.stopPropagation();
    onSelect(clip.id);

    setIsDragging(true);
    setDragStartX(e.clientX);
    setDragStartTime(clip.startTime);
  };

  // Handle trim handle dragging
  const handleTrimStartMouseDown = (e: React.MouseEvent) => {
    if (clip.locked) return;

    e.stopPropagation();
    onSelect(clip.id);

    setIsTrimming('start');
    setDragStartX(e.clientX);
    setDragStartTime(clip.startTime);
  };

  const handleTrimEndMouseDown = (e: React.MouseEvent) => {
    if (clip.locked) return;

    e.stopPropagation();
    onSelect(clip.id);

    setIsTrimming('end');
    setDragStartX(e.clientX);
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (isDragging) {
      // Move clip
      const deltaX = e.clientX - dragStartX;
      const deltaTime = (deltaX / timelineWidth) * duration;
      const newStartTime = Math.max(0, Math.min(dragStartTime + deltaTime, duration - clip.duration));

      onMove?.(clip.id, newStartTime);
    } else if (isTrimming === 'start') {
      // Trim start
      const deltaX = e.clientX - dragStartX;
      const deltaTime = (deltaX / timelineWidth) * duration;
      const newStartTime = Math.max(0, Math.min(dragStartTime + deltaTime, dragStartTime + clip.duration - 0.1));
      const newDuration = clip.duration - (newStartTime - clip.startTime);

      if (newDuration > 0.1) {
        onTrimStart?.(clip.id, newStartTime, newDuration);
      }
    } else if (isTrimming === 'end') {
      // Trim end
      const deltaX = e.clientX - dragStartX;
      const deltaTime = (deltaX / timelineWidth) * duration;
      const newDuration = Math.max(0.1, Math.min(clip.duration + deltaTime, duration - clip.startTime));

      onTrimEnd?.(clip.id, newDuration);
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
    setIsTrimming(null);
  };

  useEffect(() => {
    if (isDragging || isTrimming) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, isTrimming, dragStartX, dragStartTime]);

  // Double-click to open clip editor
  const handleDoubleClick = () => {
    onDoubleClick?.(clip.id);
  };

  // Determine clip icon
  const getClipIcon = () => {
    switch (clip.type) {
      case 'video':
        return <Film className="w-3 h-3" />;
      case 'audio':
        return <Volume2 className="w-3 h-3" />;
      case 'text':
        return <Type className="w-3 h-3" />;
      case 'image':
        return <ImageIcon className="w-3 h-3" />;
    }
  };

  // Get color based on type if not specified
  const getClipColor = () => {
    if (clip.color) return clip.color;

    switch (clip.type) {
      case 'video':
        return '#3b82f6'; // blue-600
      case 'audio':
        return '#10b981'; // green-600
      case 'text':
        return '#f59e0b'; // amber-600
      case 'image':
        return '#8b5cf6'; // purple-600
      default:
        return '#6b7280'; // gray-600
    }
  };

  const clipColor = getClipColor();

  return (
    <div
      ref={clipRef}
      className={`absolute top-2 bottom-2 rounded overflow-hidden transition-all ${
        isSelected ? 'ring-2 ring-blue-400 shadow-lg z-10' : 'z-0'
      } ${clip.locked ? 'cursor-not-allowed opacity-60' : 'cursor-move'} ${
        isDragging ? 'opacity-80' : ''
      }`}
      style={{
        left: `${clipX}px`,
        width: `${clipWidth}px`,
        backgroundColor: clipColor
      }}
      onMouseDown={handleMouseDown}
      onDoubleClick={handleDoubleClick}
    >
      {/* Background: Thumbnail or waveform */}
      {clip.type === 'video' && clip.thumbnailUrl && (
        <img
          src={clip.thumbnailUrl}
          alt={clip.name}
          className="w-full h-full object-cover opacity-40"
          draggable={false}
        />
      )}

      {clip.type === 'audio' && (
        <div className="w-full h-full flex items-center justify-center opacity-30">
          {/* Audio waveform placeholder */}
          <div className="flex items-end space-x-px h-8">
            {Array.from({ length: 20 }).map((_, i) => (
              <div
                key={i}
                className="w-1 bg-white rounded-t"
                style={{ height: `${20 + Math.random() * 80}%` }}
              ></div>
            ))}
          </div>
        </div>
      )}

      {/* Clip Content Overlay */}
      <div className="absolute inset-0 flex items-center px-2 pointer-events-none">
        <div className="flex items-center space-x-1">
          {getClipIcon()}
          <span className="text-xs font-medium text-white truncate drop-shadow-md">
            {clip.name}
          </span>
        </div>
      </div>

      {/* Clip status indicators */}
      <div className="absolute top-1 right-1 flex items-center space-x-1 pointer-events-none">
        {clip.locked && (
          <div className="bg-gray-900/70 rounded p-0.5">
            <Lock className="w-3 h-3 text-white" />
          </div>
        )}
        {clip.type === 'audio' && clip.volume === 0 && (
          <div className="bg-gray-900/70 rounded p-0.5">
            <VolumeX className="w-3 h-3 text-white" />
          </div>
        )}
      </div>

      {/* Transition indicator */}
      {clip.transition && (
        <div className="absolute top-1 left-1 bg-gray-900/70 rounded px-1.5 py-0.5 text-xs text-white pointer-events-none">
          {clip.transition.type}
        </div>
      )}

      {/* Trim handles */}
      {!clip.locked && (
        <>
          {/* Left trim handle */}
          <div
            className="absolute left-0 top-0 bottom-0 w-2 cursor-ew-resize hover:bg-white/30 flex items-center justify-center group"
            onMouseDown={handleTrimStartMouseDown}
          >
            <div className="w-0.5 h-4 bg-white/70 group-hover:bg-white rounded"></div>
          </div>

          {/* Right trim handle */}
          <div
            className="absolute right-0 top-0 bottom-0 w-2 cursor-ew-resize hover:bg-white/30 flex items-center justify-center group"
            onMouseDown={handleTrimEndMouseDown}
          >
            <div className="w-0.5 h-4 bg-white/70 group-hover:bg-white rounded"></div>
          </div>
        </>
      )}

      {/* Trim indicators (show trimmed portions) */}
      {clip.trimIn && clip.trimIn > 0 && (
        <div className="absolute left-0 top-0 bottom-0 w-1 bg-yellow-400 opacity-70"></div>
      )}
      {clip.trimOut && clip.trimOut > 0 && (
        <div className="absolute right-0 top-0 bottom-0 w-1 bg-yellow-400 opacity-70"></div>
      )}
    </div>
  );
};

export default TimelineClip;
