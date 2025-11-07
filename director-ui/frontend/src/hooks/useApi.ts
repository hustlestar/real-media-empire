/**
 * React Query hooks for API calls
 */

import { useQuery, useMutation, useQueryClient, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
import { apiUrl } from '../config/api';

// ==================== Characters ====================

export function useCharacters(search?: string) {
  return useQuery({
    queryKey: ['characters', search],
    queryFn: async () => {
      const url = search
        ? apiUrl(`/api/characters?search=${encodeURIComponent(search)}`)
        : apiUrl('/api/characters');
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch characters');
      const data = await response.json();
      return data.characters;
    },
  });
}

export function useCharacter(id: string) {
  return useQuery({
    queryKey: ['character', id],
    queryFn: async () => {
      const response = await fetch(apiUrl(`/api/characters/${id}`));
      if (!response.ok) throw new Error('Failed to fetch character');
      return response.json();
    },
    enabled: !!id,
  });
}

export function useCreateCharacter() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (character: any) => {
      const response = await fetch(apiUrl('/api/characters'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(character),
      });
      if (!response.ok) throw new Error('Failed to create character');
      return response.json();
    },
    onSuccess: () => {
      // Invalidate and refetch characters list
      queryClient.invalidateQueries({ queryKey: ['characters'] });
    },
  });
}

export function useDeleteCharacter() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const response = await fetch(apiUrl(`/api/characters/${id}`), {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Failed to delete character');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['characters'] });
    },
  });
}

// ==================== Assets ====================

export function useAssets(filters?: {
  page?: number;
  page_size?: number;
  type?: string;
  search?: string;
  favorite_only?: boolean;
}) {
  return useQuery({
    queryKey: ['assets', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters?.page) params.set('page', filters.page.toString());
      if (filters?.page_size) params.set('page_size', filters.page_size.toString());
      if (filters?.type) params.set('type', filters.type);
      if (filters?.search) params.set('search', filters.search);
      if (filters?.favorite_only) params.set('favorite_only', 'true');

      const url = params.toString()
        ? apiUrl(`/api/assets?${params}`)
        : apiUrl('/api/assets');

      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch assets');
      return response.json();
    },
  });
}

export function useUploadAsset() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (formData: FormData) => {
      const response = await fetch(apiUrl('/api/assets/upload'), {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error('Failed to upload asset');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assets'] });
    },
  });
}

export function useToggleAssetFavorite() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const response = await fetch(apiUrl(`/api/assets/${id}/toggle-favorite`), {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to toggle favorite');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assets'] });
    },
  });
}

// ==================== Publishing ====================

export function usePublishingQueue() {
  return useQuery({
    queryKey: ['publishing-queue'],
    queryFn: async () => {
      const response = await fetch(apiUrl('/api/publishing/jobs?limit=10'));
      if (!response.ok) throw new Error('Failed to fetch publishing queue');
      return response.json();
    },
    // Refresh every 5 seconds
    refetchInterval: 5000,
  });
}

export function usePublishingStats() {
  return useQuery({
    queryKey: ['publishing-stats'],
    queryFn: async () => {
      const response = await fetch(apiUrl('/api/publishing/queue/stats'));
      if (!response.ok) throw new Error('Failed to fetch publishing stats');
      return response.json();
    },
    refetchInterval: 5000,
  });
}

export function usePublishImmediate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (publishData: any) => {
      const response = await fetch(apiUrl('/api/publishing/publish/immediate'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(publishData),
      });
      if (!response.ok) throw new Error('Failed to publish');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['publishing-queue'] });
      queryClient.invalidateQueries({ queryKey: ['publishing-stats'] });
    },
  });
}

// ==================== Film Generation ====================

export function useGenerateShot() {
  return useMutation({
    mutationFn: async (shotConfig: any) => {
      const response = await fetch(apiUrl('/api/film/generate-shot'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(shotConfig),
      });
      if (!response.ok) throw new Error('Failed to generate shot');
      return response.json();
    },
  });
}

export function useGenerateScene() {
  return useMutation({
    mutationFn: async (sceneConfig: any) => {
      const response = await fetch(apiUrl('/api/film/generate-scene'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sceneConfig),
      });
      if (!response.ok) throw new Error('Failed to generate scene');
      return response.json();
    },
  });
}

// ==================== PPTX Generation ====================

export function useEstimatePPTXCost() {
  return useMutation({
    mutationFn: async (config: any) => {
      const response = await fetch(apiUrl('/api/pptx/estimate-cost'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });
      if (!response.ok) throw new Error('Failed to estimate cost');
      return response.json();
    },
  });
}

export function useGeneratePPTXOutline() {
  return useMutation({
    mutationFn: async (config: any) => {
      const response = await fetch(apiUrl('/api/pptx/generate-outline'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });
      if (!response.ok) throw new Error('Failed to generate outline');
      return response.json();
    },
  });
}

export function useGeneratePPTX() {
  return useMutation({
    mutationFn: async (formData: FormData) => {
      const response = await fetch(apiUrl('/api/pptx/generate'), {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error('Failed to generate presentation');
      return response.json();
    },
  });
}
