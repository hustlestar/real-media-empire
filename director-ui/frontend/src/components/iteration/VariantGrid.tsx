import React, { useState } from 'react';
import { Grid, ThumbsUp, ThumbsDown, Star, Play, Download, Trash2, Plus, RefreshCw } from 'lucide-react';

export interface Variant {
  id: string;
  label: string; // A, B, C, D, etc.
  videoUrl: string;
  thumbnailUrl?: string;
  prompt: string;
  promptDiff?: string; // What's different from base prompt
  status: 'generating' | 'completed' | 'error';

  // Metrics
  generationTime?: number;
  cost?: number;

  // User feedback
  rating?: number; // 1-5 stars
  liked?: boolean;
  selected?: boolean;
  notes?: string;
}

interface VariantGridProps {
  basePrompt: string;
  variants: Variant[];
  onGenerateVariants?: (count: number) => void;
  onSelectVariant?: (variant: Variant) => void;
  onRateVariant?: (variantId: string, rating: number) => void;
  onLikeVariant?: (variantId: string) => void;
  onDeleteVariant?: (variantId: string) => void;
  onDownloadVariant?: (variant: Variant) => void;
  onAddNotes?: (variantId: string, notes: string) => void;
}

const VariantGrid: React.FC<VariantGridProps> = ({
  basePrompt,
  variants,
  onGenerateVariants,
  onSelectVariant,
  onRateVariant,
  onLikeVariant,
  onDeleteVariant,
  onDownloadVariant,
  onAddNotes
}) => {
  const [viewMode, setViewMode] = useState<'grid' | 'compare'>('grid');
  const [selectedForCompare, setSelectedForCompare] = useState<string[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);

  // Handle variant selection for comparison
  const handleCompareToggle = (variantId: string) => {
    if (selectedForCompare.includes(variantId)) {
      setSelectedForCompare(selectedForCompare.filter(id => id !== variantId));
    } else if (selectedForCompare.length < 3) {
      setSelectedForCompare([...selectedForCompare, variantId]);
    }
  };

  // Generate new variants
  const handleGenerateVariants = async (count: number) => {
    setIsGenerating(true);
    try {
      await onGenerateVariants?.(count);
    } finally {
      setIsGenerating(false);
    }
  };

  // Get variants for comparison view
  const compareVariants = variants.filter(v => selectedForCompare.includes(v.id));

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Grid className="w-6 h-6 text-purple-400" />
          <div>
            <h3 className="text-lg font-bold text-white">Variant Grid</h3>
            <p className="text-sm text-gray-400">
              {variants.length} variant{variants.length !== 1 ? 's' : ''} • Compare and select the best
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {/* View Mode Toggle */}
          <div className="flex items-center bg-gray-900 rounded-lg p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`px-3 py-1.5 rounded text-sm transition ${
                viewMode === 'grid'
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Grid
            </button>
            <button
              onClick={() => setViewMode('compare')}
              disabled={selectedForCompare.length < 2}
              className={`px-3 py-1.5 rounded text-sm transition ${
                viewMode === 'compare'
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-400 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed'
              }`}
            >
              Compare ({selectedForCompare.length})
            </button>
          </div>

          {/* Generate Button */}
          <button
            onClick={() => handleGenerateVariants(3)}
            disabled={isGenerating}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-500 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg transition flex items-center space-x-2"
          >
            <RefreshCw className={`w-4 h-4 ${isGenerating ? 'animate-spin' : ''}`} />
            <span>{isGenerating ? 'Generating...' : 'Generate 3 Variants'}</span>
          </button>
        </div>
      </div>

      {/* Base Prompt */}
      <div className="mb-6 bg-gray-900 rounded-lg p-4 border border-gray-700">
        <h4 className="text-sm font-semibold text-gray-400 mb-2">Base Prompt</h4>
        <p className="text-sm text-gray-300">{basePrompt}</p>
      </div>

      {/* Grid View */}
      {viewMode === 'grid' && (
        <div className="grid grid-cols-3 gap-4">
          {variants.map((variant) => (
            <div
              key={variant.id}
              className={`bg-gray-900 rounded-lg border-2 overflow-hidden transition-all ${
                variant.selected
                  ? 'border-green-500'
                  : selectedForCompare.includes(variant.id)
                  ? 'border-purple-500'
                  : 'border-gray-700 hover:border-gray-600'
              }`}
            >
              {/* Thumbnail */}
              <div className="relative aspect-video bg-gray-950 group">
                {variant.status === 'generating' ? (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <RefreshCw className="w-8 h-8 text-purple-400 animate-spin" />
                    <span className="ml-2 text-sm text-gray-400">Generating...</span>
                  </div>
                ) : variant.thumbnailUrl ? (
                  <>
                    <img
                      src={variant.thumbnailUrl}
                      alt={variant.label}
                      className="w-full h-full object-cover"
                    />

                    {/* Play Overlay */}
                    <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition flex items-center justify-center">
                      <button
                        onClick={() => window.open(variant.videoUrl, '_blank')}
                        className="p-4 bg-white/20 hover:bg-white/30 rounded-full transition"
                      >
                        <Play className="w-6 h-6 text-white" />
                      </button>
                    </div>

                    {/* Label Badge */}
                    <div className="absolute top-2 left-2 bg-purple-600 text-white px-3 py-1 rounded-full font-bold">
                      {variant.label}
                    </div>

                    {/* Selected Badge */}
                    {variant.selected && (
                      <div className="absolute top-2 right-2 bg-green-500 text-white px-2 py-1 rounded-full text-xs font-bold flex items-center space-x-1">
                        <Star className="w-3 h-3 fill-current" />
                        <span>Selected</span>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="absolute inset-0 flex items-center justify-center text-gray-600">
                    No preview
                  </div>
                )}
              </div>

              {/* Info */}
              <div className="p-4">
                {/* Prompt Diff */}
                {variant.promptDiff && (
                  <div className="mb-3">
                    <p className="text-xs text-gray-500 mb-1">Variation:</p>
                    <p className="text-sm text-blue-400">{variant.promptDiff}</p>
                  </div>
                )}

                {/* Rating */}
                <div className="flex items-center space-x-1 mb-3">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      onClick={() => onRateVariant?.(variant.id, star)}
                      className="transition"
                    >
                      <Star
                        className={`w-4 h-4 ${
                          variant.rating && variant.rating >= star
                            ? 'fill-yellow-400 text-yellow-400'
                            : 'text-gray-600'
                        }`}
                      />
                    </button>
                  ))}
                </div>

                {/* Metrics */}
                <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                  {variant.generationTime && <span>⏱️ {variant.generationTime.toFixed(1)}s</span>}
                  {variant.cost && <span>💰 ${variant.cost.toFixed(2)}</span>}
                </div>

                {/* Actions */}
                <div className="grid grid-cols-4 gap-2">
                  <button
                    onClick={() => onLikeVariant?.(variant.id)}
                    className={`p-2 rounded transition ${
                      variant.liked
                        ? 'bg-green-600 text-white'
                        : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                    }`}
                    title="Like"
                  >
                    <ThumbsUp className="w-4 h-4" />
                  </button>

                  <button
                    onClick={() => handleCompareToggle(variant.id)}
                    className={`p-2 rounded transition ${
                      selectedForCompare.includes(variant.id)
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                    }`}
                    title="Compare"
                  >
                    <Grid className="w-4 h-4" />
                  </button>

                  <button
                    onClick={() => onDownloadVariant?.(variant)}
                    className="p-2 bg-gray-800 text-gray-400 hover:bg-gray-700 rounded transition"
                    title="Download"
                  >
                    <Download className="w-4 h-4" />
                  </button>

                  <button
                    onClick={() => onDeleteVariant?.(variant.id)}
                    className="p-2 bg-gray-800 text-gray-400 hover:bg-red-600 hover:text-white rounded transition"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                {/* Select as Final */}
                {!variant.selected && (
                  <button
                    onClick={() => onSelectVariant?.(variant)}
                    className="w-full mt-3 px-3 py-2 bg-green-600 hover:bg-green-500 rounded-lg transition text-sm font-medium flex items-center justify-center space-x-2"
                  >
                    <Star className="w-4 h-4" />
                    <span>Select This</span>
                  </button>
                )}
              </div>
            </div>
          ))}

          {/* Empty Slot */}
          {variants.length === 0 && (
            <div className="col-span-3 bg-gray-900 rounded-lg p-12 border border-gray-700 text-center">
              <Grid className="w-12 h-12 text-gray-600 mx-auto mb-3" />
              <p className="text-gray-400 mb-4">No variants generated yet</p>
              <button
                onClick={() => handleGenerateVariants(3)}
                disabled={isGenerating}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-500 disabled:bg-gray-700 rounded-lg transition inline-flex items-center space-x-2"
              >
                <Plus className="w-4 h-4" />
                <span>Generate Variants</span>
              </button>
            </div>
          )}
        </div>
      )}

      {/* Compare View */}
      {viewMode === 'compare' && compareVariants.length >= 2 && (
        <div className="space-y-6">
          {/* Side-by-side Comparison */}
          <div className={`grid ${compareVariants.length === 2 ? 'grid-cols-2' : 'grid-cols-3'} gap-4`}>
            {compareVariants.map((variant) => (
              <div key={variant.id} className="bg-gray-900 rounded-lg border border-gray-700 overflow-hidden">
                {/* Thumbnail */}
                <div className="relative aspect-video bg-gray-950">
                  {variant.thumbnailUrl && (
                    <img
                      src={variant.thumbnailUrl}
                      alt={variant.label}
                      className="w-full h-full object-cover"
                    />
                  )}
                  <div className="absolute top-2 left-2 bg-purple-600 text-white px-3 py-1 rounded-full font-bold">
                    {variant.label}
                  </div>
                </div>

                {/* Info */}
                <div className="p-4">
                  <div className="flex items-center space-x-1 mb-2">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <Star
                        key={star}
                        className={`w-4 h-4 ${
                          variant.rating && variant.rating >= star
                            ? 'fill-yellow-400 text-yellow-400'
                            : 'text-gray-600'
                        }`}
                      />
                    ))}
                  </div>

                  {variant.promptDiff && (
                    <p className="text-xs text-blue-400 mb-2">{variant.promptDiff}</p>
                  )}

                  <div className="flex items-center justify-between text-xs text-gray-500">
                    {variant.generationTime && <span>⏱️ {variant.generationTime.toFixed(1)}s</span>}
                    {variant.cost && <span>💰 ${variant.cost.toFixed(2)}</span>}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Winner Selection */}
          <div className="bg-gray-900 rounded-lg p-4 border border-purple-500/30">
            <h4 className="text-sm font-semibold text-purple-400 mb-3">Which is best?</h4>
            <div className="grid grid-cols-3 gap-3">
              {compareVariants.map((variant) => (
                <button
                  key={variant.id}
                  onClick={() => onSelectVariant?.(variant)}
                  className="px-4 py-3 bg-gray-800 hover:bg-purple-600 rounded-lg transition text-white font-medium"
                >
                  Select {variant.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tips */}
      <div className="mt-6 bg-purple-600/10 border border-purple-600/30 rounded-lg p-3">
        <p className="text-xs text-purple-400">
          <strong>💡 Pro Tip:</strong> Generate 3-5 variants at once to explore different interpretations.
          Use the rating stars to mark your favorites, then switch to Compare view for side-by-side evaluation.
        </p>
      </div>
    </div>
  );
};

export default VariantGrid;
