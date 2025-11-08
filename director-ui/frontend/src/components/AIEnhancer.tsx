/**
 * AIEnhancer - Reusable AI enhancement component
 *
 * Features:
 * - Works with any form structure
 * - Multiple AI model support via OpenRouter
 * - Custom instructions
 * - Context-aware suggestions
 * - Beautiful UI with loading states
 */

import React, { useState } from 'react';
import { Sparkles, ChevronDown, X, Wand2 } from 'lucide-react';

// Available AI models via OpenRouter - Optimized for text/blog/post writing
export const AI_MODELS = [
  // Quality Tier - Best for polished, refined content
  {
    id: 'google/gemini-2.5-flash',
    name: 'Gemini 2.5 Flash',
    description: 'Best all-around for blog posts and scripts with built-in reasoning',
    tier: 'quality'
  },
  {
    id: 'qwen/qwen3-235b-a22b-instruct',
    name: 'Qwen 3 235B',
    description: 'Excellent for technical content and detailed analysis',
    tier: 'quality'
  },
  {
    id: 'meta-llama/llama-4-maverick',
    name: 'Llama 4 Maverick',
    description: 'Strong at diverse content types with multimodal capabilities',
    tier: 'quality'
  },

  // Mid-Range Tier - Best balance of quality and cost
  {
    id: 'mistralai/mistral-medium-3.1',
    name: 'Mistral Medium 3.1',
    description: 'Enterprise quality at budget pricing, great for creative writing',
    tier: 'standard'
  },

  // Budget Tier - Ultra-cheap for high volume
  {
    id: 'deepseek/deepseek-chat-v3-0324',
    name: 'DeepSeek Chat V3',
    description: 'Best cheap option, strong reasoning and technical content',
    tier: 'budget'
  },
  {
    id: 'google/gemini-2.5-flash-lite',
    name: 'Gemini 2.5 Flash Lite',
    description: 'Ultra-low latency for batch processing and high-volume generation',
    tier: 'budget'
  }
];

interface AIEnhancerProps {
  // Field to enhance
  fieldName: string;
  fieldLabel: string;

  // Current form state
  formData: Record<string, any>;

  // Callback to update the field
  onUpdate: (fieldName: string, value: string) => void;

  // Optional: Field-specific enhancement prompt
  enhancementPrompt?: string;

  // Optional: Additional context for AI
  context?: string;

  // Optional: Custom button text
  buttonText?: string;

  // Optional: Button variant
  variant?: 'compact' | 'full';

  // Optional: Default model
  defaultModel?: string;
}

