import { useState } from 'react'
import { X, Link as LinkIcon, FileUp, Loader2 } from 'lucide-react'
import { useCreateContentFromUrl } from '@/hooks/useContent'
import toast from 'react-hot-toast'
import { useNavigate } from 'react-router-dom'

interface AddContentModalProps {
  isOpen: boolean
  onClose: () => void
}

const SOURCE_TYPES = [
  { value: 'youtube', label: 'YouTube Video', placeholder: 'https://youtube.com/watch?v=...' },
  { value: 'pdf_url', label: 'PDF URL', placeholder: 'https://example.com/document.pdf' },
  { value: 'web', label: 'Web Page', placeholder: 'https://example.com/article' },
]

export default function AddContentModal({ isOpen, onClose }: AddContentModalProps) {
  const [url, setUrl] = useState('')
  const [sourceType, setSourceType] = useState('youtube')
  const [forceReprocess, setForceReprocess] = useState(false)
  const navigate = useNavigate()
  const createContent = useCreateContentFromUrl()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!url.trim()) {
      toast.error('Please enter a URL')
      return
    }

    try {
      const result = await createContent.mutateAsync({
        url: url.trim(),
        source_type: sourceType,
        force_reprocess: forceReprocess,
      })

      toast.success('Content added successfully!')
      onClose()
      setUrl('')
      setSourceType('youtube')
      setForceReprocess(false)

      // Navigate to the content detail page
      navigate(`/content/${result.id}`)
    } catch (error: any) {
      toast.error(error.message || 'Failed to add content')
    }
  }

  const handleClose = () => {
    onClose()
    setUrl('')
    setSourceType('youtube')
    setForceReprocess(false)
  }

  if (!isOpen) return null

  const selectedSourceType = SOURCE_TYPES.find((t) => t.value === sourceType)

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-card rounded-lg shadow-xl max-w-2xl w-full border border-border">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-border">
          <div className="flex items-center gap-3">
            <LinkIcon className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-semibold text-foreground">Add New Content</h2>
          </div>
          <button
            onClick={handleClose}
            className="p-1 hover:bg-muted rounded-md transition-colors"
          >
            <X className="w-5 h-5 text-foreground" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {/* Source Type Selection */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-3">Content Type</label>
            <div className="grid grid-cols-3 gap-3">
              {SOURCE_TYPES.map((type) => (
                <button
                  key={type.value}
                  type="button"
                  onClick={() => setSourceType(type.value)}
                  className={`px-4 py-3 rounded-lg border-2 transition-all ${
                    sourceType === type.value
                      ? 'border-primary bg-primary/10 text-primary font-medium'
                      : 'border-border hover:border-muted-foreground'
                  }`}
                >
                  {type.label}
                </button>
              ))}
            </div>
          </div>

          {/* URL Input */}
          <div>
            <label htmlFor="url" className="block text-sm font-medium text-foreground mb-2">
              URL
            </label>
            <input
              id="url"
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder={selectedSourceType?.placeholder}
              className="w-full px-4 py-3 border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary bg-background text-foreground"
              required
            />
            <p className="mt-2 text-sm text-muted-foreground">
              Enter the URL of the {selectedSourceType?.label.toLowerCase()} you want to process
            </p>
          </div>

          {/* Force Reprocess Option */}
          <div className="flex items-start gap-3 p-4 bg-muted/50 rounded-lg">
            <input
              id="force-reprocess"
              type="checkbox"
              checked={forceReprocess}
              onChange={(e) => setForceReprocess(e.target.checked)}
              className="mt-1 w-4 h-4 rounded border-border text-primary focus:ring-primary"
            />
            <div>
              <label htmlFor="force-reprocess" className="font-medium text-sm text-foreground cursor-pointer">
                Force Reprocess
              </label>
              <p className="text-xs text-muted-foreground mt-1">
                Re-extract content even if this URL was previously processed. Updates tags and language detection.
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={handleClose}
              className="flex-1 px-4 py-3 border border-border rounded-lg hover:bg-muted transition-colors font-medium text-foreground"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createContent.isPending}
              className="flex-1 px-4 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {createContent.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <LinkIcon className="w-4 h-4" />
                  Add Content
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
