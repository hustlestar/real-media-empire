import React, { useState, useRef } from 'react';
import { Upload, X, Eye, Sparkles, Download, Trash2, Image as ImageIcon } from 'lucide-react';

export interface ReferenceImage {
  id: string;
  url: string;
  filename: string;
  weight: number; // 0-100 influence percentage
  analysis?: {
    dominantColors: string[];
    mood: string;
    composition: string;
    lighting: string;
    keywords: string[];
  };
  notes?: string;
}

interface ReferenceUploadProps {
  references?: ReferenceImage[];
  onReferencesChange?: (references: ReferenceImage[]) => void;
  onAnalyze?: (imageUrl: string) => Promise<ReferenceImage['analysis']>;
  maxReferences?: number;
}

const ReferenceUpload: React.FC<ReferenceUploadProps> = ({
  references = [],
  onReferencesChange,
  onAnalyze,
  maxReferences = 5
}) => {
  const [images, setImages] = useState<ReferenceImage[]>(references);
  const [isDragging, setIsDragging] = useState(false);
  const [selectedImageId, setSelectedImageId] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Handle file selection
  const handleFileSelect = async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    const remainingSlots = maxReferences - images.length;
    if (remainingSlots <= 0) {
      alert(`Maximum ${maxReferences} reference images allowed`);
      return;
    }

    const filesToProcess = Array.from(files).slice(0, remainingSlots);

    for (const file of filesToProcess) {
      if (!file.type.startsWith('image/')) {
        alert(`${file.name} is not an image file`);
        continue;
      }

      // Create preview URL
      const url = URL.createObjectURL(file);

      const newReference: ReferenceImage = {
        id: `ref_${Date.now()}_${Math.random()}`,
        url,
        filename: file.name,
        weight: 100 / (images.length + 1) // Distribute weight evenly
      };

      // Redistribute weights
      const redistributedImages = images.map(img => ({
        ...img,
        weight: 100 / (images.length + 1)
      }));

      const updatedImages = [...redistributedImages, newReference];
      setImages(updatedImages);
      onReferencesChange?.(updatedImages);

      // Auto-analyze if handler provided
      if (onAnalyze) {
        setIsAnalyzing(true);
        try {
          const analysis = await onAnalyze(url);
          const withAnalysis = updatedImages.map(img =>
            img.id === newReference.id ? { ...img, analysis } : img
          );
          setImages(withAnalysis);
          onReferencesChange?.(withAnalysis);
        } catch (error) {
          console.error('Analysis failed:', error);
        } finally {
          setIsAnalyzing(false);
        }
      }
    }
  };

  // Handle drag and drop
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFileSelect(e.dataTransfer.files);
  };

  // Remove reference
  const handleRemoveReference = (id: string) => {
    const updatedImages = images.filter(img => img.id !== id);

    // Redistribute weights
    if (updatedImages.length > 0) {
      const redistributed = updatedImages.map(img => ({
        ...img,
        weight: 100 / updatedImages.length
      }));
      setImages(redistributed);
      onReferencesChange?.(redistributed);
    } else {
      setImages([]);
      onReferencesChange?.([]);
    }

    if (selectedImageId === id) {
      setSelectedImageId(null);
    }
  };

  // Update weight
  const handleWeightChange = (id: string, newWeight: number) => {
    const updatedImages = images.map(img =>
      img.id === id ? { ...img, weight: newWeight } : img
    );

    // Normalize weights to sum to 100
    const totalWeight = updatedImages.reduce((sum, img) => sum + img.weight, 0);
    if (totalWeight > 0) {
      const normalized = updatedImages.map(img => ({
        ...img,
        weight: (img.weight / totalWeight) * 100
      }));
      setImages(normalized);
      onReferencesChange?.(normalized);
    }
  };

  // Update notes
  const handleNotesChange = (id: string, notes: string) => {
    const updatedImages = images.map(img =>
      img.id === id ? { ...img, notes } : img
    );
    setImages(updatedImages);
    onReferencesChange?.(updatedImages);
  };

  // Get selected image
  const selectedImage = images.find(img => img.id === selectedImageId);

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <ImageIcon className="w-6 h-6 text-blue-400" />
          <div>
            <h3 className="text-lg font-bold text-white">Reference Images</h3>
            <p className="text-sm text-gray-400">
              Upload images to guide visual style ({images.length}/{maxReferences})
            </p>
          </div>
        </div>

        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={images.length >= maxReferences}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg transition flex items-center space-x-2"
        >
          <Upload className="w-4 h-4" />
          <span>Upload</span>
        </button>

        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          multiple
          onChange={(e) => handleFileSelect(e.target.files)}
          className="hidden"
        />
      </div>

      {/* Upload Zone */}
      {images.length < maxReferences && (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`mb-6 border-2 border-dashed rounded-lg p-8 text-center transition ${
            isDragging
              ? 'border-blue-500 bg-blue-500/10'
              : 'border-gray-700 hover:border-gray-600 bg-gray-900'
          }`}
        >
          <Upload className="w-12 h-12 text-gray-500 mx-auto mb-3" />
          <p className="text-gray-400 mb-2">Drag and drop images here</p>
          <p className="text-sm text-gray-500">or click Upload to browse</p>
          <p className="text-xs text-gray-600 mt-2">
            Supports JPG, PNG, WebP • Max {maxReferences} images
          </p>
        </div>
      )}

      {/* Reference Grid */}
      {images.length > 0 ? (
        <div className="grid grid-cols-2 gap-4 mb-6">
          {images.map(image => (
            <div
              key={image.id}
              onClick={() => setSelectedImageId(image.id)}
              className={`bg-gray-900 rounded-lg overflow-hidden border-2 transition cursor-pointer ${
                selectedImageId === image.id
                  ? 'border-blue-500'
                  : 'border-gray-700 hover:border-gray-600'
              }`}
            >
              {/* Image Preview */}
              <div className="relative aspect-video bg-gray-950">
                <img
                  src={image.url}
                  alt={image.filename}
                  className="w-full h-full object-cover"
                />

                {/* Actions Overlay */}
                <div className="absolute top-2 right-2 flex items-center space-x-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      window.open(image.url, '_blank');
                    }}
                    className="p-2 bg-gray-900/80 hover:bg-gray-800 rounded transition"
                    title="View full size"
                  >
                    <Eye className="w-4 h-4 text-white" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRemoveReference(image.id);
                    }}
                    className="p-2 bg-gray-900/80 hover:bg-red-600 rounded transition"
                    title="Remove"
                  >
                    <Trash2 className="w-4 h-4 text-white" />
                  </button>
                </div>

                {/* Weight Badge */}
                <div className="absolute bottom-2 left-2 px-2 py-1 bg-gray-900/80 rounded text-sm font-bold text-white">
                  {Math.round(image.weight)}%
                </div>
              </div>

              {/* Info */}
              <div className="p-3">
                <p className="text-sm text-white font-medium truncate mb-2">
                  {image.filename}
                </p>

                {/* Weight Slider */}
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="1"
                  value={image.weight}
                  onClick={(e) => e.stopPropagation()}
                  onChange={(e) => handleWeightChange(image.id, parseFloat(e.target.value))}
                  className="w-full h-1 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />

                {/* Analysis Tags */}
                {image.analysis && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {image.analysis.keywords?.slice(0, 3).map((keyword, idx) => (
                      <span
                        key={idx}
                        className="text-xs px-2 py-0.5 bg-blue-600/20 text-blue-400 rounded"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="mb-6 bg-gray-900 rounded-lg p-8 border border-gray-700 text-center">
          <ImageIcon className="w-12 h-12 text-gray-600 mx-auto mb-3" />
          <p className="text-gray-400 mb-2">No reference images added</p>
          <p className="text-sm text-gray-500">Upload images to guide your visual style</p>
        </div>
      )}

      {/* Selected Image Details */}
      {selectedImage && (
        <div className="bg-gray-900 rounded-lg p-4 border border-blue-500/30">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-semibold text-blue-400">Reference Details</h4>
            <button
              onClick={() => setSelectedImageId(null)}
              className="p-1 hover:bg-gray-800 rounded transition text-gray-400"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Analysis */}
          {selectedImage.analysis ? (
            <div className="space-y-3 mb-4">
              {/* Dominant Colors */}
              {selectedImage.analysis.dominantColors && (
                <div>
                  <label className="block text-xs text-gray-500 mb-2">Dominant Colors</label>
                  <div className="flex items-center space-x-2">
                    {selectedImage.analysis.dominantColors.map((color, idx) => (
                      <div
                        key={idx}
                        className="w-8 h-8 rounded border border-gray-700"
                        style={{ backgroundColor: color }}
                        title={color}
                      ></div>
                    ))}
                  </div>
                </div>
              )}

              {/* Characteristics */}
              <div className="grid grid-cols-2 gap-3">
                {selectedImage.analysis.mood && (
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Mood</label>
                    <p className="text-sm text-white">{selectedImage.analysis.mood}</p>
                  </div>
                )}
                {selectedImage.analysis.lighting && (
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Lighting</label>
                    <p className="text-sm text-white">{selectedImage.analysis.lighting}</p>
                  </div>
                )}
                {selectedImage.analysis.composition && (
                  <div className="col-span-2">
                    <label className="block text-xs text-gray-500 mb-1">Composition</label>
                    <p className="text-sm text-white">{selectedImage.analysis.composition}</p>
                  </div>
                )}
              </div>

              {/* Keywords */}
              {selectedImage.analysis.keywords && (
                <div>
                  <label className="block text-xs text-gray-500 mb-2">Visual Keywords</label>
                  <div className="flex flex-wrap gap-1">
                    {selectedImage.analysis.keywords.map((keyword, idx) => (
                      <span
                        key={idx}
                        className="text-xs px-2 py-1 bg-gray-800 text-gray-300 rounded"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="mb-4 text-center py-4">
              <Sparkles className="w-8 h-8 text-gray-600 mx-auto mb-2" />
              <p className="text-sm text-gray-500">No analysis available</p>
            </div>
          )}

          {/* Notes */}
          <div>
            <label className="block text-xs text-gray-500 mb-2">Notes</label>
            <textarea
              value={selectedImage.notes || ''}
              onChange={(e) => handleNotesChange(selectedImage.id, e.target.value)}
              placeholder="Add notes about what to capture from this reference..."
              className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white text-sm placeholder-gray-500 focus:border-blue-500 focus:outline-none resize-none"
              rows={3}
            />
          </div>
        </div>
      )}

      {/* Analyzing Indicator */}
      {isAnalyzing && (
        <div className="mt-4 bg-blue-600/10 border border-blue-600/30 rounded-lg p-3 flex items-center space-x-3">
          <Sparkles className="w-5 h-5 text-blue-400 animate-pulse" />
          <p className="text-sm text-blue-400">Analyzing image characteristics...</p>
        </div>
      )}

      {/* Tips */}
      <div className="mt-4 bg-gray-900/50 rounded-lg p-3 border border-gray-700/50">
        <p className="text-xs text-gray-500">
          <strong className="text-gray-400">Pro Tip:</strong> Upload movie stills, artwork, or photos that capture
          the lighting, color, and composition you want. The AI will extract visual characteristics
          and blend them into your shots.
        </p>
      </div>
    </div>
  );
};

export default ReferenceUpload;
