import { useQuery } from '@tanstack/react-query'
import { getSystemPromptsApiV1PromptsGet } from '@/api/sdk.gen'

export const useSystemPrompts = (language: string = 'en') => {
  return useQuery({
    queryKey: ['prompts', language],
    queryFn: async () => {
      const response = await getSystemPromptsApiV1PromptsGet({
        query: { language },
      })
      return response.data
    },
    staleTime: 5 * 60 * 1000, // 5 minutes - prompts don't change often
  })
}
