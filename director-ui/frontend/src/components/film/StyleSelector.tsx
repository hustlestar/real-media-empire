import React, { useState, useEffect } from 'react';
import { Film, Check } from 'lucide-react';

interface CinematicStyle {
  name: string;
  description: string;
  mood: string;
  reference_films: string[];
}

interface StyleSelectorProps {
  selected: string;
  onSelect: (style: string) => void;
}

const StyleSelector: React.FC<StyleSelectorProps> = ({ selected, onSelect }) => {
  const [styles, setStyles] = useState<Record<string, CinematicStyle>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch available styles from backend
    // For now, using hardcoded styles matching backend
    setStyles({
      hollywood_blockbuster: {
        name: 'Hollywood Blockbuster',
        description: 'Epic, high-budget Hollywood production quality',
        mood: 'Epic, powerful, emotionally engaging',
        reference_films: ['Inception', 'The Dark Knight', 'Interstellar']
      },
      indie_cinema: {
        name: 'Independent Cinema',
        description: 'Naturalistic, character-driven indie aesthetic',
        mood: 'Intimate, contemplative, authentic',
        reference_films: ['Moonlight', 'Lady Bird', 'The Florida Project']
      },
      commercial_luxury: {
        name: 'Luxury Brand Commercial',
        description: 'High-end premium brand aesthetic',
        mood: 'Sophisticated, aspirational, premium',
        reference_films: ['Apple Campaigns', 'Chanel Films']
      },
      documentary_real: {
        name: 'Documentary Realism',
        description: 'Authentic documentary filmmaking style',
        mood: 'Honest, real, unfiltered',
        reference_films: ['Planet Earth II', 'Free Solo']
      },
      music_video_stylized: {
        name: 'Music Video Stylized',
        description: 'Bold, creative music video aesthetic',
        mood: 'Energetic, bold, artistic',
        reference_films: ['This Is America', 'HUMBLE.']
      },
      noir_dramatic: {
        name: 'Film Noir Dramatic',
        description: 'Classic noir with dramatic chiaroscuro',
        mood: 'Mysterious, tense, atmospheric',
        reference_films: ['Blade Runner', 'Drive', 'The Batman']
      },
      social_media_native: {
        name: 'Social Media Native',
        description: 'Modern social media optimized aesthetic',
        mood: 'Energetic, relatable, trendy',
        reference_films: ['MrBeast', 'TikTok Viral']
      },
      scifi_futuristic: {
        name: 'Sci-Fi Futuristic',
        description: 'High-tech science fiction aesthetic',
        mood: 'Futuristic, technological, otherworldly',
        reference_films: ['Ex Machina', 'Blade Runner 2049']
      },
      horror_atmospheric: {
        name: 'Horror Atmospheric',
        description: 'Psychological horror with dread',
        mood: 'Tense, unsettling, mysterious',
        reference_films: ['Hereditary', 'The Witch']
      },
      vintage_nostalgia: {
        name: 'Vintage Nostalgia',
        description: 'Warm nostalgic aesthetic',
        mood: 'Nostalgic, warm, comforting',
        reference_films: ['Call Me By Your Name', 'Carol']
      }
    });
    setLoading(false);
  }, []);

  if (loading) {
    return <div className="text-center py-8">Loading styles...</div>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {Object.entries(styles).map(([key, style]) => (
        <button
          key={key}
          onClick={() => onSelect(key)}
          className={`text-left p-4 rounded-lg transition border-2 ${
            selected === key
              ? 'bg-purple-600 bg-opacity-30 border-purple-400'
              : 'bg-gray-800 bg-opacity-50 border-gray-700 hover:border-purple-500'
          }`}
        >
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center space-x-2">
              <Film className="w-5 h-5 text-purple-400" />
              <h3 className="font-bold">{style.name}</h3>
            </div>
            {selected === key && (
              <Check className="w-5 h-5 text-green-400" />
            )}
          </div>

          <p className="text-sm text-gray-300 mb-2">{style.description}</p>

          <div className="text-xs text-gray-400 mb-2">
            <span className="font-semibold">Mood:</span> {style.mood}
          </div>

          <div className="flex flex-wrap gap-1">
            {style.reference_films.slice(0, 2).map((film, idx) => (
              <span
                key={idx}
                className="px-2 py-1 bg-purple-500 bg-opacity-20 rounded text-xs"
              >
                {film}
              </span>
            ))}
          </div>
        </button>
      ))}
    </div>
  );
};

export default StyleSelector;
