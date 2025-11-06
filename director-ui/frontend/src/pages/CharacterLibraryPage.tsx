import React, { useState, useEffect } from 'react';
import { Users, Plus, Image, Tag, Star } from 'lucide-react';
import CharacterCard from '../components/characters/CharacterCard';
import CharacterDetails from '../components/characters/CharacterDetails';
import CharacterForm from '../components/characters/CharacterForm';

interface Character {
  id: string;
  name: string;
  description: string;
  reference_images: string[];
  attributes: {
    age: string;
    gender: string;
    ethnicity: string;
    hair_color: string;
    hair_style: string;
    eye_color: string;
    height: string;
    build: string;
    clothing_style: string;
    distinctive_features: string[];
  };
  consistency_prompt: string;
  projects_used: string[];
  created_at: string;
}

const CharacterLibraryPage: React.FC = () => {
  const [characters, setCharacters] = useState<Character[]>([]);
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchCharacters();
  }, []);

  const fetchCharacters = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/characters');
      const data = await response.json();
      setCharacters(data.characters || []);
    } catch (error) {
      console.error('Error fetching characters:', error);
    }
  };

  const filteredCharacters = characters.filter(char =>
    char.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    char.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-pink-900 to-red-900 text-white">
      <header className="bg-black bg-opacity-50 backdrop-blur-md border-b border-purple-500">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Users className="w-8 h-8 text-purple-400" />
              <h1 className="text-2xl font-bold">Character Library</h1>
              <span className="px-3 py-1 bg-purple-500 bg-opacity-20 rounded-full text-sm">
                {characters.length} characters
              </span>
            </div>

            <button
              onClick={() => setShowForm(true)}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-500 rounded-lg transition flex items-center space-x-2"
            >
              <Plus className="w-4 h-4" />
              <span>New Character</span>
            </button>
          </div>

          <div className="mt-4">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search characters..."
              className="w-full px-4 py-2 bg-gray-900 bg-opacity-70 border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none"
            />
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className={`${selectedCharacter ? 'lg:col-span-3' : 'lg:col-span-4'}`}>
            {filteredCharacters.length === 0 ? (
              <div className="text-center py-20 text-gray-400">
                <Users className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <div>No characters found</div>
                <button
                  onClick={() => setShowForm(true)}
                  className="mt-4 px-6 py-2 bg-purple-600 hover:bg-purple-500 rounded-lg transition"
                >
                  Create First Character
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredCharacters.map((character) => (
                  <CharacterCard
                    key={character.id}
                    character={character}
                    onClick={() => setSelectedCharacter(character)}
                    selected={selectedCharacter?.id === character.id}
                  />
                ))}
              </div>
            )}
          </div>

          {selectedCharacter && (
            <div className="lg:col-span-1">
              <CharacterDetails
                character={selectedCharacter}
                onClose={() => setSelectedCharacter(null)}
                onUpdate={fetchCharacters}
              />
            </div>
          )}
        </div>
      </div>

      {showForm && (
        <CharacterForm
          onClose={() => setShowForm(false)}
          onSave={fetchCharacters}
        />
      )}
    </div>
  );
};

export default CharacterLibraryPage;