const AIEnhancer: React.FC<AIEnhancerProps> = ({
  fieldName,
  fieldLabel,
  formData,
  onUpdate,
  enhancementPrompt,
  context,
  buttonText = 'AI Assist',
  variant = 'compact',
  defaultModel = 'google/gemini-2.5-flash'
}) => {
  const [isEnhancing, setIsEnhancing] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [selectedModel, setSelectedModel] = useState(defaultModel);
  const [customInstructions, setCustomInstructions] = useState('');
  const [error, setError] = useState<string | null>(null);

  // Build enhancement prompt based on field and context
  const buildPrompt = () => {
    const currentValue = formData[fieldName] || '';
    const otherFields = Object.entries(formData)
      .filter(([key]) => key !== fieldName && formData[key])
      .map(([key, value]) => `${key}: ${value}`)
      .join('\n');

    let systemPrompt = `You are a professional creative writing assistant specialized in ${fieldLabel.toLowerCase()}.`;

    if (enhancementPrompt) {
      systemPrompt += `\n\n${enhancementPrompt}`;
    }

    let userPrompt = '';

    if (currentValue) {
      userPrompt = `Enhance and improve this ${fieldLabel.toLowerCase()}:\n\n${currentValue}\n\n`;
    } else {
      userPrompt = `Generate a professional ${fieldLabel.toLowerCase()} based on the following context:\n\n`;
    }

    if (otherFields) {
      userPrompt += `Context from other fields:\n${otherFields}\n\n`;
    }

    if (context) {
      userPrompt += `Additional context: ${context}\n\n`;
    }

    if (customInstructions) {
      userPrompt += `Special instructions: ${customInstructions}\n\n`;
    }

    userPrompt += `Provide ONLY the enhanced/generated ${fieldLabel.toLowerCase()}, without explanations or meta-commentary.`;

    return { systemPrompt, userPrompt };
  };

  // Call OpenRouter API
  const enhanceWithAI = async () => {
    setIsEnhancing(true);
    setError(null);

    try {
      const { systemPrompt, userPrompt } = buildPrompt();

      // Call backend API that proxies to OpenRouter
      const response = await fetch('/api/ai/enhance', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: selectedModel,
          system_prompt: systemPrompt,
          user_prompt: userPrompt,
          field_name: fieldName,
          form_data: formData
        })
      });

      if (!response.ok) {
        throw new Error('AI enhancement failed');
      }

      const result = await response.json();
      const enhancedText = result.enhanced_text || result.text || '';

      if (enhancedText) {
        onUpdate(fieldName, enhancedText);
      }
    } catch (err) {
      console.error('AI enhancement error:', err);
      setError('Failed to enhance. Please try again.');

      // Fallback to simple enhancement
      fallbackEnhancement();
    } finally {
      setIsEnhancing(false);
    }
  };

  // Fallback enhancement logic (client-side only)
  const fallbackEnhancement = () => {
    const currentValue = formData[fieldName] || '';

    // Simple enhancement based on field name
    let enhanced = '';

    if (fieldName.includes('subject') || fieldName.includes('character')) {
      enhanced = currentValue || 'Professional actor in their 30s, confident demeanor, wearing modern business casual attire';
    } else if (fieldName.includes('action')) {
      enhanced = currentValue || 'Performing a pivotal moment of realization, subtle expressions conveying inner transformation';
    } else if (fieldName.includes('location')) {
      enhanced = currentValue || 'Contemporary office space with glass walls, natural light streaming through floor-to-ceiling windows, minimalist modern design';
    } else if (fieldName.includes('idea')) {
      enhanced = currentValue || 'A compelling narrative exploring the human condition through cinematic storytelling';
    } else {
      enhanced = currentValue || `Enhanced ${fieldLabel.toLowerCase()} content`;
    }

    onUpdate(fieldName, enhanced);
  };

  const selectedModelInfo = AI_MODELS.find(m => m.id === selectedModel) || AI_MODELS[0];

  if (variant === 'compact') {
    return (
      <div className="relative">
        <button
          type="button"
          onClick={enhanceWithAI}
          disabled={isEnhancing}
          className="flex items-center space-x-1 px-3 py-1 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:from-gray-600 disabled:to-gray-600 rounded-lg text-xs font-semibold transition"
          title={`Enhance with ${selectedModelInfo.name}`}
        >
          {isEnhancing ? (
            <>
              <Sparkles className="w-3 h-3 animate-spin" />
              <span>Enhancing...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-3 h-3" />
              <span>{buttonText}</span>
            </>
          )}
        </button>
      </div>
    );
  }

  // Full variant with settings
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={enhanceWithAI}
          disabled={isEnhancing}
          className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:from-gray-600 disabled:to-gray-600 rounded-lg font-semibold transition"
        >
          {isEnhancing ? (
            <>
              <Sparkles className="w-4 h-4 animate-spin" />
              <span>Enhancing with AI...</span>
            </>
          ) : (
            <>
              <Wand2 className="w-4 h-4" />
              <span>{buttonText}</span>
            </>
          )}
        </button>

        <button
          type="button"
          onClick={() => setShowSettings(!showSettings)}
          className="flex items-center space-x-2 px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition text-sm"
        >
          <span>Settings</span>
          <ChevronDown className={`w-4 h-4 transition-transform ${showSettings ? 'rotate-180' : ''}`} />
        </button>
      </div>

      {error && (
        <div className="bg-red-900 bg-opacity-20 border border-red-500 rounded-lg p-3 flex items-center justify-between">
          <span className="text-sm text-red-300">{error}</span>
          <button onClick={() => setError(null)} className="text-red-400 hover:text-red-300">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {showSettings && (
        <div className="bg-gray-900 bg-opacity-50 border border-gray-700 rounded-lg p-4 space-y-4">
          {/* Model Selection */}
          <div>
            <label className="block text-sm font-semibold mb-2">AI Model</label>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none text-sm"
            >
              {AI_MODELS.map((model) => (
                <option key={model.id} value={model.id}>
                  {model.name} - {model.description}
                </option>
              ))}
            </select>
            <div className="mt-2 flex items-center justify-between text-xs">
              <span className="text-gray-400">{selectedModelInfo.description}</span>
              <span className={`px-2 py-0.5 rounded ${
                selectedModelInfo.tier === 'quality'
                  ? 'bg-purple-500 bg-opacity-20 text-purple-300'
                  : selectedModelInfo.tier === 'standard'
                  ? 'bg-blue-500 bg-opacity-20 text-blue-300'
                  : 'bg-green-500 bg-opacity-20 text-green-300'
              }`}>
                {selectedModelInfo.tier}
              </span>
            </div>
          </div>

          {/* Custom Instructions */}
          <div>
            <label className="block text-sm font-semibold mb-2">Custom Instructions (Optional)</label>
            <textarea
              value={customInstructions}
              onChange={(e) => setCustomInstructions(e.target.value)}
              placeholder="e.g., Make it more dramatic, add technical details, use simpler language..."
              rows={2}
              className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none text-sm resize-none"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default AIEnhancer;
