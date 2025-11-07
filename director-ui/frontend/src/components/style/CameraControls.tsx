import React, { useState } from 'react';
import { Camera, Aperture, Move, Maximize2, RefreshCw, Save } from 'lucide-react';

export interface CameraSettings {
  // Lens
  focalLength: number; // mm (14-200mm)
  aperture: number; // f-stop (1.4-22)
  sensor: 'full-frame' | 'super35' | 'micro43' | 'IMAX';

  // Focus
  depthOfField: 'shallow' | 'medium' | 'deep';
  focusDistance: number; // meters (0.5-100)

  // Framing
  shotSize: 'extreme-closeup' | 'closeup' | 'medium' | 'full' | 'wide' | 'extreme-wide';
  angle: 'low' | 'eye-level' | 'high' | 'dutch' | 'birds-eye' | 'worms-eye';
  composition: 'centered' | 'rule-of-thirds' | 'golden-ratio' | 'symmetric';

  // Movement
  movement: 'static' | 'pan' | 'tilt' | 'dolly' | 'crane' | 'handheld' | 'steadicam' | 'drone';
  movementSpeed: 'slow' | 'medium' | 'fast';

  // Aesthetics
  bokeh: 'circular' | 'hexagonal' | 'anamorphic';
  lensFl
ares: boolean;
  vignette: number; // 0-100
}

interface CameraControlsProps {
  settings?: CameraSettings;
  onSettingsChange?: (settings: CameraSettings) => void;
  onSavePreset?: (name: string, settings: CameraSettings) => void;
}

