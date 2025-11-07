import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { RefreshCw } from 'lucide-react';

import VersionHistory, { ShotVersion } from '../components/iteration/VersionHistory';
import QuickTweak from '../components/iteration/QuickTweak';
import VariantGrid, { Variant } from '../components/iteration/VariantGrid';
import RefinementTool from '../components/iteration/RefinementTool';

const IterationStudioPage: React.FC = () => {
  const { shotId } = useParams<{ shotId: string }>();
  const navigate = useNavigate();

  // Mock data - in production, fetch from API
  const [versions] = useState<ShotVersion[]>([
    {
      id: 'v1',
      version: 1,
      shotId: shotId || 'shot_001',
      createdAt: new Date(Date.now() - 86400000),
      videoUrl: '/video1.mp4',
      status: 'approved',
      prompt: 'Cinematic shot of a futuristic city at night',
      provider: 'Minimax',
      generationTime: 45.2,
      cost: 0.15
    }
  ]);

  const [variants] = useState<Variant[]>([]);

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-4 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate(-1)}
              className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded transition"
            >
              ← Back
            </button>

            <div className="border-l border-gray-700 pl-4">
              <h1 className="text-xl font-bold text-white">Iteration Studio</h1>
              <p className="text-sm text-gray-400">Refine and perfect your shots</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="space-y-8">
          {/* Version History */}
          <VersionHistory
            shotId={shotId || 'shot_001'}
            versions={versions}
            onVersionSelect={(v) => console.log('Selected:', v)}
            onRevertToVersion={(v) => console.log('Revert to:', v)}
          />

          {/* Quick Tweaks */}
          <QuickTweak
            currentShot={versions[0] ? {
              id: versions[0].id,
              prompt: versions[0].prompt,
              thumbnailUrl: versions[0].thumbnailUrl
            } : undefined}
            onApplyTweak={(t) => console.log('Apply tweak:', t)}
          />

          {/* Variant Grid */}
          <VariantGrid
            basePrompt={versions[0]?.prompt || ''}
            variants={variants}
            onGenerateVariants={(count) => console.log('Generate:', count)}
          />

          {/* Refinement Tool */}
          <RefinementTool
            imageUrl="https://via.placeholder.com/800x600"
            onApplyRefinements={(regions) => console.log('Refine:', regions)}
          />
        </div>
      </div>
    </div>
  );
};

export default IterationStudioPage;
