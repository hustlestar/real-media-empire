import React, { useState, useEffect } from 'react';
import { Send, Clock, CheckCircle, XCircle, BarChart3, Users, TrendingUp } from 'lucide-react';
import PublishQueue from '../components/publishing/PublishQueue';
import AccountManager from '../components/publishing/AccountManager';
import PublishStats from '../components/publishing/PublishStats';
import QuickPublish from '../components/publishing/QuickPublish';
import { apiUrl } from '../config/api';

const PublishingDashboardPage: React.FC = () => {
  const [queueStats, setQueueStats] = useState<any>(null);
  const [accounts, setAccounts] = useState<any[]>([]);
  const [recentJobs, setRecentJobs] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 5000); // Refresh every 5s
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, jobsRes, accountsRes] = await Promise.all([
        fetch(apiUrl('/api/publishing/queue/stats')),
        fetch(apiUrl('/api/publishing/jobs?limit=10')),
        fetch(apiUrl('/api/publishing/accounts'))
      ]);

      const stats = await statsRes.json();
      const jobs = await jobsRes.json();
      const accts = await accountsRes.json();

      setQueueStats(stats.stats);
      setRecentJobs(jobs.jobs);
      setAccounts(accts.accounts);
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-900 via-teal-900 to-blue-900 text-white">
      <header className="bg-black bg-opacity-50 backdrop-blur-md border-b border-green-500">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Send className="w-8 h-8 text-green-400" />
              <h1 className="text-2xl font-bold">Publishing Dashboard</h1>
              {queueStats && (
                <span className="px-3 py-1 bg-green-500 bg-opacity-20 rounded-full text-sm">
                  {queueStats.pending + queueStats.processing} active
                </span>
              )}
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        {/* Stats Overview */}
        {queueStats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-6 border border-blue-500 border-opacity-30">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm text-gray-400">Pending</div>
                <Clock className="w-5 h-5 text-blue-400" />
              </div>
              <div className="text-3xl font-bold">{queueStats.pending}</div>
            </div>

            <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-6 border border-yellow-500 border-opacity-30">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm text-gray-400">Processing</div>
                <div className="w-5 h-5 border-4 border-yellow-400 border-t-transparent rounded-full animate-spin"></div>
              </div>
              <div className="text-3xl font-bold">{queueStats.processing}</div>
            </div>

            <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-6 border border-green-500 border-opacity-30">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm text-gray-400">Completed</div>
                <CheckCircle className="w-5 h-5 text-green-400" />
              </div>
              <div className="text-3xl font-bold">{queueStats.completed}</div>
            </div>

            <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-6 border border-red-500 border-opacity-30">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm text-gray-400">Failed</div>
                <XCircle className="w-5 h-5 text-red-400" />
              </div>
              <div className="text-3xl font-bold">{queueStats.failed}</div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Quick Publish */}
            <QuickPublish accounts={accounts} onPublish={fetchDashboardData} />

            {/* Publishing Queue */}
            <PublishQueue jobs={recentJobs} onRefresh={fetchDashboardData} />

            {/* Statistics */}
            <PublishStats queueStats={queueStats} />
          </div>

          {/* Sidebar */}
          <div className="space-y-8">
            {/* Account Manager */}
            <AccountManager accounts={accounts} onUpdate={fetchDashboardData} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default PublishingDashboardPage;
