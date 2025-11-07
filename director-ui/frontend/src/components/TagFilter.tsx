import { useTags } from '@/hooks/useTags'
import TagBadge from './TagBadge'
import { Loader2 } from 'lucide-react'

interface TagFilterProps {
  selectedTags: string[]
  onTagToggle: (tag: string) => void
  onClearAll: () => void
}

export default function TagFilter({ selectedTags, onTagToggle, onClearAll }: TagFilterProps) {
  const { data: tagsData, isLoading } = useTags()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-4">
        <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (!tagsData || !tagsData.tags || tagsData.tags.length === 0) {
    return (
      <div className="text-sm text-muted-foreground p-4">
        No tags available
      </div>
    )
  }

  return (
    <div className="bg-card border border-border rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-sm">Filter by Tags</h3>
        {selectedTags.length > 0 && (
          <button
            onClick={onClearAll}
            className="text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            Clear all
          </button>
        )}
      </div>
      <div className="flex flex-wrap gap-2">
        {tagsData.tags.map((tagItem) => {
          const isSelected = selectedTags.includes(tagItem.name)
          return (
            <TagBadge
              key={tagItem.id}
              tag={`${tagItem.name} (${tagItem.usage_count})`}
              variant={isSelected ? 'default' : 'outline'}
              onClick={() => onTagToggle(tagItem.name)}
            />
          )
        })}
      </div>
    </div>
  )
}
