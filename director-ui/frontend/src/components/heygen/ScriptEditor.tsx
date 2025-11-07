/**
 * Script Editor - Write and edit avatar script
 *
 * Features:
 * - Rich text editor
 * - Character count
 * - Estimated duration
 * - Word count
 * - Script templates
 * - Auto-save to local storage
 */

import React, { useState, useEffect } from 'react';
import { FileText, Clock, Type, Copy, Save, Sparkles } from 'lucide-react';

interface ScriptEditorProps {
  script: string;
  title: string;
  onScriptChange: (script: string) => void;
  onTitleChange: (title: string) => void;
}

const SCRIPT_TEMPLATES = [
  {
    name: 'Product Introduction',
    template: 'Hi, I\'m excited to introduce you to [Product Name]!\n\n[Product Name] is designed to [solve problem/benefit].\n\nWith features like [feature 1], [feature 2], and [feature 3], you can [achieve goal].\n\nReady to get started? Visit [website] today!'
  },
  {
    name: 'Educational Content',
    template: 'Welcome! Today we\'re going to learn about [topic].\n\n[Topic] is important because [reason].\n\nLet me break this down into three key points:\n\nFirst, [point 1].\nSecond, [point 2].\nThird, [point 3].\n\nNow you understand [topic]! Thanks for watching!'
  },
  {
    name: 'Social Media Promo',
    template: 'Hey everyone! 👋\n\nQuick question: Are you struggling with [problem]?\n\nI have something that can help! [Solution name] makes it easy to [benefit].\n\nCheck out the link in bio to learn more!\n\n#[hashtag1] #[hashtag2]'
  },
  {
    name: 'Sales Pitch',
    template: 'What if I told you there\'s a better way to [achieve goal]?\n\nIntroducing [Product/Service] - the solution you\'ve been waiting for.\n\nUnlike other options, we offer [unique value proposition].\n\nLimited time offer: [call to action]!\n\nDon\'t miss out - act now!'
  },
  {
    name: 'Thank You Message',
    template: 'Thank you so much for [action]!\n\nYour support means the world to us.\n\nWe\'re committed to [value/promise].\n\nStay tuned for more exciting updates!\n\nSee you soon! 😊'
  }
];

export default function ScriptEditor({ script, title, onScriptChange, onTitleChange }: ScriptEditorProps) {
  const [showTemplates, setShowTemplates] = useState(false);

  // Calculate metrics
  const characterCount = script.length;
  const wordCount = script.trim() ? script.trim().split(/\s+/).length : 0;

  // Estimate duration: average speaking rate is ~150 words per minute
  const estimatedDuration = Math.ceil(wordCount / 150 * 60); // in seconds

  // Format duration
  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  // Auto-save to local storage
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (script || title) {
        localStorage.setItem('heygen_draft_script', script);
        localStorage.setItem('heygen_draft_title', title);
      }
    }, 1000); // Debounce 1 second

    return () => clearTimeout(timeoutId);
  }, [script, title]);

  // Load draft on mount
  useEffect(() => {
    const draftScript = localStorage.getItem('heygen_draft_script');
    const draftTitle = localStorage.getItem('heygen_draft_title');

    if (draftScript && !script) {
      onScriptChange(draftScript);
    }
    if (draftTitle && !title) {
      onTitleChange(draftTitle);
    }
  }, []);

  const handleApplyTemplate = (template: string) => {
    onScriptChange(template);
    setShowTemplates(false);
  };

  const handleCopyScript = () => {
    navigator.clipboard.writeText(script);
  };

  const clearDraft = () => {
    localStorage.removeItem('heygen_draft_script');
    localStorage.removeItem('heygen_draft_title');
    onScriptChange('');
    onTitleChange('');
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-2">Write Script</h2>
        <p className="text-gray-600">Create the content your avatar will speak</p>
      </div>

      {/* Title input */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Video Title (Optional)
        </label>
        <input
          type="text"
          value={title}
          onChange={(e) => onTitleChange(e.target.value)}
          placeholder="Enter a title for your video..."
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
        />
      </div>

      {/* Script editor */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        {/* Toolbar */}
        <div className="border-b border-gray-200 p-3 flex items-center justify-between bg-gray-50">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowTemplates(!showTemplates)}
              className="px-3 py-1.5 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2 text-sm"
            >
              <Sparkles className="w-4 h-4" />
              Templates
            </button>

            {script && (
              <button
                onClick={handleCopyScript}
                className="px-3 py-1.5 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2 text-sm"
              >
                <Copy className="w-4 h-4" />
                Copy
              </button>
            )}

            {(script || title) && (
              <button
                onClick={clearDraft}
                className="px-3 py-1.5 text-red-600 hover:bg-red-50 rounded-lg transition-colors text-sm"
              >
                Clear
              </button>
            )}
          </div>

          <div className="flex items-center gap-2 text-xs text-gray-500">
            <Save className="w-3 h-3" />
            <span>Auto-saved</span>
          </div>
        </div>

        {/* Template selector */}
        {showTemplates && (
          <div className="border-b border-gray-200 p-4 bg-purple-50">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Choose a template:</h3>
            <div className="grid grid-cols-2 gap-2">
              {SCRIPT_TEMPLATES.map(template => (
                <button
                  key={template.name}
                  onClick={() => handleApplyTemplate(template.template)}
                  className="px-3 py-2 bg-white border border-gray-300 rounded-lg hover:bg-purple-100 hover:border-purple-400 transition-colors text-left text-sm"
                >
                  {template.name}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Text area */}
        <textarea
          value={script}
          onChange={(e) => onScriptChange(e.target.value)}
          placeholder="Write your script here... Your avatar will speak these words exactly as written."
          className="w-full h-96 p-6 resize-none focus:outline-none focus:ring-0 font-mono text-sm leading-relaxed"
          maxLength={10000}
        />

        {/* Stats footer */}
        <div className="border-t border-gray-200 p-4 bg-gray-50">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2 text-gray-600">
                <Type className="w-4 h-4" />
                <span>{characterCount.toLocaleString()} / 10,000 characters</span>
              </div>

              <div className="flex items-center gap-2 text-gray-600">
                <FileText className="w-4 h-4" />
                <span>{wordCount} words</span>
              </div>

              <div className="flex items-center gap-2 text-gray-600">
                <Clock className="w-4 h-4" />
                <span>~{formatDuration(estimatedDuration)} estimated</span>
              </div>
            </div>

            {/* Character count indicator */}
            <div className="flex items-center gap-2">
              <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all ${
                    characterCount > 9000 ? 'bg-red-500' :
                    characterCount > 7000 ? 'bg-yellow-500' :
                    'bg-green-500'
                  }`}
                  style={{ width: `${(characterCount / 10000) * 100}%` }}
                />
              </div>
              <span className={`text-xs font-medium ${
                characterCount > 9000 ? 'text-red-600' :
                characterCount > 7000 ? 'text-yellow-600' :
                'text-green-600'
              }`}>
                {Math.floor((characterCount / 10000) * 100)}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Tips */}
      <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="text-sm font-medium text-blue-900 mb-2">💡 Script Writing Tips:</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Write conversationally - imagine you're talking to a friend</li>
          <li>• Use shorter sentences for better pacing</li>
          <li>• Add pauses with punctuation (periods, commas, ellipses)</li>
          <li>• Break long paragraphs into smaller chunks</li>
          <li>• Avoid complex jargon or hard-to-pronounce words</li>
        </ul>
      </div>
    </div>
  );
}
