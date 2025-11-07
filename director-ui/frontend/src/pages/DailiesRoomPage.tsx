import React, { useState } from 'react';
import { Film, Eye, Grid, List, Filter, X } from 'lucide-react';
import ShotGallery, { Shot } from '../components/video/ShotGallery';
import ShotReview from '../components/video/ShotReview';

/**
 * THE DAILIES ROOM
 *
 * Where directors review, approve, and provide feedback on generated shots.
 *
 * Phase 1 of director-level creative controls implementation.
 */
const DailiesRoomPage: React.FC = () => {
  const [selectedShot, setSelectedShot] = useState<Shot | null>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [showReviewPanel, setShowReviewPanel] = useState(false);

  const handleShotSelect = (shot: Shot) => {
    setSelectedShot(shot);
    setShowReviewPanel(true);
  };

  const handleReviewComplete = (shotId: string, action: 'approve' | 'reject' | 'retake') => {
    console.log(`Shot ${shotId} ${action}ed`);
    // Refresh shot gallery to show updated status
    setShowReviewPanel(false);
    setSelectedShot(null);

    // Show success toast
    const actionText = action === 'approve' ? 'approved' : action === 'reject' ? 'rejected' : 'marked for retake';
    alert(`Shot successfully ${actionText}!`);
  };

  const handleCloseReview = () => {
    setShowReviewPanel(false);
    setSelectedShot(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-gray-900 text-white">
      {/* Header */}
      <header className="bg-black bg-opacity-50 backdrop-blur-md border-b border-gray-700">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Film className="w-8 h-8 text-blue-400" />
              <div>
                <h1 className="text-2xl font-bold">The Dailies Room</h1>
                <p className="text-sm text-gray-400">Review and approve generated shots</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* View Mode Toggle */}
              <div className="flex bg-gray-800 rounded-lg p-1">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded transition ${
                    viewMode === 'grid' ? 'bg-blue-600' : 'hover:bg-gray-700'
                  }`}
                  title="Grid View"
                >
                  <Grid className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded transition ${
                    viewMode === 'list' ? 'bg-blue-600' : 'hover:bg-gray-700'
                  }`}
                  title="List View"
                >
                  <List className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Shot Gallery */}
          <div className={showReviewPanel ? 'lg:col-span-2' : 'lg:col-span-3'}>
            <ShotGallery
              onShotSelect={handleShotSelect}
              selectedShotId={selectedShot?.id}
              viewMode={viewMode}
            />
          </div>

          {/* Review Panel */}
          {showReviewPanel && selectedShot && (
            <div className="lg:col-span-1">
              <div className="sticky top-6 bg-gray-800 rounded-lg p-6 border border-gray-700">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-bold flex items-center space-x-2">
                    <Eye className="w-6 h-6 text-blue-400" />
                    <span>Shot Review</span>
                  </h2>
                  <button
                    onClick={handleCloseReview}
                    className="p-2 hover:bg-gray-700 rounded-lg transition"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <Shot Review
                  shot={selectedShot}
                  onReviewComplete={handleReviewComplete}
                  onClose={handleCloseReview}
                />
              </div>
            </div>
          )}
        </div>

        {/* Help Text (when no shot selected) */}
        {!showReviewPanel && (
          <div className="mt-8 bg-blue-500/10 border border-blue-500/30 rounded-lg p-6">
            <div className="flex items-start space-x-3">
              <Eye className="w-6 h-6 text-blue-400 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-white mb-2">How to use The Dailies Room</h3>
                <ul className="text-sm text-gray-300 space-y-1">
                  <li>• Click on any shot to review it</li>
                  <li>• Watch the shot using the video player</li>
                  <li>• Approve shots that are ready for use</li>
                  <li>• Request retakes with specific feedback for shots that need improvement</li>
                  <li>• Reject shots that are not suitable</li>
                  <li>• Filter shots by status to focus on what needs review</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DailiesRoomPage;
