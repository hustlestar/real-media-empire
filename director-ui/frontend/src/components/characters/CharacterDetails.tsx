import React from 'react';
import { X, Copy, Edit, Trash2, Film } from 'lucide-react';

const CharacterDetails: React.FC<any> = ({ character, onClose, onUpdate }) => {
  const copyPrompt = () => {
    navigator.clipboard.writeText(character.consistency_prompt);
  };

  return (
    <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-6 border border-purple-500 border-opacity-30 sticky top-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-bold">Character Details</h3>
        <button onClick={onClose} className="p-2 hover:bg-gray-700 rounded">
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="aspect-square bg-gray-900 rounded-lg mb-4 flex items-center justify-center overflow-hidden">
        {character.reference_images?.[0] ? (
          <img src={character.reference_images[0]} alt={character.name} className="w-full h-full object-cover" />
        ) : (
          <div className="text-gray-500 text-6xl">👤</div>
        )}
      </div>

      <div className="space-y-4 text-sm">
        <div>
          <div className="font-bold text-lg mb-1">{character.name}</div>
          <p className="text-gray-400">{character.description}</p>
        </div>

        <div className="border-t border-gray-700 pt-4">
          <div className="font-semibold mb-2">Attributes</div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div><span className="text-gray-400">Age:</span> {character.attributes.age}</div>
            <div><span className="text-gray-400">Gender:</span> {character.attributes.gender}</div>
            <div><span className="text-gray-400">Ethnicity:</span> {character.attributes.ethnicity}</div>
            <div><span className="text-gray-400">Hair:</span> {character.attributes.hair_color}</div>
            <div><span className="text-gray-400">Eyes:</span> {character.attributes.eye_color}</div>
            <div><span className="text-gray-400">Build:</span> {character.attributes.build}</div>
          </div>
        </div>

        <div className="border-t border-gray-700 pt-4">
          <div className="font-semibold mb-2">Consistency Prompt</div>
          <div className="bg-gray-900 rounded p-3 text-xs text-gray-300">
            {character.consistency_prompt}
          </div>
          <button
            onClick={copyPrompt}
            className="mt-2 w-full py-2 bg-purple-600 hover:bg-purple-500 rounded flex items-center justify-center space-x-2 text-xs"
          >
            <Copy className="w-4 h-4" />
            <span>Copy Prompt</span>
          </button>
        </div>

        {character.projects_used?.length > 0 && (
          <div className="border-t border-gray-700 pt-4">
            <div className="font-semibold mb-2 flex items-center space-x-2">
              <Film className="w-4 h-4" />
              <span>Used in Projects</span>
            </div>
            <div className="space-y-1">
              {character.projects_used.map((project: string, idx: number) => (
                <div key={idx} className="text-xs px-2 py-1 bg-purple-600 bg-opacity-20 rounded">
                  {project}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="mt-6 space-y-2">
        <button className="w-full py-2 bg-gray-700 hover:bg-gray-600 rounded flex items-center justify-center space-x-2">
          <Edit className="w-4 h-4" />
          <span>Edit</span>
        </button>
        <button className="w-full py-2 bg-red-600 hover:bg-red-500 rounded flex items-center justify-center space-x-2">
          <Trash2 className="w-4 h-4" />
          <span>Delete</span>
        </button>
      </div>
    </div>
  );
};

export default CharacterDetails;
