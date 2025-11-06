import React from 'react';
import { FileText, Users, Palette } from 'lucide-react';

interface PresentationConfigProps {
  config: any;
  onChange: (updates: any) => void;
}

const tones = [
  { value: 'professional', label: 'Professional', icon: '💼', desc: 'Business and corporate' },
  { value: 'casual', label: 'Casual', icon: '😊', desc: 'Friendly and relaxed' },
  { value: 'motivational', label: 'Motivational', icon: '🚀', desc: 'Inspiring and energetic' },
  { value: 'educational', label: 'Educational', icon: '📚', desc: 'Teaching and informative' },
  { value: 'sales', label: 'Sales', icon: '💰', desc: 'Persuasive and compelling' },
  { value: 'technical', label: 'Technical', icon: '⚙️', desc: 'Detailed and precise' }
];

const PresentationConfig: React.FC<PresentationConfigProps> = ({ config, onChange }) => {
  return (
    <div className="space-y-6">
      {/* Number of Slides */}
      <div>
        <label className="block text-sm font-semibold mb-2 flex items-center space-x-2">
          <FileText className="w-4 h-4 text-blue-400" />
          <span>Number of Slides</span>
        </label>
        <div className="flex items-center space-x-4">
          <input
            type="range"
            min="5"
            max="30"
            step="1"
            value={config.numSlides}
            onChange={(e) => onChange({ numSlides: parseInt(e.target.value) })}
            className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
          />
          <div className="w-16 px-3 py-2 bg-gray-900 bg-opacity-70 border border-gray-700 rounded-lg text-center font-bold">
            {config.numSlides}
          </div>
        </div>
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>5 slides</span>
          <span>30 slides</span>
        </div>
      </div>

      {/* Tone Selection */}
      <div>
        <label className="block text-sm font-semibold mb-3 flex items-center space-x-2">
          <Palette className="w-4 h-4 text-blue-400" />
          <span>Presentation Tone</span>
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {tones.map((tone) => (
            <button
              key={tone.value}
              onClick={() => onChange({ tone: tone.value })}
              className={`p-3 rounded-lg transition border-2 text-left ${
                config.tone === tone.value
                  ? 'bg-blue-600 bg-opacity-30 border-blue-400'
                  : 'bg-gray-800 bg-opacity-50 border-gray-700 hover:border-blue-500'
              }`}
            >
              <div className="text-2xl mb-1">{tone.icon}</div>
              <div className="font-semibold text-sm">{tone.label}</div>
              <div className="text-xs text-gray-400 mt-1">{tone.desc}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Target Audience */}
      <div>
        <label className="block text-sm font-semibold mb-2 flex items-center space-x-2">
          <Users className="w-4 h-4 text-blue-400" />
          <span>Target Audience (Optional)</span>
        </label>
        <input
          type="text"
          value={config.targetAudience}
          onChange={(e) => onChange({ targetAudience: e.target.value })}
          placeholder="e.g., Executives, Developers, Students, General public"
          className="w-full px-4 py-3 bg-gray-900 bg-opacity-70 border border-gray-700 rounded-lg focus:border-blue-500 focus:outline-none transition"
        />
        <p className="text-xs text-gray-400 mt-2">
          Specifying the audience helps tailor language and complexity
        </p>
      </div>

      {/* Model Selection */}
      <div>
        <label className="block text-sm font-semibold mb-2">
          AI Model
        </label>
        <select
          value={config.model}
          onChange={(e) => onChange({ model: e.target.value })}
          className="w-full px-4 py-3 bg-gray-900 bg-opacity-70 border border-gray-700 rounded-lg focus:border-blue-500 focus:outline-none transition"
        >
          <option value="gpt-4o-mini">GPT-4o Mini (Fast & Affordable)</option>
          <option value="gpt-4o">GPT-4o (Balanced)</option>
          <option value="gpt-3.5-turbo">GPT-3.5 Turbo (Fastest)</option>
        </select>
        <div className="flex items-center space-x-4 mt-2 text-xs text-gray-400">
          <span>Speed: {
            config.model === 'gpt-3.5-turbo' ? '⚡⚡⚡' :
            config.model === 'gpt-4o-mini' ? '⚡⚡' : '⚡'
          }</span>
          <span>Cost: {
            config.model === 'gpt-3.5-turbo' ? '$' :
            config.model === 'gpt-4o-mini' ? '$$' : '$$$'
          }</span>
          <span>Quality: {
            config.model === 'gpt-3.5-turbo' ? '⭐⭐⭐' :
            config.model === 'gpt-4o-mini' ? '⭐⭐⭐⭐' : '⭐⭐⭐⭐⭐'
          }</span>
        </div>
      </div>

      {/* Budget Limit */}
      <div>
        <label className="block text-sm font-semibold mb-2">
          Budget Limit (USD)
        </label>
        <div className="flex items-center space-x-3">
          <input
            type="number"
            step="0.10"
            min="0"
            value={config.budgetLimit || ''}
            onChange={(e) => onChange({ budgetLimit: e.target.value ? parseFloat(e.target.value) : null })}
            placeholder="No limit"
            className="flex-1 px-4 py-3 bg-gray-900 bg-opacity-70 border border-gray-700 rounded-lg focus:border-blue-500 focus:outline-none transition"
          />
          <button
            onClick={() => onChange({ budgetLimit: null })}
            className="px-4 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg transition text-sm"
          >
            No Limit
          </button>
        </div>
        <p className="text-xs text-gray-400 mt-2">
          Generation will stop if cost exceeds this amount
        </p>
      </div>

      {/* Quick Presets */}
      <div className="bg-blue-900 bg-opacity-20 border border-blue-600 border-opacity-30 rounded-lg p-4">
        <div className="text-xs font-semibold text-blue-300 mb-2">Quick Presets:</div>
        <div className="grid grid-cols-3 gap-2">
          <button
            onClick={() => onChange({ numSlides: 10, tone: 'professional', model: 'gpt-4o-mini', budgetLimit: 1.0 })}
            className="px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded text-xs transition"
          >
            Standard Business
          </button>
          <button
            onClick={() => onChange({ numSlides: 15, tone: 'sales', model: 'gpt-4o', budgetLimit: 2.0 })}
            className="px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded text-xs transition"
          >
            Sales Pitch
          </button>
          <button
            onClick={() => onChange({ numSlides: 20, tone: 'educational', model: 'gpt-4o-mini', budgetLimit: 1.5 })}
            className="px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded text-xs transition"
          >
            Training Course
          </button>
        </div>
      </div>
    </div>
  );
};

export default PresentationConfig;
