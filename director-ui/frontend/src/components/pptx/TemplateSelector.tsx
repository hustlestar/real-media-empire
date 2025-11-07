import React from 'react';
import { Palette, Image } from 'lucide-react';

interface TemplateSelectorProps {
  config: any;
  onChange: (updates: any) => void;
}

const templates = [
  { name: 'professional', label: 'Professional', color: '#1F4E78' },
  { name: 'modern', label: 'Modern', color: '#2C3E50' },
  { name: 'creative', label: 'Creative', color: '#9B59B6' },
  { name: 'minimal', label: 'Minimal', color: '#34495E' },
  { name: 'vibrant', label: 'Vibrant', color: '#E74C3C' },
  { name: 'nature', label: 'Nature', color: '#27AE60' }
];

const fontFamilies = [
  'Calibri', 'Arial', 'Times New Roman', 'Georgia', 'Helvetica', 'Verdana'
];

const TemplateSelector: React.FC<TemplateSelectorProps> = ({ config, onChange }) => {
  return (
    <div className="space-y-6">
      {/* Aspect Ratio */}
      <div>
        <label className="block text-sm font-semibold mb-3">Aspect Ratio</label>
        <div className="grid grid-cols-2 gap-4">
          <button
            onClick={() => onChange({ aspectRatio: '16:9' })}
            className={`p-4 rounded-lg transition border-2 ${
              config.aspectRatio === '16:9'
                ? 'bg-blue-600 bg-opacity-30 border-blue-400'
                : 'bg-gray-800 bg-opacity-50 border-gray-700 hover:border-blue-500'
            }`}
          >
            <div className="w-full h-12 bg-blue-500 bg-opacity-20 rounded mb-2"></div>
            <div className="font-semibold text-sm text-center">16:9</div>
            <div className="text-xs text-gray-400 text-center">Widescreen</div>
          </button>

          <button
            onClick={() => onChange({ aspectRatio: '4:3' })}
            className={`p-4 rounded-lg transition border-2 ${
              config.aspectRatio === '4:3'
                ? 'bg-blue-600 bg-opacity-30 border-blue-400'
                : 'bg-gray-800 bg-opacity-50 border-gray-700 hover:border-blue-500'
            }`}
          >
            <div className="w-3/4 h-12 bg-blue-500 bg-opacity-20 rounded mx-auto mb-2"></div>
            <div className="font-semibold text-sm text-center">4:3</div>
            <div className="text-xs text-gray-400 text-center">Standard</div>
          </button>
        </div>
      </div>

      {/* Theme */}
      <div>
        <label className="block text-sm font-semibold mb-3 flex items-center space-x-2">
          <Palette className="w-4 h-4 text-blue-400" />
          <span>Theme</span>
        </label>
        <div className="grid grid-cols-3 gap-3">
          {templates.map((template) => (
            <button
              key={template.name}
              onClick={() => onChange({ themeName: template.name, primaryColor: template.color })}
              className={`p-3 rounded-lg transition border-2 ${
                config.themeName === template.name
                  ? 'bg-blue-600 bg-opacity-30 border-blue-400'
                  : 'bg-gray-800 bg-opacity-50 border-gray-700 hover:border-blue-500'
              }`}
            >
              <div
                className="w-full h-8 rounded mb-2"
                style={{ backgroundColor: template.color }}
              ></div>
              <div className="font-semibold text-xs text-center">{template.label}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Font Family */}
      <div>
        <label className="block text-sm font-semibold mb-2">Font Family</label>
        <select
          value={config.fontFamily}
          onChange={(e) => onChange({ fontFamily: e.target.value })}
          className="w-full px-4 py-3 bg-gray-900 bg-opacity-70 border border-gray-700 rounded-lg focus:border-blue-500 focus:outline-none transition"
        >
          {fontFamilies.map((font) => (
            <option key={font} value={font} style={{ fontFamily: font }}>
              {font}
            </option>
          ))}
        </select>
      </div>

      {/* Primary Color */}
      <div>
        <label className="block text-sm font-semibold mb-2">Primary Color</label>
        <div className="flex items-center space-x-3">
          <input
            type="color"
            value={config.primaryColor}
            onChange={(e) => onChange({ primaryColor: e.target.value })}
            className="w-16 h-12 rounded cursor-pointer"
          />
          <input
            type="text"
            value={config.primaryColor}
            onChange={(e) => onChange({ primaryColor: e.target.value })}
            placeholder="#1F4E78"
            className="flex-1 px-4 py-3 bg-gray-900 bg-opacity-70 border border-gray-700 rounded-lg focus:border-blue-500 focus:outline-none transition font-mono"
          />
        </div>
      </div>

      {/* Custom Template Upload */}
      <div className="bg-blue-900 bg-opacity-20 border border-blue-600 border-opacity-30 rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <Image className="w-4 h-4 text-blue-400" />
            <span className="text-sm font-semibold">Custom Template</span>
          </div>
          <span className="text-xs text-gray-400">Optional</span>
        </div>
        <label className="block">
          <div className="border-2 border-dashed border-blue-500 border-opacity-50 rounded-lg p-6 text-center hover:border-blue-400 hover:bg-blue-900 hover:bg-opacity-10 transition cursor-pointer">
            <Image className="w-8 h-8 text-blue-400 mx-auto mb-2" />
            <span className="text-sm text-blue-300">Upload PPTX Template</span>
            <input
              type="file"
              accept=".pptx"
              onChange={(e) => {
                const file = e.target.files?.[0];
                // In real implementation, upload file and get path
                onChange({ templatePath: file ? `/templates/${file.name}` : null });
              }}
              className="hidden"
            />
          </div>
        </label>
        {config.templatePath && (
          <div className="mt-2 text-xs text-blue-300">
            Using: {config.templatePath.split('/').pop()}
          </div>
        )}
      </div>
    </div>
  );
};

export default TemplateSelector;
