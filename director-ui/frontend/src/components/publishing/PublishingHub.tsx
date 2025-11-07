/**
 * Publishing Hub - Main component for multi-platform social media publishing
 *
 * Features:
 * - Publish to multiple platforms simultaneously
 * - Schedule posts for future publishing
 * - Platform-specific content optimization
 * - Social account management
 * - Publishing history and analytics
 * - Platform limits and recommendations
 */

import React, { useState } from 'react';
import {
  Send,
  Calendar,
  Settings,
  BarChart3,
  AlertCircle,
  CheckCircle,
  Clock,
  Globe
} from 'lucide-react';
import PublishForm from './PublishForm';
import ScheduleManager from './ScheduleManager';
import AccountManager from './AccountManager';
import PublishingAnalytics from './PublishingAnalytics';
import PlatformLimits from './PlatformLimits';

export interface SocialAccount {
  id: string;
  platform: string;
  accountName: string;
  accountHandle: string;
  isActive: boolean;
  followerCount: number;
}

export interface PublishingPost {
  id: string;
  platform: string;
  caption: string;
  contentUrl: string;
  status: 'draft' | 'scheduled' | 'publishing' | 'published' | 'failed';
  scheduledAt?: string;
  publishedAt?: string;
  platformPostId?: string;
  platformUrl?: string;
  error?: string;
}

type Tab = 'publish' | 'schedule' | 'accounts' | 'analytics' | 'limits';

export default function PublishingHub() {
  const [activeTab, setActiveTab] = useState<Tab>('publish');
  const [selectedAccounts, setSelectedAccounts] = useState<string[]>([]);
  const [recentPublishes, setRecentPublishes] = useState<PublishingPost[]>([]);

  const tabs: Array<{ id: Tab; label: string; icon: React.ReactNode }> = [
    { id: 'publish', label: 'Publish', icon: <Send className="w-4 h-4" /> },
    { id: 'schedule', label: 'Schedule', icon: <Calendar className="w-4 h-4" /> },
    { id: 'accounts', label: 'Accounts', icon: <Settings className="w-4 h-4" /> },
    { id: 'analytics', label: 'Analytics', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'limits', label: 'Platform Info', icon: <Globe className="w-4 h-4" /> }
  ];

  const handlePublishSuccess = (post: PublishingPost) => {
    setRecentPublishes([post, ...recentPublishes.slice(0, 9)]);
  };

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <Send className="w-6 h-6 text-blue-600" />
              Publishing Hub
            </h1>
            <p className="text-sm text-gray-500 mt-1">
              Publish and schedule content across all your social media platforms
            </p>
          </div>

          {/* Quick stats */}
          <div className="flex items-center gap-6 text-sm">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{selectedAccounts.length}</div>
              <div className="text-gray-500">Accounts Selected</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{recentPublishes.filter(p => p.status === 'published').length}</div>
              <div className="text-gray-500">Published Today</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{recentPublishes.filter(p => p.status === 'scheduled').length}</div>
              <div className="text-gray-500">Scheduled</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tab navigation */}
      <div className="bg-white border-b border-gray-200">
        <div className="flex space-x-1 px-6">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                px-4 py-3 flex items-center gap-2 border-b-2 transition-colors
                ${activeTab === tab.id
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
                }
              `}
            >
              {tab.icon}
              <span className="font-medium">{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Content area */}
      <div className="flex-1 overflow-auto p-6">
        {activeTab === 'publish' && (
          <div className="max-w-6xl mx-auto">
            <PublishForm
              selectedAccounts={selectedAccounts}
              onAccountsChange={setSelectedAccounts}
              onPublishSuccess={handlePublishSuccess}
            />

            {/* Recent publishes */}
            {recentPublishes.length > 0 && (
              <div className="mt-8">
                <h2 className="text-lg font-semibold mb-4">Recent Activity</h2>
                <div className="space-y-3">
                  {recentPublishes.map(post => (
                    <div
                      key={post.id}
                      className="bg-white rounded-lg border border-gray-200 p-4"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-medium capitalize">{post.platform}</span>
                            {post.status === 'published' && (
                              <CheckCircle className="w-4 h-4 text-green-600" />
                            )}
                            {post.status === 'scheduled' && (
                              <Clock className="w-4 h-4 text-purple-600" />
                            )}
                            {post.status === 'failed' && (
                              <AlertCircle className="w-4 h-4 text-red-600" />
                            )}
                          </div>
                          <p className="text-sm text-gray-600 line-clamp-2">{post.caption}</p>
                          {post.platformUrl && (
                            <a
                              href={post.platformUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-sm text-blue-600 hover:underline mt-1 inline-block"
                            >
                              View post →
                            </a>
                          )}
                        </div>
                        <span className={`
                          px-2 py-1 rounded text-xs font-medium
                          ${post.status === 'published' ? 'bg-green-100 text-green-800' :
                            post.status === 'scheduled' ? 'bg-purple-100 text-purple-800' :
                            post.status === 'failed' ? 'bg-red-100 text-red-800' :
                            'bg-gray-100 text-gray-800'
                          }
                        `}>
                          {post.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'schedule' && (
          <ScheduleManager onPublishSuccess={handlePublishSuccess} />
        )}

        {activeTab === 'accounts' && (
          <AccountManager
            selectedAccounts={selectedAccounts}
            onAccountsChange={setSelectedAccounts}
          />
        )}

        {activeTab === 'analytics' && (
          <PublishingAnalytics />
        )}

        {activeTab === 'limits' && (
          <PlatformLimits />
        )}
      </div>
    </div>
  );
}
