import React, { createContext, useContext, useState, useCallback, type ReactNode, useEffect } from 'react';
import type { ContentResponse } from '../api/types.gen';

const STORAGE_KEY = 'bundler_items';
const FORM_STATE_KEY = 'bundle_form_state';

export interface BundleItem {
  id: string;
  content: ContentResponse;
}

export interface BundlerState {
  items: BundleItem[];
  isOpen: boolean;
}

export interface BundlerContextType {
  // State
  items: BundleItem[];
  isOpen: boolean;

  // Actions
  addItem: (content: ContentResponse) => void;
  removeItem: (contentId: string) => void;
  clearItems: () => void;
  clearFormState: () => void;
  togglePanel: () => void;
  openPanel: () => void;
  closePanel: () => void;
  hasItem: (contentId: string) => boolean;
  getItemCount: () => number;
  loadBundle: (contents: ContentResponse[]) => void;
}

const BundlerContext = createContext<BundlerContextType | undefined>(undefined);

export const useBundlerContext = () => {
  const context = useContext(BundlerContext);
  if (!context) {
    throw new Error('useBundlerContext must be used within BundlerProvider');
  }
  return context;
};

interface BundlerProviderProps {
  children: ReactNode;
}

// Load initial state from localStorage
const loadInitialItems = (): BundleItem[] => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      return Array.isArray(parsed) ? parsed : [];
    }
  } catch (error) {
    console.error('Failed to load bundle items from localStorage:', error);
  }
  return [];
};

// Save items to localStorage
const saveItems = (items: BundleItem[]) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  } catch (error) {
    console.error('Failed to save bundle items to localStorage:', error);
  }
};

export const BundlerProvider: React.FC<BundlerProviderProps> = ({ children }) => {
  const [items, setItems] = useState<BundleItem[]>(loadInitialItems);
  const [isOpen, setIsOpen] = useState(false);

  // Save to localStorage whenever items change
  useEffect(() => {
    saveItems(items);
    // Auto-open panel if items exist
    if (items.length > 0 && !isOpen) {
      setIsOpen(true);
    }
  }, [items]);

  const addItem = useCallback((content: ContentResponse) => {
    setItems(prev => {
      // Check if item already exists
      if (prev.some(item => item.id === content.id)) {
        return prev;
      }

      const newItem: BundleItem = {
        id: content.id,
        content
      };

      return [...prev, newItem];
    });
    // Open panel when adding items manually
    setIsOpen(true);
  }, []);

  const removeItem = useCallback((contentId: string) => {
    setItems(prev => {
      const newItems = prev.filter(item => item.id !== contentId);

      // Auto-close panel when last item is removed
      if (newItems.length === 0) {
        setIsOpen(false);
      }

      return newItems;
    });
  }, []);

  const clearItems = useCallback(() => {
    setItems([]);
    setIsOpen(false);
  }, []);

  const clearFormState = useCallback(() => {
    try {
      localStorage.removeItem(FORM_STATE_KEY);
    } catch (error) {
      console.error('Failed to clear form state from localStorage:', error);
    }
  }, []);

  const togglePanel = useCallback(() => {
    setIsOpen(prev => !prev);
  }, []);

  const openPanel = useCallback(() => {
    setIsOpen(true);
  }, []);

  const closePanel = useCallback(() => {
    setIsOpen(false);
  }, []);

  const hasItem = useCallback((contentId: string) => {
    return items.some(item => item.id === contentId);
  }, [items]);

  const getItemCount = useCallback(() => {
    return items.length;
  }, [items]);

  const loadBundle = useCallback((contents: ContentResponse[]) => {
    const newItems: BundleItem[] = contents.map(content => ({
      id: content.id,
      content
    }));
    setItems(newItems);
    setIsOpen(true);
  }, []);

  const value: BundlerContextType = {
    items,
    isOpen,
    addItem,
    removeItem,
    clearItems,
    clearFormState,
    togglePanel,
    openPanel,
    closePanel,
    hasItem,
    getItemCount,
    loadBundle
  };

  return (
    <BundlerContext.Provider value={value}>
      {children}
    </BundlerContext.Provider>
  );
};
