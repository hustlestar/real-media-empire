import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useListBundles, useDeleteBundle } from '../hooks/useBundler';
import { formatDistanceToNow } from 'date-fns';

export const BundlesPage: React.FC = () => {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const pageSize = 20;

  const { data, isLoading } = useListBundles(page, pageSize);
  const deleteBundle = useDeleteBundle();

  const handleDelete = async (bundleId: string) => {
    if (!confirm('Are you sure you want to delete this bundle? All processing attempts will also be deleted.')) {
      return;
    }

    try {
      await deleteBundle.mutateAsync(bundleId);
    } catch (error) {
      console.error('Failed to delete bundle:', error);
      alert('Failed to delete bundle');
    }
  };

  const handleViewDetails = (bundleId: string) => {
    navigate(`/bundles/${bundleId}`);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-muted-foreground">Loading bundles...</div>
      </div>
    );
  }

  const bundles = data?.items || [];
  const totalPages = data ? Math.ceil(data.total / pageSize) : 0;

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Bundles</h1>
          <p className="text-muted-foreground">
            Manage your content bundles and processing history
          </p>
        </div>

      {/* Bundles List */}
      {bundles.length === 0 ? (
        <div className="text-center py-20">
          <svg
            className="mx-auto h-12 w-12 text-muted-foreground mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
            />
          </svg>
          <h3 className="text-lg font-medium mb-2">No bundles yet</h3>
          <p className="text-muted-foreground mb-4">
            Start by adding content items to a bundle from the content list
          </p>
          <button
            onClick={() => navigate('/content')}
            className="inline-flex items-center px-4 py-2 text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 hover:shadow-md rounded-md transition-all duration-200 cursor-pointer"
          >
            Go to Content
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {bundles.map((bundle) => (
            <div
              key={bundle.id}
              className="bg-card border border-border rounded-lg p-6 hover:shadow-lg transition-all duration-200 cursor-pointer"
              onClick={() => handleViewDetails(bundle.id)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold">
                      {bundle.name || 'Unnamed Bundle'}
                    </h3>
                    <span className="text-sm px-2 py-1 bg-primary/10 text-primary rounded">
                      {bundle.content_ids.length} {bundle.content_ids.length === 1 ? 'item' : 'items'}
                    </span>
                  </div>

                  <div className="flex items-center gap-4 text-sm text-muted-foreground mb-3">
                    <span>
                      Created {formatDistanceToNow(new Date(bundle.created_at), { addSuffix: true })}
                    </span>
                    {bundle.updated_at !== bundle.created_at && (
                      <span>
                        Updated {formatDistanceToNow(new Date(bundle.updated_at), { addSuffix: true })}
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={(e) => {e.stopPropagation(); handleViewDetails(bundle.id)}}
                      className="text-sm font-medium text-primary hover:text-primary/80 hover:underline"
                    >
                      View Details & History
                    </button>
                  </div>
                </div>

                <div className="flex gap-2 ml-4">
                  <button
                    onClick={(e) => {e.stopPropagation(); handleViewDetails(bundle.id)}}
                    className="px-3 py-2 text-sm font-medium border border-border hover:bg-muted hover:shadow-md rounded-md transition-all duration-200"
                    title="View details"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </button>
                  <button
                    onClick={(e) => {e.stopPropagation(); handleDelete(bundle.id)}}
                    disabled={deleteBundle.isPending}
                    className="px-3 py-2 text-sm font-medium bg-destructive/10 text-destructive hover:bg-destructive/20 hover:shadow-md rounded-md disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                    title="Delete bundle"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-8 flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-4 py-2 text-sm font-medium border border-border hover:bg-muted hover:shadow-md rounded-md disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            >
              Previous
            </button>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="px-4 py-2 text-sm font-medium border border-border hover:bg-muted hover:shadow-md rounded-md disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            >
              Next
            </button>
          </div>
        </div>
      )}
      </div>
    </div>
  );
};
