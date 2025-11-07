/**
 * Schedule Manager - View and manage scheduled posts
 */

import React, { useState } from 'react';
import { Calendar, Clock, Trash2, Edit } from 'lucide-react';
import { PublishingPost } from './PublishingHub';

interface ScheduleManagerProps {
  onPublishSuccess: (post: PublishingPost) => void;
}

export default function ScheduleManager({ onPublishSuccess }: ScheduleManagerProps) {
  // Mock scheduled posts
  const [scheduledPosts] = useState<PublishingPost[]>([
    {
      id: '1',
      platform: 'tiktok',
      caption: 'Check out our new product launch! 🚀',
      contentUrl: 'https://example.com/video1.mp4',
      status: 'scheduled',
      scheduledAt: '2025-01-08T14:00:00Z'
    },
    {
      id: '2',
      platform: 'instagram',
      caption: 'Behind the scenes of our latest photoshoot 📸',
      contentUrl: 'https://example.com/video2.mp4',
      status: 'scheduled',
      scheduledAt: '2025-01-08T18:00:00Z'
    }
  ]);

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <div className="max-w-5xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold">Scheduled Posts</h2>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            New Schedule
          </button>
        </div>

        {scheduledPosts.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Calendar className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No scheduled posts</p>
          </div>
        ) : (
          <div className="space-y-3">
            {scheduledPosts.map(post => (
              <div
                key={post.id}
                className="border border-gray-200 rounded-lg p-4 hover:border-blue-400 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs font-medium capitalize">
                        {post.platform}
                      </span>
                      <div className="flex items-center gap-1 text-sm text-gray-500">
                        <Clock className="w-4 h-4" />
                        {post.scheduledAt && formatDateTime(post.scheduledAt)}
                      </div>
                    </div>
                    <p className="text-gray-900 mb-2">{post.caption}</p>
                    <p className="text-sm text-gray-500">Content: {post.contentUrl}</p>
                  </div>

                  <div className="flex items-center gap-2 ml-4">
                    <button className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors">
                      <Edit className="w-4 h-4" />
                    </button>
                    <button className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
