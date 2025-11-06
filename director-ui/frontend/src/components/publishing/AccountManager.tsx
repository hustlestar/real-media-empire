import React, { useState } from 'react';
import { Users, Plus, Trash2 } from 'lucide-react';

const AccountManager: React.FC<any> = ({ accounts, onUpdate }) => {
  const [showAddModal, setShowAddModal] = useState(false);

  return (
    <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-6 border border-green-500 border-opacity-30">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Users className="w-5 h-5 text-green-400" />
          <h2 className="text-lg font-bold">Accounts</h2>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="p-2 bg-green-600 hover:bg-green-500 rounded-lg"
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>

      <div className="space-y-3">
        {accounts.map((account: any) => (
          <div key={account.account_id} className="bg-gray-900 bg-opacity-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="font-semibold">{account.account_id}</div>
              <button className="p-1 hover:bg-red-600 rounded">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
            <div className="flex flex-wrap gap-1">
              {account.platforms.map((platform: string) => (
                <span key={platform} className="px-2 py-1 bg-green-600 bg-opacity-30 rounded text-xs">
                  {platform}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AccountManager;
