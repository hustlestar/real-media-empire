import React, { useState } from 'react';
import { Film, ChevronDown, ChevronUp, Play, Copy, Download } from 'lucide-react';

interface Shot {
  shot_number: number;
  prompt: string;
  negative_prompt: string;
  metadata: {
    style: string;
    shot_type: string;
    lighting: string;
    emotion: string;
  };
  duration_seconds: number;
}

interface SceneSequencerProps {
  shots: Shot[];
}

const SceneSequencer: React.FC<SceneSequencerProps> = ({ shots }) => {
  const [expandedShot, setExpandedShot] = useState<number | null>(null);

  const toggleShot = (shotNumber: number) => {
    setExpandedShot(expandedShot === shotNumber ? null : shotNumber);
  };

  const copyAllPrompts = () => {
    const allPrompts = shots
      .map((shot, idx) => `SHOT ${idx + 1}:\n${shot.prompt}`)
      .join('\n\n---\n\n');
    navigator.clipboard.writeText(allPrompts);
  };

  const downloadScene = () => {
    const content = shots
      .map((shot, idx) => `
SHOT ${idx + 1} - ${shot.metadata.shot_type.replace(/_/g, ' ').toUpperCase()}
${'='.repeat(60)}

Duration: ${shot.duration_seconds}s
Style: ${shot.metadata.style.replace(/_/g, ' ')}
Lighting: ${shot.metadata.lighting.replace(/_/g, ' ')}
Emotion: ${shot.metadata.emotion.replace(/_/g, ' ')}

PROMPT:
${shot.prompt}

NEGATIVE PROMPT:
${shot.negative_prompt}
      `.trim())
      .join('\n\n' + '='.repeat(60) + '\n\n');

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'scene_sequence.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  const totalDuration = shots.reduce((sum, shot) => sum + shot.duration_seconds, 0);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-4 border border-purple-500 border-opacity-30">
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="flex items-center space-x-2 mb-1">
              <Film className="w-5 h-5 text-purple-400" />
              <h3 className="font-bold">Scene Sequence</h3>
            </div>
            <div className="text-sm text-gray-400">
              {shots.length} shots • {totalDuration}s total
            </div>
          </div>

          <div className="flex space-x-2">
            <button
              onClick={copyAllPrompts}
              className="p-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition"
              title="Copy all prompts"
            >
              <Copy className="w-4 h-4" />
            </button>

            <button
              onClick={downloadScene}
              className="p-2 bg-purple-600 hover:bg-purple-500 rounded-lg transition"
              title="Download scene"
            >
              <Download className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Timeline */}
        <div className="bg-gray-900 bg-opacity-50 rounded-lg p-3">
          <div className="flex items-center space-x-1">
            {shots.map((shot, idx) => (
              <div
                key={idx}
                className="flex-1 h-8 bg-purple-600 bg-opacity-70 rounded flex items-center justify-center text-xs font-semibold hover:bg-opacity-100 transition cursor-pointer"
                onClick={() => toggleShot(shot.shot_number)}
                title={`Shot ${idx + 1}: ${shot.metadata.shot_type} (${shot.duration_seconds}s)`}
              >
                {idx + 1}
              </div>
            ))}
          </div>
          <div className="flex items-center justify-between mt-2 text-xs text-gray-400">
            <span>0s</span>
            <span>{totalDuration}s</span>
          </div>
        </div>
      </div>

      {/* Shot List */}
      <div className="space-y-3">
        {shots.map((shot, idx) => (
          <div
            key={shot.shot_number}
            className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl border border-purple-500 border-opacity-30 overflow-hidden"
          >
            {/* Shot Header */}
            <button
              onClick={() => toggleShot(shot.shot_number)}
              className="w-full p-4 flex items-center justify-between hover:bg-white hover:bg-opacity-5 transition"
            >
              <div className="flex items-center space-x-4">
                <div className="w-10 h-10 bg-purple-600 rounded-lg flex items-center justify-center font-bold">
                  {idx + 1}
                </div>

                <div className="text-left">
                  <div className="font-semibold text-sm">
                    {shot.metadata.shot_type.replace(/_/g, ' ').toUpperCase()}
                  </div>
                  <div className="text-xs text-gray-400">
                    {shot.duration_seconds}s • {shot.metadata.style.replace(/_/g, ' ')}
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <div className="hidden md:flex space-x-2 text-xs">
                  <span className="px-2 py-1 bg-gray-700 rounded">
                    {shot.metadata.lighting.replace(/_/g, ' ')}
                  </span>
                  <span className="px-2 py-1 bg-gray-700 rounded">
                    {shot.metadata.emotion.replace(/_/g, ' ')}
                  </span>
                </div>

                {expandedShot === shot.shot_number ? (
                  <ChevronUp className="w-5 h-5 text-gray-400" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-gray-400" />
                )}
              </div>
            </button>

            {/* Shot Details (Expanded) */}
            {expandedShot === shot.shot_number && (
              <div className="border-t border-gray-700 p-4 space-y-4">
                {/* Prompt */}
                <div>
                  <div className="text-xs font-semibold text-purple-300 mb-2">PROMPT</div>
                  <div className="bg-gray-900 bg-opacity-50 rounded-lg p-3 text-sm text-gray-300 leading-relaxed">
                    {shot.prompt}
                  </div>
                </div>

                {/* Negative Prompt */}
                {shot.negative_prompt && (
                  <div>
                    <div className="text-xs font-semibold text-red-300 mb-2">NEGATIVE PROMPT</div>
                    <div className="bg-red-900 bg-opacity-20 rounded-lg p-3 text-xs text-gray-300">
                      {shot.negative_prompt}
                    </div>
                  </div>
                )}

                {/* Metadata Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div className="bg-gray-900 bg-opacity-50 rounded p-2">
                    <div className="text-xs text-gray-400">Style</div>
                    <div className="text-sm font-semibold mt-1">
                      {shot.metadata.style.replace(/_/g, ' ')}
                    </div>
                  </div>

                  <div className="bg-gray-900 bg-opacity-50 rounded p-2">
                    <div className="text-xs text-gray-400">Shot Type</div>
                    <div className="text-sm font-semibold mt-1">
                      {shot.metadata.shot_type.replace(/_/g, ' ')}
                    </div>
                  </div>

                  <div className="bg-gray-900 bg-opacity-50 rounded p-2">
                    <div className="text-xs text-gray-400">Lighting</div>
                    <div className="text-sm font-semibold mt-1">
                      {shot.metadata.lighting.replace(/_/g, ' ')}
                    </div>
                  </div>

                  <div className="bg-gray-900 bg-opacity-50 rounded p-2">
                    <div className="text-xs text-gray-400">Emotion</div>
                    <div className="text-sm font-semibold mt-1">
                      {shot.metadata.emotion.replace(/_/g, ' ')}
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex space-x-2">
                  <button
                    onClick={() => navigator.clipboard.writeText(shot.prompt)}
                    className="flex-1 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition text-sm flex items-center justify-center space-x-2"
                  >
                    <Copy className="w-4 h-4" />
                    <span>Copy Prompt</span>
                  </button>

                  <button
                    className="px-4 py-2 bg-purple-600 hover:bg-purple-500 rounded-lg transition text-sm flex items-center space-x-2"
                    title="Generate video from this shot"
                  >
                    <Play className="w-4 h-4" />
                    <span>Generate</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Scene Actions */}
      <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-4 border border-purple-500 border-opacity-30">
        <button className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 rounded-lg font-bold transition flex items-center justify-center space-x-2">
          <Play className="w-5 h-5" />
          <span>Generate Complete Scene</span>
        </button>
      </div>
    </div>
  );
};

export default SceneSequencer;
