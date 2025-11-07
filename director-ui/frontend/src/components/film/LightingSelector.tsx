import React from 'react';
import { Lightbulb, Check } from 'lucide-react';

interface LightingSelectorProps {
  selected: string;
  onSelect: (lighting: string) => void;
}

const lightingSetups = {
  golden_hour_exterior: {
    name: 'Golden Hour Exterior',
    mood: 'Magical, warm, romantic',
    colorTemp: '5500-6500K',
    contrast: '3:1 - 4:1'
  },
  blue_hour_twilight: {
    name: 'Blue Hour Twilight',
    mood: 'Moody, mysterious, contemplative',
    colorTemp: '8000-12000K',
    contrast: '2:1'
  },
  three_point_studio: {
    name: 'Three-Point Studio',
    mood: 'Professional, controlled, polished',
    colorTemp: '5600K',
    contrast: '4:1'
  },
  natural_window_light: {
    name: 'Natural Window Light',
    mood: 'Intimate, peaceful, natural',
    colorTemp: '5000-6500K',
    contrast: '2:1 - 3:1'
  },
  dramatic_single_source: {
    name: 'Dramatic Single Light',
    mood: 'Dramatic, mysterious, noir',
    colorTemp: 'Varies',
    contrast: '8:1+'
  },
  neon_urban_night: {
    name: 'Neon Urban Night',
    mood: 'Urban, nocturnal, cyberpunk',
    colorTemp: 'Mixed',
    contrast: 'High'
  },
  firelight_warm: {
    name: 'Firelight Warm',
    mood: 'Cozy, intimate, primitive',
    colorTemp: '2000-2700K',
    contrast: '4:1 (variable)'
  },
  overcast_soft: {
    name: 'Overcast Soft Daylight',
    mood: 'Melancholic, muted, realistic',
    colorTemp: '6500-7000K',
    contrast: '1:1 - 1.5:1'
  },
  high_key_commercial: {
    name: 'High Key Commercial',
    mood: 'Happy, optimistic, bright',
    colorTemp: '5600K',
    contrast: '2:1'
  },
  low_key_noir: {
    name: 'Low Key Noir',
    mood: 'Noir, mysterious, dangerous',
    colorTemp: 'Mixed',
    contrast: '10:1+'
  },
  magic_hour_backlight: {
    name: 'Magic Hour Backlight',
    mood: 'Dreamlike, romantic, magical',
    colorTemp: '3200-5000K',
    contrast: '4:1'
  }
};

const LightingSelector: React.FC<LightingSelectorProps> = ({ selected, onSelect }) => {
  return (
    <div className="space-y-2 max-h-[600px] overflow-y-auto custom-scrollbar">
      {Object.entries(lightingSetups).map(([key, lighting]) => (
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
                <Lightbulb className="w-4 h-4 text-yellow-400" />
                <h4 className="font-semibold text-sm">{lighting.name}</h4>
              </div>
              <p className="text-xs text-gray-300 mb-1">
                {lighting.mood}
              </p>
              <div className="flex space-x-3 text-xs text-gray-400">
                <span>🌡️ {lighting.colorTemp}</span>
                <span>⚡ {lighting.contrast}</span>
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

export default LightingSelector;
