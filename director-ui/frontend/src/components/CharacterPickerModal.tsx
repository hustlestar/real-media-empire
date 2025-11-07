import React, { useState, useEffect } from 'react';
import { X, Search, User, Check, Eye } from 'lucide-react';
import { apiUrl } from '../config/api';

interface CharacterAttributes {
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
}

interface Character {
  id: string;
  name: string;
  description: string;
  reference_images: string[];
  attributes: CharacterAttributes;
  consistency_prompt: string;
  projects_used: string[];
}

interface CharacterPickerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (character: Character) => void;
  title?: string;
}

const CharacterPickerModal: React.FC<CharacterPickerModalProps> = ({
  isOpen,
  onClose,
  onSelect,
  title = 'Select Character'
}) => {
  const [characters, setCharacters] = useState<Character[]>([]);
  const [filteredCharacters, setFilteredCharacters] = useState<Character[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(null);
  const [previewCharacter, setPreviewCharacter] = useState<Character | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchCharacters();
    }
  }, [isOpen]);

  useEffect(() => {
    applyFilters();
  }, [characters, searchQuery]);

  const fetchCharacters = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(apiUrl('/api/characters'));
      const data = await response.json();
      setCharacters(data.characters || []);
    } catch (error) {
      console.error('Error fetching characters:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...characters];

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(character =>
        character.name.toLowerCase().includes(query) ||
        character.description.toLowerCase().includes(query)
      );
    }

    setFilteredCharacters(filtered);
  };

  const handleSelect = () => {
    if (selectedCharacter) {
      onSelect(selectedCharacter);
      onClose();
      setSelectedCharacter(null);
      setSearchQuery('');
      setPreviewCharacter(null);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-gradient-to-br from-purple-900/90 to-pink-900/90 backdrop-blur-md rounded-2xl shadow-2xl w-full max-w-6xl max-h-[90vh] flex">
        {/* Main Selection Area */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-white/10">
            <h2 className="text-2xl font-bold text-white">{title}</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/10 rounded-lg transition"
            >
              <X className="w-5 h-5 text-white/70" />
            </button>
          </div>

          {/* Search */}
          <div className="p-6 border-b border-white/10">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-white/50" />
              <input
                type="text"
                placeholder="Search characters by name or description..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-pink-500"
              />
            </div>
          </div>

          {/* Character Grid */}
          <div className="flex-1 overflow-y-auto p-6">
            {isLoading ? (
              <div className="flex items-center justify-center h-64">
                <div className="text-white/70">Loading characters...</div>
              </div>
            ) : filteredCharacters.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-64 text-white/70">
                <User className="w-16 h-16 mb-4 opacity-50" />
                <p>No characters found</p>
                <p className="text-sm mt-2">Create characters in the Character Library first</p>
              </div>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {filteredCharacters.map((character) => {
                  const isSelected = selectedCharacter?.id === character.id;
                  const mainImage = character.reference_images?.[0];

                  return (
                    <div
                      key={character.id}
                      className={`relative group cursor-pointer rounded-xl overflow-hidden transition ${
                        isSelected
                          ? 'ring-2 ring-pink-400 shadow-lg shadow-pink-500/50'
                          : 'hover:ring-2 hover:ring-white/30'
                      }`}
                    >
                      {/* Character Card */}
                      <div
                        onClick={() => setSelectedCharacter(character)}
                        className="bg-white/5 backdrop-blur-sm border border-white/10"
                      >
                        {/* Image/Avatar */}
                        <div className="aspect-square bg-gradient-to-br from-purple-600/20 to-pink-600/20 flex items-center justify-center">
                          {mainImage ? (
                            <img
                              src={mainImage}
                              alt={character.name}
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <User className="w-20 h-20 text-white/30" />
                          )}
                        </div>

                        {/* Character Info */}
                        <div className="p-4">
                          <h3 className="text-white font-bold text-lg mb-1">{character.name}</h3>
                          <p className="text-white/70 text-sm line-clamp-2 mb-3">{character.description}</p>

                          {/* Quick Attributes */}
                          <div className="flex flex-wrap gap-2">
                            {character.attributes.age && (
                              <span className="px-2 py-1 bg-white/10 rounded text-xs text-white/80">
                                {character.attributes.age}
                              </span>
                            )}
                            {character.attributes.gender && (
                              <span className="px-2 py-1 bg-white/10 rounded text-xs text-white/80">
                                {character.attributes.gender}
                              </span>
                            )}
                            {character.attributes.ethnicity && (
                              <span className="px-2 py-1 bg-white/10 rounded text-xs text-white/80">
                                {character.attributes.ethnicity}
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Selected Indicator */}
                        {isSelected && (
                          <div className="absolute top-3 right-3 bg-pink-500 rounded-full p-1.5">
                            <Check className="w-4 h-4 text-white" />
                          </div>
                        )}
                      </div>

                      {/* Preview Button */}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setPreviewCharacter(character);
                        }}
                        className="absolute bottom-3 right-3 p-2 bg-white/10 hover:bg-white/20 rounded-lg backdrop-blur-sm transition"
                      >
                        <Eye className="w-4 h-4 text-white" />
                      </button>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="p-6 border-t border-white/10 flex items-center justify-between">
            <div className="text-sm text-white/70">
              {filteredCharacters.length} character{filteredCharacters.length !== 1 ? 's' : ''} available
              {selectedCharacter && (
                <span className="ml-4 text-white">
                  Selected: <span className="font-medium">{selectedCharacter.name}</span>
                </span>
              )}
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={onClose}
                className="px-6 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleSelect}
                disabled={!selectedCharacter}
                className={`px-6 py-2 rounded-lg font-medium transition ${
                  selectedCharacter
                    ? 'bg-pink-600 text-white hover:bg-pink-500'
                    : 'bg-white/10 text-white/50 cursor-not-allowed'
                }`}
              >
                Use This Character
              </button>
            </div>
          </div>
        </div>

        {/* Preview Panel */}
        {previewCharacter && (
          <div className="w-96 border-l border-white/10 bg-black/20 backdrop-blur-md flex flex-col">
            <div className="p-6 border-b border-white/10 flex items-center justify-between">
              <h3 className="text-lg font-bold text-white">Character Details</h3>
              <button
                onClick={() => setPreviewCharacter(null)}
                className="p-1 hover:bg-white/10 rounded transition"
              >
                <X className="w-4 h-4 text-white/70" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {/* Reference Images */}
              {previewCharacter.reference_images.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-white/70 mb-2">Reference Images</h4>
                  <div className="grid grid-cols-2 gap-2">
                    {previewCharacter.reference_images.map((img, idx) => (
                      <img
                        key={idx}
                        src={img}
                        alt={`Reference ${idx + 1}`}
                        className="w-full aspect-square object-cover rounded-lg"
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Attributes */}
              <div>
                <h4 className="text-sm font-semibold text-white/70 mb-2">Attributes</h4>
                <div className="space-y-2">
                  {Object.entries(previewCharacter.attributes).map(([key, value]) => (
                    value && (
                      <div key={key} className="flex justify-between text-sm">
                        <span className="text-white/60 capitalize">{key.replace(/_/g, ' ')}:</span>
                        <span className="text-white font-medium">
                          {Array.isArray(value) ? value.join(', ') : value}
                        </span>
                      </div>
                    )
                  ))}
                </div>
              </div>

              {/* Consistency Prompt */}
              <div>
                <h4 className="text-sm font-semibold text-white/70 mb-2">Consistency Prompt</h4>
                <pre className="text-xs text-white/80 bg-white/5 p-3 rounded-lg whitespace-pre-wrap font-mono">
                  {previewCharacter.consistency_prompt}
                </pre>
              </div>

              {/* Projects Used */}
              {previewCharacter.projects_used.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-white/70 mb-2">Used in Projects</h4>
                  <div className="space-y-1">
                    {previewCharacter.projects_used.map((project, idx) => (
                      <div key={idx} className="text-sm text-white/80 bg-white/5 px-3 py-2 rounded">
                        {project}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CharacterPickerModal;
