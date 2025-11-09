import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiUrl } from '../config/api';

interface Workspace {
  id: string;
  name: string;
  slug: string;
  owner_id: number;
  storage_quota_gb: number;
  monthly_budget_usd: number;
  settings: Record<string, any>;
  created_at: string;
  updated_at: string;
}

interface WorkspaceStats {
  workspace_id: string;
  workspace_name: string;
  totals: {
    projects: number;
    films: number;
    characters: number;
    assets: number;
  };
  storage: {
    used_gb: number;
    quota_gb: number;
    percent_used: number;
  };
  costs: {
    total_spent_usd: number;
    monthly_budget_usd: number;
    percent_used: number;
  };
}

interface WorkspaceContextType {
  currentWorkspace: Workspace | null;
  workspaces: Workspace[];
  stats: WorkspaceStats | null;
  setCurrentWorkspace: (workspace: Workspace | null) => void;
  refreshWorkspaces: () => Promise<void>;
  refreshStats: () => Promise<void>;
  loading: boolean;
  error: string | null;
}

const WorkspaceContext = createContext<WorkspaceContextType | undefined>(undefined);

interface WorkspaceProviderProps {
  children: ReactNode;
}

export const WorkspaceProvider: React.FC<WorkspaceProviderProps> = ({ children }) => {
  const [currentWorkspace, setCurrentWorkspace] = useState<Workspace | null>(null);
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [stats, setStats] = useState<WorkspaceStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load workspaces on mount
  const refreshWorkspaces = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(apiUrl('/api/workspaces'));
      if (!response.ok) {
        throw new Error('Failed to fetch workspaces');
      }

      const data = await response.json();
      setWorkspaces(data.workspaces || []);

      // Auto-select first workspace if none selected
      if (!currentWorkspace && data.workspaces.length > 0) {
        const savedWorkspaceId = localStorage.getItem('currentWorkspaceId');
        const workspace = savedWorkspaceId
          ? data.workspaces.find((w: Workspace) => w.id === savedWorkspaceId)
          : data.workspaces[0];

        if (workspace) {
          setCurrentWorkspace(workspace);
          localStorage.setItem('currentWorkspaceId', workspace.id);
        }
      }
    } catch (err) {
      console.error('Error fetching workspaces:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  // Load workspace stats
  const refreshStats = async () => {
    if (!currentWorkspace) return;

    try {
      const response = await fetch(apiUrl(`/api/workspaces/${currentWorkspace.id}/stats`));
      if (!response.ok) {
        throw new Error('Failed to fetch workspace stats');
      }

      const data = await response.json();
      setStats(data);
    } catch (err) {
      console.error('Error fetching workspace stats:', err);
    }
  };

  // Load workspaces on mount
  useEffect(() => {
    refreshWorkspaces();
  }, []);

  // Refresh stats when workspace changes
  useEffect(() => {
    if (currentWorkspace) {
      refreshStats();
      // Save to localStorage
      localStorage.setItem('currentWorkspaceId', currentWorkspace.id);
    }
  }, [currentWorkspace]);

  const value: WorkspaceContextType = {
    currentWorkspace,
    workspaces,
    stats,
    setCurrentWorkspace,
    refreshWorkspaces,
    refreshStats,
    loading,
    error
  };

  return (
    <WorkspaceContext.Provider value={value}>
      {children}
    </WorkspaceContext.Provider>
  );
};

export const useWorkspace = (): WorkspaceContextType => {
  const context = useContext(WorkspaceContext);
  if (context === undefined) {
    throw new Error('useWorkspace must be used within a WorkspaceProvider');
  }
  return context;
};
