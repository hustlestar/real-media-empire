import React from 'react';
import { BarChart3, TrendingUp } from 'lucide-react';

const PublishStats: React.FC<any> = ({ queueStats }) => {
  if (!queueStats) return null;

  const totalJobs = queueStats.total || 0;
  const successRate = totalJobs > 0 ? ((queueStats.completed / totalJobs) * 100).toFixed(1) : 0;

  return (
    <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-6 border border-green-500 border-opacity-30">
      <div className="flex items-center space-x-2 mb-4">
        <BarChart3 className="w-5 h-5 text-green-400" />
        <h2 className="text-xl font-bold">Statistics</h2>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-900 bg-opacity-50 rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">Success Rate</div>
          <div className="text-2xl font-bold text-green-300">{successRate}%</div>
        </div>

        <div className="bg-gray-900 bg-opacity-50 rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">Total Jobs</div>
          <div className="text-2xl font-bold">{totalJobs}</div>
        </div>

        <div className="bg-gray-900 bg-opacity-50 rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">Scheduled</div>
          <div className="text-2xl font-bold text-blue-300">{queueStats.scheduled || 0}</div>
        </div>

        <div className="bg-gray-900 bg-opacity-50 rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">Cancelled</div>
          <div className="text-2xl font-bold text-gray-400">{queueStats.cancelled || 0}</div>
        </div>
      </div>
    </div>
  );
};

export default PublishStats;
