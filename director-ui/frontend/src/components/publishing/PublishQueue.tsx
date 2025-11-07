import React from 'react';
import { Clock, CheckCircle, XCircle, Loader } from 'lucide-react';

const PublishQueue: React.FC<any> = ({ jobs, onRefresh }) => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'failed': return <XCircle className="w-5 h-5 text-red-400" />;
      case 'processing': return <Loader className="w-5 h-5 text-yellow-400 animate-spin" />;
      default: return <Clock className="w-5 h-5 text-blue-400" />;
    }
  };

  return (
    <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-6 border border-green-500 border-opacity-30">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">Publishing Queue</h2>
        <button onClick={onRefresh} className="text-sm text-green-300 hover:text-green-100">Refresh</button>
      </div>

      <div className="space-y-3">
        {jobs.map((job: any) => (
          <div key={job.job_id} className="bg-gray-900 bg-opacity-50 rounded-lg p-4">
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                <div className="font-semibold">{job.title}</div>
                <div className="text-sm text-gray-400">
                  {job.platforms.join(', ')} • {job.account_id}
                </div>
              </div>
              {getStatusIcon(job.status)}
            </div>

            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>{new Date(job.created_at).toLocaleString()}</span>
              <span className="px-2 py-1 bg-gray-800 rounded uppercase">{job.status}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PublishQueue;
