import React, { useState, useEffect } from 'react';
import { X, Save, Upload, Sparkles, RefreshCw, Download, Zap, Image as ImageIcon } from 'lucide-react';
import { apiUrl } from '../../config/api';
import { useWorkspace } from '../../contexts/WorkspaceContext';

const CharacterForm: React.FC<any> = ({ onClose, onSave }) => {
  const { currentWorkspace } = useWorkspace();
  const [characterType, setCharacterType] = useState('human');
  const [characterTypes, setCharacterTypes] = useState<any>({});
  const [formData, setFormData] = useState<any>({
    name: '',
    description: '',
    // Universal
    distinctive_features: '',
    color_scheme: '',
    texture: '',
    // Human
    age: '',
    gender: '',
    ethnicity: '',
    hair_color: '',
    hair_style: '',
    eye_color: '',
    height: '',
    build: '',
    clothing_style: '',
    // Animal
    species: '',
    breed: '',
    fur_color: '',
    fur_texture: '',
    size: '',
    temperament: '',
    // Robot
    model_type: '',
    material: '',
    power_source: '',
    capabilities: '',
    // Creature/Fantasy
    creature_type: '',
    abilities: '',
    habitat: '',
    magic_type: '',
    // Alien
    alien_species: '',
    home_planet: '',
    physiology: ''
  });

  // Image generation state
  const [availableModels, setAvailableModels] = useState<any>({});
  const [selectedModel, setSelectedModel] = useState('flux-dev');
  const [generatedImages, setGeneratedImages] = useState<string[]>([]);
  const [selectedImages, setSelectedImages] = useState<string[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationPrompt, setGenerationPrompt] = useState('');
  const [generationSeed, setGenerationSeed] = useState<number | null>(null);
  const [numVariations, setNumVariations] = useState(1);
  const [lastCost, setLastCost] = useState(0);
  const [showImageGen, setShowImageGen] = useState(false);

  // Load available models and types
  useEffect(() => {
    loadAvailableModels();
    loadCharacterTypes();
  }, []);

  const loadAvailableModels = async () => {
    try {
      const response = await fetch(apiUrl('/api/characters/models/available'));
      if (response.ok) {
        const data = await response.json();
        setAvailableModels(data.models);
        setSelectedModel(data.recommended);
      }
    } catch (error) {
      console.error('Failed to load models:', error);
    }
  };

  const loadCharacterTypes = async () => {
    try {
      const response = await fetch(apiUrl('/api/characters/types/available'));
      if (response.ok) {
        const data = await response.json();
        setCharacterTypes(data.types);
        setCharacterType(data.default);
      }
    } catch (error) {
      console.error('Failed to load character types:', error);
    }
  };

  const handleGenerateImages = async () => {
    if (!formData.name || !formData.description) {
      alert('Please fill in character name and description first');
      return;
    }

    setIsGenerating(true);
    try {
      // Build prompt from character attributes based on type
      const promptParts = [
        `${formData.description}`,
        characterType && characterType !== 'human' && `${characterTypes[characterType]?.name || characterType}`
      ];

      // Add type-specific attributes
      if (characterTypes[characterType]) {
        characterTypes[characterType].attributes.forEach((attr: string) => {
          if (formData[attr]) {
            promptParts.push(`${getFieldLabel(attr)}: ${formData[attr]}`);
          }
        });
      }

      // Add universal fields
      if (formData.distinctive_features) {
        promptParts.push(`Features: ${formData.distinctive_features}`);
      }
      if (generationPrompt) {
        promptParts.push(`Additional: ${generationPrompt}`);
      }

      const finalPrompt = promptParts.filter(Boolean).join(', ');

      const response = await fetch(apiUrl('/api/characters/generate-image'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: finalPrompt,
          model: selectedModel,
          num_images: numVariations,
          seed: generationSeed,
          add_to_character: false
        })
      });

      if (response.ok) {
        const data = await response.json();
        setGeneratedImages([...generatedImages, ...data.images]);
        setLastCost(data.cost);
        setGenerationSeed(Math.floor(Math.random() * 1000000)); // New seed for next iteration
      } else {
        const error = await response.json();
        alert(`Generation failed: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Image generation error:', error);
      alert('Failed to generate images. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const toggleImageSelection = (imageUrl: string) => {
    if (selectedImages.includes(imageUrl)) {
      setSelectedImages(selectedImages.filter(url => url !== imageUrl));
    } else {
      setSelectedImages([...selectedImages, imageUrl]);
    }
  };

  const handleSave = async () => {
    if (!currentWorkspace) {
      alert('Please select a workspace first');
      return;
    }

    try {
      // Build attributes object with all filled fields
      const attributes: any = {
        character_type: characterType,
        distinctive_features: formData.distinctive_features ? formData.distinctive_features.split(',').map((f: string) => f.trim()) : []
      };

      // Add type-specific attributes if they have values
      Object.keys(formData).forEach(key => {
        if (key !== 'name' && key !== 'description' && key !== 'distinctive_features' && formData[key]) {
          attributes[key] = formData[key];
        }
      });

      const characterData = {
        workspace_id: currentWorkspace.id,
        name: formData.name,
        description: formData.description,
        reference_images: selectedImages,
        attributes: attributes,
        projects_used: []
      };

      await fetch(apiUrl('/api/characters'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(characterData)
      });
      onSave();
      onClose();
    } catch (error) {
      console.error('Error saving character:', error);
      alert('Failed to save character. Please try again.');
    }
  };

  // Helper function to get field label
  const getFieldLabel = (fieldName: string): string => {
    const labels: Record<string, string> = {
      species: 'Species/Type',
      breed: 'Breed',
      fur_color: 'Fur/Coat Color',
      fur_texture: 'Fur Texture',
      size: 'Size',
      temperament: 'Temperament',
      model_type: 'Model/Type',
      material: 'Material',
      power_source: 'Power Source',
      capabilities: 'Capabilities',
      creature_type: 'Creature Type',
      abilities: 'Abilities',
      habitat: 'Habitat',
      magic_type: 'Magic Type',
      alien_species: 'Species',
      home_planet: 'Home Planet',
      physiology: 'Physiology',
      color_scheme: 'Color Scheme',
      texture: 'Texture/Surface',
      age: 'Age',
      gender: 'Gender',
      ethnicity: 'Ethnicity',
      hair_color: 'Hair Color',
      hair_style: 'Hair Style',
      eye_color: 'Eye Color',
      height: 'Height',
      build: 'Build',
      clothing_style: 'Clothing Style'
    };
    return labels[fieldName] || fieldName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
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

          {/* Character Type Selector */}
          <div>
            <label className="block text-sm font-semibold mb-3">Character Type *</label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {Object.entries(characterTypes).map(([key, type]: [string, any]) => (
                <button
                  key={key}
                  onClick={() => setCharacterType(key)}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    characterType === key
                      ? 'border-purple-500 bg-purple-900 bg-opacity-30'
                      : 'border-gray-700 bg-gray-900 hover:border-purple-400'
                  }`}
                >
                  <div className="text-3xl mb-2">{type.icon}</div>
                  <div className="text-sm font-semibold">{type.name}</div>
                </button>
              ))}
            </div>
            {characterTypes[characterType] && (
              <p className="text-xs text-gray-400 mt-2">
                {characterTypes[characterType].description}
              </p>
            )}
          </div>

          {/* Type-Specific Attributes */}
          {characterTypes[characterType] && (
            <div className="grid grid-cols-2 gap-4">
              {characterTypes[characterType].attributes.map((attrKey: string) => (
                <div key={attrKey}>
                  <label className="block text-sm font-semibold mb-2">{getFieldLabel(attrKey)}</label>
                  <input
                    type="text"
                    value={formData[attrKey] || ''}
                    onChange={(e) => setFormData({...formData, [attrKey]: e.target.value})}
                    className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg"
                    placeholder={`Enter ${getFieldLabel(attrKey).toLowerCase()}`}
                  />
                </div>
              ))}
            </div>
          )}

          {/* Universal Fields */}
          <div>
            <label className="block text-sm font-semibold mb-2">Distinctive Features (comma-separated)</label>
            <textarea
              value={formData.distinctive_features}
              onChange={(e) => setFormData({...formData, distinctive_features: e.target.value})}
              rows={2}
              className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg resize-none"
              placeholder="e.g., Glowing eyes, metal plates on chest, long whiskers"
            />
          </div>

          {/* AI Image Generation Section */}
          <div className="border-2 border-purple-500 border-opacity-50 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-purple-400" />
                AI Character Image Generation
              </h3>
              <button
                onClick={() => setShowImageGen(!showImageGen)}
                className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm"
              >
                {showImageGen ? 'Hide' : 'Show'}
              </button>
            </div>

            {showImageGen && (
              <div className="space-y-4">
                {/* Model Selection */}
                <div>
                  <label className="block text-sm font-semibold mb-2">Model Selection</label>
                  <select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg"
                  >
                    {Object.entries(availableModels).map(([key, model]: [string, any]) => (
                      <option key={key} value={key}>
                        {model.name} - ${model.cost_per_image.toFixed(3)}/img - Quality: {model.consistency_score}/10
                      </option>
                    ))}
                  </select>
                  {availableModels[selectedModel] && (
                    <p className="text-xs text-gray-400 mt-1">
                      {availableModels[selectedModel].description}
                    </p>
                  )}
                </div>

                {/* Refinement Prompt */}
                <div>
                  <label className="block text-sm font-semibold mb-2">Refinement (Optional)</label>
                  <input
                    type="text"
                    value={generationPrompt}
                    onChange={(e) => setGenerationPrompt(e.target.value)}
                    placeholder="e.g., smiling, professional lighting, studio background"
                    className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg"
                  />
                </div>

                {/* Generation Options */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold mb-2">Variations</label>
                    <input
                      type="number"
                      value={numVariations}
                      onChange={(e) => setNumVariations(parseInt(e.target.value))}
                      min="1"
                      max="4"
                      className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold mb-2">Seed (for iteration)</label>
                    <input
                      type="number"
                      value={generationSeed || ''}
                      onChange={(e) => setGenerationSeed(e.target.value ? parseInt(e.target.value) : null)}
                      placeholder="Random"
                      className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg"
                    />
                  </div>
                </div>

                {/* Generate Button */}
                <button
                  onClick={handleGenerateImages}
                  disabled={isGenerating || !formData.name || !formData.description}
                  className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:from-gray-600 disabled:to-gray-600 rounded-lg font-semibold flex items-center justify-center gap-2"
                >
                  {isGenerating ? (
                    <>
                      <RefreshCw className="w-5 h-5 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5" />
                      Generate Images
                    </>
                  )}
                </button>

                {lastCost > 0 && (
                  <div className="text-xs text-gray-400 text-center">
                    Last generation cost: ${lastCost.toFixed(3)}
                  </div>
                )}

                {/* Generated Images Grid */}
                {generatedImages.length > 0 && (
                  <div>
                    <label className="block text-sm font-semibold mb-3">
                      Generated Images ({generatedImages.length}) - Click to select for character
                    </label>
                    <div className="grid grid-cols-2 gap-3 max-h-64 overflow-y-auto">
                      {generatedImages.map((imageUrl, idx) => (
                        <div
                          key={idx}
                          onClick={() => toggleImageSelection(imageUrl)}
                          className={`relative cursor-pointer rounded-lg overflow-hidden border-2 transition-all ${
                            selectedImages.includes(imageUrl)
                              ? 'border-purple-500 ring-2 ring-purple-400'
                              : 'border-gray-600 hover:border-purple-400'
                          }`}
                        >
                          <img src={imageUrl} alt={`Generated ${idx + 1}`} className="w-full h-32 object-cover" />
                          {selectedImages.includes(imageUrl) && (
                            <div className="absolute top-2 right-2 bg-purple-500 text-white rounded-full p-1">
                              <Zap className="w-4 h-4" />
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                    <div className="text-xs text-gray-400 mt-2">
                      {selectedImages.length} image{selectedImages.length !== 1 ? 's' : ''} selected as reference
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Alternative: Manual Upload */}
            <div className="mt-4 border-t border-gray-700 pt-4">
              <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                <Upload className="w-4 h-4" />
                Or upload existing images
              </div>
              <label className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded cursor-pointer inline-block">
                <span>Select Images</span>
                <input type="file" multiple accept="image/*" className="hidden" />
              </label>
            </div>
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
