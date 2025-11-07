/**
 * Generation Status - Track and display video generation progress
 *
 * Features:
 * - Real-time status updates
 * - Progress indicator
 * - Video preview when complete
 * - Cost and duration display
 * - Error handling
 * - Polling for status updates
 */

import React, { useState, useEffect } from 'react';
import {
  CheckCircle,
  Loader2,
  AlertCircle,
  Clock,
  DollarSign,
  Film,
  Download,
  ExternalLink
} from 'lucide-react';
import { GenerationResult } from './AvatarStudio';

interface GenerationStatusProps {
  result: GenerationResult;
}

export default function GenerationStatus({ result }: GenerationStatusProps) {
  const [currentStatus, setCurrentStatus] = useState(result.status);
  const [videoUrl, setVideoUrl] = useState(result.videoUrl);
  const [error, setError] = useState(result.error);
  const [polling, setPolling] = useState(result.status === 'pending' || result.status === 'processing');

  useEffect(() => {
    if (!polling) return;

    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`/api/heygen/videos/${result.videoId}/status`);
        if (!response.ok) throw new Error('Failed to fetch status');

        const data = await response.json();

        setCurrentStatus(data.status);

        if (data.status === 'completed') {
          setVideoUrl(data.video_url);
          setPolling(false);
        } else if (data.status === 'failed') {
          setError(data.error || 'Generation failed');
          setPolling(false);
        }
      } catch (err) {
        console.error('Status polling error:', err);
        // Continue polling on errors, but stop after some time
      }
    }, 10000); // Poll every 10 seconds

    // Stop polling after 5 minutes
    const timeout = setTimeout(() => {
      setPolling(false);
      if (currentStatus !== 'completed') {
        setError('Generation timeout - please check status manually');
      }
    }, 300000);

    return () => {
      clearInterval(pollInterval);
      clearTimeout(timeout);
    };
  }, [polling, result.videoId, currentStatus]);

  const getStatusIcon = () => {
    switch (currentStatus) {
      case 'pending':
        return <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />;
      case 'processing':
        return <Loader2 className="w-6 h-6 text-purple-600 animate-spin" />;
      case 'completed':
        return <CheckCircle className="w-6 h-6 text-green-600" />;
      case 'failed':
        return <AlertCircle className="w-6 h-6 text-red-600" />;
      default:
        return <Loader2 className="w-6 h-6 text-gray-600 animate-spin" />;
    }
  };

  const getStatusColor = () => {
    switch (currentStatus) {
      case 'pending':
        return 'bg-blue-50 border-blue-200 text-blue-800';
      case 'processing':
        return 'bg-purple-50 border-purple-200 text-purple-800';
      case 'completed':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'failed':
        return 'bg-red-50 border-red-200 text-red-800';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  const getStatusMessage = () => {
    switch (currentStatus) {
      case 'pending':
        return 'Your video generation request has been queued...';
      case 'processing':
        return 'HeyGen is generating your avatar video. This may take a few minutes...';
      case 'completed':
        return 'Video generated successfully! Ready to download.';
      case 'failed':
        return error || 'Video generation failed. Please try again.';
      default:
        return 'Processing your request...';
    }
  };

  return (
    <div className="space-y-6">
      {/* Status card */}
      <div className={`rounded-lg border p-6 ${getStatusColor()}`}>
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0">
            {getStatusIcon()}
          </div>
          <div className="flex-1">
            <h3 className="font-medium text-lg capitalize mb-1">{currentStatus}</h3>
            <p className="text-sm">{getStatusMessage()}</p>

            {polling && (
              <div className="mt-3">
                <div className="w-full bg-white bg-opacity-50 rounded-full h-2 overflow-hidden">
                  <div className="h-full bg-current rounded-full animate-pulse" style={{ width: '60%' }} />
                </div>
                <p className="text-xs mt-2 opacity-75">
                  Checking status every 10 seconds...
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Metadata */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="font-medium mb-4">Generation Details</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="flex items-center gap-2">
            <Film className="w-4 h-4 text-gray-400" />
            <span className="text-gray-600">Video ID:</span>
            <code className="text-xs bg-gray-100 px-2 py-1 rounded">{result.videoId}</code>
          </div>

          <div className="flex items-center gap-2">
            <DollarSign className="w-4 h-4 text-gray-400" />
            <span className="text-gray-600">Cost:</span>
            <span className="font-medium">${result.cost.toFixed(2)}</span>
          </div>

          {result.duration > 0 && (
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-gray-400" />
              <span className="text-gray-600">Duration:</span>
              <span className="font-medium">{result.duration.toFixed(1)}s</span>
            </div>
          )}
        </div>

        {/* Additional metadata */}
        {result.metadata && Object.keys(result.metadata).length > 0 && (
          <details className="mt-4">
            <summary className="text-sm text-gray-600 cursor-pointer hover:text-gray-900">
              View full metadata
            </summary>
            <pre className="mt-2 text-xs bg-gray-50 p-3 rounded overflow-auto max-h-48">
              {JSON.stringify(result.metadata, null, 2)}
            </pre>
          </details>
        )}
      </div>

      {/* Video preview (when completed) */}
      {currentStatus === 'completed' && videoUrl && (
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <div className="p-4 border-b border-gray-200 flex items-center justify-between">
            <h3 className="font-medium">Video Preview</h3>
            <div className="flex items-center gap-2">
              <a
                href={videoUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center gap-2"
              >
                <ExternalLink className="w-4 h-4" />
                Open in new tab
              </a>
              <a
                href={videoUrl}
                download
                className="px-3 py-1.5 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Download
              </a>
            </div>
          </div>

          <div className="aspect-[9/16] max-w-md mx-auto bg-black">
            <video
              src={videoUrl}
              controls
              className="w-full h-full"
              onError={(e) => {
                console.error('Video playback error');
              }}
            >
              Your browser does not support video playback.
            </video>
          </div>
        </div>
      )}

      {/* Error details (when failed) */}
      {currentStatus === 'failed' && error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h4 className="font-medium text-red-900 mb-2">Error Details</h4>
          <p className="text-sm text-red-700">{error}</p>
          <div className="mt-4 flex gap-2">
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm"
            >
              Try Again
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
