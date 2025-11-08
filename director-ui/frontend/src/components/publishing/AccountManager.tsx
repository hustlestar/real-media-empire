import React, { useState } from 'react';
import { Users, Plus, Trash2, Key, CheckCircle, XCircle } from 'lucide-react';
import { apiUrl } from '../../config/api';

const AccountManager: React.FC<any> = ({ accounts, onUpdate }) => {
  const [showAddModal, setShowAddModal] = useState(false);
  const [isDeleting, setIsDeleting] = useState<string | null>(null);

  const handleDeleteAccount = async (accountId: string, platform: string) => {
    if (!confirm(`Delete ${platform} from ${accountId}?`)) return;

    setIsDeleting(`${accountId}-${platform}`);
    try {
      // In a real implementation, you'd call the delete API
      // For now, just trigger a refresh
      await onUpdate();
    } catch (error) {
      console.error('Error deleting account:', error);
    } finally {
      setIsDeleting(null);
    }
  };

  return (
    <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-6 border border-green-500 border-opacity-30">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Users className="w-5 h-5 text-green-400" />
          <h2 className="text-lg font-bold">Social Accounts</h2>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="p-2 bg-green-600 hover:bg-green-500 rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>

      {!accounts || accounts.length === 0 ? (
        <div className="text-center py-8 text-gray-400">
          <Users className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>No accounts configured</p>
          <p className="text-sm mt-1">Add your first social media account to start publishing</p>
        </div>
      ) : (
        <div className="space-y-3">
          {accounts.map((account: any) => (
            <div key={account.account_id} className="bg-gray-900 bg-opacity-50 rounded-lg p-4 hover:bg-opacity-70 transition-all">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <div className="font-semibold">{account.account_id}</div>
                  <CheckCircle className="w-4 h-4 text-green-400" />
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                {account.platforms && account.platforms.length > 0 ? (
                  account.platforms.map((platform: string) => (
                    <div
                      key={platform}
                      className="flex items-center space-x-1 px-3 py-1 bg-green-600 bg-opacity-30 rounded-full text-xs group"
                    >
                      <span className="capitalize">{platform}</span>
                      <button
                        onClick={() => handleDeleteAccount(account.account_id, platform)}
                        disabled={isDeleting === `${account.account_id}-${platform}`}
                        className="ml-1 opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        {isDeleting === `${account.account_id}-${platform}` ? (
                          <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        ) : (
                          <XCircle className="w-3 h-3 hover:text-red-400" />
                        )}
                      </button>
                    </div>
                  ))
                ) : (
                  <span className="text-xs text-gray-500">No platforms connected</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Account Modal */}
      {showAddModal && (
        <AddAccountModal
          onClose={() => setShowAddModal(false)}
          onSuccess={() => {
            setShowAddModal(false);
            onUpdate();
          }}
        />
      )}
    </div>
  );
};

// Add Account Modal Component
interface AddAccountModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

const AddAccountModal: React.FC<AddAccountModalProps> = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    account_id: '',
    platform: 'tiktok',
    credentials: {
      api_key: '',
      user: '',
      client_secrets_file: '',
      channel_name: '',
      channel_id: '',
      page_id: ''
    }
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!formData.account_id || !formData.platform) return;

    setIsSubmitting(true);
    try {
      await fetch(apiUrl('/api/publishing/accounts'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          account_id: formData.account_id,
          platform: formData.platform,
          credentials: formData.credentials
        })
      });

      onSuccess();
    } catch (error) {
      console.error('Error adding account:', error);
      alert('Failed to add account. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-xl max-w-md w-full">
        <div className="p-6">
          <h3 className="text-xl font-bold mb-4 flex items-center space-x-2">
            <Key className="w-5 h-5 text-green-400" />
            <span>Add Social Account</span>
          </h3>

          <div className="space-y-4">
            <div>
              <label className="block text-sm mb-2">Account ID</label>
              <input
                type="text"
                value={formData.account_id}
                onChange={(e) => setFormData({ ...formData, account_id: e.target.value })}
                placeholder="my_brand_account"
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg"
              />
            </div>

            <div>
              <label className="block text-sm mb-2">Platform</label>
              <select
                value={formData.platform}
                onChange={(e) => setFormData({ ...formData, platform: e.target.value })}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg"
              >
                <option value="tiktok">TikTok</option>
                <option value="instagram">Instagram</option>
                <option value="facebook">Facebook</option>
                <option value="linkedin">LinkedIn</option>
                <option value="youtube">YouTube</option>
              </select>
            </div>

            {/* Platform-specific fields */}
            {formData.platform === 'youtube' ? (
              <>
                <div>
                  <label className="block text-sm mb-2">Client Secrets File Path</label>
                  <input
                    type="text"
                    value={formData.credentials.client_secrets_file}
                    onChange={(e) => setFormData({
                      ...formData,
                      credentials: { ...formData.credentials, client_secrets_file: e.target.value }
                    })}
                    placeholder="/path/to/client_secrets.json"
                    className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm mb-2">Channel Name</label>
                  <input
                    type="text"
                    value={formData.credentials.channel_name}
                    onChange={(e) => setFormData({
                      ...formData,
                      credentials: { ...formData.credentials, channel_name: e.target.value }
                    })}
                    placeholder="My Channel"
                    className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm mb-2">Channel ID</label>
                  <input
                    type="text"
                    value={formData.credentials.channel_id}
                    onChange={(e) => setFormData({
                      ...formData,
                      credentials: { ...formData.credentials, channel_id: e.target.value }
                    })}
                    placeholder="UCxxxxxxxxxxxxxxxxxx"
                    className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg"
                  />
                </div>
              </>
            ) : formData.platform === 'facebook' ? (
              <>
                <div>
                  <label className="block text-sm mb-2">API Key</label>
                  <input
                    type="password"
                    value={formData.credentials.api_key}
                    onChange={(e) => setFormData({
                      ...formData,
                      credentials: { ...formData.credentials, api_key: e.target.value }
                    })}
                    placeholder="Your API key"
                    className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm mb-2">Page ID</label>
                  <input
                    type="text"
                    value={formData.credentials.page_id}
                    onChange={(e) => setFormData({
                      ...formData,
                      credentials: { ...formData.credentials, page_id: e.target.value }
                    })}
                    placeholder="Facebook Page ID"
                    className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg"
                  />
                </div>
              </>
            ) : (
              <>
                <div>
                  <label className="block text-sm mb-2">API Key</label>
                  <input
                    type="password"
                    value={formData.credentials.api_key}
                    onChange={(e) => setFormData({
                      ...formData,
                      credentials: { ...formData.credentials, api_key: e.target.value }
                    })}
                    placeholder="Your API key"
                    className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm mb-2">Username</label>
                  <input
                    type="text"
                    value={formData.credentials.user}
                    onChange={(e) => setFormData({
                      ...formData,
                      credentials: { ...formData.credentials, user: e.target.value }
                    })}
                    placeholder="Username"
                    className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg"
                  />
                </div>
              </>
            )}
          </div>

          <div className="flex justify-end space-x-3 mt-6">
            <button
              onClick={onClose}
              disabled={isSubmitting}
              className="px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={!formData.account_id || !formData.platform || isSubmitting}
              className="px-6 py-2 bg-green-600 hover:bg-green-500 rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Adding...</span>
                </>
              ) : (
                <span>Add Account</span>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AccountManager;
