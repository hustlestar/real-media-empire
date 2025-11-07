import React, { useState } from 'react';
import { Zap, ChevronRight, Blend, ArrowRightLeft, Clock, X } from 'lucide-react';

export interface Transition {
  type: 'fade' | 'dissolve' | 'wipe' | 'slide' | 'zoom' | 'none';
  duration: number; // in seconds
  easing?: 'linear' | 'ease-in' | 'ease-out' | 'ease-in-out';
  direction?: 'left' | 'right' | 'up' | 'down'; // For wipe and slide
}

interface TransitionEditorProps {
  clipId: string;
  clipName: string;
  currentTransition?: Transition;
  onApply: (clipId: string, transition: Transition) => void;
  onRemove?: (clipId: string) => void;
  onClose: () => void;
}

const TransitionEditor: React.FC<TransitionEditorProps> = ({
  clipId,
  clipName,
  currentTransition,
  onApply,
  onRemove,
  onClose
}) => {
  const [transition, setTransition] = useState<Transition>(
    currentTransition || {
      type: 'fade',
      duration: 0.5,
      easing: 'ease-in-out',
      direction: 'right'
    }
  );

  const transitionTypes = [
    {
      id: 'none' as const,
      name: 'None',
      description: 'No transition',
      icon: <X className="w-5 h-5" />
    },
    {
      id: 'fade' as const,
      name: 'Fade',
      description: 'Smooth opacity fade',
      icon: <Zap className="w-5 h-5" />
    },
    {
      id: 'dissolve' as const,
      name: 'Dissolve',
      description: 'Cross-dissolve blend',
      icon: <Blend className="w-5 h-5" />
    },
    {
      id: 'wipe' as const,
      name: 'Wipe',
      description: 'Directional wipe',
      icon: <ChevronRight className="w-5 h-5" />
    },
    {
      id: 'slide' as const,
      name: 'Slide',
      description: 'Sliding transition',
      icon: <ArrowRightLeft className="w-5 h-5" />
    },
    {
      id: 'zoom' as const,
      name: 'Zoom',
      description: 'Zoom in/out transition',
      icon: <Blend className="w-5 h-5" />
    }
  ];

  const handleApply = () => {
    onApply(clipId, transition);
    onClose();
  };

  const handleRemove = () => {
    onRemove?.(clipId);
    onClose();
  };

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6 max-w-2xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-bold text-white">Transition Editor</h3>
          <p className="text-sm text-gray-400">Edit transition for: {clipName}</p>
        </div>
        <button
          onClick={onClose}
          className="p-2 hover:bg-gray-700 rounded transition text-gray-400"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Transition Type Selection */}
      <div className="mb-6">
        <label className="block text-sm font-semibold text-gray-300 mb-3">
          Transition Type
        </label>
        <div className="grid grid-cols-3 gap-3">
          {transitionTypes.map(type => (
            <button
              key={type.id}
              onClick={() => setTransition({ ...transition, type: type.id })}
              className={`p-4 rounded-lg border-2 transition-all ${
                transition.type === type.id
                  ? 'border-blue-500 bg-blue-500/10 text-white'
                  : 'border-gray-700 bg-gray-900 text-gray-400 hover:border-gray-600'
              }`}
            >
              <div className="flex flex-col items-center space-y-2">
                {type.icon}
                <span className="text-sm font-medium">{type.name}</span>
                <span className="text-xs opacity-75 text-center">{type.description}</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Duration Control */}
      {transition.type !== 'none' && (
        <div className="mb-6">
          <label className="block text-sm font-semibold text-gray-300 mb-3">
            <Clock className="w-4 h-4 inline mr-1" />
            Duration
          </label>
          <div className="flex items-center space-x-4">
            <input
              type="range"
              min="0.1"
              max="3"
              step="0.1"
              value={transition.duration}
              onChange={(e) => setTransition({ ...transition, duration: parseFloat(e.target.value) })}
              className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
            />
            <div className="w-20 text-center">
              <input
                type="number"
                min="0.1"
                max="3"
                step="0.1"
                value={transition.duration}
                onChange={(e) => setTransition({ ...transition, duration: parseFloat(e.target.value) })}
                className="w-full px-2 py-1 bg-gray-900 border border-gray-700 rounded text-white text-sm text-center"
              />
              <span className="text-xs text-gray-500">seconds</span>
            </div>
          </div>
        </div>
      )}

      {/* Easing Control */}
      {transition.type !== 'none' && (
        <div className="mb-6">
          <label className="block text-sm font-semibold text-gray-300 mb-3">
            Easing
          </label>
          <div className="grid grid-cols-4 gap-2">
            {(['linear', 'ease-in', 'ease-out', 'ease-in-out'] as const).map(easing => (
              <button
                key={easing}
                onClick={() => setTransition({ ...transition, easing })}
                className={`px-3 py-2 rounded text-sm transition-all ${
                  transition.easing === easing
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-900 text-gray-400 hover:bg-gray-700'
                }`}
              >
                {easing}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Direction Control (for wipe and slide) */}
      {(transition.type === 'wipe' || transition.type === 'slide') && (
        <div className="mb-6">
          <label className="block text-sm font-semibold text-gray-300 mb-3">
            Direction
          </label>
          <div className="grid grid-cols-4 gap-2">
            {(['left', 'right', 'up', 'down'] as const).map(direction => (
              <button
                key={direction}
                onClick={() => setTransition({ ...transition, direction })}
                className={`px-3 py-2 rounded text-sm capitalize transition-all ${
                  transition.direction === direction
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-900 text-gray-400 hover:bg-gray-700'
                }`}
              >
                {direction}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Preview Area */}
      <div className="mb-6 bg-gray-900 rounded-lg p-6 border border-gray-700">
        <div className="text-sm font-semibold text-gray-300 mb-3">Preview</div>
        <div className="flex items-center justify-center space-x-4">
          {/* Clip A */}
          <div className="w-24 h-16 bg-blue-600 rounded flex items-center justify-center text-white text-xs font-bold">
            Clip A
          </div>

          {/* Transition Visualization */}
          <div className="flex-1 max-w-xs">
            <div className="text-center text-xs text-gray-400 mb-2">
              {transition.type === 'none'
                ? 'No transition'
                : `${transition.type} (${transition.duration}s)`}
            </div>
            <div className="h-1 bg-gray-700 rounded-full relative overflow-hidden">
              {transition.type !== 'none' && (
                <div
                  className="absolute top-0 left-0 h-full bg-blue-400 rounded-full animate-pulse"
                  style={{ width: '50%' }}
                ></div>
              )}
            </div>
          </div>

          {/* Clip B */}
          <div className="w-24 h-16 bg-purple-600 rounded flex items-center justify-center text-white text-xs font-bold">
            Clip B
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-between space-x-3">
        <button
          onClick={handleRemove}
          className="px-4 py-2 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-lg transition"
        >
          Remove Transition
        </button>

        <div className="flex items-center space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition"
          >
            Cancel
          </button>
          <button
            onClick={handleApply}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition"
          >
            Apply Transition
          </button>
        </div>
      </div>

      {/* Quick Presets */}
      <div className="mt-6 pt-6 border-t border-gray-700">
        <div className="text-sm font-semibold text-gray-300 mb-3">Quick Presets</div>
        <div className="grid grid-cols-3 gap-2">
          <button
            onClick={() => setTransition({ type: 'fade', duration: 0.3, easing: 'ease-out' })}
            className="px-3 py-2 bg-gray-900 hover:bg-gray-700 rounded text-xs text-gray-300 transition"
          >
            Quick Fade (0.3s)
          </button>
          <button
            onClick={() => setTransition({ type: 'dissolve', duration: 1, easing: 'ease-in-out' })}
            className="px-3 py-2 bg-gray-900 hover:bg-gray-700 rounded text-xs text-gray-300 transition"
          >
            Smooth Dissolve (1s)
          </button>
          <button
            onClick={() => setTransition({ type: 'wipe', duration: 0.5, easing: 'linear', direction: 'right' })}
            className="px-3 py-2 bg-gray-900 hover:bg-gray-700 rounded text-xs text-gray-300 transition"
          >
            Wipe Right (0.5s)
          </button>
        </div>
      </div>
    </div>
  );
};

export default TransitionEditor;
