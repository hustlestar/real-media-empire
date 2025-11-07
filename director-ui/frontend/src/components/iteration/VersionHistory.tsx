import React, { useState } from 'react';
import { History, Eye, RotateCcw, Copy, GitBranch, Clock, Zap, Check, X } from 'lucide-react';

export interface ShotVersion {
  id: string;
  version: number;
  shotId: string;
  createdAt: Date;
  videoUrl: string;
  thumbnailUrl?: string;
  status: 'generating' | 'completed' | 'approved' | 'rejected';

  // Generation parameters
  prompt: string;
  stylePresetId?: string;
  stylePresetName?: string;
  provider: string;

  // What changed from previous version
  changes?: {
    prompt?: boolean;
    style?: boolean;
    camera?: boolean;
    color?: boolean;
  };

  // Performance metrics
  generationTime?: number; // seconds
  cost?: number; // dollars

  // Review info
  reviewNotes?: string;
  reviewedBy?: string;
}

interface VersionHistoryProps {
  shotId: string;
  versions: ShotVersion[];
  currentVersionId?: string;
  onVersionSelect?: (version: ShotVersion) => void;
  onRevertToVersion?: (version: ShotVersion) => void;
  onCompareVersions?: (version1: ShotVersion, version2: ShotVersion) => void;
  onDuplicateVersion?: (version: ShotVersion) => void;
}

