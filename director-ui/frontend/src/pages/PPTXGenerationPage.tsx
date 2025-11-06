import React, { useState } from 'react';
import { FileText, Sparkles, Youtube, Globe, Upload, Download, DollarSign, Zap } from 'lucide-react';
import ContentSourceSelector from '../components/pptx/ContentSourceSelector';
import PresentationConfig from '../components/pptx/PresentationConfig';
import TemplateSelector from '../components/pptx/TemplateSelector';
import OutlinePreview from '../components/pptx/OutlinePreview';
import CostEstimator from '../components/pptx/CostEstimator';
import GenerationProgress from '../components/pptx/GenerationProgress';

type ContentSource = 'ai' | 'youtube' | 'web' | 'file';
type ToneType = 'professional' | 'casual' | 'motivational' | 'educational' | 'sales' | 'technical';

interface PPTXConfig {
  presentationId: string;
  contentSource: ContentSource;

  // AI Generation
  topic: string;
  brief: string;
  additionalInstructions: string;

  // Content from external sources
  youtubeUrl: string;
  webUrl: string;
  uploadedFile: File | null;

  // Presentation settings
  numSlides: number;
  tone: ToneType;
  targetAudience: string;

  // Template settings
  templatePath: string | null;
  aspectRatio: '16:9' | '4:3';
  themeName: string;
  fontFamily: string;
  primaryColor: string;

  // Generation settings
  model: string;
  budgetLimit: number | null;
  aiEnhance: boolean;
}

