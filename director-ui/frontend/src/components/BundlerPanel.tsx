import React, { useState } from 'react';
import { useBundlerContext } from '../context/BundlerContext';
import { useCreateBundle } from '../hooks/useBundler';
import { BundleConfigModal } from './BundleConfigModal';

export const BundlerPanel: React.FC = () => {
  const { items, isOpen, removeItem, clearItems, clearFormState, closePanel, openPanel } = useBundlerContext();
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [bundleName, setBundleName] = useState('');
  const createBundle = useCreateBundle();

  const handleSaveBundle = async () => {
    if (items.length === 0) return;

    try {
      await createBundle.mutateAsync({
        name: bundleName || undefined,
        content_ids: items.map(item => item.id)
      });

      setBundleName('');
      alert('Bundle saved successfully!');
    } catch (error) {
      console.error('Failed to save bundle:', error);
      alert('Failed to save bundle');
    }
  };

  const handleProcess = () => {
    setShowConfigModal(true);
  };

  const handleClear = () => {
    clearItems();
    clearFormState();
    setBundleName('');
  };

  // Don't render anything if no items
  if (items.length === 0) return null;

  // Show minimized button when panel is closed
  if (!isOpen) {
    return (
      <button
        onClick={openPanel}
        className="fixed right-4 top-4 bg-primary text-primary-foreground p-4 rounded-full shadow-lg hover:shadow-xl transition-all duration-200 z-50 flex items-center gap-2"
        title={`Open bundle (${items.length} items)`}
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
        <span className="font-semibold">{items.length}</span>
      </button>
    );
  }

  return (
    <>
      <div className="fixed right-0 top-0 h-full w-80 bg-card border-l border-border shadow-lg z-40 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-muted">
          <h3 className="text-lg font-semibold text-foreground">
            Bundle ({items.length})
          </h3>
          <button
            onClick={closePanel}
            className="p-1 hover:bg-muted-foreground/10 rounded-md transition-colors"
            title="Minimize panel"
          >
            <svg className="w-5 h-5 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>

        {/* Items List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {items.map((item, index) => (
            <div
              key={item.id}
              className="p-3 bg-muted border border-border rounded-lg hover:bg-muted/80 transition-colors"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-medium text-muted-foreground">#{index + 1}</span>
                    <span className="text-xs px-2 py-0.5 bg-primary/10 text-primary rounded">
                      {item.content.source_type}
                    </span>
                  </div>
                  <p className="text-sm text-foreground truncate">
                    {item.content.metadata?.title || item.content.metadata?.url || 'Untitled'}
                  </p>
                  {item.content.metadata?.url && (
                    <p className="text-xs text-muted-foreground truncate mt-1">
                      {item.content.metadata.url}
                    </p>
                  )}
                </div>
                <button
                  onClick={() => removeItem(item.id)}
                  className="p-1 hover:bg-destructive/10 rounded transition-colors flex-shrink-0"
                  title="Remove from bundle"
                >
                  <svg className="w-4 h-4 text-destructive" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Actions */}
        <div className="border-t border-border p-4 space-y-3 bg-muted">
          {/* Save Bundle */}
          <div>
            <label className="block text-xs font-medium text-foreground mb-1">
              Bundle Name (optional)
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={bundleName}
                onChange={(e) => setBundleName(e.target.value)}
                placeholder="My research bundle..."
                className="flex-1 px-3 py-2 text-sm border border-border bg-background rounded-md focus:ring-2 focus:ring-primary focus:border-primary"
              />
              <button
                onClick={handleSaveBundle}
                disabled={createBundle.isPending}
                className="px-4 py-2 text-sm font-medium bg-secondary text-secondary-foreground hover:bg-secondary/90 rounded-md disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Save
              </button>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2">
            <button
              onClick={handleProcess}
              className="flex-1 px-4 py-2 text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 hover:shadow-md rounded-md transition-all duration-200 cursor-pointer"
            >
              Process Bundle
            </button>
            <button
              onClick={handleClear}
              className="px-4 py-2 text-sm font-medium border border-border hover:bg-muted hover:shadow-md rounded-md transition-all duration-200 cursor-pointer"
            >
              Clear
            </button>
          </div>
        </div>
      </div>

      {/* Config Modal */}
      {showConfigModal && (
        <BundleConfigModal
          contentIds={items.map(item => item.id)}
          onClose={() => setShowConfigModal(false)}
        />
      )}
    </>
  );
};
