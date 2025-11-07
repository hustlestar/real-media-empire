import React, { useState } from 'react';
import { Send, Zap } from 'lucide-react';
import { apiUrl } from '../../config/api';

const QuickPublish: React.FC<any> = ({ accounts, onPublish }) => {
  const [videoPath, setVideoPath] = useState('');
  const [title, setTitle] = useState('');
  const [platforms, setPlatforms] = useState<string[]>([]);
  const [accountId, setAccountId] = useState('');

  const handlePublish = async () => {
    if (!videoPath || !title || platforms.length === 0 || !accountId) return;

    try {
      await fetch(apiUrl('/api/publishing/publish/immediate'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          account_id: accountId,
          platforms,
          video_path: videoPath,
          title,
          description: ''
        })
      });

      onPublish();
      setVideoPath('');
      setTitle('');
      setPlatforms([]);
    } catch (error) {
      console.error('Publish error:', error);
    }
  };

  return (
    <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-6 border border-green-500 border-opacity-30">
      <div className="flex items-center space-x-2 mb-4">
        <Zap className="w-5 h-5 text-green-400" />
        <h2 className="text-xl font-bold">Quick Publish</h2>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm mb-2">Video Path</label>
          <input
            type="text"
            value={videoPath}
            onChange={(e) => setVideoPath(e.target.value)}
            placeholder="/path/to/video.mp4"
            className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg"
          />
        </div>

        <div>
          <label className="block text-sm mb-2">Title</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Video title"
            className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg"
          />
        </div>

        <div>
          <label className="block text-sm mb-2">Account</label>
          <select
            value={accountId}
            onChange={(e) => setAccountId(e.target.value)}
            className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg"
          >
            <option value="">Select account</option>
            {accounts.map((acc: any) => (
              <option key={acc.account_id} value={acc.account_id}>{acc.account_id}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm mb-2">Platforms</label>
          <div className="grid grid-cols-2 gap-2">
            {['tiktok', 'instagram', 'facebook', 'linkedin', 'youtube'].map(platform => (
              <label key={platform} className="flex items-center space-x-2 p-2 bg-gray-900 rounded cursor-pointer">
                <input
                  type="checkbox"
                  checked={platforms.includes(platform)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setPlatforms([...platforms, platform]);
                    } else {
                      setPlatforms(platforms.filter(p => p !== platform));
                    }
                  }}
                />
                <span className="capitalize">{platform}</span>
              </label>
            ))}
          </div>
        </div>

        <button
          onClick={handlePublish}
          disabled={!videoPath || !title || platforms.length === 0 || !accountId}
          className="w-full py-3 bg-green-600 hover:bg-green-500 rounded-lg font-semibold flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Send className="w-5 h-5" />
          <span>Publish Now</span>
        </button>
      </div>
    </div>
  );
};

export default QuickPublish;
