/**
 * Publishing Analytics - View performance metrics for published posts
 */

import React from 'react';
import { TrendingUp, Eye, Heart, MessageCircle, Share2, BarChart3 } from 'lucide-react';

interface AnalyticsData {
  platform: string;
  totalPosts: number;
  totalViews: number;
  totalLikes: number;
  totalComments: number;
  totalShares: number;
  engagementRate: number;
}

export default function PublishingAnalytics() {
  // Mock analytics data
  const analyticsData: AnalyticsData[] = [
    {
      platform: 'tiktok',
      totalPosts: 24,
      totalViews: 125000,
      totalLikes: 8500,
      totalComments: 450,
      totalShares: 320,
      engagementRate: 7.4
    },
    {
      platform: 'instagram',
      totalPosts: 18,
      totalViews: 85000,
      totalLikes: 6200,
      totalComments: 380,
      totalShares: 210,
      engagementRate: 8.1
    },
    {
      platform: 'youtube',
      totalPosts: 12,
      totalViews: 250000,
      totalLikes: 12000,
      totalComments: 890,
      totalShares: 1200,
      engagementRate: 5.6
    }
  ];

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  return (
    <div className="max-w-7xl mx-auto">
      {/* Overview cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <div className="text-gray-500 text-sm">Total Posts</div>
            <BarChart3 className="w-5 h-5 text-blue-600" />
          </div>
          <div className="text-3xl font-bold text-gray-900">54</div>
          <div className="text-sm text-green-600 mt-1">+12% this month</div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <div className="text-gray-500 text-sm">Total Views</div>
            <Eye className="w-5 h-5 text-purple-600" />
          </div>
          <div className="text-3xl font-bold text-gray-900">460K</div>
          <div className="text-sm text-green-600 mt-1">+18% this month</div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <div className="text-gray-500 text-sm">Total Engagement</div>
            <Heart className="w-5 h-5 text-red-600" />
          </div>
          <div className="text-3xl font-bold text-gray-900">27.8K</div>
          <div className="text-sm text-green-600 mt-1">+15% this month</div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <div className="text-gray-500 text-sm">Avg. Engagement</div>
            <TrendingUp className="w-5 h-5 text-green-600" />
          </div>
          <div className="text-3xl font-bold text-gray-900">7.1%</div>
          <div className="text-sm text-green-600 mt-1">+2.3% this month</div>
        </div>
      </div>

      {/* Platform breakdown */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold mb-6">Platform Performance</h2>

        <div className="space-y-6">
          {analyticsData.map(data => (
            <div key={data.platform} className="border-b border-gray-200 pb-6 last:border-b-0 last:pb-0">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium capitalize">{data.platform}</h3>
                <span className="text-sm text-gray-500">{data.totalPosts} posts</span>
              </div>

              <div className="grid grid-cols-5 gap-4">
                <div>
                  <div className="flex items-center gap-1 text-gray-500 text-xs mb-1">
                    <Eye className="w-3 h-3" />
                    Views
                  </div>
                  <div className="text-xl font-semibold text-gray-900">
                    {formatNumber(data.totalViews)}
                  </div>
                </div>

                <div>
                  <div className="flex items-center gap-1 text-gray-500 text-xs mb-1">
                    <Heart className="w-3 h-3" />
                    Likes
                  </div>
                  <div className="text-xl font-semibold text-gray-900">
                    {formatNumber(data.totalLikes)}
                  </div>
                </div>

                <div>
                  <div className="flex items-center gap-1 text-gray-500 text-xs mb-1">
                    <MessageCircle className="w-3 h-3" />
                    Comments
                  </div>
                  <div className="text-xl font-semibold text-gray-900">
                    {formatNumber(data.totalComments)}
                  </div>
                </div>

                <div>
                  <div className="flex items-center gap-1 text-gray-500 text-xs mb-1">
                    <Share2 className="w-3 h-3" />
                    Shares
                  </div>
                  <div className="text-xl font-semibold text-gray-900">
                    {formatNumber(data.totalShares)}
                  </div>
                </div>

                <div>
                  <div className="flex items-center gap-1 text-gray-500 text-xs mb-1">
                    <TrendingUp className="w-3 h-3" />
                    Engagement
                  </div>
                  <div className="text-xl font-semibold text-green-600">
                    {data.engagementRate}%
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Top performing posts */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mt-8">
        <h2 className="text-xl font-semibold mb-4">Top Performing Posts</h2>
        <p className="text-gray-500 text-sm">Coming soon - view your best performing content across all platforms</p>
      </div>
    </div>
  );
}
