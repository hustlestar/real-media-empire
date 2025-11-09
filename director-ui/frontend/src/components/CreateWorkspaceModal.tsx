import React, { useState } from 'react';
import { X, Briefcase } from 'lucide-react';
import { apiUrl } from '../config/api';

interface CreateWorkspaceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function CreateWorkspaceModal({ isOpen, onClose, onSuccess }: CreateWorkspaceModalProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsCreating(true);

    try {
      const response = await fetch(apiUrl('/api/workspaces/workspaces'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          description: description || undefined,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create workspace');
      }

      // Reset form
      setName('');
      setDescription('');

      // Call success callback to refresh workspace list
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 sm:p-6 backdrop-blur-sm overflow-y-auto">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black bg-opacity-75"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-gray-800 border border-gray-700 rounded-xl p-6 w-full max-w-md shadow-2xl my-auto max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-600 rounded-lg">
              <Briefcase className="w-5 h-5 text-white" />
            </div>
            <h2 className="text-xl font-bold text-white">Create Workspace</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-700 rounded-lg transition"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Workspace Name <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., My Film Studio"
              required
              className="w-full px-4 py-2 bg-gray-900 border border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Description (Optional)
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What is this workspace for?"
              rows={3}
              className="w-full px-4 py-2 bg-gray-900 border border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-white resize-none"
            />
          </div>

          {error && (
            <div className="p-3 bg-red-900 bg-opacity-30 border border-red-600 rounded-lg">
              <p className="text-sm text-red-300">{error}</p>
            </div>
          )}

          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg font-medium transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isCreating || !name.trim()}
              className="flex-1 px-4 py-2 bg-purple-600 hover:bg-purple-500 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium transition"
            >
              {isCreating ? 'Creating...' : 'Create Workspace'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
