import React, { useState } from 'react';
import { User, Activity, MapPin, Info, Users, Video, Sparkles } from 'lucide-react';

interface PromptConfig {
  subject: string;
  action: string;
  location: string;
  additionalDetails: string;
  characterConsistency: string;
  cameraMotion: string;
  [key: string]: string;
}

interface PromptBuilderProps {
  config: PromptConfig;
  onChange: (config: PromptConfig) => void;
}

const PromptBuilder: React.FC<PromptBuilderProps> = ({ config, onChange }) => {
  const [generatingField, setGeneratingField] = useState<string | null>(null);

  const handleChange = (field: string, value: string) => {
    onChange({ ...config, [field]: value });
  };

  // AI Assist: Generate suggestions for fields
  const handleAIAssist = async (field: string) => {
    setGeneratingField(field);

    try {
      // Create context from existing fields
      const context = {
        subject: config.subject || null,
        action: config.action || null,
        location: config.location || null
      };

      // Simple AI generation based on field type
      // In production, this would call an AI API
      let suggestion = '';

      switch (field) {
        case 'subject':
          // Generate character description
          if (config.action) {
            suggestion = 'Professional actor in their 30s, confident demeanor, wearing modern business casual attire';
          } else {
            suggestion = 'Charismatic protagonist, distinctive features, natural presence';
          }
          break;

        case 'action':
          // Generate action description
          if (config.subject) {
            suggestion = `${config.subject.split(',')[0] || 'The character'} performing a pivotal moment of realization, subtle expressions conveying inner transformation`;
          } else {
            suggestion = 'Contemplative moment of discovery, nuanced performance capturing emotional depth';
          }
          break;

        case 'location':
          // Generate location description
          if (config.action.includes('office') || config.action.includes('work')) {
            suggestion = 'Contemporary office space with glass walls, natural light streaming through floor-to-ceiling windows, minimalist modern design';
          } else {
            suggestion = 'Atmospheric interior with dramatic lighting, cinematic composition, rich visual textures';
          }
          break;

        case 'additionalDetails':
          suggestion = 'Specific wardrobe details: tailored fit, neutral color palette. Props: laptop, coffee cup. Makeup: natural, professional.';
          break;

        default:
          suggestion = 'AI-generated suggestion';
      }

      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 800));

      handleChange(field, suggestion);
    } catch (error) {
      console.error('AI assist error:', error);
    } finally {
      setGeneratingField(null);
    }
  };

  return (
    <div className="space-y-4">
      {/* Subject */}
      <div>
        <label className="block text-sm font-semibold mb-2 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <User className="w-4 h-4 text-purple-400" />
            <span>Subject / Character</span>
            <span className="text-red-400">*</span>
          </div>
          <button
            type="button"
            onClick={() => handleAIAssist('subject')}
            disabled={generatingField === 'subject'}
            className="flex items-center space-x-1 px-3 py-1 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:from-gray-600 disabled:to-gray-600 rounded-lg text-xs font-semibold transition"
            title="Generate with AI"
          >
            {generatingField === 'subject' ? (
              <>
                <Sparkles className="w-3 h-3 animate-spin" />
                <span>Generating...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-3 h-3" />
                <span>AI Assist</span>
              </>
            )}
          </button>
        </label>
        <input
          type="text"
          value={config.subject}
          onChange={(e) => handleChange('subject', e.target.value)}
          placeholder="Emma, professional woman in her 30s, confident CEO"
          className="w-full px-4 py-3 bg-gray-900 bg-opacity-70 border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none transition"
        />
        <p className="text-xs text-gray-400 mt-1">
          Describe the main subject(s) in detail. Include age, appearance, clothing, character traits.
        </p>
      </div>

      {/* Action */}
      <div>
        <label className="block text-sm font-semibold mb-2 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Activity className="w-4 h-4 text-purple-400" />
            <span>Action / What's Happening</span>
            <span className="text-red-400">*</span>
          </div>
          <button
            type="button"
            onClick={() => handleAIAssist('action')}
            disabled={generatingField === 'action'}
            className="flex items-center space-x-1 px-3 py-1 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:from-gray-600 disabled:to-gray-600 rounded-lg text-xs font-semibold transition"
            title="Generate with AI"
          >
            {generatingField === 'action' ? (
              <>
                <Sparkles className="w-3 h-3 animate-spin" />
                <span>Generating...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-3 h-3" />
                <span>AI Assist</span>
              </>
            )}
          </button>
        </label>
        <textarea
          value={config.action}
          onChange={(e) => handleChange('action', e.target.value)}
          placeholder="reviewing successful product metrics on laptop, moment of triumph, realization of achievement"
          rows={3}
          className="w-full px-4 py-3 bg-gray-900 bg-opacity-70 border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none transition resize-none"
        />
        <p className="text-xs text-gray-400 mt-1">
          Describe the action, moment, or story beat happening in this shot.
        </p>
      </div>

      {/* Location */}
      <div>
        <label className="block text-sm font-semibold mb-2 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <MapPin className="w-4 h-4 text-purple-400" />
            <span>Location / Setting</span>
            <span className="text-red-400">*</span>
          </div>
          <button
            type="button"
            onClick={() => handleAIAssist('location')}
            disabled={generatingField === 'location'}
            className="flex items-center space-x-1 px-3 py-1 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:from-gray-600 disabled:to-gray-600 rounded-lg text-xs font-semibold transition"
            title="Generate with AI"
          >
            {generatingField === 'location' ? (
              <>
                <Sparkles className="w-3 h-3 animate-spin" />
                <span>Generating...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-3 h-3" />
                <span>AI Assist</span>
              </>
            )}
          </button>
        </label>
        <input
          type="text"
          value={config.location}
          onChange={(e) => handleChange('location', e.target.value)}
          placeholder="modern tech office with floor-to-ceiling windows, city skyline visible, golden hour light"
          className="w-full px-4 py-3 bg-gray-900 bg-opacity-70 border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none transition"
        />
        <p className="text-xs text-gray-400 mt-1">
          Describe the location, environment, time of day, weather, and atmosphere.
        </p>
      </div>

      {/* Character Consistency */}
      <div>
        <label className="block text-sm font-semibold mb-2 flex items-center space-x-2">
          <Users className="w-4 h-4 text-purple-400" />
          <span>Character Consistency (Optional)</span>
        </label>
        <input
          type="text"
          value={config.characterConsistency}
          onChange={(e) => handleChange('characterConsistency', e.target.value)}
          placeholder="same woman from previous shots, reference: char_emma_001"
          className="w-full px-4 py-3 bg-gray-900 bg-opacity-70 border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none transition"
        />
        <p className="text-xs text-gray-400 mt-1">
          Reference to maintain character consistency across shots.
        </p>
      </div>

      {/* Camera Motion */}
      <div>
        <label className="block text-sm font-semibold mb-2 flex items-center space-x-2">
          <Video className="w-4 h-4 text-purple-400" />
          <span>Camera Motion (Optional)</span>
        </label>
        <select
          value={config.cameraMotion}
          onChange={(e) => handleChange('cameraMotion', e.target.value)}
          className="w-full px-4 py-3 bg-gray-900 bg-opacity-70 border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none transition"
        >
          <option value="">None / Locked-off</option>
          <option value="slow_push_in">Slow Push-In</option>
          <option value="slow_pull_out">Slow Pull-Out</option>
          <option value="pan_left">Pan Left</option>
          <option value="pan_right">Pan Right</option>
          <option value="tilt_up">Tilt Up</option>
          <option value="tilt_down">Tilt Down</option>
          <option value="dolly_track">Dolly Track</option>
          <option value="steadicam_follow">Steadicam Follow</option>
          <option value="handheld">Handheld</option>
          <option value="crane_up">Crane Up</option>
          <option value="crane_down">Crane Down</option>
        </select>
        <p className="text-xs text-gray-400 mt-1">
          Specify camera movement during the shot.
        </p>
      </div>

      {/* Additional Details */}
      <div>
        <label className="block text-sm font-semibold mb-2 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Info className="w-4 h-4 text-purple-400" />
            <span>Additional Details (Optional)</span>
          </div>
          <button
            type="button"
            onClick={() => handleAIAssist('additionalDetails')}
            disabled={generatingField === 'additionalDetails'}
            className="flex items-center space-x-1 px-3 py-1 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:from-gray-600 disabled:to-gray-600 rounded-lg text-xs font-semibold transition"
            title="Generate with AI"
          >
            {generatingField === 'additionalDetails' ? (
              <>
                <Sparkles className="w-3 h-3 animate-spin" />
                <span>Generating...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-3 h-3" />
                <span>AI Assist</span>
              </>
            )}
          </button>
        </label>
        <textarea
          value={config.additionalDetails}
          onChange={(e) => handleChange('additionalDetails', e.target.value)}
          placeholder="Add any specific details: props, wardrobe, makeup, special effects, etc."
          rows={2}
          className="w-full px-4 py-3 bg-gray-900 bg-opacity-70 border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none transition resize-none"
        />
        <p className="text-xs text-gray-400 mt-1">
          Any additional creative direction or specific requirements.
        </p>
      </div>

      {/* Tips */}
      <div className="bg-purple-900 bg-opacity-20 border border-purple-500 border-opacity-30 rounded-lg p-4">
        <h4 className="font-semibold text-sm mb-2 text-purple-300">💡 Pro Tips</h4>
        <ul className="text-xs text-gray-300 space-y-1">
          <li>• Be specific with descriptions - detail creates better results</li>
          <li>• Include time of day and lighting conditions in location</li>
          <li>• Character details help AI understand the subject better</li>
          <li>• Reference films, directors, or specific visual styles when possible</li>
        </ul>
      </div>
    </div>
  );
};

export default PromptBuilder;
