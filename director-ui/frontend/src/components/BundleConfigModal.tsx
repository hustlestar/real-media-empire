import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProcessBundle, useCreateBundle } from '../hooks/useBundler';
import { useContentList } from '../hooks/useContent';
import { useSystemPrompts } from '../hooks/usePrompts';
import { useBundlerContext } from '../context/BundlerContext';
import { PromptSection } from './PromptSection';
import type { BundleProcessConfig } from '../api/types.gen';

interface BundleConfigModalProps {
  contentIds: string[];
  onClose: () => void;
  bundleId?: string;
}

const PROCESSING_TYPES = [
  { value: 'summary', label: 'Summary' },
  { value: 'mvp_plan', label: 'MVP Plan' },
  { value: 'content_ideas', label: 'Content Ideas' },
  { value: 'blog_post', label: 'Blog Post & Video Script' }
];

const LANGUAGES = [
  { value: 'en', label: 'English' },
  { value: 'ru', label: 'Russian' },
  { value: 'es', label: 'Spanish' }
];

const BUNDLE_FORM_STATE_KEY = 'bundle_form_state';

interface BundleFormState {
  processingType: string;
  outputLanguage: string;
  customInstructions: string;
  systemPrompt: string;
  userPrompt: string;
  bundleName: string;
}

