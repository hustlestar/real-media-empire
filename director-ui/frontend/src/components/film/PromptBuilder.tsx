import React, { useState } from 'react';
import { User, Activity, MapPin, Info, Users, Video } from 'lucide-react';
import AIEnhancer from '../AIEnhancer';

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
  const handleChange = (field: string, value: string) => {
    onChange({ ...config, [field]: value });
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
          <AIEnhancer
            fieldName="subject"
            fieldLabel="Subject / Character"
            formData={config}
            onUpdate={handleChange}
            enhancementPrompt="Generate a detailed character description including age, appearance, clothing, and character traits."
            variant="compact"
          />
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
          <AIEnhancer
            fieldName="action"
            fieldLabel="Action"
            formData={config}
            onUpdate={handleChange}
            enhancementPrompt="Generate a compelling action description focusing on the moment, story beat, and emotional beats happening in this shot."
            variant="compact"
          />
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
          <AIEnhancer
            fieldName="location"
            fieldLabel="Location / Setting"
            formData={config}
            onUpdate={handleChange}
            enhancementPrompt="Generate a vivid location description including environment, time of day, weather, lighting, and atmosphere."
            variant="compact"
          />
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
          <AIEnhancer
            fieldName="additionalDetails"
            fieldLabel="Additional Details"
            formData={config}
            onUpdate={handleChange}
            enhancementPrompt="Generate specific production details including props, wardrobe, makeup, special effects, and other creative direction."
            variant="compact"
          />
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
