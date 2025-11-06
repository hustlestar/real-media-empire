import React from 'react';
import { Heart, Check } from 'lucide-react';

interface EmotionSelectorProps {
  selected: string;
  onSelect: (emotion: string) => void;
}

const emotions = {
  triumph_victory: {
    name: 'Triumph/Victory',
    energy: 'High',
    icon: '🏆',
    colors: 'Golds, warm yellows'
  },
  contemplation_reflection: {
    name: 'Contemplation/Reflection',
    energy: 'Low-Medium',
    icon: '🤔',
    colors: 'Muted blues, grays'
  },
  tension_anxiety: {
    name: 'Tension/Anxiety',
    energy: 'High nervous',
    icon: '😰',
    colors: 'Cool blue-grays, greens'
  },
  joy_delight: {
    name: 'Joy/Delight',
    energy: 'Medium-High',
    icon: '😄',
    colors: 'Warm pastels, bright'
  },
  melancholy_sadness: {
    name: 'Melancholy/Sadness',
    energy: 'Low',
    icon: '😢',
    colors: 'Blues, grays, muted'
  },
  determination_resolve: {
    name: 'Determination/Resolve',
    energy: 'Medium-High',
    icon: '💪',
    colors: 'Strong saturated, deep'
  },
  fear_terror: {
    name: 'Fear/Terror',
    energy: 'High panic',
    icon: '😱',
    colors: 'Dark blues, harsh contrast'
  },
  anger_rage: {
    name: 'Anger/Rage',
    energy: 'High aggressive',
    icon: '😠',
    colors: 'Reds, oranges, harsh'
  },
  surprise_shock: {
    name: 'Surprise/Shock',
    energy: 'Sudden spike',
    icon: '😮',
    colors: 'High contrast, bright'
  },
  love_tenderness: {
    name: 'Love/Tenderness',
    energy: 'Gentle warm',
    icon: '❤️',
    colors: 'Warm soft tones, peaches'
  },
  curiosity_interest: {
    name: 'Curiosity/Interest',
    energy: 'Alert engaged',
    icon: '🔍',
    colors: 'Clear bright, natural'
  },
  exhaustion_defeat: {
    name: 'Exhaustion/Defeat',
    energy: 'Zero',
    icon: '😫',
    colors: 'Desaturated, grays'
  }
};

const EmotionSelector: React.FC<EmotionSelectorProps> = ({ selected, onSelect }) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
      {Object.entries(emotions).map(([key, emotion]) => (
        <button
          key={key}
          onClick={() => onSelect(key)}
          className={`p-4 rounded-lg transition border-2 ${
            selected === key
              ? 'bg-purple-600 bg-opacity-30 border-purple-400 scale-105'
              : 'bg-gray-800 bg-opacity-50 border-gray-700 hover:border-purple-500 hover:scale-102'
          }`}
        >
          <div className="text-center">
            <div className="text-3xl mb-2">{emotion.icon}</div>
            <div className="font-semibold text-sm mb-1">{emotion.name}</div>
            <div className="text-xs text-gray-400 mb-1">
              ⚡ {emotion.energy}
            </div>
            <div className="text-xs text-gray-500">{emotion.colors}</div>
            {selected === key && (
              <div className="mt-2">
                <Check className="w-5 h-5 text-green-400 mx-auto" />
              </div>
            )}
          </div>
        </button>
      ))}
    </div>
  );
};

export default EmotionSelector;