const PPTXGenerationPage: React.FC = () => {
  const [config, setConfig] = useState<PPTXConfig>({
    presentationId: `pptx_${Date.now()}`,
    contentSource: 'ai',
    topic: '',
    brief: '',
    additionalInstructions: '',
    youtubeUrl: '',
    webUrl: '',
    uploadedFile: null,
    numSlides: 10,
    tone: 'professional',
    targetAudience: '',
    templatePath: null,
    aspectRatio: '16:9',
    themeName: 'professional',
    fontFamily: 'Calibri',
    primaryColor: '#1F4E78',
    model: 'gpt-4o-mini',
    budgetLimit: 1.0,
    aiEnhance: false
  });

  const [isGenerating, setIsGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [generationStage, setGenerationStage] = useState('');
  const [generatedOutline, setGeneratedOutline] = useState<any>(null);
  const [estimatedCost, setEstimatedCost] = useState<number | null>(null);
  const [resultFilePath, setResultFilePath] = useState<string | null>(null);

  const updateConfig = (updates: Partial<PPTXConfig>) => {
    setConfig(prev => ({ ...prev, ...updates }));
  };

  const handleEstimateCost = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/pptx/estimate-cost', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content_source: config.contentSource,
          topic: config.topic,
          num_slides: config.numSlides,
          model: config.model
        })
      });
      const result = await response.json();
      setEstimatedCost(result.estimated_cost);
    } catch (error) {
      console.error('Error estimating cost:', error);
    }
  };

  const handleGenerateOutline = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/pptx/generate-outline', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content_source: config.contentSource,
          topic: config.topic,
          brief: config.brief,
          youtube_url: config.youtubeUrl,
          web_url: config.webUrl,
          num_slides: config.numSlides,
          tone: config.tone,
          model: config.model
        })
      });
      const result = await response.json();
      setGeneratedOutline(result.outline);
    } catch (error) {
      console.error('Error generating outline:', error);
    }
  };

  const handleGenerate = async () => {
    try {
      setIsGenerating(true);
      setGenerationProgress(0);
      setGenerationStage('Initializing...');

      // Prepare form data for file upload
      const formData = new FormData();
      formData.append('presentation_id', config.presentationId);
      formData.append('content_source', config.contentSource);
      formData.append('topic', config.topic);
      formData.append('brief', config.brief);
      formData.append('num_slides', config.numSlides.toString());
      formData.append('tone', config.tone);
      formData.append('target_audience', config.targetAudience);
      formData.append('model', config.model);

      if (config.budgetLimit) {
        formData.append('budget_limit', config.budgetLimit.toString());
      }

      if (config.youtubeUrl) {
        formData.append('youtube_url', config.youtubeUrl);
      }

      if (config.webUrl) {
        formData.append('web_url', config.webUrl);
      }

      if (config.uploadedFile) {
        formData.append('file', config.uploadedFile);
      }

      const response = await fetch('http://localhost:8000/api/pptx/generate', {
        method: 'POST',
        body: formData
      });

      const result = await response.json();

      setResultFilePath(result.file_path);
      setGenerationProgress(100);
      setGenerationStage('Complete!');

    } catch (error) {
      console.error('Error generating presentation:', error);
      setGenerationStage('Error occurred');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-indigo-900 to-purple-900 text-white">
      {/* Header */}
      <header className="bg-black bg-opacity-50 backdrop-blur-md border-b border-blue-500">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <FileText className="w-8 h-8 text-blue-400" />
              <h1 className="text-2xl font-bold">PowerPoint Generation Studio</h1>
              <span className="px-3 py-1 bg-blue-500 bg-opacity-20 rounded-full text-sm">
                AI-Powered Presentations
              </span>
            </div>

            <div className="flex items-center space-x-4">
              {estimatedCost !== null && (
                <div className="px-4 py-2 bg-green-600 bg-opacity-20 border border-green-500 rounded-lg flex items-center space-x-2">
                  <DollarSign className="w-4 h-4 text-green-400" />
                  <span className="text-sm">Estimated: ${estimatedCost.toFixed(4)}</span>
                </div>
              )}

              <button
                onClick={handleEstimateCost}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition text-sm"
              >
                Estimate Cost
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Panel - Configuration */}
          <div className="lg:col-span-2 space-y-6">
            {/* Content Source */}
            <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-6 border border-blue-500 border-opacity-30">
              <h2 className="text-xl font-bold mb-4 flex items-center space-x-2">
                <Sparkles className="w-6 h-6 text-blue-400" />
                <span>Content Source</span>
              </h2>

              <ContentSourceSelector
                selected={config.contentSource}
                onSelect={(source) => updateConfig({ contentSource: source })}
                config={config}
                onChange={updateConfig}
              />
            </div>

            {/* Presentation Configuration */}
            <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-6 border border-blue-500 border-opacity-30">
              <h2 className="text-xl font-bold mb-4">Presentation Settings</h2>

              <PresentationConfig
                config={config}
                onChange={updateConfig}
              />
            </div>

            {/* Template Selection */}
            <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-6 border border-blue-500 border-opacity-30">
              <h2 className="text-xl font-bold mb-4">Template & Style</h2>

              <TemplateSelector
                config={config}
                onChange={updateConfig}
              />
            </div>

            {/* AI Enhancement */}
            <div className="bg-gradient-to-r from-blue-900 to-indigo-900 bg-opacity-30 backdrop-blur-md rounded-xl p-6 border border-blue-400 border-opacity-50">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <Zap className="w-5 h-5 text-yellow-400" />
                    <h3 className="font-bold text-lg">AI Content Enhancement</h3>
                    <span className="px-2 py-0.5 bg-yellow-500 bg-opacity-20 text-yellow-300 text-xs rounded-full">
                      GPT-4
                    </span>
                  </div>
                  <p className="text-sm text-gray-300">
                    Enhance slide content with more engaging language, better structure, and professional polish.
                  </p>
                </div>

                <label className="relative inline-flex items-center cursor-pointer ml-4">
                  <input
                    type="checkbox"
                    checked={config.aiEnhance}
                    onChange={(e) => updateConfig({ aiEnhance: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-14 h-8 bg-gray-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-1 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-gradient-to-r peer-checked:from-blue-600 peer-checked:to-indigo-600"></div>
                </label>
              </div>
            </div>

            {/* Generate Outline Button */}
            <button
              onClick={handleGenerateOutline}
              disabled={isGenerating || !config.topic}
              className="w-full py-3 bg-blue-600 hover:bg-blue-500 rounded-xl font-semibold transition flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <FileText className="w-5 h-5" />
              <span>Generate Outline Preview</span>
            </button>

            {/* Generate Button */}
            <button
              onClick={handleGenerate}
              disabled={isGenerating || !config.topic}
              className={`w-full py-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 rounded-xl font-bold text-lg transition flex items-center justify-center space-x-3 ${
                isGenerating ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              {isGenerating ? (
                <>
                  <div className="w-6 h-6 border-4 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-6 h-6" />
                  <span>Generate Presentation</span>
                  {config.aiEnhance && <Zap className="w-5 h-5 text-yellow-300" />}
                </>
              )}
            </button>
          </div>

          {/* Right Panel - Preview & Progress */}
          <div className="space-y-6">
            {isGenerating && (
              <GenerationProgress
                progress={generationProgress}
                stage={generationStage}
              />
            )}

            {generatedOutline && !isGenerating && (
              <OutlinePreview outline={generatedOutline} />
            )}

            {resultFilePath && !isGenerating && (
              <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-6 border border-green-500 border-opacity-30">
                <div className="text-center">
                  <div className="w-16 h-16 bg-green-500 bg-opacity-20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <FileText className="w-8 h-8 text-green-400" />
                  </div>

                  <h3 className="text-xl font-bold mb-2 text-green-300">
                    Presentation Generated!
                  </h3>

                  <p className="text-sm text-gray-300 mb-4">
                    Your PowerPoint is ready for download
                  </p>

                  <a
                    href={`http://localhost:8000/api/pptx/download/${config.presentationId}`}
                    download
                    className="inline-flex items-center space-x-2 px-6 py-3 bg-green-600 hover:bg-green-500 rounded-lg transition"
                  >
                    <Download className="w-5 h-5" />
                    <span>Download PPTX</span>
                  </a>

                  <div className="mt-4 text-xs text-gray-400">
                    File: {resultFilePath.split('/').pop()}
                  </div>
                </div>
              </div>
            )}

            {/* Cost Estimator */}
            {estimatedCost !== null && !isGenerating && (
              <CostEstimator
                estimatedCost={estimatedCost}
                budgetLimit={config.budgetLimit}
                numSlides={config.numSlides}
                model={config.model}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PPTXGenerationPage;
