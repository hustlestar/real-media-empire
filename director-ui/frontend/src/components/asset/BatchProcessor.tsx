import React, { useState } from 'react';
import { Layers, Play, Pause, CheckCircle, XCircle, Clock, Download, Trash2, FileText, Palette, Camera, Zap, Settings } from 'lucide-react';

export interface BatchAsset {
  id: string;
  title: string;
  thumbnailUrl?: string;
  type: 'shot' | 'scene' | 'image';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number; // 0-100
  error?: string;
}

export interface BatchOperation {
  id: string;
  type: 'export' | 'style' | 'color' | 'camera' | 'prompt' | 'delete' | 'archive';
  name: string;
  icon: React.ReactNode;
  description: string;
  settings: Record<string, any>;
}

export interface BatchJob {
  id: string;
  operation: BatchOperation;
  assets: BatchAsset[];
  status: 'pending' | 'running' | 'paused' | 'completed' | 'failed';
  progress: number; // 0-100
  startedAt?: Date;
  completedAt?: Date;
  successCount: number;
  failureCount: number;
}

interface BatchProcessorProps {
  selectedAssets?: BatchAsset[];
  onDeselectAsset?: (assetId: string) => void;
  onClearSelection?: () => void;
  onStartJob?: (operation: BatchOperation, assets: BatchAsset[]) => Promise<void>;
  onCancelJob?: (jobId: string) => void;
  activeJobs?: BatchJob[];
}

