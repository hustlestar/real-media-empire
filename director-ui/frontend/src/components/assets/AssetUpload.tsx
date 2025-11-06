import React, { useState } from 'react';
import { X, Upload, File } from 'lucide-react';

const AssetUpload: React.FC<any> = ({ onClose, onUploadComplete }) => {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);

  const handleUpload = async () => {
    if (files.length === 0) return;

    setUploading(true);
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    try {
      await fetch('http://localhost:8000/api/assets/upload', {
        method: 'POST',
        body: formData
      });
      onUploadComplete();
      onClose();
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-xl p-8 max-w-2xl w-full mx-4">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">Upload Assets</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-700 rounded"><X className="w-6 h-6" /></button>
        </div>

        <div className="border-2 border-dashed border-gray-600 rounded-lg p-12 text-center mb-6">
          <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <div className="text-lg mb-2">Drag and drop files here</div>
          <div className="text-sm text-gray-400 mb-4">or click to browse</div>
          <label className="px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg cursor-pointer inline-block">
            <span>Select Files</span>
            <input
              type="file"
              multiple
              onChange={(e) => setFiles(Array.from(e.target.files || []))}
              className="hidden"
              accept="image/*,video/*,audio/*"
            />
          </label>
        </div>

        {files.length > 0 && (
          <div className="mb-6">
            <div className="text-sm text-gray-400 mb-2">{files.length} file(s) selected</div>
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {files.map((file, idx) => (
                <div key={idx} className="flex items-center space-x-3 p-2 bg-gray-900 rounded">
                  <File className="w-4 h-4 text-blue-400" />
                  <span className="flex-1 text-sm">{file.name}</span>
                  <span className="text-xs text-gray-400">{(file.size / (1024 * 1024)).toFixed(2)} MB</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex space-x-3">
          <button onClick={onClose} className="flex-1 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg">
            Cancel
          </button>
          <button
            onClick={handleUpload}
            disabled={files.length === 0 || uploading}
            className="flex-1 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? 'Uploading...' : `Upload ${files.length} file(s)`}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AssetUpload;
