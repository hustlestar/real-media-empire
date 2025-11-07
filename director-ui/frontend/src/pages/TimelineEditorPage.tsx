import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Film,
  Scissors,
  Combine,
  Wand2,
  Volume2,
  Download,
  Save,
  Undo,
  Redo,
  Plus,
  Settings,
  Eye
} from 'lucide-react';
import { apiUrl } from '../config/api';
import Timeline from '../components/timeline/Timeline';
import TimelineTrack, { Track } from '../components/timeline/TimelineTrack';
import { Clip } from '../components/timeline/TimelineClip';
import TransitionEditor, { Transition } from '../components/timeline/TransitionEditor';
import AudioMixer, { AudioTrackConfig, VolumeKeyframe } from '../components/timeline/AudioMixer';
import VideoPlayer from '../components/video/VideoPlayer';

interface TimelineEditorPageProps {}

const TimelineEditorPage: React.FC<TimelineEditorPageProps> = () => {
  const { filmProjectId } = useParams<{ filmProjectId: string }>();
  const navigate = useNavigate();

  // Timeline state
  const [tracks, setTracks] = useState<Track[]>([]);
  const [duration, setDuration] = useState(120); // Total timeline duration in seconds
  const [currentTime, setCurrentTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [selectedClipId, setSelectedClipId] = useState<string | null>(null);

  // UI state
  const [showTransitionEditor, setShowTransitionEditor] = useState(false);
  const [showAudioMixer, setShowAudioMixer] = useState(false);
  const [showPreview, setShowPreview] = useState(true);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  // Edit history for undo/redo
  const [editHistory, setEditHistory] = useState<Track[][]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);

  // Load timeline data
  useEffect(() => {
    if (filmProjectId) {
      loadTimelineData();
    }
  }, [filmProjectId]);

  const loadTimelineData = async () => {
    try {
      // Fetch shots for the project
      const response = await fetch(apiUrl(`/api/film/shots?film_project_id=${filmProjectId}`));
      const data = await response.json();

      if (data.shots && data.shots.length > 0) {
        // Convert shots to clips
        const videoClips: Clip[] = data.shots.map((shot: any, idx: number) => ({
          id: shot.id,
          trackId: 'video-track-1',
          startTime: idx * 5, // Place clips sequentially
          duration: parseFloat(shot.duration) || 5,
          type: 'video' as const,
          name: shot.shot_id,
          thumbnailUrl: shot.thumbnail_url,
          color: '#3b82f6',
          locked: false
        }));

        // Create initial tracks
        const initialTracks: Track[] = [
          {
            id: 'video-track-1',
            type: 'video',
            name: 'Main Video',
            clips: videoClips,
            volume: 1.0,
            muted: false,
            locked: false,
            visible: true
          },
          {
            id: 'audio-track-1',
            type: 'audio',
            name: 'Music',
            clips: [],
            volume: 0.8,
            muted: false,
            locked: false,
            visible: true
          },
          {
            id: 'audio-track-2',
            type: 'audio',
            name: 'Sound Effects',
            clips: [],
            volume: 1.0,
            muted: false,
            locked: false,
            visible: true
          }
        ];

        setTracks(initialTracks);
        saveToHistory(initialTracks);

        // Calculate total duration
        const maxEndTime = Math.max(...videoClips.map(c => c.startTime + c.duration));
        setDuration(maxEndTime + 10); // Add 10s buffer
      }
    } catch (error) {
      console.error('Error loading timeline:', error);
    }
  };

  // History management
  const saveToHistory = (newTracks: Track[]) => {
    const newHistory = editHistory.slice(0, historyIndex + 1);
    newHistory.push(JSON.parse(JSON.stringify(newTracks))); // Deep copy
    setEditHistory(newHistory);
    setHistoryIndex(newHistory.length - 1);
  };

  const undo = () => {
    if (historyIndex > 0) {
      setHistoryIndex(historyIndex - 1);
      setTracks(JSON.parse(JSON.stringify(editHistory[historyIndex - 1])));
    }
  };

  const redo = () => {
    if (historyIndex < editHistory.length - 1) {
      setHistoryIndex(historyIndex + 1);
      setTracks(JSON.parse(JSON.stringify(editHistory[historyIndex + 1])));
    }
  };

  // Clip operations
  const handleClipMove = (clipId: string, newStartTime: number) => {
    const updatedTracks = tracks.map(track => ({
      ...track,
      clips: track.clips.map(clip =>
        clip.id === clipId ? { ...clip, startTime: newStartTime } : clip
      )
    }));

    setTracks(updatedTracks);
    saveToHistory(updatedTracks);
  };

  const handleClipTrimStart = (clipId: string, newStartTime: number, newDuration: number) => {
    const updatedTracks = tracks.map(track => ({
      ...track,
      clips: track.clips.map(clip =>
        clip.id === clipId
          ? { ...clip, startTime: newStartTime, duration: newDuration }
          : clip
      )
    }));

    setTracks(updatedTracks);
    saveToHistory(updatedTracks);
  };

  const handleClipTrimEnd = (clipId: string, newDuration: number) => {
    const updatedTracks = tracks.map(track => ({
      ...track,
      clips: track.clips.map(clip =>
        clip.id === clipId ? { ...clip, duration: newDuration } : clip
      )
    }));

    setTracks(updatedTracks);
    saveToHistory(updatedTracks);
  };

  const handleClipSelect = (clipId: string) => {
    setSelectedClipId(clipId);
  };

  const handleClipDoubleClick = (clipId: string) => {
    setShowTransitionEditor(true);
  };

  // Track operations
  const handleTrackVolumeChange = (trackId: string, volume: number) => {
    const updatedTracks = tracks.map(track =>
      track.id === trackId ? { ...track, volume } : track
    );
    setTracks(updatedTracks);
  };

  const handleTrackMuteToggle = (trackId: string) => {
    const updatedTracks = tracks.map(track =>
      track.id === trackId ? { ...track, muted: !track.muted } : track
    );
    setTracks(updatedTracks);
  };

  const handleTrackLockToggle = (trackId: string) => {
    const updatedTracks = tracks.map(track =>
      track.id === trackId ? { ...track, locked: !track.locked } : track
    );
    setTracks(updatedTracks);
  };

  const handleTrackVisibilityToggle = (trackId: string) => {
    const updatedTracks = tracks.map(track =>
      track.id === trackId ? { ...track, visible: !track.visible } : track
    );
    setTracks(updatedTracks);
  };

  // Transition operations
  const handleTransitionApply = (clipId: string, transition: Transition) => {
    const updatedTracks = tracks.map(track => ({
      ...track,
      clips: track.clips.map(clip =>
        clip.id === clipId ? { ...clip, transition } : clip
      )
    }));

    setTracks(updatedTracks);
    saveToHistory(updatedTracks);
  };

  const handleTransitionRemove = (clipId: string) => {
    const updatedTracks = tracks.map(track => ({
      ...track,
      clips: track.clips.map(clip =>
        clip.id === clipId ? { ...clip, transition: undefined } : clip
      )
    }));

    setTracks(updatedTracks);
    saveToHistory(updatedTracks);
  };

  // Audio mixer operations
  const handleAudioTrackUpdate = (trackId: string, config: Partial<AudioTrackConfig>) => {
    const updatedTracks = tracks.map(track =>
      track.id === trackId ? { ...track, ...config } : track
    );
    setTracks(updatedTracks);
    saveToHistory(updatedTracks);
  };

  // Export operations
  const handleExport = async () => {
    try {
      const response = await fetch(apiUrl('/api/editing/export'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          film_project_id: filmProjectId,
          output_format: 'mp4',
          quality: 'preview',
          resolution: '1080p'
        })
      });

      const result = await response.json();

      if (result.output_url) {
        alert(`Export completed! File: ${result.output_url}`);
      }
    } catch (error) {
      console.error('Export error:', error);
      alert('Export failed. Please try again.');
    }
  };

  // Playback control
  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleTimeChange = (time: number) => {
    setCurrentTime(time);
  };

  // Get selected clip
  const selectedClip = tracks
    .flatMap(t => t.clips)
    .find(c => c.id === selectedClipId);

  // Convert tracks to audio mixer format
  const audioTracksForMixer: AudioTrackConfig[] = tracks
    .filter(t => t.type === 'audio' || t.type === 'video')
    .map(track => ({
      id: track.id,
      name: track.name,
      type: track.type === 'audio' ? 'music' : 'dialogue',
      volume: track.volume,
      muted: track.muted,
      solo: false,
      volumeEnvelope: []
    }));

  return (
    <div className="h-screen flex flex-col bg-gray-900 text-white">
      {/* Top Toolbar */}
      <div className="bg-gray-800 border-b border-gray-700 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate(-1)}
            className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded transition"
          >
            ← Back
          </button>

          <div className="border-l border-gray-700 pl-4">
            <h1 className="text-lg font-bold text-white">Timeline Editor</h1>
            <p className="text-xs text-gray-400">Project: {filmProjectId}</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {/* Edit Tools */}
          <button
            onClick={undo}
            disabled={historyIndex <= 0}
            className="p-2 hover:bg-gray-700 rounded transition disabled:opacity-30 disabled:cursor-not-allowed"
            title="Undo"
          >
            <Undo className="w-5 h-5" />
          </button>

          <button
            onClick={redo}
            disabled={historyIndex >= editHistory.length - 1}
            className="p-2 hover:bg-gray-700 rounded transition disabled:opacity-30 disabled:cursor-not-allowed"
            title="Redo"
          >
            <Redo className="w-5 h-5" />
          </button>

          <div className="border-l border-gray-700 pl-2 ml-2 flex items-center space-x-2">
            <button
              onClick={() => setShowTransitionEditor(!showTransitionEditor)}
              className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded transition flex items-center space-x-2"
            >
              <Wand2 className="w-4 h-4" />
              <span>Transitions</span>
            </button>

            <button
              onClick={() => setShowAudioMixer(!showAudioMixer)}
              className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded transition flex items-center space-x-2"
            >
              <Volume2 className="w-4 h-4" />
              <span>Audio Mixer</span>
            </button>

            <button
              onClick={() => setShowPreview(!showPreview)}
              className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded transition flex items-center space-x-2"
            >
              <Eye className="w-4 h-4" />
              <span>Preview</span>
            </button>
          </div>

          <div className="border-l border-gray-700 pl-2 ml-2 flex items-center space-x-2">
            <button
              onClick={handleExport}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded transition flex items-center space-x-2"
            >
              <Download className="w-4 h-4" />
              <span>Export</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Preview */}
        {showPreview && (
          <div className="w-1/3 bg-gray-800 border-r border-gray-700 p-4">
            <div className="mb-3">
              <h3 className="text-sm font-semibold text-white mb-2">Preview</h3>
            </div>

            {/* Video Preview */}
            {previewUrl ? (
              <VideoPlayer
                src={previewUrl}
                onTimeUpdate={setCurrentTime}
              />
            ) : (
              <div className="aspect-video bg-gray-900 rounded-lg flex items-center justify-center border border-gray-700">
                <div className="text-center">
                  <Film className="w-12 h-12 text-gray-600 mx-auto mb-2" />
                  <p className="text-sm text-gray-500">No preview available</p>
                  <p className="text-xs text-gray-600 mt-1">Add clips to timeline to preview</p>
                </div>
              </div>
            )}

            {/* Clip Info */}
            {selectedClip && (
              <div className="mt-4 bg-gray-900 rounded-lg p-3">
                <h4 className="text-sm font-semibold text-white mb-2">Selected Clip</h4>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Name:</span>
                    <span className="text-white">{selectedClip.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Duration:</span>
                    <span className="text-white">{selectedClip.duration.toFixed(2)}s</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Start:</span>
                    <span className="text-white">{selectedClip.startTime.toFixed(2)}s</span>
                  </div>
                  {selectedClip.transition && (
                    <div className="flex justify-between">
                      <span className="text-gray-400">Transition:</span>
                      <span className="text-white capitalize">{selectedClip.transition.type}</span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Right Panel - Timeline */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <Timeline
            tracks={tracks}
            duration={duration}
            currentTime={currentTime}
            onTimeChange={handleTimeChange}
            onClipMove={handleClipMove}
            onClipResize={handleClipTrimEnd}
            onClipSelect={handleClipSelect}
            onPlayPause={handlePlayPause}
            isPlaying={isPlaying}
          />
        </div>
      </div>

      {/* Modals/Overlays */}
      {showTransitionEditor && selectedClip && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-8">
          <TransitionEditor
            clipId={selectedClip.id}
            clipName={selectedClip.name}
            currentTransition={selectedClip.transition}
            onApply={handleTransitionApply}
            onRemove={handleTransitionRemove}
            onClose={() => setShowTransitionEditor(false)}
          />
        </div>
      )}

      {showAudioMixer && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-8 overflow-auto">
          <AudioMixer
            tracks={audioTracksForMixer}
            duration={duration}
            currentTime={currentTime}
            onTrackUpdate={handleAudioTrackUpdate}
            onClose={() => setShowAudioMixer(false)}
          />
        </div>
      )}

      {/* Quick Actions Panel */}
      <div className="bg-gray-800 border-t border-gray-700 px-4 py-2 flex items-center justify-between text-xs text-gray-400">
        <div>
          Timeline: {tracks.length} tracks • {tracks.flatMap(t => t.clips).length} clips •{' '}
          {duration.toFixed(1)}s total
        </div>
        <div className="flex items-center space-x-4">
          <span>Zoom: Alt+Scroll</span>
          <span>Split: S</span>
          <span>Delete: Del</span>
        </div>
      </div>
    </div>
  );
};

export default TimelineEditorPage;
