import React, { useState, useRef } from 'react';
import { Target, Square, Circle, Eraser, Sparkles, Undo, Redo, Save, Trash2 } from 'lucide-react';

export interface Region {
  id: string;
  type: 'rectangle' | 'circle' | 'freeform';
  coordinates: {
    x: number;
    y: number;
    width?: number;
    height?: number;
    radius?: number;
    points?: Array<{ x: number; y: number }>;
  };
  refinement: {
    action: 'enhance' | 'fix' | 'change' | 'remove';
    description: string;
    intensity: number; // 0-100
  };
}

interface RefinementToolProps {
  imageUrl: string;
  regions?: Region[];
  onRegionsChange?: (regions: Region[]) => void;
  onApplyRefinements?: (regions: Region[]) => void;
}

const RefinementTool: React.FC<RefinementToolProps> = ({
  imageUrl,
  regions = [],
  onRegionsChange,
  onApplyRefinements
}) => {
  const [tool, setTool] = useState<'select' | 'rectangle' | 'circle' | 'eraser'>('select');
  const [currentRegions, setCurrentRegions] = useState<Region[]>(regions);
  const [selectedRegionId, setSelectedRegionId] = useState<string | null>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [drawStart, setDrawStart] = useState<{ x: number; y: number } | null>(null);

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);

  // Refinement presets
  const refinementPresets = [
    {
      action: 'enhance' as const,
      name: 'Enhance Detail',
      description: 'Add more detail and sharpness',
      icon: <Sparkles className="w-4 h-4" />
    },
    {
      action: 'fix' as const,
      name: 'Fix Issues',
      description: 'Fix artifacts, blur, or errors',
      icon: <Target className="w-4 h-4" />
    },
    {
      action: 'change' as const,
      name: 'Change Element',
      description: 'Replace or modify specific elements',
      icon: <Sparkles className="w-4 h-4" />
    },
    {
      action: 'remove' as const,
      name: 'Remove',
      description: 'Remove unwanted elements',
      icon: <Eraser className="w-4 h-4" />
    }
  ];

  // Add region
  const handleAddRegion = (region: Omit<Region, 'id'>) => {
    const newRegion: Region = {
      ...region,
      id: `region_${Date.now()}`
    };

    const updated = [...currentRegions, newRegion];
    setCurrentRegions(updated);
    onRegionsChange?.(updated);
    setSelectedRegionId(newRegion.id);
  };

  // Remove region
  const handleRemoveRegion = (regionId: string) => {
    const updated = currentRegions.filter(r => r.id !== regionId);
    setCurrentRegions(updated);
    onRegionsChange?.(updated);

    if (selectedRegionId === regionId) {
      setSelectedRegionId(null);
    }
  };

  // Update region refinement
  const handleUpdateRefinement = (
    regionId: string,
    updates: Partial<Region['refinement']>
  ) => {
    const updated = currentRegions.map(r =>
      r.id === regionId
        ? { ...r, refinement: { ...r.refinement, ...updates } }
        : r
    );

    setCurrentRegions(updated);
    onRegionsChange?.(updated);
  };

  // Canvas mouse handlers (simplified - full implementation would use proper canvas drawing)
  const handleCanvasMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (tool === 'select' || tool === 'eraser') return;

    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;

    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;

    setIsDrawing(true);
    setDrawStart({ x, y });
  };

  const handleCanvasMouseUp = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing || !drawStart) return;

    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;

    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;

    // Create region based on tool
    if (tool === 'rectangle') {
      handleAddRegion({
        type: 'rectangle',
        coordinates: {
          x: Math.min(drawStart.x, x),
          y: Math.min(drawStart.y, y),
          width: Math.abs(x - drawStart.x),
          height: Math.abs(y - drawStart.y)
        },
        refinement: {
          action: 'enhance',
          description: '',
          intensity: 50
        }
      });
    } else if (tool === 'circle') {
      const radius = Math.sqrt(
        Math.pow(x - drawStart.x, 2) + Math.pow(y - drawStart.y, 2)
      );

      handleAddRegion({
        type: 'circle',
        coordinates: {
          x: drawStart.x,
          y: drawStart.y,
          radius
        },
        refinement: {
          action: 'enhance',
          description: '',
          intensity: 50
        }
      });
    }

    setIsDrawing(false);
    setDrawStart(null);
  };

  // Apply all refinements
  const handleApply = () => {
    if (currentRegions.length === 0) {
      alert('No regions defined. Add regions first.');
      return;
    }

    const missingDescriptions = currentRegions.filter(r => !r.refinement.description);
    if (missingDescriptions.length > 0) {
      alert('Please add descriptions for all regions.');
      return;
    }

    onApplyRefinements?.(currentRegions);
  };

  // Get selected region
  const selectedRegion = currentRegions.find(r => r.id === selectedRegionId);

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Target className="w-6 h-6 text-green-400" />
          <div>
            <h3 className="text-lg font-bold text-white">Refinement Tool</h3>
            <p className="text-sm text-gray-400">Target specific regions for improvement</p>
          </div>
        </div>

        <button
          onClick={handleApply}
          disabled={currentRegions.length === 0}
          className="px-4 py-2 bg-green-600 hover:bg-green-500 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg transition flex items-center space-x-2"
        >
          <Sparkles className="w-4 h-4" />
          <span>Apply Refinements</span>
        </button>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Canvas Area */}
        <div className="space-y-4">
          {/* Toolbar */}
          <div className="flex items-center space-x-2 bg-gray-900 rounded-lg p-2">
            <button
              onClick={() => setTool('select')}
              className={`p-2 rounded transition ${
                tool === 'select' ? 'bg-green-600 text-white' : 'text-gray-400 hover:bg-gray-800'
              }`}
              title="Select"
            >
              <Target className="w-5 h-5" />
            </button>

            <button
              onClick={() => setTool('rectangle')}
              className={`p-2 rounded transition ${
                tool === 'rectangle' ? 'bg-green-600 text-white' : 'text-gray-400 hover:bg-gray-800'
              }`}
              title="Rectangle"
            >
              <Square className="w-5 h-5" />
            </button>

            <button
              onClick={() => setTool('circle')}
              className={`p-2 rounded transition ${
                tool === 'circle' ? 'bg-green-600 text-white' : 'text-gray-400 hover:bg-gray-800'
              }`}
              title="Circle"
            >
              <Circle className="w-5 h-5" />
            </button>

            <button
              onClick={() => setTool('eraser')}
              className={`p-2 rounded transition ${
                tool === 'eraser' ? 'bg-green-600 text-white' : 'text-gray-400 hover:bg-gray-800'
              }`}
              title="Eraser"
            >
              <Eraser className="w-5 h-5" />
            </button>

            <div className="flex-1"></div>

            <button
              onClick={() => setCurrentRegions([])}
              className="p-2 text-red-400 hover:bg-gray-800 rounded transition"
              title="Clear All"
            >
              <Trash2 className="w-5 h-5" />
            </button>
          </div>

          {/* Canvas */}
          <div className="relative bg-gray-900 rounded-lg border border-gray-700 overflow-hidden">
            <img
              ref={imageRef}
              src={imageUrl}
              alt="Refinement target"
              className="w-full"
            />

            <canvas
              ref={canvasRef}
              onMouseDown={handleCanvasMouseDown}
              onMouseUp={handleCanvasMouseUp}
              className="absolute inset-0 w-full h-full cursor-crosshair"
            />

            {/* Render regions as overlays */}
            {currentRegions.map((region) => (
              <div
                key={region.id}
                className={`absolute border-2 pointer-events-none ${
                  selectedRegionId === region.id ? 'border-green-400' : 'border-blue-400'
                }`}
                style={
                  region.type === 'rectangle'
                    ? {
                        left: `${region.coordinates.x}%`,
                        top: `${region.coordinates.y}%`,
                        width: `${region.coordinates.width}%`,
                        height: `${region.coordinates.height}%`
                      }
                    : region.type === 'circle'
                    ? {
                        left: `${region.coordinates.x}%`,
                        top: `${region.coordinates.y}%`,
                        width: `${(region.coordinates.radius || 0) * 2}%`,
                        height: `${(region.coordinates.radius || 0) * 2}%`,
                        borderRadius: '50%',
                        transform: 'translate(-50%, -50%)'
                      }
                    : {}
                }
              >
                <div className="absolute -top-6 left-0 bg-green-600 text-white text-xs px-2 py-1 rounded">
                  {region.refinement.action}
                </div>
              </div>
            ))}
          </div>

          {/* Instructions */}
          <div className="bg-gray-900 rounded-lg p-3 border border-gray-700">
            <p className="text-xs text-gray-400">
              <strong className="text-gray-300">Instructions:</strong> Select a tool and draw on the
              image to define regions. Then configure the refinement action on the right.
            </p>
          </div>
        </div>

        {/* Regions Panel */}
        <div className="space-y-4">
          <h4 className="text-sm font-semibold text-white">
            Regions ({currentRegions.length})
          </h4>

          {currentRegions.length > 0 ? (
            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {currentRegions.map((region, idx) => (
                <div
                  key={region.id}
                  onClick={() => setSelectedRegionId(region.id)}
                  className={`bg-gray-900 rounded-lg p-4 border-2 cursor-pointer transition ${
                    selectedRegionId === region.id
                      ? 'border-green-500'
                      : 'border-gray-700 hover:border-gray-600'
                  }`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <h5 className="text-white font-semibold">Region {idx + 1}</h5>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRemoveRegion(region.id);
                      }}
                      className="p-1 hover:bg-gray-800 rounded transition text-red-400"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Action Selection */}
                  <div className="mb-3">
                    <label className="block text-xs text-gray-500 mb-2">Action</label>
                    <div className="grid grid-cols-2 gap-2">
                      {refinementPresets.map((preset) => (
                        <button
                          key={preset.action}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleUpdateRefinement(region.id, { action: preset.action });
                          }}
                          className={`px-3 py-2 rounded text-xs transition flex items-center space-x-2 ${
                            region.refinement.action === preset.action
                              ? 'bg-green-600 text-white'
                              : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                          }`}
                        >
                          {preset.icon}
                          <span>{preset.name}</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Description */}
                  <div className="mb-3">
                    <label className="block text-xs text-gray-500 mb-2">
                      Description (what to do)
                    </label>
                    <textarea
                      value={region.refinement.description}
                      onChange={(e) =>
                        handleUpdateRefinement(region.id, { description: e.target.value })
                      }
                      onClick={(e) => e.stopPropagation()}
                      placeholder="E.g., 'Make the face more detailed' or 'Remove background object'"
                      className="w-full px-3 py-2 bg-gray-950 border border-gray-700 rounded text-white text-sm placeholder-gray-600 focus:border-green-500 focus:outline-none resize-none"
                      rows={3}
                    />
                  </div>

                  {/* Intensity */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-xs text-gray-500">Intensity</label>
                      <span className="text-xs text-white">{region.refinement.intensity}%</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={region.refinement.intensity}
                      onChange={(e) =>
                        handleUpdateRefinement(region.id, { intensity: parseFloat(e.target.value) })
                      }
                      onClick={(e) => e.stopPropagation()}
                      className="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-green-600"
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-gray-900 rounded-lg p-8 border border-gray-700 text-center">
              <Target className="w-12 h-12 text-gray-600 mx-auto mb-3" />
              <p className="text-gray-400 mb-2">No regions defined</p>
              <p className="text-sm text-gray-500">
                Use the tools to draw regions on the image
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Tips */}
      <div className="mt-6 bg-green-600/10 border border-green-600/30 rounded-lg p-3">
        <p className="text-xs text-green-400">
          <strong>💡 Pro Tip:</strong> Be specific in your descriptions. Instead of "fix this", say
          "sharpen the eyes and add more detail to the iris" for better results.
        </p>
      </div>
    </div>
  );
};

export default RefinementTool;