const VersionHistory: React.FC<VersionHistoryProps> = ({
  shotId,
  versions,
  currentVersionId,
  onVersionSelect,
  onRevertToVersion,
  onCompareVersions,
  onDuplicateVersion
}) => {
  const [selectedVersionId, setSelectedVersionId] = useState<string | null>(currentVersionId || null);
  const [compareMode, setCompareMode] = useState(false);
  const [compareVersionIds, setCompareVersionIds] = useState<string[]>([]);
  const [expandedVersionId, setExpandedVersionId] = useState<string | null>(null);

  // Sort versions by version number descending (newest first)
  const sortedVersions = [...versions].sort((a, b) => b.version - a.version);

  // Handle version selection
  const handleVersionClick = (version: ShotVersion) => {
    if (compareMode) {
      // In compare mode, toggle selection
      if (compareVersionIds.includes(version.id)) {
        setCompareVersionIds(compareVersionIds.filter(id => id !== version.id));
      } else if (compareVersionIds.length < 2) {
        setCompareVersionIds([...compareVersionIds, version.id]);
      }
    } else {
      // Normal mode, select version
      setSelectedVersionId(version.id);
      onVersionSelect?.(version);
    }
  };

  // Handle compare button
  const handleCompare = () => {
    if (compareVersionIds.length === 2) {
      const v1 = versions.find(v => v.id === compareVersionIds[0]);
      const v2 = versions.find(v => v.id === compareVersionIds[1]);
      if (v1 && v2) {
        onCompareVersions?.(v1, v2);
      }
    }
  };

  // Toggle compare mode
  const toggleCompareMode = () => {
    setCompareMode(!compareMode);
    setCompareVersionIds([]);
  };

  // Format date
  const formatDate = (date: Date): string => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString();
  };

  // Get status icon and color
  const getStatusDisplay = (status: ShotVersion['status']) => {
    switch (status) {
      case 'generating':
        return { icon: <Clock className="w-4 h-4" />, color: 'text-blue-400', bg: 'bg-blue-600/20' };
      case 'completed':
        return { icon: <Zap className="w-4 h-4" />, color: 'text-gray-400', bg: 'bg-gray-600/20' };
      case 'approved':
        return { icon: <Check className="w-4 h-4" />, color: 'text-green-400', bg: 'bg-green-600/20' };
      case 'rejected':
        return { icon: <X className="w-4 h-4" />, color: 'text-red-400', bg: 'bg-red-600/20' };
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <History className="w-6 h-6 text-blue-400" />
          <div>
            <h3 className="text-lg font-bold text-white">Version History</h3>
            <p className="text-sm text-gray-400">
              {versions.length} version{versions.length !== 1 ? 's' : ''} • Shot: {shotId}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={toggleCompareMode}
            className={`px-3 py-2 rounded-lg transition flex items-center space-x-2 ${
              compareMode
                ? 'bg-purple-600 text-white'
                : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
            }`}
          >
            <GitBranch className="w-4 h-4" />
            <span>{compareMode ? 'Cancel Compare' : 'Compare'}</span>
          </button>

          {compareMode && compareVersionIds.length === 2 && (
            <button
              onClick={handleCompare}
              className="px-3 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg transition"
            >
              Compare Selected
            </button>
          )}
        </div>
      </div>

      {/* Version Timeline */}
      <div className="space-y-3 max-h-[600px] overflow-y-auto">
        {sortedVersions.map((version, idx) => {
          const isSelected = selectedVersionId === version.id;
          const isInCompare = compareVersionIds.includes(version.id);
          const isExpanded = expandedVersionId === version.id;
          const isCurrent = currentVersionId === version.id;
          const statusDisplay = getStatusDisplay(version.status);

          return (
            <div
              key={version.id}
              className={`bg-gray-900 rounded-lg border-2 transition-all ${
                isSelected
                  ? 'border-blue-500'
                  : isInCompare
                  ? 'border-purple-500'
                  : 'border-gray-700 hover:border-gray-600'
              }`}
            >
              {/* Version Header */}
              <div
                className="p-4 cursor-pointer"
                onClick={() => handleVersionClick(version)}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-start space-x-3">
                    {/* Thumbnail */}
                    {version.thumbnailUrl && (
                      <div className="relative">
                        <img
                          src={version.thumbnailUrl}
                          alt={`Version ${version.version}`}
                          className="w-20 h-14 object-cover rounded border border-gray-700"
                        />
                        {isCurrent && (
                          <div className="absolute -top-2 -right-2 bg-green-500 text-white text-xs px-2 py-0.5 rounded-full">
                            Current
                          </div>
                        )}
                      </div>
                    )}

                    {/* Version Info */}
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <h4 className="text-white font-semibold">Version {version.version}</h4>
                        <span className={`px-2 py-0.5 rounded text-xs ${statusDisplay.bg} ${statusDisplay.color} flex items-center space-x-1`}>
                          {statusDisplay.icon}
                          <span className="capitalize">{version.status}</span>
                        </span>
                        {version.changes && Object.keys(version.changes).length > 0 && (
                          <span className="text-xs text-yellow-400">
                            {Object.keys(version.changes).length} change{Object.keys(version.changes).length > 1 ? 's' : ''}
                          </span>
                        )}
                      </div>

                      <p className="text-sm text-gray-400 mb-1">
                        {formatDate(version.createdAt)} • {version.provider}
                      </p>

                      {version.stylePresetName && (
                        <p className="text-xs text-blue-400">
                          Style: {version.stylePresetName}
                        </p>
                      )}

                      {/* Metrics */}
                      <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                        {version.generationTime && (
                          <span>⏱️ {version.generationTime.toFixed(1)}s</span>
                        )}
                        {version.cost && (
                          <span>💰 ${version.cost.toFixed(2)}</span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center space-x-1">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setExpandedVersionId(isExpanded ? null : version.id);
                      }}
                      className="p-2 hover:bg-gray-800 rounded transition"
                      title="View details"
                    >
                      <Eye className="w-4 h-4 text-gray-400" />
                    </button>

                    {!isCurrent && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onRevertToVersion?.(version);
                        }}
                        className="p-2 hover:bg-gray-800 rounded transition"
                        title="Revert to this version"
                      >
                        <RotateCcw className="w-4 h-4 text-blue-400" />
                      </button>
                    )}

                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onDuplicateVersion?.(version);
                      }}
                      className="p-2 hover:bg-gray-800 rounded transition"
                      title="Duplicate and modify"
                    >
                      <Copy className="w-4 h-4 text-green-400" />
                    </button>
                  </div>
                </div>

                {/* Changes from previous version */}
                {version.changes && Object.keys(version.changes).length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-2">
                    {version.changes.prompt && (
                      <span className="text-xs px-2 py-1 bg-yellow-600/20 text-yellow-400 rounded">
                        Prompt updated
                      </span>
                    )}
                    {version.changes.style && (
                      <span className="text-xs px-2 py-1 bg-purple-600/20 text-purple-400 rounded">
                        Style changed
                      </span>
                    )}
                    {version.changes.camera && (
                      <span className="text-xs px-2 py-1 bg-blue-600/20 text-blue-400 rounded">
                        Camera settings
                      </span>
                    )}
                    {version.changes.color && (
                      <span className="text-xs px-2 py-1 bg-pink-600/20 text-pink-400 rounded">
                        Color grading
                      </span>
                    )}
                  </div>
                )}

                {/* Review notes */}
                {version.reviewNotes && (
                  <div className="mt-2 text-sm text-gray-400 italic">
                    "{version.reviewNotes}"
                    {version.reviewedBy && (
                      <span className="text-gray-500"> — {version.reviewedBy}</span>
                    )}
                  </div>
                )}
              </div>

              {/* Expanded Details */}
              {isExpanded && (
                <div className="px-4 pb-4 border-t border-gray-800 pt-4">
                  <div className="space-y-3">
                    {/* Full Prompt */}
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">Generation Prompt</label>
                      <p className="text-sm text-gray-300 bg-gray-950 rounded p-3 leading-relaxed">
                        {version.prompt}
                      </p>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center space-x-3">
                      <button
                        onClick={() => navigator.clipboard.writeText(version.prompt)}
                        className="px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded text-sm transition flex items-center space-x-2"
                      >
                        <Copy className="w-4 h-4" />
                        <span>Copy Prompt</span>
                      </button>

                      <button
                        onClick={() => window.open(version.videoUrl, '_blank')}
                        className="px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded text-sm transition flex items-center space-x-2"
                      >
                        <Eye className="w-4 h-4" />
                        <span>View Full Size</span>
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Empty State */}
      {versions.length === 0 && (
        <div className="bg-gray-900 rounded-lg p-8 text-center border border-gray-700">
          <History className="w-12 h-12 text-gray-600 mx-auto mb-3" />
          <p className="text-gray-400 mb-2">No versions yet</p>
          <p className="text-sm text-gray-500">Generate your first shot to start tracking versions</p>
        </div>
      )}

      {/* Tips */}
      <div className="mt-4 bg-blue-600/10 border border-blue-600/30 rounded-lg p-3">
        <p className="text-xs text-blue-400">
          <strong>💡 Pro Tip:</strong> Version history tracks all iterations of a shot. Click the revert
          button to go back to a previous version, or use compare mode to see differences side-by-side.
        </p>
      </div>
    </div>
  );
};

export default VersionHistory;