const CameraControls: React.FC<CameraControlsProps> = ({
  settings,
  onSettingsChange,
  onSavePreset
}) => {
  const [camera, setCamera] = useState<CameraSettings>(
    settings || {
      focalLength: 50,
      aperture: 2.8,
      sensor: 'full-frame',
      depthOfField: 'medium',
      focusDistance: 3,
      shotSize: 'medium',
      angle: 'eye-level',
      composition: 'rule-of-thirds',
      movement: 'static',
      movementSpeed: 'medium',
      bokeh: 'circular',
      lensFlares: false,
      vignette: 20
    }
  );

  const [presetName, setPresetName] = useState('');

  // Update setting
  const handleUpdate = (updates: Partial<CameraSettings>) => {
    const updated = { ...camera, ...updates };
    setCamera(updated);
    onSettingsChange?.(updated);
  };

  // Save preset
  const handleSavePreset = () => {
    if (!presetName.trim()) {
      alert('Please enter a preset name');
      return;
    }

    onSavePreset?.(presetName, camera);
    setPresetName('');
    alert(`Preset "${presetName}" saved!`);
  };

  // Famous camera presets
  const presets: Array<{ name: string; description: string; settings: Partial<CameraSettings> }> = [
    {
      name: 'Nolan IMAX',
      description: 'Epic wide shots, deep focus',
      settings: {
        focalLength: 28,
        aperture: 11,
        sensor: 'IMAX',
        depthOfField: 'deep',
        shotSize: 'wide',
        angle: 'eye-level',
        movement: 'dolly',
        movementSpeed: 'slow'
      }
    },
    {
      name: 'Deakins Low Light',
      description: 'Wide angle, shallow DOF, natural',
      settings: {
        focalLength: 35,
        aperture: 1.4,
        sensor: 'full-frame',
        depthOfField: 'shallow',
        shotSize: 'medium',
        angle: 'eye-level',
        movement: 'steadicam',
        movementSpeed: 'slow'
      }
    },
    {
      name: 'Wes Anderson Symmetry',
      description: 'Centered, static, medium focal length',
      settings: {
        focalLength: 40,
        aperture: 5.6,
        sensor: 'super35',
        depthOfField: 'medium',
        shotSize: 'full',
        angle: 'eye-level',
        composition: 'centered',
        movement: 'static',
        movementSpeed: 'slow'
      }
    },
    {
      name: 'Spielberg Close-up',
      description: 'Intimate portrait, shallow DOF',
      settings: {
        focalLength: 85,
        aperture: 2.0,
        sensor: 'full-frame',
        depthOfField: 'shallow',
        shotSize: 'closeup',
        angle: 'eye-level',
        movement: 'dolly',
        movementSpeed: 'slow'
      }
    },
    {
      name: 'Action Wide',
      description: 'Dynamic, wide, fast movement',
      settings: {
        focalLength: 24,
        aperture: 4.0,
        sensor: 'super35',
        depthOfField: 'deep',
        shotSize: 'wide',
        angle: 'low',
        movement: 'crane',
        movementSpeed: 'fast'
      }
    }
  ];

  // Apply preset
  const handleApplyPreset = (preset: typeof presets[0]) => {
    handleUpdate(preset.settings);
  };

  // Generate camera prompt
  const generatePrompt = (): string => {
    let prompt = `Shot on ${camera.sensor} sensor with ${camera.focalLength}mm lens at f/${camera.aperture}. `;
    prompt += `${camera.shotSize} shot from ${camera.angle} angle. `;
    prompt += `${camera.depthOfField} depth of field. `;

    if (camera.movement !== 'static') {
      prompt += `${camera.movementSpeed} ${camera.movement} movement. `;
    }

    prompt += `${camera.composition} composition. `;

    if (camera.lensFlares) {
      prompt += 'Cinematic lens flares. ';
    }

    if (camera.vignette > 0) {
      prompt += 'Natural vignette. ';
    }

    prompt += 'Professional cinematography.';

    return prompt;
  };

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Camera className="w-6 h-6 text-blue-400" />
          <div>
            <h3 className="text-lg font-bold text-white">Camera Controls</h3>
            <p className="text-sm text-gray-400">Lens, framing, and camera movement</p>
          </div>
        </div>

        <button
          onClick={() => navigator.clipboard.writeText(generatePrompt())}
          className="px-3 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg transition text-sm flex items-center space-x-2"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Generate Prompt</span>
        </button>
      </div>

      {/* Quick Presets */}
      <div className="mb-6 bg-gray-900 rounded-lg p-4 border border-gray-700">
        <h4 className="text-sm font-semibold text-white mb-3">Quick Presets</h4>
        <div className="grid grid-cols-2 gap-2">
          {presets.map((preset, idx) => (
            <button
              key={idx}
              onClick={() => handleApplyPreset(preset)}
              className="bg-gray-800 hover:bg-gray-700 rounded-lg p-3 border border-gray-700 text-left transition"
            >
              <h5 className="text-white text-sm font-medium mb-1">{preset.name}</h5>
              <p className="text-xs text-gray-400">{preset.description}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Lens Settings */}
      <div className="mb-6 bg-gray-900 rounded-lg p-4 border border-gray-700">
        <div className="flex items-center space-x-2 mb-4">
          <Aperture className="w-5 h-5 text-blue-400" />
          <h4 className="text-sm font-semibold text-white">Lens & Focus</h4>
        </div>

        <div className="space-y-4">
          {/* Focal Length */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm text-gray-400">Focal Length</label>
              <span className="text-sm text-white">{camera.focalLength}mm</span>
            </div>
            <input
              type="range"
              min="14"
              max="200"
              step="1"
              value={camera.focalLength}
              onChange={(e) => handleUpdate({ focalLength: parseFloat(e.target.value) })}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>14mm (Ultra-Wide)</span>
              <span>50mm (Normal)</span>
              <span>200mm (Telephoto)</span>
            </div>
          </div>

          {/* Aperture */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm text-gray-400">Aperture</label>
              <span className="text-sm text-white">f/{camera.aperture}</span>
            </div>
            <input
              type="range"
              min="1.4"
              max="22"
              step="0.1"
              value={camera.aperture}
              onChange={(e) => handleUpdate({ aperture: parseFloat(e.target.value) })}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>f/1.4 (Shallow DOF)</span>
              <span>f/22 (Deep DOF)</span>
            </div>
          </div>

          {/* Sensor */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Sensor Format</label>
            <div className="grid grid-cols-4 gap-2">
              {['full-frame', 'super35', 'micro43', 'IMAX'].map(sensor => (
                <button
                  key={sensor}
                  onClick={() => handleUpdate({ sensor: sensor as CameraSettings['sensor'] })}
                  className={`px-3 py-2 rounded text-sm transition ${
                    camera.sensor === sensor
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                  }`}
                >
                  {sensor === 'full-frame' ? 'Full Frame' : sensor === 'super35' ? 'Super 35' : sensor === 'micro43' ? 'Micro 4/3' : 'IMAX'}
                </button>
              ))}
            </div>
          </div>

          {/* Depth of Field */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Depth of Field</label>
            <div className="grid grid-cols-3 gap-2">
              {['shallow', 'medium', 'deep'].map(dof => (
                <button
                  key={dof}
                  onClick={() => handleUpdate({ depthOfField: dof as CameraSettings['depthOfField'] })}
                  className={`px-3 py-2 rounded text-sm capitalize transition ${
                    camera.depthOfField === dof
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                  }`}
                >
                  {dof}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Framing */}
      <div className="mb-6 bg-gray-900 rounded-lg p-4 border border-gray-700">
        <div className="flex items-center space-x-2 mb-4">
          <Maximize2 className="w-5 h-5 text-green-400" />
          <h4 className="text-sm font-semibold text-white">Framing</h4>
        </div>

        <div className="space-y-4">
          {/* Shot Size */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Shot Size</label>
            <div className="grid grid-cols-3 gap-2">
              {['extreme-closeup', 'closeup', 'medium', 'full', 'wide', 'extreme-wide'].map(size => (
                <button
                  key={size}
                  onClick={() => handleUpdate({ shotSize: size as CameraSettings['shotSize'] })}
                  className={`px-2 py-2 rounded text-xs capitalize transition ${
                    camera.shotSize === size
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                  }`}
                >
                  {size.replace('-', ' ')}
                </button>
              ))}
            </div>
          </div>

          {/* Angle */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Camera Angle</label>
            <div className="grid grid-cols-3 gap-2">
              {['low', 'eye-level', 'high', 'dutch', 'birds-eye', 'worms-eye'].map(angle => (
                <button
                  key={angle}
                  onClick={() => handleUpdate({ angle: angle as CameraSettings['angle'] })}
                  className={`px-2 py-2 rounded text-xs capitalize transition ${
                    camera.angle === angle
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                  }`}
                >
                  {angle.replace('-', ' ')}
                </button>
              ))}
            </div>
          </div>

          {/* Composition */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Composition</label>
            <div className="grid grid-cols-3 gap-2">
              {['centered', 'rule-of-thirds', 'golden-ratio', 'symmetric'].map(comp => (
                <button
                  key={comp}
                  onClick={() => handleUpdate({ composition: comp as CameraSettings['composition'] })}
                  className={`px-2 py-2 rounded text-xs capitalize transition ${
                    camera.composition === comp
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                  }`}
                >
                  {comp.replace('-', ' ')}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Movement */}
      <div className="mb-6 bg-gray-900 rounded-lg p-4 border border-gray-700">
        <div className="flex items-center space-x-2 mb-4">
          <Move className="w-5 h-5 text-purple-400" />
          <h4 className="text-sm font-semibold text-white">Camera Movement</h4>
        </div>

        <div className="space-y-4">
          {/* Movement Type */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Movement Type</label>
            <div className="grid grid-cols-4 gap-2">
              {['static', 'pan', 'tilt', 'dolly', 'crane', 'handheld', 'steadicam', 'drone'].map(movement => (
                <button
                  key={movement}
                  onClick={() => handleUpdate({ movement: movement as CameraSettings['movement'] })}
                  className={`px-2 py-2 rounded text-xs capitalize transition ${
                    camera.movement === movement
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                  }`}
                >
                  {movement}
                </button>
              ))}
            </div>
          </div>

          {/* Movement Speed */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Movement Speed</label>
            <div className="grid grid-cols-3 gap-2">
              {['slow', 'medium', 'fast'].map(speed => (
                <button
                  key={speed}
                  onClick={() => handleUpdate({ movementSpeed: speed as CameraSettings['movementSpeed'] })}
                  className={`px-3 py-2 rounded text-sm capitalize transition ${
                    camera.movementSpeed === speed
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                  }`}
                >
                  {speed}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Aesthetics */}
      <div className="mb-6 bg-gray-900 rounded-lg p-4 border border-gray-700">
        <h4 className="text-sm font-semibold text-white mb-4">Aesthetics</h4>

        <div className="space-y-4">
          {/* Bokeh */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Bokeh Shape</label>
            <div className="grid grid-cols-3 gap-2">
              {['circular', 'hexagonal', 'anamorphic'].map(bokeh => (
                <button
                  key={bokeh}
                  onClick={() => handleUpdate({ bokeh: bokeh as CameraSettings['bokeh'] })}
                  className={`px-3 py-2 rounded text-sm capitalize transition ${
                    camera.bokeh === bokeh
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                  }`}
                >
                  {bokeh}
                </button>
              ))}
            </div>
          </div>

          {/* Lens Flares */}
          <div className="flex items-center justify-between">
            <label className="text-sm text-gray-400">Lens Flares</label>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={camera.lensFlares}
                onChange={(e) => handleUpdate({ lensFlares: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          {/* Vignette */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm text-gray-400">Vignette</label>
              <span className="text-sm text-white">{camera.vignette}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={camera.vignette}
              onChange={(e) => handleUpdate({ vignette: parseFloat(e.target.value) })}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
            />
          </div>
        </div>
      </div>

      {/* Generated Prompt */}
      <div className="bg-blue-600/10 border border-blue-600/30 rounded-lg p-4 mb-4">
        <div className="flex items-center justify-between mb-2">
          <h4 className="text-sm font-semibold text-blue-400">Camera Prompt</h4>
          <button
            onClick={() => navigator.clipboard.writeText(generatePrompt())}
            className="text-xs px-2 py-1 bg-gray-800 hover:bg-gray-700 rounded text-gray-400 transition"
          >
            Copy
          </button>
        </div>
        <p className="text-sm text-gray-300 leading-relaxed">{generatePrompt()}</p>
      </div>

      {/* Save Preset */}
      <div className="flex items-center space-x-3">
        <input
          type="text"
          value={presetName}
          onChange={(e) => setPresetName(e.target.value)}
          placeholder="Preset name (e.g., 'Hero Wide Shot')"
          className="flex-1 px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none"
        />
        <button
          onClick={handleSavePreset}
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition flex items-center space-x-2"
        >
          <Save className="w-4 h-4" />
          <span>Save Preset</span>
        </button>
      </div>
    </div>
  );
};

export default CameraControls;