const BatchProcessor: React.FC<BatchProcessorProps> = ({
  selectedAssets = [],
  onDeselectAsset,
  onClearSelection,
  onStartJob,
  onCancelJob,
  activeJobs = []
}) => {
  const [selectedOperation, setSelectedOperation] = useState<BatchOperation | null>(null);
  const [operationSettings, setOperationSettings] = useState<Record<string, any>>({});
  const [showSettings, setShowSettings] = useState(false);

  // Available batch operations
  const operations: Omit<BatchOperation, 'id' | 'settings'>[] = [
    {
      type: 'export',
      name: 'Export',
      icon: <Download className="w-5 h-5" />,
      description: 'Export assets in specified format and resolution'
    },
    {
      type: 'style',
      name: 'Apply Style',
      icon: <Palette className="w-5 h-5" />,
      description: 'Apply style preset to all selected assets'
    },
    {
      type: 'color',
      name: 'Color Grade',
      icon: <Palette className="w-5 h-5" />,
      description: 'Apply color grading settings uniformly'
    },
    {
      type: 'camera',
      name: 'Camera Settings',
      icon: <Camera className="w-5 h-5" />,
      description: 'Update camera and lens settings'
    },
    {
      type: 'prompt',
      name: 'Regenerate',
      icon: <Zap className="w-5 h-5" />,
      description: 'Regenerate assets with modified prompts'
    },
    {
      type: 'archive',
      name: 'Archive',
      icon: <FileText className="w-5 h-5" />,
      description: 'Archive selected assets'
    },
    {
      type: 'delete',
      name: 'Delete',
      icon: <Trash2 className="w-5 h-5" />,
      description: 'Permanently delete selected assets'
    }
  ];

  // Handle operation selection
  const handleSelectOperation = (op: Omit<BatchOperation, 'id' | 'settings'>) => {
    setSelectedOperation({
      id: `batch_${Date.now()}`,
      ...op,
      settings: {}
    });
    setOperationSettings(getDefaultSettings(op.type));
    setShowSettings(true);
  };

  // Get default settings for operation type
  const getDefaultSettings = (type: string): Record<string, any> => {
    switch (type) {
      case 'export':
        return {
          format: 'mp4',
          resolution: '1080p',
          quality: 'high',
          includeAudio: true
        };
      case 'style':
        return {
          stylePresetId: '',
          blendWeight: 50,
          preserveOriginal: true
        };
      case 'color':
        return {
          temperature: 0,
          tint: 0,
          saturation: 100,
          contrast: 100,
          brightness: 0
        };
      case 'camera':
        return {
          focalLength: 50,
          aperture: 5.6,
          depthOfField: 'medium'
        };
      case 'prompt':
        return {
          promptModifier: '',
          regenerateAll: false,
          provider: 'minimax'
        };
      default:
        return {};
    }
  };

  // Handle settings change
  const handleSettingChange = (key: string, value: any) => {
    setOperationSettings({ ...operationSettings, [key]: value });
  };

  // Start batch job
  const handleStartJob = async () => {
    if (!selectedOperation) return;

    const operation: BatchOperation = {
      ...selectedOperation,
      settings: operationSettings
    };

    await onStartJob?.(operation, selectedAssets);
    setShowSettings(false);
    setSelectedOperation(null);
  };

  // Render settings panel based on operation type
  const renderSettings = () => {
    if (!selectedOperation) return null;

    switch (selectedOperation.type) {
      case 'export':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Format</label>
              <select
                value={operationSettings.format}
                onChange={(e) => handleSettingChange('format', e.target.value)}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white focus:border-blue-500 focus:outline-none"
              >
                <option value="mp4">MP4</option>
                <option value="mov">MOV</option>
                <option value="webm">WebM</option>
                <option value="png">PNG Sequence</option>
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">Resolution</label>
              <select
                value={operationSettings.resolution}
                onChange={(e) => handleSettingChange('resolution', e.target.value)}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white focus:border-blue-500 focus:outline-none"
              >
                <option value="4k">4K (3840x2160)</option>
                <option value="1080p">1080p (1920x1080)</option>
                <option value="720p">720p (1280x720)</option>
                <option value="480p">480p (854x480)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">Quality</label>
              <select
                value={operationSettings.quality}
                onChange={(e) => handleSettingChange('quality', e.target.value)}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white focus:border-blue-500 focus:outline-none"
              >
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>

            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={operationSettings.includeAudio}
                onChange={(e) => handleSettingChange('includeAudio', e.target.checked)}
                className="w-4 h-4 rounded bg-gray-800 border-gray-700 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-300">Include Audio</span>
            </label>
          </div>
        );

      case 'style':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Style Preset</label>
              <select
                value={operationSettings.stylePresetId}
                onChange={(e) => handleSettingChange('stylePresetId', e.target.value)}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white focus:border-blue-500 focus:outline-none"
              >
                <option value="">Select preset...</option>
                <option value="cinematic">Cinematic</option>
                <option value="noir">Film Noir</option>
                <option value="vibrant">Vibrant Colors</option>
                <option value="pastel">Pastel Dreams</option>
              </select>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm text-gray-400">Blend Weight</label>
                <span className="text-sm text-white">{operationSettings.blendWeight}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={operationSettings.blendWeight}
                onChange={(e) => handleSettingChange('blendWeight', parseInt(e.target.value))}
                className="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
            </div>

            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={operationSettings.preserveOriginal}
                onChange={(e) => handleSettingChange('preserveOriginal', e.target.checked)}
                className="w-4 h-4 rounded bg-gray-800 border-gray-700 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-300">Preserve Original Versions</span>
            </label>
          </div>
        );

      case 'color':
        return (
          <div className="space-y-4">
            {(['temperature', 'tint', 'saturation', 'contrast', 'brightness'] as const).map(param => (
              <div key={param}>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm text-gray-400 capitalize">{param}</label>
                  <span className="text-sm text-white">
                    {param === 'saturation' || param === 'contrast'
                      ? `${operationSettings[param]}%`
                      : operationSettings[param] > 0
                      ? `+${operationSettings[param]}`
                      : operationSettings[param]}
                  </span>
                </div>
                <input
                  type="range"
                  min={param === 'saturation' || param === 'contrast' ? 0 : -100}
                  max={param === 'saturation' || param === 'contrast' ? 200 : 100}
                  value={operationSettings[param]}
                  onChange={(e) => handleSettingChange(param, parseInt(e.target.value))}
                  className="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
              </div>
            ))}
          </div>
        );

      case 'prompt':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">
                Prompt Modifier (appended to existing prompts)
              </label>
              <textarea
                value={operationSettings.promptModifier}
                onChange={(e) => handleSettingChange('promptModifier', e.target.value)}
                placeholder="e.g., 'in golden hour lighting' or 'cinematic wide shot'"
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white placeholder-gray-600 focus:border-blue-500 focus:outline-none resize-none"
                rows={3}
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">Video Provider</label>
              <select
                value={operationSettings.provider}
                onChange={(e) => handleSettingChange('provider', e.target.value)}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white focus:border-blue-500 focus:outline-none"
              >
                <option value="minimax">Minimax</option>
                <option value="kling">Kling</option>
                <option value="runway">Runway</option>
              </select>
            </div>

            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={operationSettings.regenerateAll}
                onChange={(e) => handleSettingChange('regenerateAll', e.target.checked)}
                className="w-4 h-4 rounded bg-gray-800 border-gray-700 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-300">Regenerate All (ignore existing)</span>
            </label>
          </div>
        );

      default:
        return (
          <p className="text-sm text-gray-400">No additional settings required for this operation.</p>
        );
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Layers className="w-6 h-6 text-orange-400" />
          <div>
            <h3 className="text-lg font-bold text-white">Batch Processor</h3>
            <p className="text-sm text-gray-400">
              {selectedAssets.length} asset{selectedAssets.length !== 1 ? 's' : ''} selected
            </p>
          </div>
        </div>

        {selectedAssets.length > 0 && (
          <button
            onClick={onClearSelection}
            className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition text-sm"
          >
            Clear Selection
          </button>
        )}
      </div>

      {/* Selected Assets */}
      {selectedAssets.length > 0 && (
        <div className="mb-6 bg-gray-900 rounded-lg p-4 border border-gray-700">
          <h4 className="text-sm font-semibold text-white mb-3">Selected Assets</h4>
          <div className="grid grid-cols-6 gap-3 max-h-48 overflow-y-auto pr-2">
            {selectedAssets.map((asset) => (
              <div
                key={asset.id}
                className="relative bg-gray-950 rounded-lg overflow-hidden border border-gray-700 group"
              >
                {asset.thumbnailUrl ? (
                  <img
                    src={asset.thumbnailUrl}
                    alt={asset.title}
                    className="w-full aspect-video object-cover"
                  />
                ) : (
                  <div className="w-full aspect-video flex items-center justify-center bg-gray-900">
                    <Layers className="w-6 h-6 text-gray-600" />
                  </div>
                )}

                <button
                  onClick={() => onDeselectAsset?.(asset.id)}
                  className="absolute top-1 right-1 p-1 bg-red-600 hover:bg-red-500 rounded-full opacity-0 group-hover:opacity-100 transition"
                >
                  <XCircle className="w-3 h-3 text-white" />
                </button>

                <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/80 to-transparent p-2">
                  <p className="text-xs text-white truncate">{asset.title}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Operations Grid */}
      <div className="mb-6">
        <h4 className="text-sm font-semibold text-white mb-3">Select Operation</h4>
        <div className="grid grid-cols-4 gap-3">
          {operations.map((op) => (
            <button
              key={op.type}
              onClick={() => handleSelectOperation(op)}
              disabled={selectedAssets.length === 0}
              className={`p-4 rounded-lg border-2 transition-all text-left disabled:opacity-50 disabled:cursor-not-allowed ${
                selectedOperation?.type === op.type
                  ? 'border-blue-500 bg-blue-500/10'
                  : 'border-gray-700 bg-gray-900 hover:border-gray-600'
              }`}
            >
              <div className="flex items-center space-x-3 mb-2">
                <div className={`p-2 rounded-lg ${
                  selectedOperation?.type === op.type ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-400'
                }`}>
                  {op.icon}
                </div>
                <h5 className="text-white font-semibold">{op.name}</h5>
              </div>
              <p className="text-xs text-gray-400">{op.description}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && selectedOperation && (
        <div className="mb-6 bg-gray-900 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Settings className="w-5 h-5 text-blue-400" />
              <h4 className="text-sm font-semibold text-white">{selectedOperation.name} Settings</h4>
            </div>
            <button
              onClick={() => setShowSettings(false)}
              className="text-gray-400 hover:text-white transition"
            >
              <XCircle className="w-5 h-5" />
            </button>
          </div>

          {renderSettings()}

          <div className="mt-4 pt-4 border-t border-gray-700 flex items-center justify-between">
            <p className="text-sm text-gray-400">
              This will process {selectedAssets.length} asset{selectedAssets.length !== 1 ? 's' : ''}
            </p>
            <button
              onClick={handleStartJob}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg transition flex items-center space-x-2 font-medium"
            >
              <Play className="w-4 h-4" />
              <span>Start Processing</span>
            </button>
          </div>
        </div>
      )}

      {/* Active Jobs */}
      {activeJobs.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-white mb-3">Active Jobs</h4>
          <div className="space-y-3">
            {activeJobs.map((job) => (
              <div
                key={job.id}
                className="bg-gray-900 rounded-lg p-4 border border-gray-700"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-lg ${
                      job.status === 'completed' ? 'bg-green-600' :
                      job.status === 'failed' ? 'bg-red-600' :
                      job.status === 'running' ? 'bg-blue-600' :
                      'bg-gray-700'
                    }`}>
                      {job.operation.icon}
                    </div>
                    <div>
                      <h5 className="text-white font-semibold">{job.operation.name}</h5>
                      <p className="text-xs text-gray-400">
                        {job.assets.length} assets • {job.successCount} succeeded • {job.failureCount} failed
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    {job.status === 'running' && (
                      <button
                        onClick={() => onCancelJob?.(job.id)}
                        className="p-2 bg-gray-800 hover:bg-gray-700 rounded transition"
                        title="Cancel"
                      >
                        <Pause className="w-4 h-4 text-gray-400" />
                      </button>
                    )}

                    {job.status === 'completed' && (
                      <CheckCircle className="w-5 h-5 text-green-400" />
                    )}

                    {job.status === 'failed' && (
                      <XCircle className="w-5 h-5 text-red-400" />
                    )}

                    {job.status === 'pending' && (
                      <Clock className="w-5 h-5 text-gray-400" />
                    )}
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mb-2">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-gray-400">
                      {job.status === 'completed' ? 'Completed' :
                       job.status === 'failed' ? 'Failed' :
                       job.status === 'running' ? 'Processing...' :
                       'Pending'}
                    </span>
                    <span className="text-xs text-white">{Math.round(job.progress)}%</span>
                  </div>
                  <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all ${
                        job.status === 'completed' ? 'bg-green-600' :
                        job.status === 'failed' ? 'bg-red-600' :
                        'bg-blue-600'
                      }`}
                      style={{ width: `${job.progress}%` }}
                    />
                  </div>
                </div>

                {/* Time info */}
                {job.startedAt && (
                  <div className="text-xs text-gray-500">
                    Started {job.startedAt.toLocaleTimeString()}
                    {job.completedAt && ` • Completed ${job.completedAt.toLocaleTimeString()}`}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {selectedAssets.length === 0 && activeJobs.length === 0 && (
        <div className="bg-gray-900 rounded-lg p-12 border border-gray-700 text-center">
          <Layers className="w-12 h-12 text-gray-600 mx-auto mb-3" />
          <p className="text-gray-400 mb-2">No assets selected</p>
          <p className="text-sm text-gray-500">
            Select multiple assets to perform batch operations
          </p>
        </div>
      )}

      {/* Tips */}
      <div className="mt-6 bg-orange-600/10 border border-orange-600/30 rounded-lg p-3">
        <p className="text-xs text-orange-400">
          <strong>💡 Pro Tip:</strong> Batch operations are perfect for applying consistent style, color grading,
          or export settings across multiple shots. Jobs run in the background, so you can continue working.
        </p>
      </div>
    </div>
  );
};

export default BatchProcessor;
