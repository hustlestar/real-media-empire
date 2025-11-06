import React from 'react';
import { useBundleAttemptDiff } from '../hooks/useBundler';
import { formatDistanceToNow } from 'date-fns';

interface BundleDiffViewerProps {
  attemptId1: string;
  attemptId2: string;
  onClose: () => void;
}

export const BundleDiffViewer: React.FC<BundleDiffViewerProps> = ({
  attemptId1,
  attemptId2,
  onClose
}) => {
  const { data: diff, isLoading } = useBundleAttemptDiff(attemptId1, attemptId2);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-5xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-800">
            Compare Attempts
          </h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded-md transition-colors"
          >
            <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-gray-600">Loading comparison...</div>
            </div>
          ) : diff ? (
            <div className="space-y-6">
              {/* Summary of Changes */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-blue-900 mb-2">Summary</h3>
                <div className="text-sm text-blue-800 space-y-1">
                  {diff.changes.processing_type_changed && (
                    <p>✓ Processing type changed</p>
                  )}
                  {diff.changes.language_changed && (
                    <p>✓ Output language changed</p>
                  )}
                  {diff.changes.custom_instructions_changed && (
                    <p>✓ Custom instructions changed</p>
                  )}
                  {diff.changes.system_prompt_changed && (
                    <p>✓ System prompt changed</p>
                  )}
                  {!diff.changes.processing_type_changed &&
                   !diff.changes.language_changed &&
                   !diff.changes.custom_instructions_changed &&
                   !diff.changes.system_prompt_changed && (
                    <p className="text-gray-600">No configuration changes detected</p>
                  )}
                </div>
              </div>

              {/* Side-by-Side Comparison */}
              <div className="grid grid-cols-2 gap-6">
                {/* Attempt 1 */}
                <div className="border border-gray-200 rounded-lg p-4">
                  <div className="mb-4 pb-3 border-b border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      Attempt #{diff.attempt_1.attempt_number}
                    </h3>
                    <p className="text-xs text-gray-500">
                      {formatDistanceToNow(new Date(diff.attempt_1.created_at), { addSuffix: true })}
                    </p>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase">Processing Type</label>
                      <p className={`text-sm ${diff.changes.processing_type_changed ? 'bg-yellow-100 px-2 py-1 rounded' : ''}`}>
                        {diff.attempt_1.processing_type}
                      </p>
                    </div>

                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase">Language</label>
                      <p className={`text-sm ${diff.changes.language_changed ? 'bg-yellow-100 px-2 py-1 rounded' : ''}`}>
                        {diff.attempt_1.output_language}
                      </p>
                    </div>

                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase">Custom Instructions</label>
                      <p className={`text-sm text-gray-700 ${diff.changes.custom_instructions_changed ? 'bg-yellow-100 px-2 py-1 rounded' : ''}`}>
                        {diff.attempt_1.custom_instructions || (
                          <span className="text-gray-400 italic">None</span>
                        )}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Attempt 2 */}
                <div className="border border-gray-200 rounded-lg p-4">
                  <div className="mb-4 pb-3 border-b border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      Attempt #{diff.attempt_2.attempt_number}
                    </h3>
                    <p className="text-xs text-gray-500">
                      {formatDistanceToNow(new Date(diff.attempt_2.created_at), { addSuffix: true })}
                    </p>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase">Processing Type</label>
                      <p className={`text-sm ${diff.changes.processing_type_changed ? 'bg-green-100 px-2 py-1 rounded' : ''}`}>
                        {diff.attempt_2.processing_type}
                      </p>
                    </div>

                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase">Language</label>
                      <p className={`text-sm ${diff.changes.language_changed ? 'bg-green-100 px-2 py-1 rounded' : ''}`}>
                        {diff.attempt_2.output_language}
                      </p>
                    </div>

                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase">Custom Instructions</label>
                      <p className={`text-sm text-gray-700 ${diff.changes.custom_instructions_changed ? 'bg-green-100 px-2 py-1 rounded' : ''}`}>
                        {diff.attempt_2.custom_instructions || (
                          <span className="text-gray-400 italic">None</span>
                        )}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Legend */}
              <div className="flex items-center gap-4 text-xs text-gray-600 pt-2 border-t border-gray-200">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-yellow-100 border border-yellow-200 rounded"></div>
                  <span>Previous value</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-green-100 border border-green-200 rounded"></div>
                  <span>Current value</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <p>Unable to load comparison</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end px-6 py-4 border-t border-gray-200 bg-gray-50">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 rounded-md transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
