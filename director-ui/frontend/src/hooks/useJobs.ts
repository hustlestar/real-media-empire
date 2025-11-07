import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  listJobsApiV1ProcessingJobsGet,
  createJobApiV1ProcessingJobsPost,
  getJobApiV1ProcessingJobsJobIdGet,
  getJobWithResultApiV1ProcessingJobsJobIdResultGet,
  retryJobApiV1ProcessingJobsJobIdRetryPost,
} from '@/api/sdk.gen'
import type { JobCreate } from '@/api/types.gen'

export const useJobsList = (
  page = 1,
  pageSize = 20,
  status?: string,
  contentId?: string
) => {
  return useQuery({
    queryKey: ['jobs', page, pageSize, status, contentId],
    queryFn: async () => {
      const response = await listJobsApiV1ProcessingJobsGet({
        query: {
          page,
          page_size: pageSize,
          status,
          content_id: contentId,
        },
      })
      return response.data
    },
  })
}

export const useCreateJob = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: JobCreate) => {
      const response = await createJobApiV1ProcessingJobsPost({
        body: data,
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
    },
  })
}

export const useJob = (jobId: string) => {
  return useQuery({
    queryKey: ['jobs', jobId],
    queryFn: async () => {
      const response = await getJobApiV1ProcessingJobsJobIdGet({
        path: { job_id: jobId },
      })
      return response.data
    },
    enabled: !!jobId,
  })
}

export const useJobWithResult = (jobId: string) => {
  return useQuery({
    queryKey: ['jobs', jobId, 'result'],
    queryFn: async () => {
      const response = await getJobWithResultApiV1ProcessingJobsJobIdResultGet({
        path: { job_id: jobId },
      })
      return response.data
    },
    enabled: !!jobId,
  })
}

export const useRetryJob = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (jobId: string) => {
      const response = await retryJobApiV1ProcessingJobsJobIdRetryPost({
        path: { job_id: jobId },
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
    },
  })
}