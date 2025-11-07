import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Image, Sparkles, GitBranch, Layers, Search } from 'lucide-react';

import VisualSearch, { VisualSearchResult, VisualFilters } from '../components/asset/VisualSearch';
import SemanticSearch, { SemanticSearchResult, SearchQuery } from '../components/asset/SemanticSearch';
import LineageViewer, { AssetNode, LineageData } from '../components/asset/LineageViewer';
import BatchProcessor, { BatchAsset, BatchOperation, BatchJob } from '../components/asset/BatchProcessor';

const AssetStudioPage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'visual' | 'semantic' | 'lineage' | 'batch'>('visual');

  // Visual Search state
  const [visualResults, setVisualResults] = useState<VisualSearchResult[]>([]);

  // Semantic Search state
  const [semanticResults, setSemanticResults] = useState<SemanticSearchResult[]>([]);
  const [savedQueries, setSavedQueries] = useState<string[]>([
    'dramatic sunset over futuristic city',
    'close-up emotional performance'
  ]);

  // Lineage state
  const [lineageData, setLineageData] = useState<LineageData | undefined>({
    rootNode: {
      id: 'shot_001',
      type: 'original',
      title: 'Opening Shot - City Skyline',
      thumbnailUrl: 'https://via.placeholder.com/200x120',
      metadata: {
        createdAt: new Date(Date.now() - 86400000 * 7),
        prompt: 'Cinematic wide shot of futuristic city skyline at sunset',
        status: 'approved'
      },
      children: [
        {
          id: 'shot_001_v2',
          type: 'version',
          title: 'Version 2 - More Dramatic',
          thumbnailUrl: 'https://via.placeholder.com/200x120',
          metadata: {
            createdAt: new Date(Date.now() - 86400000 * 6),
            prompt: 'Cinematic wide shot of futuristic city skyline at sunset with dramatic lighting',
            changes: 'Added dramatic lighting',
            status: 'approved'
          },
          parentId: 'shot_001',
          children: [
            {
              id: 'shot_001_v2_var_a',
              type: 'variant',
              title: 'Variant A - Warm tones',
              thumbnailUrl: 'https://via.placeholder.com/200x120',
              metadata: {
                createdAt: new Date(Date.now() - 86400000 * 5),
                changes: 'Warmer color palette',
                status: 'pending'
              },
              parentId: 'shot_001_v2'
            },
            {
              id: 'shot_001_v2_var_b',
              type: 'variant',
              title: 'Variant B - Cool tones',
              thumbnailUrl: 'https://via.placeholder.com/200x120',
              metadata: {
                createdAt: new Date(Date.now() - 86400000 * 5),
                changes: 'Cooler color palette',
                status: 'approved'
              },
              parentId: 'shot_001_v2',
              children: [
                {
                  id: 'shot_001_v2_var_b_refined',
                  type: 'refinement',
                  title: 'Refined - Enhanced details',
                  thumbnailUrl: 'https://via.placeholder.com/200x120',
                  metadata: {
                    createdAt: new Date(Date.now() - 86400000 * 4),
                    changes: 'Enhanced building details',
                    status: 'approved'
                  },
                  parentId: 'shot_001_v2_var_b'
                }
              ]
            }
          ]
        },
        {
          id: 'shot_001_v3',
          type: 'version',
          title: 'Version 3 - Different angle',
          thumbnailUrl: 'https://via.placeholder.com/200x120',
          metadata: {
            createdAt: new Date(Date.now() - 86400000 * 3),
            prompt: 'Cinematic high-angle shot of futuristic city skyline at sunset',
            changes: 'Changed to high angle',
            status: 'rejected'
          },
          parentId: 'shot_001'
        }
      ]
    },
    totalNodes: 7,
    totalBranches: 3,
    maxDepth: 3
  });

  // Batch Processor state
  const [selectedAssets, setSelectedAssets] = useState<BatchAsset[]>([]);
  const [activeJobs, setActiveJobs] = useState<BatchJob[]>([]);

  // Handlers - Visual Search
  const handleVisualSearch = async (
    imageFile: File,
    filters: VisualFilters
  ): Promise<VisualSearchResult[]> => {
    // Mock implementation - in production, send to API
    console.log('Visual search:', imageFile.name, filters);

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1500));

    // Mock results
    const mockResults: VisualSearchResult[] = [
      {
        id: 'result_1',
        assetType: 'shot',
        thumbnailUrl: 'https://via.placeholder.com/400x300',
        similarity: 95,
        metadata: {
          filename: 'city_sunset_001.mp4',
          resolution: '1920x1080',
          duration: 5.2,
          createdAt: new Date(Date.now() - 86400000),
          tags: ['city', 'sunset', 'aerial'],
          dominantColors: ['#FF6B35', '#004E89', '#F7931E'],
          mood: 'dramatic',
          composition: 'wide shot'
        }
      },
      {
        id: 'result_2',
        assetType: 'frame',
        thumbnailUrl: 'https://via.placeholder.com/400x300',
        similarity: 87,
        metadata: {
          filename: 'urban_landscape_frame_042.png',
          resolution: '3840x2160',
          createdAt: new Date(Date.now() - 86400000 * 2),
          tags: ['urban', 'landscape', 'architecture'],
          dominantColors: ['#1A1A2E', '#16213E', '#E94560'],
          mood: 'moody',
          composition: 'symmetrical'
        },
        source: {
          filmId: 'film_123',
          shotId: 'shot_042'
        }
      },
      {
        id: 'result_3',
        assetType: 'image',
        thumbnailUrl: 'https://via.placeholder.com/400x300',
        similarity: 82,
        metadata: {
          filename: 'skyline_reference.jpg',
          resolution: '2560x1440',
          createdAt: new Date(Date.now() - 86400000 * 5),
          tags: ['skyline', 'reference', 'cityscape'],
          dominantColors: ['#2C3E50', '#E67E22', '#ECF0F1']
        }
      }
    ];

    setVisualResults(mockResults);
    return mockResults;
  };

  // Handlers - Semantic Search
  const handleSemanticSearch = async (query: SearchQuery): Promise<SemanticSearchResult[]> => {
    // Mock implementation
    console.log('Semantic search:', query);

    await new Promise(resolve => setTimeout(resolve, 1000));

    const mockResults: SemanticSearchResult[] = [
      {
        id: 'sem_1',
        assetType: 'shot',
        title: 'Dramatic City Sunset - Shot 12',
        description: 'Wide establishing shot of futuristic cityscape at golden hour with dramatic cloud formations',
        thumbnailUrl: 'https://via.placeholder.com/400x300',
        semanticScore: 94,
        metadata: {
          duration: 8.5,
          resolution: '1920x1080',
          createdAt: new Date(Date.now() - 86400000),
          tags: ['dramatic', 'sunset', 'city', 'wide-shot'],
          prompt: 'Cinematic wide shot of futuristic city at sunset',
          style: 'cinematic',
          mood: 'dramatic',
          subjects: ['city', 'buildings', 'sky']
        },
        highlights: ['dramatic', 'sunset', 'city']
      },
      {
        id: 'sem_2',
        assetType: 'scene',
        title: 'Urban Dawn Sequence',
        description: 'Complete sequence showing city waking up at sunrise with time-lapse elements',
        thumbnailUrl: 'https://via.placeholder.com/400x300',
        semanticScore: 88,
        metadata: {
          duration: 45.2,
          resolution: '3840x2160',
          createdAt: new Date(Date.now() - 86400000 * 3),
          tags: ['urban', 'sunrise', 'time-lapse', 'sequence'],
          style: 'documentary',
          mood: 'inspiring',
          subjects: ['city', 'people', 'traffic']
        },
        highlights: ['city', 'sunrise']
      }
    ];

    setSemanticResults(mockResults);
    return mockResults;
  };

  const handleSaveQuery = (query: string) => {
    if (!savedQueries.includes(query)) {
      setSavedQueries([...savedQueries, query]);
    }
  };

  // Handlers - Lineage Viewer
  const handleLineageNodeSelect = (node: AssetNode) => {
    console.log('Selected node:', node);
  };

  const handleLineageNodeView = (node: AssetNode) => {
    console.log('View node:', node);
    // Navigate to preview or detailed view
  };

  const handleLineageNodeDownload = (node: AssetNode) => {
    console.log('Download node:', node);
  };

  const handleLineageNodeDelete = (nodeId: string) => {
    console.log('Delete node:', nodeId);
    // Update lineage data
  };

  const handleLineageNodeDuplicate = (node: AssetNode) => {
    console.log('Duplicate node:', node);
  };

  const handleLineageNodeApprove = (nodeId: string) => {
    console.log('Approve node:', nodeId);
  };

  // Handlers - Batch Processor
  const handleBatchDeselectAsset = (assetId: string) => {
    setSelectedAssets(selectedAssets.filter(a => a.id !== assetId));
  };

  const handleBatchClearSelection = () => {
    setSelectedAssets([]);
  };

  const handleBatchStartJob = async (operation: BatchOperation, assets: BatchAsset[]) => {
    console.log('Start batch job:', operation, assets);

    // Create new job
    const job: BatchJob = {
      id: `job_${Date.now()}`,
      operation,
      assets,
      status: 'running',
      progress: 0,
      startedAt: new Date(),
      successCount: 0,
      failureCount: 0
    };

    setActiveJobs([...activeJobs, job]);

    // Simulate job progress
    const interval = setInterval(() => {
      setActiveJobs(prev => {
        const updated = prev.map(j => {
          if (j.id === job.id && j.progress < 100) {
            const newProgress = Math.min(100, j.progress + 10);
            const isComplete = newProgress === 100;

            return {
              ...j,
              progress: newProgress,
              status: isComplete ? 'completed' : 'running',
              completedAt: isComplete ? new Date() : undefined,
              successCount: isComplete ? assets.length : j.successCount
            };
          }
          return j;
        });

        // Clear interval if job is done
        const currentJob = updated.find(j => j.id === job.id);
        if (currentJob?.status === 'completed') {
          clearInterval(interval);
        }

        return updated;
      });
    }, 500);
  };

  const handleBatchCancelJob = (jobId: string) => {
    setActiveJobs(prev => prev.map(j =>
      j.id === jobId ? { ...j, status: 'paused' as const } : j
    ));
  };

  // Tab configuration
  const tabs = [
    {
      id: 'visual' as const,
      name: 'Visual Search',
      icon: <Image className="w-5 h-5" />,
      description: 'Find similar assets by image'
    },
    {
      id: 'semantic' as const,
      name: 'Semantic Search',
      icon: <Sparkles className="w-5 h-5" />,
      description: 'Search with natural language'
    },
    {
      id: 'lineage' as const,
      name: 'Asset Lineage',
      icon: <GitBranch className="w-5 h-5" />,
      description: 'View asset family trees'
    },
    {
      id: 'batch' as const,
      name: 'Batch Processor',
      icon: <Layers className="w-5 h-5" />,
      description: 'Bulk operations'
    }
  ];

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
              <h1 className="text-xl font-bold text-white">Asset Studio Pro</h1>
              <p className="text-sm text-gray-400">Advanced asset management and discovery</p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <Search className="w-5 h-5 text-gray-400" />
            <span className="text-sm text-gray-400">
              {visualResults.length + semanticResults.length} results found
            </span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex space-x-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-3 border-b-2 transition-all ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-white bg-gray-900/50'
                    : 'border-transparent text-gray-400 hover:text-white hover:bg-gray-900/30'
                }`}
              >
                {tab.icon}
                <span className="font-medium">{tab.name}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {activeTab === 'visual' && (
          <VisualSearch
            onSearch={handleVisualSearch}
            onResultSelect={(result) => console.log('Select result:', result)}
            onDownload={(result) => console.log('Download:', result)}
            onDelete={(resultId) => console.log('Delete:', resultId)}
          />
        )}

        {activeTab === 'semantic' && (
          <SemanticSearch
            onSearch={handleSemanticSearch}
            onResultSelect={(result) => console.log('Select result:', result)}
            onSaveQuery={handleSaveQuery}
            savedQueries={savedQueries}
          />
        )}

        {activeTab === 'lineage' && (
          <LineageViewer
            data={lineageData}
            onNodeSelect={handleLineageNodeSelect}
            onNodeView={handleLineageNodeView}
            onNodeDownload={handleLineageNodeDownload}
            onNodeDelete={handleLineageNodeDelete}
            onNodeDuplicate={handleLineageNodeDuplicate}
            onNodeApprove={handleLineageNodeApprove}
          />
        )}

        {activeTab === 'batch' && (
          <BatchProcessor
            selectedAssets={selectedAssets}
            onDeselectAsset={handleBatchDeselectAsset}
            onClearSelection={handleBatchClearSelection}
            onStartJob={handleBatchStartJob}
            onCancelJob={handleBatchCancelJob}
            activeJobs={activeJobs}
          />
        )}
      </div>
    </div>
  );
};

export default AssetStudioPage;
