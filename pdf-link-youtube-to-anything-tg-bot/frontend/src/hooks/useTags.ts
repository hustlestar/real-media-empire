import { useQuery } from '@tanstack/react-query'
import { getTagsApiV1TagsGet } from '@/api/sdk.gen'

export interface Tag {
  id: string
  name: string
  created_at: string
  usage_count: number
}

export const useTags = () => {
  return useQuery({
    queryKey: ['tags'],
    queryFn: async () => {
      const response = await getTagsApiV1TagsGet()
      return response.data
    },
  })
}