// Load form state from localStorage
const loadFormState = (): Partial<BundleFormState> => {
  try {
    const stored = localStorage.getItem(BUNDLE_FORM_STATE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (error) {
    console.error('Failed to load form state from localStorage:', error);
  }
  return {};
};

// Save form state to localStorage
const saveFormState = (state: Partial<BundleFormState>) => {
  try {
    localStorage.setItem(BUNDLE_FORM_STATE_KEY, JSON.stringify(state));
  } catch (error) {
    console.error('Failed to save form state to localStorage:', error);
  }
};

export const BundleConfigModal: React.FC<BundleConfigModalProps> = ({
  contentIds,
  onClose,
  bundleId: existingBundleId
}) => {
  const navigate = useNavigate();
  const savedState = loadFormState();
  const { clearItems } = useBundlerContext();

  const [processingType, setProcessingType] = useState(savedState.processingType || 'summary');
  const [outputLanguage, setOutputLanguage] = useState(savedState.outputLanguage || 'en');
  const [customInstructions, setCustomInstructions] = useState(savedState.customInstructions || '');
  const [systemPrompt, setSystemPrompt] = useState(savedState.systemPrompt || '');
  const [userPrompt, setUserPrompt] = useState(savedState.userPrompt || '');
  const [combinedPreview, setCombinedPreview] = useState('');
  const [bundleName, setBundleName] = useState(savedState.bundleName || '');
  const [finalPrompt, setFinalPrompt] = useState('');

  const processBundle = useProcessBundle();
  const createBundle = useCreateBundle();
  const { data: contentItems } = useContentList(1, 100);
  const { data: systemPrompts, isLoading: promptsLoading } = useSystemPrompts(outputLanguage);

  // Save form state to localStorage whenever any field changes
  useEffect(() => {
    saveFormState({
      processingType,
      outputLanguage,
      customInstructions,
      systemPrompt,
      userPrompt,
      bundleName
    });
  }, [processingType, outputLanguage, customInstructions, systemPrompt, userPrompt, bundleName]);

  // Generate combined content preview
  useEffect(() => {
    if (!contentItems?.items) return;

    const selectedContent = contentItems.items
      .filter(item => contentIds.includes(item.id))
      .map((item, idx) => {
        const title = item.metadata?.title || item.metadata?.url || `Content ${idx + 1}`;
        return `=== ${title} ===\nSource: ${item.source_type}\n[Content will be extracted here]\n`;
      })
      .join('\n---\n\n');

    setCombinedPreview(selectedContent);
  }, [contentIds, contentItems]);

  // Update system prompt from backend when processing type or language changes
  // Backend prompts take precedence over saved prompts
  useEffect(() => {
    if (!systemPrompts) return;

    const promptData = systemPrompts[processingType];
    if (promptData?.system_prompt) {
      setSystemPrompt(promptData.system_prompt);
    }
  }, [processingType, systemPrompts]);

  // Generate final combined prompt that will be sent to AI
  useEffect(() => {
    if (!contentItems?.items) return;

    // Build the user message that would be sent
    const selectedContent = contentItems.items
      .filter(item => contentIds.includes(item.id))
      .map(item => item.metadata?.title || item.metadata?.url || 'Untitled')
      .join('\n- ');

    let basePrompt = '';
    if (processingType === 'summary') {
      basePrompt = `Please provide a comprehensive summary of the following ${contentIds.length} sources:\n\n- ${selectedContent}\n\nThe content from all sources is provided below. Create a unified summary that captures the key points from all sources, noting any connections or contrasts between them.\n\n${combinedPreview}`;
    } else if (processingType === 'mvp_plan') {
      basePrompt = `Based on the following ${contentIds.length} sources, create a detailed MVP plan:\n\n- ${selectedContent}\n\nAnalyze all the content below and create a comprehensive MVP plan that incorporates insights from all sources.\n\n${combinedPreview}`;
    } else if (processingType === 'content_ideas') {
      basePrompt = `Generate creative content ideas based on the following ${contentIds.length} sources:\n\n- ${selectedContent}\n\nUse the content from all sources below to generate innovative content ideas that combine themes and insights from multiple sources.\n\n${combinedPreview}`;
    }

    // Add custom instructions if provided
    const finalUserPrompt = customInstructions
      ? `${basePrompt}\n\nAdditional Instructions: ${customInstructions}`
      : basePrompt;

    // Add user prompt template if provided
    const completePrompt = userPrompt
      ? `${finalUserPrompt}\n\n${userPrompt}`
      : finalUserPrompt;

    setFinalPrompt(completePrompt);
  }, [processingType, contentIds, contentItems, combinedPreview, customInstructions, userPrompt]);

  const handleProcess = async () => {
    try {
      let bundleIdToUse = existingBundleId;

      // Create bundle first if it doesn't exist
      if (!bundleIdToUse) {
        const newBundle = await createBundle.mutateAsync({
          name: bundleName || undefined,
          content_ids: contentIds
        });
        bundleIdToUse = newBundle.id;
      }

      const config: BundleProcessConfig = {
        processing_type: processingType,
        output_language: outputLanguage,
        custom_instructions: customInstructions || undefined,
        system_prompt: systemPrompt,
        user_prompt: userPrompt || undefined,
        combined_content_preview: combinedPreview || undefined
      };

      const attempt = await processBundle.mutateAsync({
        bundleId: bundleIdToUse,
        config
      });

      // Close modal and clear bundle panel
      onClose();
      clearItems();

      // Navigate to the job detail page if we have a job_id
      if (attempt?.job_id) {
        navigate(`/jobs/${attempt.job_id}`);
      }
    } catch (error) {
      console.error('Failed to process bundle:', error);
      alert('Failed to process bundle');
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-card rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-border">
          <h2 className="text-xl font-semibold text-foreground">
            Configure Bundle Processing
          </h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-muted rounded-md transition-colors"
          >
            <svg className="w-6 h-6 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-6">
          {/* Basic Config */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Processing Type
              </label>
              <select
                value={processingType}
                onChange={(e) => setProcessingType(e.target.value)}
                className="w-full px-3 py-2 border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-primary bg-background text-foreground"
              >
                {PROCESSING_TYPES.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Output Language
              </label>
              <select
                value={outputLanguage}
                onChange={(e) => setOutputLanguage(e.target.value)}
                className="w-full px-3 py-2 border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-primary bg-background text-foreground"
              >
                {LANGUAGES.map(lang => (
                  <option key={lang.value} value={lang.value}>
                    {lang.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {!existingBundleId && (
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Bundle Name (optional)
              </label>
              <input
                type="text"
                value={bundleName}
                onChange={(e) => setBundleName(e.target.value)}
                placeholder="My research bundle..."
                className="w-full px-3 py-2 border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-primary bg-background text-foreground"
              />
            </div>
          )}

          {/* Custom Instructions */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Custom Instructions (optional)
            </label>
            <textarea
              value={customInstructions}
              onChange={(e) => setCustomInstructions(e.target.value)}
              placeholder="Add any specific instructions or focus areas..."
              rows={3}
              className="w-full px-3 py-2 border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-primary bg-background text-foreground"
            />
          </div>

          {/* Prompts */}
          <div className="space-y-4">
            <PromptSection
              title="System Prompt"
              prompt={systemPrompt}
              onPromptChange={setSystemPrompt}
              editable={true}
              minHeight="150px"
            />

            <PromptSection
              title="User Prompt Template (optional)"
              prompt={userPrompt}
              onPromptChange={setUserPrompt}
              editable={true}
              placeholder="Add custom user prompt template..."
              minHeight="100px"
              collapsed={true}
            />

            <PromptSection
              title="Combined Content Preview"
              prompt={combinedPreview}
              editable={false}
              minHeight="150px"
              collapsed={true}
            />

            <PromptSection
              title="Final User Prompt (what will be sent to AI)"
              prompt={finalPrompt}
              editable={false}
              minHeight="200px"
              collapsed={false}
            />
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-border bg-muted">
          <div className="text-sm text-muted-foreground">
            {contentIds.length} content {contentIds.length === 1 ? 'item' : 'items'} will be processed
          </div>
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium border border-border hover:bg-accent rounded-md transition-colors text-foreground"
            >
              Cancel
            </button>
            <button
              onClick={handleProcess}
              disabled={processBundle.isPending || createBundle.isPending}
              className="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 rounded-md disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {processBundle.isPending || createBundle.isPending ? 'Processing...' : 'Process Bundle'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
