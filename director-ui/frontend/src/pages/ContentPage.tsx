import { useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { useContentList, useDeleteContent } from '@/hooks/useContent'
import { Loader2, Plus } from 'lucide-react'
import ContentCard from '@/components/ContentCard'
import TagFilter from '@/components/TagFilter'
import AddContentModal from '@/components/AddContentModal'
import toast from 'react-hot-toast'

export default function ContentPage() {
  const [page, setPage] = useState(1)
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const { data, isLoading, error } = useContentList(page, 20)
  const deleteContent = useDeleteContent()

  // Client-side filtering by tags
  const filteredItems = useMemo(() => {
    console.log('=== TAG FILTERING DEBUG ===')
    console.log('selectedTags:', selectedTags)
    console.log('data?.items:', data?.items)

    if (!data?.items || selectedTags.length === 0) {
      console.log('No filtering - returning all items')
      return data?.items || []
    }

    console.log('Filtering items...')
    const filtered = data.items.filter(item => {
      console.log('Checking item:', item.id)
      console.log('  item.tags:', item.tags)
      console.log('  item.tags type:', typeof item.tags, Array.isArray(item.tags))

      // item.tags is an array of tag names (strings)
      if (!item.tags || !Array.isArray(item.tags) || item.tags.length === 0) {
        console.log('  -> NO TAGS, excluding')
        return false
      }

      // Check if any selected tag is in the item's tags array
      const matches = selectedTags.some(selectedTag => {
        const included = item.tags.includes(selectedTag)
        console.log(`  Checking "${selectedTag}" in tags:`, included)
        return included
      })

      console.log('  -> Match result:', matches)
      return matches
    })

    console.log('Filtered result count:', filtered.length)
    console.log('=== END DEBUG ===')
    return filtered
  }, [data?.items, selectedTags])

  const handleTagToggle = (tag: string) => {
    setSelectedTags(prev =>
      prev.includes(tag)
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    )
  }

  const handleClearTags = () => {
    setSelectedTags([])
  }

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this content?')) {
      try {
        await deleteContent.mutateAsync(id)
        toast.success('Content deleted successfully')
      } catch (err) {
        toast.error('Failed to delete content')
      }
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen p-8 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold mb-8">Content Library</h1>
          <div className="bg-destructive/10 border border-destructive text-destructive px-4 py-3 rounded">
            Error loading content: {error.message}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8 flex items-start justify-between">
          <div>
            <h1 className="text-4xl font-bold">Content Library</h1>
            <p className="text-muted-foreground mt-2">
              {data?.total || 0} items • Browse and process your content
            </p>
          </div>
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="flex items-center gap-2 px-6 py-3 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 hover:shadow-md transition-all duration-200 font-medium"
          >
            <Plus className="w-5 h-5" />
            <span>Add Content</span>
          </button>
        </div>

        {/* Tag Filter */}
        <div className="mb-6">
          <TagFilter
            selectedTags={selectedTags}
            onTagToggle={handleTagToggle}
            onClearAll={handleClearTags}
          />
        </div>

        {data && data.items && data.items.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-muted-foreground text-lg mb-4">No content yet</p>
            <p className="text-sm text-muted-foreground">
              Send YouTube links, PDFs, or web pages to the Telegram bot to get started!
            </p>
          </div>
        ) : (
          <>
            {filteredItems.length === 0 && selectedTags.length > 0 ? (
              <div className="text-center py-20">
                <p className="text-muted-foreground text-lg mb-4">No content matches selected tags</p>
                <p className="text-sm text-muted-foreground">
                  Try selecting different tags or clear all filters
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                {filteredItems.map((item) => (
                  <ContentCard key={item.id} item={item} onDelete={handleDelete} />
                ))}
              </div>
            )}

            {data && data.total > 20 && (
              <div className="flex items-center justify-between border-t pt-6">
                <div className="text-sm text-muted-foreground">
                  Showing {((page - 1) * 20) + 1} to {Math.min(page * 20, data.total)} of {data.total} items
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="px-4 py-2 border rounded hover:bg-muted disabled:opacity-50"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setPage(p => p + 1)}
                    disabled={!data || page * 20 >= data.total}
                    className="px-4 py-2 border rounded hover:bg-muted disabled:opacity-50"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      <AddContentModal isOpen={isAddModalOpen} onClose={() => setIsAddModalOpen(false)} />
    </div>
  )
}