import React from 'react';
import { Camera, Check } from 'lucide-react';

interface ShotTypeSelectorProps {
  selected: string;
  onSelect: (shotType: string) => void;
}

const shotTypes = {
  establishing_wide: {
    name: 'Establishing Wide',
    description: 'Wide shot establishing location and context',
    duration: '4-8s',
    lens: '24-35mm'
  },
  wide_master: {
    name: 'Wide Master',
    description: 'Scene-covering wide showing all action',
    duration: '5-15s',
    lens: '28-40mm'
  },
  medium_shot: {
    name: 'Medium Shot',
    description: 'Waist-up framing, balanced character and environment',
    duration: '3-8s',
    lens: '50mm'
  },
  medium_closeup: {
    name: 'Medium Close-Up',
    description: 'Chest-up emphasizing facial expressions',
    duration: '2-6s',
    lens: '75-85mm'
  },
  closeup_character: {
    name: 'Close-Up',
    description: 'Face-filling for maximum emotional impact',
    duration: '2-5s',
    lens: '85-135mm'
  },
  extreme_closeup: {
    name: 'Extreme Close-Up',
    description: 'Detail-focused for emphasis',
    duration: '1-3s',
    lens: '100-200mm'
  },
  over_shoulder: {
    name: 'Over-the-Shoulder',
    description: 'Framing subject over another character\'s shoulder',
    duration: '2-6s',
    lens: '50-85mm'
  },
  two_shot: {
    name: 'Two Shot',
    description: 'Framing two subjects showing relationship',
    duration: '3-8s',
    lens: '40-50mm'
  },
  action_dynamic: {
    name: 'Dynamic Action',
    description: 'High-energy capturing fast movement',
    duration: '1-4s',
    lens: '24-50mm'
  },
  pov_subjective: {
    name: 'Point of View (POV)',
    description: 'Camera as character\'s eyes',
    duration: '2-6s',
    lens: '40-50mm'
  },
  insert_detail: {
    name: 'Insert Detail',
    description: 'Close shot of object or action detail',
    duration: '1-3s',
    lens: '60-100mm'
  },
  reaction_shot: {
    name: 'Reaction Shot',
    description: 'Close-up capturing character\'s reaction',
    duration: '1-4s',
    lens: '85-135mm'
  }
};

const ShotTypeSelector: React.FC<ShotTypeSelectorProps> = ({ selected, onSelect }) => {
  return (
    <div className="space-y-2 max-h-[600px] overflow-y-auto custom-scrollbar">
      {Object.entries(shotTypes).map(([key, shot]) => (
        <button
          key={key}
          onClick={() => onSelect(key)}
          className={`w-full text-left p-3 rounded-lg transition border ${
            selected === key
              ? 'bg-purple-600 bg-opacity-30 border-purple-400'
              : 'bg-gray-800 bg-opacity-30 border-gray-700 hover:border-purple-500'
          }`}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-1">
                <Camera className="w-4 h-4 text-purple-400" />
                <h4 className="font-semibold text-sm">{shot.name}</h4>
              </div>
              <p className="text-xs text-gray-300 mb-1">{shot.description}</p>
              <div className="flex space-x-3 text-xs text-gray-400">
                <span>⏱️ {shot.duration}</span>
                <span>📷 {shot.lens}</span>
              </div>
            </div>
            {selected === key && (
              <Check className="w-5 h-5 text-green-400 ml-2 flex-shrink-0" />
            )}
          </div>
        </button>
      ))}
    </div>
  );
};

export default ShotTypeSelector;
