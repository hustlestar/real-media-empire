import React, { useState } from 'react';
import { X, Save, Upload } from 'lucide-react';
import { apiUrl } from '../../config/api';

const CharacterForm: React.FC<any> = ({ onClose, onSave }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    age: '',
    gender: '',
    ethnicity: '',
    hair_color: '',
    hair_style: '',
    eye_color: '',
    height: '',
    build: '',
    clothing_style: '',
    distinctive_features: ''
  });

  const handleSave = async () => {
    try {
      await fetch(apiUrl('/api/characters'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      onSave();
      onClose();
    } catch (error) {
      console.error('Error saving character:', error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 overflow-y-auto">
      <div className="bg-gray-800 rounded-xl p-8 max-w-3xl w-full mx-4 my-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">Create Character</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-700 rounded">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="space-y-6 max-h-[70vh] overflow-y-auto pr-2">
          <div>
            <label className="block text-sm font-semibold mb-2">Character Name *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg"
              placeholder="e.g., Emma Thompson"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2">Description *</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              rows={3}
              className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg resize-none"
              placeholder="Brief character description..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold mb-2">Age</label>
              <input type="text" value={formData.age} onChange={(e) => setFormData({...formData, age: e.target.value})} className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg" placeholder="e.g., 30s, Mid-40s" />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">Gender</label>
              <input type="text" value={formData.gender} onChange={(e) => setFormData({...formData, gender: e.target.value})} className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg" />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">Ethnicity</label>
              <input type="text" value={formData.ethnicity} onChange={(e) => setFormData({...formData, ethnicity: e.target.value})} className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg" />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">Hair Color</label>
              <input type="text" value={formData.hair_color} onChange={(e) => setFormData({...formData, hair_color: e.target.value})} className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg" />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">Eye Color</label>
              <input type="text" value={formData.eye_color} onChange={(e) => setFormData({...formData, eye_color: e.target.value})} className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg" />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">Build</label>
              <input type="text" value={formData.build} onChange={(e) => setFormData({...formData, build: e.target.value})} className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg" placeholder="e.g., Athletic, Slim" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2">Clothing Style</label>
            <input type="text" value={formData.clothing_style} onChange={(e) => setFormData({...formData, clothing_style: e.target.value})} className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg" placeholder="e.g., Business casual, Street wear" />
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2">Distinctive Features</label>
            <textarea
              value={formData.distinctive_features}
              onChange={(e) => setFormData({...formData, distinctive_features: e.target.value})}
              rows={2}
              className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg resize-none"
              placeholder="e.g., Small scar above left eyebrow, wears glasses"
            />
          </div>

          <div className="border-2 border-dashed border-purple-500 border-opacity-50 rounded-lg p-6 text-center">
            <Upload className="w-12 h-12 text-purple-400 mx-auto mb-2" />
            <div className="text-sm text-gray-400 mb-2">Upload Reference Images</div>
            <label className="px-4 py-2 bg-purple-600 hover:bg-purple-500 rounded cursor-pointer inline-block">
              <span>Select Images</span>
              <input type="file" multiple accept="image/*" className="hidden" />
            </label>
          </div>
        </div>

        <div className="flex space-x-3 mt-6">
          <button onClick={onClose} className="flex-1 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg">
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={!formData.name || !formData.description}
            className="flex-1 py-3 bg-purple-600 hover:bg-purple-500 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            <Save className="w-5 h-5" />
            <span>Save Character</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default CharacterForm;
