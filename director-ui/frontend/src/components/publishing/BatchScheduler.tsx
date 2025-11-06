import React, { useState } from 'react';
import { Calendar, Send, List, Plus, Trash2 } from 'lucide-react';
import { format, addDays, addHours } from 'date-fns';
import { apiUrl } from '../../config/api';

interface BatchPublishItem {
  id: string;
  video_path: string;
  title: string;
  description: string;
  scheduled_time: Date;
  platforms: string[];
}

interface BatchSchedulerProps {
  accounts: any[];
  onSchedule: () => void;
}

const BatchScheduler: React.FC<BatchSchedulerProps> = ({ accounts, onSchedule }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState('');
  const [batchItems, setBatchItems] = useState<BatchPublishItem[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const addBatchItem = () => {
    const newItem: BatchPublishItem = {
      id: Date.now().toString(),
      video_path: '',
      title: '',
      description: '',
      scheduled_time: addHours(new Date(), 1),
      platforms: []
    };
    setBatchItems([...batchItems, newItem]);
  };

  const removeBatchItem = (id: string) => {
    setBatchItems(batchItems.filter(item => item.id !== id));
  };

  const updateBatchItem = (id: string, updates: Partial<BatchPublishItem>) => {
    setBatchItems(batchItems.map(item =>
      item.id === id ? { ...item, ...updates } : item
    ));
  };

  const handleBatchSubmit = async () => {
    if (!selectedAccount || batchItems.length === 0) return;

    setIsSubmitting(true);
    try {
      const requests = batchItems.map(item => ({
        account_id: selectedAccount,
        platforms: item.platforms,
        video_path: item.video_path,
        title: item.title,
        description: item.description,
        scheduled_time: item.scheduled_time.toISOString(),
        priority: 5,
        max_retries: 3
      }));

      await fetch(apiUrl('/api/publishing/publish/batch'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ publishes: requests })
      });

      setBatchItems([]);
      setIsOpen(false);
      onSchedule();
    } catch (error) {
      console.error('Batch schedule error:', error);
      alert('Failed to schedule batch. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const generateSmartSchedule = () => {
    const now = new Date();
    const updatedItems = batchItems.map((item, index) => ({
      ...item,
      scheduled_time: addHours(now, (index + 1) * 2) // 2 hours apart
    }));
    setBatchItems(updatedItems);
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="px-4 py-2 bg-purple-600 hover:bg-purple-500 rounded-lg font-semibold flex items-center space-x-2"
      >
        <List className="w-5 h-5" />
        <span>Batch Schedule</span>
      </button>

      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-900 rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold flex items-center space-x-2">
                  <Calendar className="w-6 h-6 text-purple-400" />
                  <span>Batch Schedule Publishes</span>
                </h3>
                <button
                  onClick={() => setIsOpen(false)}
                  className="text-gray-400 hover:text-white"
                >
                  ✕
                </button>
              </div>

              {/* Account Selection */}
              <div className="mb-6">
                <label className="block text-sm mb-2">Account</label>
                <select
                  value={selectedAccount}
                  onChange={(e) => setSelectedAccount(e.target.value)}
                  className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg"
                >
                  <option value="">Select account</option>
                  {accounts.map((acc: any) => (
                    <option key={acc.account_id} value={acc.account_id}>{acc.account_id}</option>
                  ))}
                </select>
              </div>

              {/* Batch Items */}
              <div className="space-y-4 mb-6">
                {batchItems.map((item, index) => (
                  <div key={item.id} className="p-4 bg-gray-800 rounded-lg border border-gray-700">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-semibold">Video #{index + 1}</h4>
                      <button
                        onClick={() => removeBatchItem(item.id)}
                        className="p-1 hover:bg-red-600 rounded"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm mb-1">Video Path</label>
                        <input
                          type="text"
                          value={item.video_path}
                          onChange={(e) => updateBatchItem(item.id, { video_path: e.target.value })}
                          placeholder="/path/to/video.mp4"
                          className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-sm"
                        />
                      </div>
                      <div>
                        <label className="block text-sm mb-1">Title</label>
                        <input
                          type="text"
                          value={item.title}
                          onChange={(e) => updateBatchItem(item.id, { title: e.target.value })}
                          placeholder="Video title"
                          className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-sm"
                        />
                      </div>
                    </div>

                    <div className="mt-3">
                      <label className="block text-sm mb-1">Description</label>
                      <input
                        type="text"
                        value={item.description}
                        onChange={(e) => updateBatchItem(item.id, { description: e.target.value })}
                        placeholder="Video description"
                        className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-sm"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4 mt-3">
                      <div>
                        <label className="block text-sm mb-1">Schedule Date & Time</label>
                        <input
                          type="datetime-local"
                          value={format(item.scheduled_time, "yyyy-MM-dd'T'HH:mm")}
                          onChange={(e) => updateBatchItem(item.id, {
                            scheduled_time: new Date(e.target.value)
                          })}
                          className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-sm"
                        />
                      </div>
                      <div>
                        <label className="block text-sm mb-1">Platforms</label>
                        <div className="flex flex-wrap gap-2">
                          {['tiktok', 'instagram', 'youtube', 'facebook', 'linkedin'].map(platform => (
                            <label key={platform} className="flex items-center space-x-1 text-xs">
                              <input
                                type="checkbox"
                                checked={item.platforms.includes(platform)}
                                onChange={(e) => {
                                  if (e.target.checked) {
                                    updateBatchItem(item.id, {
                                      platforms: [...item.platforms, platform]
                                    });
                                  } else {
                                    updateBatchItem(item.id, {
                                      platforms: item.platforms.filter(p => p !== platform)
                                    });
                                  }
                                }}
                              />
                              <span className="capitalize">{platform}</span>
                            </label>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Actions */}
              <div className="flex items-center justify-between">
                <div className="space-x-2">
                  <button
                    onClick={addBatchItem}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg flex items-center space-x-2"
                  >
                    <Plus className="w-4 h-4" />
                    <span>Add Video</span>
                  </button>
                  {batchItems.length > 0 && (
                    <button
                      onClick={generateSmartSchedule}
                      className="px-4 py-2 bg-purple-600 hover:bg-purple-500 rounded-lg flex items-center space-x-2"
                    >
                      <Calendar className="w-4 h-4" />
                      <span>Auto-Schedule (2hr intervals)</span>
                    </button>
                  )}
                </div>

                <div className="flex space-x-3">
                  <button
                    onClick={() => setIsOpen(false)}
                    disabled={isSubmitting}
                    className="px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg disabled:opacity-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleBatchSubmit}
                    disabled={!selectedAccount || batchItems.length === 0 || isSubmitting}
                    className="px-6 py-2 bg-green-600 hover:bg-green-500 rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                  >
                    {isSubmitting ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        <span>Scheduling...</span>
                      </>
                    ) : (
                      <>
                        <Send className="w-5 h-5" />
                        <span>Schedule {batchItems.length} Videos</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default BatchScheduler;
