import React, { useState, useEffect } from 'react';
import { Volume2, Play, Pause, RefreshCw, Sparkles, Settings, AlertCircle, CheckCircle } from 'lucide-react';
import { apiUrl } from '../../config/api';

interface PronunciationFix {
  word: string;
  phonetic: string;
  alternative?: string;
}

interface VoiceConfig {
  text: string;
  voice: string;
  provider: 'google' | 'elevenlabs' | 'openai';
  speed: number;
  pitch: number;
  volume: number;
  emotion?: string;
  pronunciationFixes: PronunciationFix[];
  emphasisWords: string[];
  pauses: Array<{ after_word: string, duration_ms: number }>;
}

interface VoiceEditorProps {
  initialText: string;
  onGenerate?: (audioUrl: string, config: VoiceConfig) => void;
  showProviderPrompt?: boolean;
}

const VoiceEditor: React.FC<VoiceEditorProps> = ({
  initialText,
  onGenerate,
  showProviderPrompt = true
}) => {
  const [config, setConfig] = useState<VoiceConfig>({
    text: initialText,
    voice: 'en-US-Studio-M',
    provider: 'elevenlabs',
    speed: 1.0,
    pitch: 0,
    volume: 100,
    emotion: 'neutral',
    pronunciationFixes: [],
    emphasisWords: [],
    pauses: []
  });

  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedAudio, setGeneratedAudio] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioElement, setAudioElement] = useState<HTMLAudioElement | null>(null);
  const [providerPrompt, setProviderPrompt] = useState<string>('');
  const [showPronunciationHelper, setShowPronunciationHelper] = useState(false);
  const [selectedWord, setSelectedWord] = useState<string>('');

  useEffect(() => {
    setConfig(prev => ({ ...prev, text: initialText }));
  }, [initialText]);

  // Generate TTS-provider-specific prompt
  useEffect(() => {
    generateProviderPrompt();
  }, [config.provider, config.text, config.pronunciationFixes, config.emphasisWords, config.emotion]);

  const generateProviderPrompt = () => {
    let prompt = config.text;

    if (config.provider === 'elevenlabs') {
      // ElevenLabs: Use phonetic notation for pronunciation
      let enhancedText = prompt;
      config.pronunciationFixes.forEach(fix => {
        const regex = new RegExp(`\\b${fix.word}\\b`, 'gi');
        // ElevenLabs uses custom phonetic notation
        enhancedText = enhancedText.replace(regex, `${fix.word} (${fix.phonetic})`);
      });

      // Add emphasis with ** markers (ElevenLabs specific)
      config.emphasisWords.forEach(word => {
        const regex = new RegExp(`\\b${word}\\b`, 'gi');
        enhancedText = enhancedText.replace(regex, `**${word}**`);
      });

      // Add pauses with commas/periods
      config.pauses.forEach(pause => {
        const regex = new RegExp(`\\b${pause.after_word}\\b`, 'gi');
        const pauseMarker = pause.duration_ms > 500 ? '...' : ',';
        enhancedText = enhancedText.replace(regex, `${pause.after_word}${pauseMarker}`);
      });

      setProviderPrompt(enhancedText);

    } else if (config.provider === 'google') {
      // Google TTS: Generate SSML
      let ssml = '<speak>';

      // Apply emotion via prosody
      if (config.emotion && config.emotion !== 'neutral') {
        const emotionMap: Record<string, { rate: string, pitch: string }> = {
          excited: { rate: 'fast', pitch: '+2st' },
          calm: { rate: 'slow', pitch: '-1st' },
          sad: { rate: 'slow', pitch: '-2st' },
          angry: { rate: 'medium', pitch: '+3st' },
          fearful: { rate: 'fast', pitch: '+1st' }
        };
        const emotion = emotionMap[config.emotion];
        if (emotion) {
          ssml += `<prosody rate="${emotion.rate}" pitch="${emotion.pitch}">`;
        }
      }

      let enhancedText = prompt;

      // Add pronunciation using phoneme tag
      config.pronunciationFixes.forEach(fix => {
        const regex = new RegExp(`\\b${fix.word}\\b`, 'gi');
        enhancedText = enhancedText.replace(
          regex,
          `<phoneme alphabet="ipa" ph="${fix.phonetic}">${fix.word}</phoneme>`
        );
      });

      // Add emphasis
      config.emphasisWords.forEach(word => {
        const regex = new RegExp(`\\b${word}\\b`, 'gi');
        enhancedText = enhancedText.replace(regex, `<emphasis level="strong">${word}</emphasis>`);
      });

      // Add pauses
      config.pauses.forEach(pause => {
        const regex = new RegExp(`\\b${pause.after_word}\\b`, 'gi');
        enhancedText = enhancedText.replace(
          regex,
          `${pause.after_word}<break time="${pause.duration_ms}ms"/>`
        );
      });

      ssml += enhancedText;

      if (config.emotion && config.emotion !== 'neutral') {
        ssml += '</prosody>';
      }

      ssml += '</speak>';
      setProviderPrompt(ssml);

    } else if (config.provider === 'openai') {
      // OpenAI TTS: Simple text with punctuation for pacing
      let enhancedText = prompt;

      // Use punctuation for pauses
      config.pauses.forEach(pause => {
        const regex = new RegExp(`\\b${pause.after_word}\\b`, 'gi');
        const pauseMarker = pause.duration_ms > 300 ? '...' : ',';
        enhancedText = enhancedText.replace(regex, `${pause.after_word}${pauseMarker}`);
      });

      // Capitalize emphasized words
      config.emphasisWords.forEach(word => {
        const regex = new RegExp(`\\b${word}\\b`, 'gi');
        enhancedText = enhancedText.replace(regex, word.toUpperCase());
      });

      setProviderPrompt(enhancedText);
    }
  };

  const handleWordClick = (word: string) => {
    setSelectedWord(word);
    setShowPronunciationHelper(true);
  };

  const addPronunciationFix = (word: string, phonetic: string) => {
    setConfig(prev => ({
      ...prev,
      pronunciationFixes: [
        ...prev.pronunciationFixes.filter(f => f.word !== word),
        { word, phonetic }
      ]
    }));
    setShowPronunciationHelper(false);
  };

  const toggleEmphasis = (word: string) => {
    setConfig(prev => ({
      ...prev,
      emphasisWords: prev.emphasisWords.includes(word)
        ? prev.emphasisWords.filter(w => w !== word)
        : [...prev.emphasisWords, word]
    }));
  };

  const addPause = (word: string, duration: number) => {
    setConfig(prev => ({
      ...prev,
      pauses: [
        ...prev.pauses.filter(p => p.after_word !== word),
        { after_word: word, duration_ms: duration }
      ]
    }));
  };

  const generateAudio = async () => {
    try {
      setIsGenerating(true);

      const response = await fetch(apiUrl('/api/audio/generate'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: config.text,
          provider_prompt: providerPrompt,
          provider: config.provider,
          voice: config.voice,
          speed: config.speed,
          pitch: config.pitch,
          volume: config.volume / 100,
          emotion: config.emotion,
          pronunciation_fixes: config.pronunciationFixes
        })
      });

      const result = await response.json();
      setGeneratedAudio(result.audio_url);
      onGenerate?.(result.audio_url, config);

      // Auto-play
      const audio = new Audio(result.audio_url);
      setAudioElement(audio);
      audio.play();
      setIsPlaying(true);
      audio.onended = () => setIsPlaying(false);
    } catch (error) {
      console.error('Error generating audio:', error);
      alert('Failed to generate audio. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const togglePlayback = () => {
    if (!audioElement || !generatedAudio) return;

    if (isPlaying) {
      audioElement.pause();
      setIsPlaying(false);
    } else {
      audioElement.play();
      setIsPlaying(true);
    }
  };

  const words = config.text.split(/\s+/);

  return (
    <div className="space-y-6">
      {/* Provider Selection */}
      <div className="bg-gray-800 rounded-lg p-4">
        <label className="block text-sm font-semibold text-gray-300 mb-2">
          TTS Provider
        </label>
        <div className="grid grid-cols-3 gap-3">
          {(['elevenlabs', 'google', 'openai'] as const).map(provider => (
            <button
              key={provider}
              onClick={() => setConfig(prev => ({ ...prev, provider }))}
              className={`px-4 py-3 rounded-lg transition ${
                config.provider === provider
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              <div className="text-sm font-medium capitalize">{provider}</div>
              <div className="text-xs text-gray-400 mt-1">
                {provider === 'elevenlabs' && 'Premium quality'}
                {provider === 'google' && 'SSML support'}
                {provider === 'openai' && 'Fast & cheap'}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Text Editor with Word Selection */}
      <div className="bg-gray-800 rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <label className="text-sm font-semibold text-gray-300">
            Script Text
          </label>
          <div className="text-xs text-gray-400">
            Click words to add pronunciation fixes or emphasis
          </div>
        </div>

        <div className="bg-gray-900 rounded-lg p-4 min-h-32 flex flex-wrap gap-2">
          {words.map((word, idx) => {
            const hasPronounciation = config.pronunciationFixes.some(f => f.word === word);
            const hasEmphasis = config.emphasisWords.includes(word);
            const hasPause = config.pauses.some(p => p.after_word === word);

            return (
              <button
                key={idx}
                onClick={() => handleWordClick(word)}
                className={`px-2 py-1 rounded text-sm transition ${
                  hasPronounciation
                    ? 'bg-yellow-600 text-white'
                    : hasEmphasis
                    ? 'bg-purple-600 text-white'
                    : hasPause
                    ? 'bg-blue-600 text-white'
                    : 'hover:bg-gray-700 text-gray-200'
                }`}
              >
                {word}
              </button>
            );
          })}
        </div>

        {/* Legend */}
        <div className="flex items-center space-x-4 mt-3 text-xs text-gray-400">
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-yellow-600 rounded"></div>
            <span>Pronunciation fixed</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-purple-600 rounded"></div>
            <span>Emphasized</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-blue-600 rounded"></div>
            <span>Pause after</span>
          </div>
        </div>
      </div>

      {/* Word Helper Modal */}
      {showPronunciationHelper && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-bold text-white mb-4">
              Edit: "{selectedWord}"
            </h3>

            <div className="space-y-4">
              {/* Pronunciation Fix */}
              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">
                  Pronunciation (IPA)
                </label>
                <input
                  type="text"
                  placeholder="e.g., ˈθiːtə (for theta)"
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      addPronunciationFix(selectedWord, e.currentTarget.value);
                    }
                  }}
                />
                <div className="text-xs text-gray-400 mt-1">
                  Press Enter to apply. Use IPA notation for best results.
                </div>
              </div>

              {/* Quick Actions */}
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => {
                    toggleEmphasis(selectedWord);
                    setShowPronunciationHelper(false);
                  }}
                  className={`px-4 py-2 rounded-lg transition ${
                    config.emphasisWords.includes(selectedWord)
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {config.emphasisWords.includes(selectedWord) ? 'Remove' : 'Add'} Emphasis
                </button>

                <button
                  onClick={() => {
                    addPause(selectedWord, 500);
                    setShowPronunciationHelper(false);
                  }}
                  className="px-4 py-2 bg-gray-700 text-gray-300 hover:bg-gray-600 rounded-lg transition"
                >
                  Add Pause After
                </button>
              </div>

              <button
                onClick={() => setShowPronunciationHelper(false)}
                className="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Voice Controls */}
      <div className="grid grid-cols-2 gap-4">
        {/* Speed */}
        <div className="bg-gray-800 rounded-lg p-4">
          <label className="block text-sm font-semibold text-gray-300 mb-2">
            Speed: {config.speed}x
          </label>
          <input
            type="range"
            min="0.5"
            max="2"
            step="0.1"
            value={config.speed}
            onChange={(e) => setConfig(prev => ({ ...prev, speed: parseFloat(e.target.value) }))}
            className="w-full"
          />
        </div>

        {/* Pitch (Google only) */}
        {config.provider === 'google' && (
          <div className="bg-gray-800 rounded-lg p-4">
            <label className="block text-sm font-semibold text-gray-300 mb-2">
              Pitch: {config.pitch > 0 ? '+' : ''}{config.pitch}st
            </label>
            <input
              type="range"
              min="-10"
              max="10"
              step="1"
              value={config.pitch}
              onChange={(e) => setConfig(prev => ({ ...prev, pitch: parseInt(e.target.value) }))}
              className="w-full"
            />
          </div>
        )}

        {/* Emotion (ElevenLabs) */}
        {config.provider === 'elevenlabs' && (
          <div className="bg-gray-800 rounded-lg p-4">
            <label className="block text-sm font-semibold text-gray-300 mb-2">
              Emotion
            </label>
            <select
              value={config.emotion}
              onChange={(e) => setConfig(prev => ({ ...prev, emotion: e.target.value }))}
              className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white"
            >
              <option value="neutral">Neutral</option>
              <option value="excited">Excited</option>
              <option value="calm">Calm</option>
              <option value="sad">Sad</option>
              <option value="angry">Angry</option>
              <option value="fearful">Fearful</option>
            </select>
          </div>
        )}
      </div>

      {/* Provider-Specific Prompt Preview */}
      {showProviderPrompt && (
        <div className="bg-gray-800 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm font-semibold text-gray-300 flex items-center space-x-2">
              <Sparkles className="w-4 h-4" />
              <span>{config.provider.charAt(0).toUpperCase() + config.provider.slice(1)}-Optimized Prompt</span>
            </label>
            <div className="flex items-center space-x-1 text-xs text-green-400">
              <CheckCircle className="w-4 h-4" />
              <span>Auto-generated</span>
            </div>
          </div>
          <pre className="bg-gray-900 rounded-lg p-3 text-xs text-gray-300 whitespace-pre-wrap max-h-32 overflow-y-auto">
            {providerPrompt}
          </pre>
          <div className="text-xs text-gray-400 mt-2">
            {config.provider === 'elevenlabs' && '✓ Includes phonetic notation and emphasis markers'}
            {config.provider === 'google' && '✓ Full SSML with prosody and phonemes'}
            {config.provider === 'openai' && '✓ Optimized punctuation for natural pacing'}
          </div>
        </div>
      )}

      {/* Generate Button */}
      <div className="flex items-center space-x-3">
        <button
          onClick={generateAudio}
          disabled={isGenerating}
          className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg transition flex items-center justify-center space-x-2"
        >
          {isGenerating ? (
            <>
              <RefreshCw className="w-5 h-5 animate-spin" />
              <span>Generating...</span>
            </>
          ) : (
            <>
              <Volume2 className="w-5 h-5" />
              <span>Generate Voice</span>
            </>
          )}
        </button>

        {generatedAudio && (
          <button
            onClick={togglePlayback}
            className="px-6 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg transition flex items-center space-x-2"
          >
            {isPlaying ? (
              <>
                <Pause className="w-5 h-5" />
                <span>Pause</span>
              </>
            ) : (
              <>
                <Play className="w-5 h-5" />
                <span>Play</span>
              </>
            )}
          </button>
        )}
      </div>

      {/* Current Fixes Display */}
      {(config.pronunciationFixes.length > 0 || config.emphasisWords.length > 0 || config.pauses.length > 0) && (
        <div className="bg-gray-800 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-gray-300 mb-3">Applied Modifications</h4>
          <div className="space-y-2 text-sm">
            {config.pronunciationFixes.map((fix, idx) => (
              <div key={idx} className="flex items-center justify-between text-yellow-400">
                <span>"{fix.word}" → [{fix.phonetic}]</span>
                <button
                  onClick={() => setConfig(prev => ({
                    ...prev,
                    pronunciationFixes: prev.pronunciationFixes.filter(f => f.word !== fix.word)
                  }))}
                  className="text-xs text-gray-400 hover:text-red-400"
                >
                  Remove
                </button>
              </div>
            ))}
            {config.emphasisWords.map((word, idx) => (
              <div key={idx} className="flex items-center justify-between text-purple-400">
                <span>Emphasis: "{word}"</span>
                <button
                  onClick={() => toggleEmphasis(word)}
                  className="text-xs text-gray-400 hover:text-red-400"
                >
                  Remove
                </button>
              </div>
            ))}
            {config.pauses.map((pause, idx) => (
              <div key={idx} className="flex items-center justify-between text-blue-400">
                <span>Pause after "{pause.after_word}" ({pause.duration_ms}ms)</span>
                <button
                  onClick={() => setConfig(prev => ({
                    ...prev,
                    pauses: prev.pauses.filter(p => p.after_word !== pause.after_word)
                  }))}
                  className="text-xs text-gray-400 hover:text-red-400"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default VoiceEditor;
