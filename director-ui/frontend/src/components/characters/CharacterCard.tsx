import React from 'react';
import { User, Tag } from 'lucide-react';

const CharacterCard: React.FC<any> = ({ character, onClick, selected }) => (
  <div
    onClick={onClick}
    className={`bg-black bg-opacity-40 backdrop-blur-md rounded-xl overflow-hidden border-2 transition cursor-pointer ${
      selected ? 'border-purple-500 ring-2 ring-purple-500' : 'border-purple-500 border-opacity-30 hover:border-purple-400'
    }`}
  >
    <div className="aspect-square bg-gray-900 flex items-center justify-center">
      {character.reference_images?.length > 0 ? (
        <img src={character.reference_images[0]} alt={character.name} className="w-full h-full object-cover" />
      ) : (
        <User className="w-20 h-20 text-gray-600" />
      )}
    </div>

    <div className="p-4">
      <h3 className="font-bold text-lg mb-1">{character.name}</h3>
      <p className="text-sm text-gray-400 mb-3 line-clamp-2">{character.description}</p>

      <div className="space-y-2 text-xs">
        <div className="flex items-center space-x-2 text-gray-400">
          <span>{character.attributes.age}</span>
          <span>•</span>
          <span>{character.attributes.gender}</span>
          <span>•</span>
          <span>{character.attributes.ethnicity}</span>
        </div>

        {character.projects_used?.length > 0 && (
          <div className="flex items-center space-x-1">
            <Tag className="w-3 h-3 text-purple-400" />
            <span className="text-gray-400">{character.projects_used.length} projects</span>
          </div>
        )}
      </div>
    </div>
  </div>
);

export default CharacterCard;
