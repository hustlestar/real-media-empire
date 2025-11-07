import React, { useState } from 'react';
import { Eye, Copy, Download, Film, Lightbulb, Camera, Heart, AlertCircle, Zap, ChevronDown, ChevronUp } from 'lucide-react';

interface PromptResult {
  prompt: string;
  negative_prompt: string;
  metadata: {
    style: string;
    shot_type: string;
    lighting: string;
    emotion: string;
  };
  director_notes: string[];
  technical_notes: {
    camera: string[];
    lighting: string[];
    performance: string[];
  };
  ai_enhanced?: boolean;
  original_prompt?: string;
}

interface PromptPreviewProps {
  prompt: PromptResult;
}

const PromptPreview: React.FC<PromptPreviewProps> = ({ prompt }) => {
  const [showOriginal, setShowOriginal] = useState<boolean>(false);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    // Could add toast notification here
  };

  const downloadPrompt = () => {
    const content = `
CINEMATIC PROMPT
===============

${prompt.prompt}

NEGATIVE PROMPT
==============
${prompt.negative_prompt}

DIRECTOR'S NOTES
===============
${prompt.director_notes.join('\n')}

TECHNICAL NOTES
==============

Camera:
${prompt.technical_notes.camera.join('\n')}

Lighting:
${prompt.technical_notes.lighting.join('\n')}

Performance:
${prompt.technical_notes.performance.join('\n')}
    `.trim();

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'cinematic_prompt.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-4 border border-purple-500 border-opacity-30">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Eye className="w-5 h-5 text-purple-400" />
            <h3 className="font-bold">Generated Prompt</h3>
            {prompt.ai_enhanced && (
              <span className="px-2 py-1 bg-yellow-500 bg-opacity-20 text-yellow-300 text-xs rounded-full flex items-center space-x-1">
                <Zap className="w-3 h-3" />
                <span>AI Enhanced</span>
              </span>
            )}
          </div>

          <div className="flex space-x-2">
            <button
              onClick={() => copyToClipboard(prompt.prompt)}
              className="p-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition"
              title="Copy to clipboard"
            >
              <Copy className="w-4 h-4" />
            </button>

            <button
              onClick={downloadPrompt}
              className="p-2 bg-purple-600 hover:bg-purple-500 rounded-lg transition"
              title="Download"
            >
              <Download className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* AI Enhancement Info */}
        {prompt.ai_enhanced && prompt.original_prompt && (
          <div className="mb-4 bg-yellow-900 bg-opacity-20 border border-yellow-600 border-opacity-30 rounded-lg p-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-xs text-yellow-200">
                <Zap className="w-4 h-4" />
                <span className="font-semibold">AI-Enhanced Prompt</span>
                <span className="text-yellow-300 opacity-80">
                  • {Math.round(((prompt.prompt.length - prompt.original_prompt.length) / prompt.original_prompt.length) * 100)}% more detail
                </span>
              </div>
              <button
                onClick={() => setShowOriginal(!showOriginal)}
                className="text-xs text-yellow-300 hover:text-yellow-100 flex items-center space-x-1"
              >
                <span>{showOriginal ? 'Hide' : 'Compare with'} original</span>
                {showOriginal ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              </button>
            </div>
          </div>
        )}

        {/* Original Prompt Comparison */}
        {prompt.ai_enhanced && prompt.original_prompt && showOriginal && (
          <div className="mb-4 bg-gray-800 bg-opacity-50 rounded-lg p-4 border border-gray-600">
            <div className="text-xs font-semibold text-gray-400 mb-2">ORIGINAL PROMPT (Before AI Enhancement)</div>
            <div className="text-sm text-gray-400 leading-relaxed whitespace-pre-wrap opacity-75">
              {prompt.original_prompt}
            </div>
          </div>
        )}

        {/* Main Prompt */}
        <div className="bg-gray-900 bg-opacity-50 rounded-lg p-4 mb-4">
          {prompt.ai_enhanced && (
            <div className="text-xs font-semibold text-yellow-300 mb-2 flex items-center space-x-1">
              <Zap className="w-3 h-3" />
              <span>ENHANCED PROMPT</span>
            </div>
          )}
          <div className="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap">
            {prompt.prompt}
          </div>
        </div>

        {/* Negative Prompt */}
        {prompt.negative_prompt && (
          <div className="bg-red-900 bg-opacity-20 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <AlertCircle className="w-4 h-4 text-red-400" />
              <span className="text-sm font-semibold text-red-300">Negative Prompt</span>
            </div>
            <div className="text-xs text-gray-300 leading-relaxed">
              {prompt.negative_prompt}
            </div>
          </div>
        )}
      </div>

      {/* Metadata */}
      <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-4 border border-purple-500 border-opacity-30">
        <h4 className="font-semibold mb-3 flex items-center space-x-2">
          <Film className="w-4 h-4 text-purple-400" />
          <span>Configuration</span>
        </h4>

        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="bg-gray-900 bg-opacity-50 rounded p-3">
            <div className="text-xs text-gray-400 mb-1">Style</div>
            <div className="font-semibold">{prompt.metadata.style.replace(/_/g, ' ')}</div>
          </div>

          <div className="bg-gray-900 bg-opacity-50 rounded p-3">
            <div className="text-xs text-gray-400 mb-1">Shot Type</div>
            <div className="font-semibold">{prompt.metadata.shot_type.replace(/_/g, ' ')}</div>
          </div>

          <div className="bg-gray-900 bg-opacity-50 rounded p-3">
            <div className="text-xs text-gray-400 mb-1">Lighting</div>
            <div className="font-semibold">{prompt.metadata.lighting.replace(/_/g, ' ')}</div>
          </div>

          <div className="bg-gray-900 bg-opacity-50 rounded p-3">
            <div className="text-xs text-gray-400 mb-1">Emotion</div>
            <div className="font-semibold">{prompt.metadata.emotion.replace(/_/g, ' ')}</div>
          </div>
        </div>
      </div>

      {/* Director's Notes */}
      <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-4 border border-purple-500 border-opacity-30">
        <h4 className="font-semibold mb-3 flex items-center space-x-2">
          <Film className="w-4 h-4 text-purple-400" />
          <span>Director's Notes</span>
        </h4>

        <ul className="space-y-2">
          {prompt.director_notes.map((note, idx) => (
            <li key={idx} className="text-sm text-gray-300 flex items-start space-x-2">
              <span className="text-purple-400 mt-1">•</span>
              <span>{note}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Technical Notes */}
      <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-4 border border-purple-500 border-opacity-30">
        <h4 className="font-semibold mb-3">Technical Specifications</h4>

        <div className="space-y-4">
          {/* Camera */}
          <div>
            <div className="flex items-center space-x-2 mb-2">
              <Camera className="w-4 h-4 text-blue-400" />
              <span className="text-sm font-semibold text-blue-300">Camera</span>
            </div>
            <ul className="space-y-1 ml-6">
              {prompt.technical_notes.camera.map((note, idx) => (
                <li key={idx} className="text-xs text-gray-400">• {note}</li>
              ))}
            </ul>
          </div>

          {/* Lighting */}
          <div>
            <div className="flex items-center space-x-2 mb-2">
              <Lightbulb className="w-4 h-4 text-yellow-400" />
              <span className="text-sm font-semibold text-yellow-300">Lighting</span>
            </div>
            <ul className="space-y-1 ml-6">
              {prompt.technical_notes.lighting.map((note, idx) => (
                <li key={idx} className="text-xs text-gray-400">• {note}</li>
              ))}
            </ul>
          </div>

          {/* Performance */}
          <div>
            <div className="flex items-center space-x-2 mb-2">
              <Heart className="w-4 h-4 text-pink-400" />
              <span className="text-sm font-semibold text-pink-300">Performance</span>
            </div>
            <ul className="space-y-1 ml-6">
              {prompt.technical_notes.performance.map((note, idx) => (
                <li key={idx} className="text-xs text-gray-400">• {note}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PromptPreview;
