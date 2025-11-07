import React, { useState, useEffect } from 'react';
import { Play, Pause, Volume2, CheckCircle, Download, RefreshCw, Zap } from 'lucide-react';
import { apiUrl } from '../../config/api';

interface AudioTake {
  id: string;
  audioUrl: string;
  config: {
    provider: string;
    voice: string;
    speed: number;
    pitch?: number;
    emotion?: string;
  };
  waveform?: string; // Data URL for waveform image
  duration: number;
  selected?: boolean;
}

interface VoiceComparisonProps {
  text: string;
  providerPrompt: string;
  onTakeSelected?: (take: AudioTake) => void;
}

const VoiceComparison: React.FC<VoiceComparisonProps> = ({
  text,
  providerPrompt,
  onTakeSelected
}) => {
  const [takes, setTakes] = useState<AudioTake[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [playingTakeId, setPlayingTakeId] = useState<string | null>(null);
  const [audioElements, setAudioElements] = useState<Map<string, HTMLAudioElement>>(new Map());
  const [selectedTakeId, setSelectedTakeId] = useState<string | null>(null);

  // Generate multiple takes with variations
  const generateTakes = async () => {
    try {
      setIsGenerating(true);

      // Generate 3 variations
      const variations = [
        { speed: 0.9, emotion: 'neutral', label: 'Slower' },
        { speed: 1.0, emotion: 'neutral', label: 'Normal' },
        { speed: 1.1, emotion: 'excited', label: 'Faster + Excited' }
      ];

      const takePromises = variations.map(async (variation, idx) => {
        const response = await fetch(apiUrl('/api/audio/generate'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text,
            provider_prompt: providerPrompt,
            provider: 'elevenlabs', // Default to ElevenLabs for comparison
            voice: 'en-US-Studio-M',
            speed: variation.speed,
            emotion: variation.emotion
          })
        });

        const result = await response.json();

        return {
          id: `take-${idx}`,
          audioUrl: result.audio_url,
          config: {
            provider: 'elevenlabs',
            voice: 'en-US-Studio-M',
            speed: variation.speed,
            emotion: variation.emotion
          },
          duration: result.duration || 0,
          selected: false
        };
      });

      const generatedTakes = await Promise.all(takePromises);
      setTakes(generatedTakes);

      // Create audio elements
      const newAudioElements = new Map<string, HTMLAudioElement>();
      generatedTakes.forEach(take => {
        const audio = new Audio(take.audioUrl);
        audio.onended = () => setPlayingTakeId(null);
        newAudioElements.set(take.id, audio);
      });
      setAudioElements(newAudioElements);

    } catch (error) {
      console.error('Error generating takes:', error);
      alert('Failed to generate voice takes. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const togglePlayback = (takeId: string) => {
    const audio = audioElements.get(takeId);
    if (!audio) return;

    // Stop other takes
    audioElements.forEach((otherAudio, otherId) => {
      if (otherId !== takeId && !otherAudio.paused) {
        otherAudio.pause();
        otherAudio.currentTime = 0;
      }
    });

    if (playingTakeId === takeId) {
      audio.pause();
      audio.currentTime = 0;
      setPlayingTakeId(null);
    } else {
      audio.play();
      setPlayingTakeId(takeId);
    }
  };

  const selectTake = (takeId: string) => {
    setSelectedTakeId(takeId);
    const take = takes.find(t => t.id === takeId);
    if (take) {
      onTakeSelected?.({ ...take, selected: true });
    }
  };

  const downloadTake = (take: AudioTake) => {
    const link = document.createElement('a');
    link.href = take.audioUrl;
    link.download = `voice-take-${take.id}.mp3`;
    link.click();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-white">Voice Take Comparison</h3>
          <p className="text-sm text-gray-400">Generate and compare different voice variations</p>
        </div>

        <button
          onClick={generateTakes}
          disabled={isGenerating || takes.length > 0}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg transition flex items-center space-x-2"
        >
          {isGenerating ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Generating 3 takes...</span>
            </>
          ) : takes.length > 0 ? (
            <>
              <CheckCircle className="w-4 h-4" />
              <span>Takes Ready</span>
            </>
          ) : (
            <>
              <Zap className="w-4 h-4" />
              <span>Generate Takes</span>
            </>
          )}
        </button>
      </div>

      {/* Takes Grid */}
      {takes.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {takes.map((take, idx) => (
            <div
              key={take.id}
              className={`bg-gray-800 rounded-lg p-4 border-2 transition-all ${
                selectedTakeId === take.id
                  ? 'border-blue-500 ring-2 ring-blue-500/50'
                  : 'border-gray-700 hover:border-gray-600'
              }`}
            >
              {/* Take Header */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-sm font-bold">
                    {String.fromCharCode(65 + idx)}
                  </div>
                  <span className="font-semibold text-white">
                    Take {String.fromCharCode(65 + idx)}
                  </span>
                </div>
                {selectedTakeId === take.id && (
                  <CheckCircle className="w-5 h-5 text-blue-400" />
                )}
              </div>

              {/* Waveform Placeholder */}
              <div className="bg-gray-900 rounded h-20 mb-3 flex items-center justify-center">
                <Volume2 className="w-8 h-8 text-gray-600" />
              </div>

              {/* Take Info */}
              <div className="space-y-2 text-sm text-gray-400 mb-3">
                <div className="flex justify-between">
                  <span>Speed:</span>
                  <span className="text-white">{take.config.speed}x</span>
                </div>
                <div className="flex justify-between">
                  <span>Emotion:</span>
                  <span className="text-white capitalize">{take.config.emotion}</span>
                </div>
                {take.duration > 0 && (
                  <div className="flex justify-between">
                    <span>Duration:</span>
                    <span className="text-white">{take.duration.toFixed(1)}s</span>
                  </div>
                )}
              </div>

              {/* Controls */}
              <div className="space-y-2">
                {/* Play Button */}
                <button
                  onClick={() => togglePlayback(take.id)}
                  className="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition flex items-center justify-center space-x-2"
                >
                  {playingTakeId === take.id ? (
                    <>
                      <Pause className="w-4 h-4" />
                      <span>Pause</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4" />
                      <span>Play</span>
                    </>
                  )}
                </button>

                {/* Select Button */}
                <button
                  onClick={() => selectTake(take.id)}
                  className={`w-full px-4 py-2 rounded-lg transition flex items-center justify-center space-x-2 ${
                    selectedTakeId === take.id
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  <CheckCircle className="w-4 h-4" />
                  <span>{selectedTakeId === take.id ? 'Selected' : 'Select This'}</span>
                </button>

                {/* Download Button */}
                <button
                  onClick={() => downloadTake(take)}
                  className="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition flex items-center justify-center space-x-2 text-gray-300"
                >
                  <Download className="w-4 h-4" />
                  <span>Download</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {takes.length === 0 && !isGenerating && (
        <div className="bg-gray-800 rounded-lg p-8 text-center">
          <Volume2 className="w-12 h-12 text-gray-600 mx-auto mb-3" />
          <p className="text-gray-400">Click "Generate Takes" to create 3 voice variations</p>
          <p className="text-sm text-gray-500 mt-2">Compare different speeds and emotions to find the perfect voice</p>
        </div>
      )}

      {/* Quick Comparison Tips */}
      {takes.length > 0 && (
        <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-white mb-2">Director's Tips</h4>
          <ul className="text-sm text-gray-300 space-y-1">
            <li>• Listen to all takes before selecting</li>
            <li>• Take A: Slower pace for clarity</li>
            <li>• Take B: Normal speed baseline</li>
            <li>• Take C: Faster with excitement for energy</li>
            <li>• Consider the emotion and pacing of your scene</li>
          </ul>
        </div>
      )}

      {/* Regenerate Button */}
      {takes.length > 0 && (
        <button
          onClick={() => {
            setTakes([]);
            setAudioElements(new Map());
            setPlayingTakeId(null);
            setSelectedTakeId(null);
          }}
          className="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition flex items-center justify-center space-x-2"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Generate New Takes</span>
        </button>
      )}
    </div>
  );
};

export default VoiceComparison;
