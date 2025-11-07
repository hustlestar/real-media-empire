import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useBundle, useBundleAttempts, useUpdateBundle, useDeleteBundle } from '../hooks/useBundler';
import { useContentList } from '../hooks/useContent';
import { useBundlerContext } from '../context/BundlerContext';
import { BundleConfigModal } from '../components/BundleConfigModal';
import { BundleDiffViewer } from '../components/BundleDiffViewer';
import { formatDistanceToNow } from 'date-fns';

export const BundleDetailPage: React.FC = () => {
  const { bundleId } = useParams<{ bundleId: string }>();
  const navigate = useNavigate();
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [showDiffModal, setShowDiffModal] = useState(false);
  const [selectedAttempts, setSelectedAttempts] = useState<string[]>([]);
  const [editingName, setEditingName] = useState(false);
  const [newName, setNewName] = useState('');

  const { data: bundle, isLoading: bundleLoading } = useBundle(bundleId);
  const { data: attempts, isLoading: attemptsLoading } = useBundleAttempts(bundleId);
  const { data: contentItems } = useContentList(1, 100);
  const { loadBundle } = useBundlerContext();
  const updateBundle = useUpdateBundle();
  const deleteBundle = useDeleteBundle();

  const handleUpdateName = async () => {
    if (!bundleId || !newName.trim()) return;

    try {
      await updateBundle.mutateAsync({
        bundleId,
        data: { name: newName }
      });
      setEditingName(false);
      setNewName('');
    } catch (error) {
      console.error('Failed to update bundle name:', error);
      alert('Failed to update bundle name');
    }
  };

  const handleDelete = async () => {
    if (!bundleId) return;
    if (!confirm('Are you sure you want to delete this bundle? All processing attempts will also be deleted.')) {
      return;
    }

    try {
      await deleteBundle.mutateAsync(bundleId);
      navigate('/bundles');
    } catch (error) {
      console.error('Failed to delete bundle:', error);
      alert('Failed to delete bundle');
    }
  };

  const handleAttemptSelect = (attemptId: string) => {
    setSelectedAttempts(prev => {
      if (prev.includes(attemptId)) {
        return prev.filter(id => id !== attemptId);
      }
      if (prev.length >= 2) {
        return [prev[1], attemptId];
      }
      return [...prev, attemptId];
    });
  };

  const handleCompareDiff = () => {
    if (selectedAttempts.length === 2) {
      setShowDiffModal(true);
    }
  };

  const handleLoadToBundle = () => {
    if (!bundle || !contentItems?.items) return;

    // Find all content items that match the bundle's content_ids
    const bundleContents = contentItems.items.filter(item =>
      bundle.content_ids.includes(item.id)
    );

    if (bundleContents.length === 0) {
      alert('Content items not found');
      return;
    }

    loadBundle(bundleContents);
    navigate('/content');
  };

  if (bundleLoading || attemptsLoading) {
    return (
      <div className="min-h-screen p-8 flex items-center justify-center">
        <div className="text-muted-foreground">Loading bundle details...</div>
      </div>
    );
  }

  if (!bundle) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-5xl mx-auto">
          <div className="text-center py-12">
            <h2 className="text-2xl font-bold mb-2">Bundle not found</h2>
            <button
              onClick={() => navigate('/bundles')}
              className="text-primary hover:underline"
            >
              Back to bundles
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <button
          onClick={() => navigate('/bundles')}
          className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground mb-6"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Bundles
        </button>

        <div className="bg-card border border-border rounded-lg p-6 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              {editingName ? (
                <div className="flex items-center gap-2 mb-2">
                  <input
                    type="text"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    placeholder={bundle.name || 'Unnamed Bundle'}
                    className="text-2xl font-bold border-b-2 border-primary focus:outline-none bg-transparent"
                    autoFocus
                  />
                  <button
                    onClick={handleUpdateName}
                    className="px-3 py-1 text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 rounded"
                  >
                    Save
                  </button>
                  <button
                    onClick={() => {
                      setEditingName(false);
                      setNewName('');
                    }}
                    className="px-3 py-1 text-sm font-medium border border-border hover:bg-muted rounded"
                  >
                    Cancel
                  </button>
                </div>
              ) : (
                <div className="flex items-center gap-3 mb-2">
                  <h1 className="text-2xl font-bold">
                    {bundle.name || 'Unnamed Bundle'}
                  </h1>
                  <button
                    onClick={() => {
                      setNewName(bundle.name || '');
                      setEditingName(true);
                    }}
                    className="p-1 text-muted-foreground hover:text-foreground"
                    title="Edit name"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                    </svg>
                  </button>
                </div>
              )}

              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <span>{bundle.content_ids.length} content items</span>
                <span>•</span>
                <span>{bundle.attempt_count || 0} processing attempts</span>
                <span>•</span>
                <span>Created {formatDistanceToNow(new Date(bundle.created_at), { addSuffix: true })}</span>
              </div>
            </div>

            <div className="flex gap-2 ml-4">
              <button
                onClick={handleLoadToBundle}
                className="px-4 py-2 text-sm font-medium border border-border hover:bg-muted rounded-lg transition-colors"
                title="Load this bundle into the bundle panel"
              >
                Load to Bundle
              </button>
              <button
                onClick={() => setShowConfigModal(true)}
                className="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 rounded-lg transition-colors"
              >
                Process Again
              </button>
              <button
                onClick={handleDelete}
                disabled={deleteBundle.isPending}
                className="px-4 py-2 text-sm font-medium text-destructive border border-destructive hover:bg-destructive/10 rounded-lg disabled:opacity-50 transition-colors"
              >
                Delete Bundle
              </button>
            </div>
          </div>
        </div>

        {/* Content Items */}
        <div className="bg-card border border-border rounded-lg p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Content Items</h2>
          <div className="space-y-2">
            {bundle.content_items && bundle.content_items.length > 0 ? (
              bundle.content_items.map((item, index) => (
                <div key={item.id} className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
                  <span className="text-sm font-medium text-muted-foreground">#{index + 1}</span>
                  <span className="text-xs px-2 py-1 bg-primary/10 text-primary rounded">
                    {item.source_type}
                  </span>
                  <span className="text-sm flex-1 truncate">
                    {item.metadata?.title || item.metadata?.url || 'Untitled'}
                  </span>
                </div>
              ))
            ) : (
              <p className="text-sm text-muted-foreground">No content items found</p>
            )}
        </div>
      </div>

        {/* Processing Attempts */}
        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Processing History</h2>
            {selectedAttempts.length === 2 && (
              <button
                onClick={handleCompareDiff}
                className="px-3 py-1 text-sm font-medium text-primary bg-primary/10 hover:bg-primary/20 rounded-md transition-colors"
              >
                Compare Selected
              </button>
            )}
          </div>

          {attempts && attempts.length > 0 ? (
            <div className="space-y-2">
              {attempts.map((attempt) => (
                <div
                  key={attempt.id}
                  className={`p-4 border rounded-lg cursor-pointer transition-all ${
                    selectedAttempts.includes(attempt.id)
                      ? 'border-primary bg-primary/5'
                      : 'border-border hover:border-primary/50'
                  }`}
                  onClick={() => handleAttemptSelect(attempt.id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-sm font-semibold">
                          Attempt #{attempt.attempt_number}
                        </span>
                        <span className="text-xs px-2 py-1 bg-muted text-muted-foreground rounded">
                          {attempt.processing_type}
                        </span>
                        <span className="text-xs px-2 py-1 bg-muted text-muted-foreground rounded">
                          {attempt.output_language}
                        </span>
                      </div>

                      {attempt.custom_instructions && (
                        <p className="text-sm text-muted-foreground mb-2 line-clamp-2">
                          {attempt.custom_instructions}
                        </p>
                      )}

                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <span>{formatDistanceToNow(new Date(attempt.created_at), { addSuffix: true })}</span>
                        {attempt.job_id && (
                          <>
                            <span>•</span>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                navigate(`/jobs/${attempt.job_id}`);
                              }}
                              className="text-primary hover:underline"
                            >
                              View Job
                            </button>
                          </>
                        )}
                      </div>
                    </div>

                    {selectedAttempts.includes(attempt.id) && (
                      <div className="ml-2">
                        <svg className="w-6 h-6 text-primary" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <p className="mb-2">No processing attempts yet</p>
              <button
                onClick={() => setShowConfigModal(true)}
                className="text-sm text-primary hover:underline"
              >
                Process this bundle now
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Modals */}
      {showConfigModal && bundleId && (
        <BundleConfigModal
          contentIds={bundle.content_ids}
          bundleId={bundleId}
          onClose={() => setShowConfigModal(false)}
        />
      )}

      {showDiffModal && selectedAttempts.length === 2 && (
        <BundleDiffViewer
          attemptId1={selectedAttempts[0]}
          attemptId2={selectedAttempts[1]}
          onClose={() => setShowDiffModal(false)}
        />
      )}
    </div>
  );
};
