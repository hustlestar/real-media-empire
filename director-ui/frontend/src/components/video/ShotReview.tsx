import React, { useState } from 'react';
import { CheckCircle, XCircle, RefreshCw, MessageSquare, ThumbsUp, ThumbsDown, AlertCircle, Send } from 'lucide-react';
import VideoPlayer from './VideoPlayer';
import { Shot } from './ShotGallery';
import { apiUrl } from '../../config/api';

interface ShotReviewProps {
  shot: Shot;
  onReviewComplete?: (shotId: string, action: 'approve' | 'reject' | 'retake') => void;
  onClose?: () => void;
}

const ShotReview: React.FC<ShotReviewProps> = ({ shot, onReviewComplete, onClose }) => {
  const [notes, setNotes] = useState('');
  const [reviewAction, setReviewAction] = useState<'approve' | 'reject' | 'retake' | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [showNotesInput, setShowNotesInput] = useState(false);

  const handleQuickApprove = async () => {
    await submitReview('approved', 'Approved for use');
  };

  const handleQuickReject = async () => {
    setReviewAction('reject');
    setShowNotesInput(true);
  };

  const handleRequestRetake = async () => {
    setReviewAction('retake');
    setShowNotesInput(true);
  };

  const submitReview = async (status: string, reviewNotes: string) => {
    try {
      setSubmitting(true);
      const response = await fetch(apiUrl(`/api/film/shots/${shot.id}/review`), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status,
          notes: reviewNotes,
          reviewer: 'director' // In production, get from auth context
        })
      });

      if (response.ok) {
        const action = status === 'approved' ? 'approve' : status === 'rejected' ? 'reject' : 'retake';
        onReviewComplete?.(shot.id, action);
      }
    } catch (error) {
      console.error('Error submitting review:', error);
      alert('Failed to submit review. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSubmitWithNotes = async () => {
    if (!reviewAction) return;

    let status = 'needs_revision';
    if (reviewAction === 'approve') status = 'approved';
    if (reviewAction === 'reject') status = 'rejected';

    await submitReview(status, notes);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">{shot.shot_id}</h2>
          <p className="text-sm text-gray-400 mt-1">Review and provide feedback</p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition"
          >
            Close
          </button>
        )}
      </div>

      {/* Video Player */}
      <VideoPlayer src={shot.video_url} poster={shot.thumbnail_url || shot.image_url} />

      {/* Shot Details */}
      <div className="bg-gray-800 rounded-lg p-4">
        <h3 className="font-semibold text-white mb-2">Shot Details</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-400">Duration:</span>
            <span className="ml-2 text-white">{shot.duration}s</span>
          </div>
          <div>
            <span className="text-gray-400">Status:</span>
            <span className="ml-2 text-white capitalize">{shot.status}</span>
          </div>
          <div className="col-span-2">
            <span className="text-gray-400">Prompt:</span>
            <p className="mt-1 text-white">{shot.prompt}</p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      {!showNotesInput && (
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="font-semibold text-white mb-4">Director's Decision</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Approve */}
            <button
              onClick={handleQuickApprove}
              disabled={submitting}
              className="flex flex-col items-center justify-center p-6 bg-green-600 hover:bg-green-500 rounded-lg transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <CheckCircle className="w-12 h-12 text-white mb-3" />
              <span className="text-lg font-semibold text-white">Approve</span>
              <span className="text-xs text-green-200 mt-1">Ready for use</span>
            </button>

            {/* Request Retake */}
            <button
              onClick={handleRequestRetake}
              disabled={submitting}
              className="flex flex-col items-center justify-center p-6 bg-yellow-600 hover:bg-yellow-500 rounded-lg transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <RefreshCw className="w-12 h-12 text-white mb-3" />
              <span className="text-lg font-semibold text-white">Request Retake</span>
              <span className="text-xs text-yellow-200 mt-1">Needs revision</span>
            </button>

            {/* Reject */}
            <button
              onClick={handleQuickReject}
              disabled={submitting}
              className="flex flex-col items-center justify-center p-6 bg-red-600 hover:bg-red-500 rounded-lg transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <XCircle className="w-12 h-12 text-white mb-3" />
              <span className="text-lg font-semibold text-white">Reject</span>
              <span className="text-xs text-red-200 mt-1">Not suitable</span>
            </button>
          </div>
        </div>
      )}

      {/* Notes Input (when action selected) */}
      {showNotesInput && (
        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <MessageSquare className="w-5 h-5 text-blue-400 mr-2" />
            <h3 className="font-semibold text-white">
              {reviewAction === 'approve' && 'Approval Notes (Optional)'}
              {reviewAction === 'reject' && 'Rejection Reason'}
              {reviewAction === 'retake' && 'Retake Instructions'}
            </h3>
          </div>

          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder={
              reviewAction === 'approve'
                ? 'Add any notes about this shot (optional)...'
                : reviewAction === 'reject'
                ? 'Explain why this shot is not suitable...'
                : 'Describe what needs to be changed for the retake...'
            }
            className="w-full h-32 px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none resize-none"
            required={reviewAction !== 'approve'}
          />

          {/* Common Feedback Templates */}
          <div className="mt-4">
            <p className="text-xs text-gray-400 mb-2">Quick feedback templates:</p>
            <div className="flex flex-wrap gap-2">
              {reviewAction === 'retake' && (
                <>
                  <button
                    onClick={() => setNotes('Lighting needs to be more dramatic')}
                    className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs text-gray-300 transition"
                  >
                    More dramatic lighting
                  </button>
                  <button
                    onClick={() => setNotes('Action needs more tension and energy')}
                    className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs text-gray-300 transition"
                  >
                    More tension
                  </button>
                  <button
                    onClick={() => setNotes('Color palette should be cooler/darker')}
                    className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs text-gray-300 transition"
                  >
                    Darker colors
                  </button>
                  <button
                    onClick={() => setNotes('Camera angle needs adjustment - try lower angle')}
                    className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs text-gray-300 transition"
                  >
                    Adjust camera angle
                  </button>
                  <button
                    onClick={() => setNotes('Character expression too subtle, needs more emotion')}
                    className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs text-gray-300 transition"
                  >
                    More emotion
                  </button>
                </>
              )}
              {reviewAction === 'reject' && (
                <>
                  <button
                    onClick={() => setNotes('Does not match the project aesthetic')}
                    className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs text-gray-300 transition"
                  >
                    Wrong aesthetic
                  </button>
                  <button
                    onClick={() => setNotes('Quality not sufficient for final delivery')}
                    className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs text-gray-300 transition"
                  >
                    Quality issues
                  </button>
                  <button
                    onClick={() => setNotes('Composition issues - subject not properly framed')}
                    className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs text-gray-300 transition"
                  >
                    Composition issues
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Submit Buttons */}
          <div className="flex items-center justify-end space-x-3 mt-6">
            <button
              onClick={() => {
                setShowNotesInput(false);
                setReviewAction(null);
                setNotes('');
              }}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmitWithNotes}
              disabled={submitting || (reviewAction !== 'approve' && !notes.trim())}
              className={`flex items-center space-x-2 px-6 py-2 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed ${
                reviewAction === 'approve'
                  ? 'bg-green-600 hover:bg-green-500'
                  : reviewAction === 'reject'
                  ? 'bg-red-600 hover:bg-red-500'
                  : 'bg-yellow-600 hover:bg-yellow-500'
              }`}
            >
              <Send className="w-4 h-4" />
              <span>
                {submitting ? 'Submitting...' :
                 reviewAction === 'approve' ? 'Confirm Approval' :
                 reviewAction === 'reject' ? 'Confirm Rejection' :
                 'Request Retake'}
              </span>
            </button>
          </div>
        </div>
      )}

      {/* Previous Reviews */}
      {shot.review && (
        <div className="bg-gray-800 rounded-lg p-4">
          <h3 className="font-semibold text-white mb-3">Previous Review</h3>
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              {shot.review.status === 'approved' && <ThumbsUp className="w-5 h-5 text-green-400" />}
              {shot.review.status === 'rejected' && <ThumbsDown className="w-5 h-5 text-red-400" />}
              {shot.review.status === 'needs_revision' && <AlertCircle className="w-5 h-5 text-yellow-400" />}
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <span className="font-medium text-white capitalize">{shot.review.status.replace('_', ' ')}</span>
                <span className="text-xs text-gray-400">{shot.review.reviewed_at}</span>
              </div>
              {shot.review.notes && (
                <p className="text-sm text-gray-300">{shot.review.notes}</p>
              )}
              {shot.review.reviewer && (
                <p className="text-xs text-gray-500 mt-1">— {shot.review.reviewer}</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ShotReview;
