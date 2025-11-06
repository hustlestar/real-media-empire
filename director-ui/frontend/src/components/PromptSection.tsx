import React, { useState } from 'react';

interface PromptSectionProps {
  title: string;
  prompt: string;
  onPromptChange?: (prompt: string) => void;
  editable?: boolean;
  placeholder?: string;
  minHeight?: string;
  collapsed?: boolean;
}

export const PromptSection: React.FC<PromptSectionProps> = ({
  title,
  prompt,
  onPromptChange,
  editable = false,
  placeholder = 'Enter prompt...',
  minHeight = '120px',
  collapsed: initialCollapsed = false
}) => {
  const [isCollapsed, setIsCollapsed] = useState(initialCollapsed);

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      {/* Header */}
      <div
        className="flex items-center justify-between px-4 py-2 bg-gray-50 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        <h4 className="text-sm font-medium text-gray-700">{title}</h4>
        <svg
          className={`w-4 h-4 text-gray-500 transition-transform ${isCollapsed ? 'transform rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>

      {/* Content */}
      {!isCollapsed && (
        <div className="p-4">
          {editable ? (
            <textarea
              value={prompt}
              onChange={(e) => onPromptChange?.(e.target.value)}
              placeholder={placeholder}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono text-sm resize-y"
              style={{ minHeight }}
            />
          ) : (
            <div
              className="w-full px-3 py-2 bg-gray-50 rounded-md font-mono text-sm whitespace-pre-wrap break-words text-gray-700"
              style={{ minHeight }}
            >
              {prompt || <span className="text-gray-400 italic">No prompt</span>}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
