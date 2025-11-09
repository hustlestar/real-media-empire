import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  listContentApiV1ContentGet,
  createContentFromUrlApiV1ContentFromUrlPost,
  getContentApiV1ContentContentIdGet,
  getContentWithTextApiV1ContentContentIdTextGet,
  deleteContentApiV1ContentContentIdDelete,
  updateContentLanguageApiV1ContentContentIdLanguagePatch,
} from '@/api/sdk.gen'
import type { ContentCreateFromUrl } from '@/api/types.gen'

export const useContentList = (page = 1, pageSize = 20, sourceType?: string) => {
  return useQuery({
    queryKey: ['content', page, pageSize, sourceType],
    queryFn: async () => {
      const response = await listContentApiV1ContentGet({
        query: {
          page,
          page_size: pageSize,
          source_type: sourceType,
        },
      })
      return response.data
    },
  })
}

export const useCreateContentFromUrl = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: ContentCreateFromUrl) => {
      const response = await createContentFromUrlApiV1ContentFromUrlPost({
        body: data,
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content'] })
    },
  })
}

export const useContent = (contentId: string) => {
  return useQuery({
    queryKey: ['content', contentId],
    queryFn: async () => {
      const response = await getContentApiV1ContentContentIdGet({
        path: { content_id: contentId },
      })
      return response.data
    },
    enabled: !!contentId,
  })
}

export const useContentWithText = (contentId: string, language?: string) => {
  return useQuery({
    queryKey: ['content', contentId, 'text', language],
    queryFn: async () => {
      const response = await getContentWithTextApiV1ContentContentIdTextGet({
        path: { content_id: contentId },
        query: language ? { language } : undefined,
      })
      return response.data
    },
    enabled: !!contentId,
  })
}

export const useDeleteContent = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (contentId: string) => {
      await deleteContentApiV1ContentContentIdDelete({
        path: { content_id: contentId },
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content'] })
    },
  })
}

export const useReprocessContent = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ url, sourceType, targetLanguage }: { url: string; sourceType: string; targetLanguage?: string }) => {
      const response = await createContentFromUrlApiV1ContentFromUrlPost({
        body: {
          url,
          source_type: sourceType,
          force_reprocess: true,
          target_language: targetLanguage,
        },
      })
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['content'] })
    },
  })
}

export const useUpdateContentLanguage = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ contentId, language }: { contentId: string; language: string }) => {
      const response = await updateContentLanguageApiV1ContentContentIdLanguagePatch({
        path: { content_id: contentId },
        query: { language },
      })
      return response.data
    },
    onSuccess: (data, variables) => {
      // Invalidate all content queries to refetch with updated language
      queryClient.invalidateQueries({ queryKey: ['content', variables.contentId] })
      queryClient.invalidateQueries({ queryKey: ['content'] })
    },
  })
}