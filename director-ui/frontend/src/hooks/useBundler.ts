import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  listBundlesApiV1BundlesGet,
  createBundleApiV1BundlesPost,
  getBundleApiV1BundlesBundleIdGet,
  updateBundleApiV1BundlesBundleIdPut,
  deleteBundleApiV1BundlesBundleIdDelete,
  processBundleApiV1BundlesBundleIdProcessPost,
  getBundleAttemptsApiV1BundlesBundleIdAttemptsGet,
  getBundleAttemptApiV1BundlesAttemptsAttemptIdGet,
  getBundleAttemptDiffApiV1BundlesAttemptsAttemptId1DiffAttemptId2Get,
} from '../api/sdk.gen';
import type {
  BundleCreate,
  BundleUpdate,
  BundleProcessConfig,
} from '../api/types.gen';

// Query Keys
export const bundleKeys = {
  all: ['bundles'] as const,
  lists: () => [...bundleKeys.all, 'list'] as const,
  list: (page: number, pageSize: number) => [...bundleKeys.lists(), { page, pageSize }] as const,
  details: () => [...bundleKeys.all, 'detail'] as const,
  detail: (id: string) => [...bundleKeys.details(), id] as const,
  attempts: (bundleId: string) => [...bundleKeys.all, 'attempts', bundleId] as const,
  attempt: (attemptId: string) => [...bundleKeys.all, 'attempt', attemptId] as const,
  diff: (attemptId1: string, attemptId2: string) => [...bundleKeys.all, 'diff', attemptId1, attemptId2] as const,
};

// Create Bundle
export const useCreateBundle = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: BundleCreate) => {
      const response = await createBundleApiV1BundlesPost({
        body: data
      });
      return response.data!;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: bundleKeys.lists() });
    }
  });
};

// List Bundles
export const useListBundles = (page: number = 1, pageSize: number = 20) => {
  return useQuery({
    queryKey: bundleKeys.list(page, pageSize),
    queryFn: async () => {
      const response = await listBundlesApiV1BundlesGet({
        query: { page, page_size: pageSize }
      });
      return response.data!;
    }
  });
};

// Get Bundle Details
export const useBundle = (bundleId: string | undefined) => {
  return useQuery({
    queryKey: bundleId ? bundleKeys.detail(bundleId) : ['bundles', 'null'],
    queryFn: async () => {
      if (!bundleId) return null;

      const response = await getBundleApiV1BundlesBundleIdGet({
        path: { bundle_id: bundleId }
      });
      return response.data!;
    },
    enabled: !!bundleId
  });
};

// Update Bundle
export const useUpdateBundle = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ bundleId, data }: { bundleId: string; data: BundleUpdate }) => {
      const response = await updateBundleApiV1BundlesBundleIdPut({
        path: { bundle_id: bundleId },
        body: data
      });
      return response.data!;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: bundleKeys.detail(variables.bundleId) });
      queryClient.invalidateQueries({ queryKey: bundleKeys.lists() });
    }
  });
};

// Delete Bundle
export const useDeleteBundle = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (bundleId: string) => {
      await deleteBundleApiV1BundlesBundleIdDelete({
        path: { bundle_id: bundleId }
      });
      return bundleId;
    },
    onSuccess: (bundleId) => {
      queryClient.invalidateQueries({ queryKey: bundleKeys.lists() });
      queryClient.removeQueries({ queryKey: bundleKeys.detail(bundleId) });
    }
  });
};

// Process Bundle
export const useProcessBundle = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ bundleId, config }: { bundleId: string; config: BundleProcessConfig }) => {
      const response = await processBundleApiV1BundlesBundleIdProcessPost({
        path: { bundle_id: bundleId },
        body: config
      });
      return response.data!;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: bundleKeys.attempts(variables.bundleId) });
      queryClient.invalidateQueries({ queryKey: bundleKeys.detail(variables.bundleId) });
      // Invalidate jobs list as well since new job was created
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
    }
  });
};

// Get Bundle Attempts
export const useBundleAttempts = (bundleId: string | undefined) => {
  return useQuery({
    queryKey: bundleId ? bundleKeys.attempts(bundleId) : ['bundles', 'attempts', 'null'],
    queryFn: async () => {
      if (!bundleId) return [];

      const response = await getBundleAttemptsApiV1BundlesBundleIdAttemptsGet({
        path: { bundle_id: bundleId }
      });
      return response.data!;
    },
    enabled: !!bundleId
  });
};

// Get Single Attempt
export const useBundleAttempt = (attemptId: string | undefined) => {
  return useQuery({
    queryKey: attemptId ? bundleKeys.attempt(attemptId) : ['bundles', 'attempt', 'null'],
    queryFn: async () => {
      if (!attemptId) return null;

      const response = await getBundleAttemptApiV1BundlesAttemptsAttemptIdGet({
        path: { attempt_id: attemptId }
      });
      return response.data!;
    },
    enabled: !!attemptId
  });
};

// Get Attempt Diff
export const useBundleAttemptDiff = (attemptId1: string | undefined, attemptId2: string | undefined) => {
  return useQuery({
    queryKey: attemptId1 && attemptId2 ? bundleKeys.diff(attemptId1, attemptId2) : ['bundles', 'diff', 'null'],
    queryFn: async () => {
      if (!attemptId1 || !attemptId2) return null;

      const response = await getBundleAttemptDiffApiV1BundlesAttemptsAttemptId1DiffAttemptId2Get({
        path: {
          attempt_id_1: attemptId1,
          attempt_id_2: attemptId2
        }
      });
      return response.data!;
    },
    enabled: !!attemptId1 && !!attemptId2
  });
};
