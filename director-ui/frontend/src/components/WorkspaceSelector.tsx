import React, { useState } from 'react';
import { Briefcase, ChevronDown, Plus, BarChart3 } from 'lucide-react';
import { useWorkspace } from '../contexts/WorkspaceContext';

const WorkspaceSelector: React.FC = () => {
  const { currentWorkspace, workspaces, stats, setCurrentWorkspace, loading } = useWorkspace();
  const [isOpen, setIsOpen] = useState(false);

  if (loading) {
    return (
      <div className="flex items-center space-x-2 px-4 py-2 bg-gray-800 rounded-lg">
        <Briefcase className="w-5 h-5 text-gray-400 animate-pulse" />
        <span className="text-sm text-gray-400">Loading...</span>
      </div>
    );
  }

  if (workspaces.length === 0) {
    return (
      <div className="flex items-center space-x-2 px-4 py-2 bg-yellow-900 bg-opacity-20 border border-yellow-600 rounded-lg">
        <Briefcase className="w-5 h-5 text-yellow-400" />
        <span className="text-sm text-yellow-300">No workspaces</span>
        <button className="ml-2 px-2 py-1 bg-yellow-600 hover:bg-yellow-500 rounded text-xs transition">
          Create One
        </button>
      </div>
    );
  }

  return (
    <div className="relative">
      {/* Current Workspace Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between space-x-3 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition min-w-[250px]"
      >
        <div className="flex items-center space-x-3">
          <Briefcase className="w-5 h-5 text-purple-400" />
          <div className="text-left">
            <div className="text-sm font-medium text-white">
              {currentWorkspace?.name || 'Select Workspace'}
            </div>
            {stats && (
              <div className="text-xs text-gray-400">
                {stats.totals.films} films • {stats.storage.used_gb.toFixed(1)}GB used
              </div>
            )}
          </div>
        </div>
        <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />

          {/* Menu */}
          <div className="absolute top-full left-0 mt-2 w-80 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-20 overflow-hidden">
            {/* Header */}
            <div className="px-4 py-3 bg-gray-900 border-b border-gray-700">
              <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
                Select Workspace
              </div>
            </div>

            {/* Workspace List */}
            <div className="max-h-96 overflow-y-auto">
              {workspaces.map((workspace) => (
                <button
                  key={workspace.id}
                  onClick={() => {
                    setCurrentWorkspace(workspace);
                    setIsOpen(false);
                  }}
                  className={`w-full flex items-center justify-between px-4 py-3 hover:bg-gray-700 transition ${
                    currentWorkspace?.id === workspace.id ? 'bg-purple-900 bg-opacity-30' : ''
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      currentWorkspace?.id === workspace.id
                        ? 'bg-purple-600'
                        : 'bg-gray-700'
                    }`}>
                      <Briefcase className="w-5 h-5 text-white" />
                    </div>
                    <div className="text-left">
                      <div className="text-sm font-medium text-white">
                        {workspace.name}
                      </div>
                      <div className="text-xs text-gray-400">
                        {workspace.slug}
                      </div>
                    </div>
                  </div>

                  {currentWorkspace?.id === workspace.id && (
                    <div className="w-2 h-2 bg-purple-400 rounded-full" />
                  )}
                </button>
              ))}
            </div>

            {/* Footer */}
            <div className="px-4 py-3 bg-gray-900 border-t border-gray-700 space-y-2">
              <button className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-purple-600 hover:bg-purple-500 rounded-lg transition">
                <Plus className="w-4 h-4" />
                <span className="text-sm font-medium">Create Workspace</span>
              </button>

              {currentWorkspace && (
                <button className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition">
                  <BarChart3 className="w-4 h-4" />
                  <span className="text-sm">View Statistics</span>
                </button>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default WorkspaceSelector;
