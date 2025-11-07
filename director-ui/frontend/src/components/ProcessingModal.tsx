import { useState } from 'react'
import { X, Sparkles, Loader2 } from 'lucide-react'

export interface ProcessingParams {
  processingType: string
  language: string
  customPrompt?: string
}

interface ProcessingModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (params: ProcessingParams) => void
  isLoading?: boolean
}

const processingTypes = [
  { value: 'summary', label: 'Summary', description: 'Generate a concise summary' },
  { value: 'mvp_plan', label: 'MVP Plan', description: 'Create a product development plan' },
  { value: 'content_ideas', label: 'Content Ideas', description: 'Generate creative content ideas' },
  { value: 'blog_post', label: 'Blog Post & Video Script', description: 'SEO-optimized blog post with YouTube script' },
]

const languages = [
  { value: 'en', label: 'English' },
  { value: 'ru', label: 'Русский' },
  { value: 'es', label: 'Español' },
]

export default function ProcessingModal({ isOpen, onClose, onSubmit, isLoading = false }: ProcessingModalProps) {
  const [processingType, setProcessingType] = useState('summary')
  const [language, setLanguage] = useState('en')
  const [customPrompt, setCustomPrompt] = useState('')

  if (!isOpen) return null

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({
      processingType,
      language,
      customPrompt: customPrompt.trim() || undefined,
    })
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-card border border-border rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-xl">
        <div className="flex items-center justify-between p-6 border-b border-border">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-bold text-foreground">Process Content with AI</h2>
          </div>
          <button
            onClick={onClose}
            disabled={isLoading}
            className="text-muted-foreground hover:text-foreground disabled:opacity-50"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-foreground mb-3">Processing Type</label>
            <div className="space-y-2">
              {processingTypes.map((type) => (
                <label
                  key={type.value}
                  className={`flex items-start gap-3 p-4 border rounded-lg cursor-pointer transition-colors ${
                    processingType === type.value
                      ? 'border-primary bg-primary/5'
                      : 'border-border hover:border-primary/50'
                  }`}
                >
                  <input
                    type="radio"
                    name="processingType"
                    value={type.value}
                    checked={processingType === type.value}
                    onChange={(e) => setProcessingType(e.target.value)}
                    disabled={isLoading}
                    className="mt-1"
                  />
                  <div className="flex-1">
                    <div className="font-medium text-foreground">{type.label}</div>
                    <div className="text-sm text-muted-foreground">{type.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">Language</label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              disabled={isLoading}
              className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
            >
              {languages.map((lang) => (
                <option key={lang.value} value={lang.value}>
                  {lang.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Custom Instructions <span className="text-muted-foreground font-normal">(optional)</span>
            </label>
            <textarea
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              disabled={isLoading}
              placeholder="Add any specific instructions or requirements..."
              rows={4}
              className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary resize-none"
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
              className="flex-1 px-4 py-2 border border-border rounded-lg hover:bg-muted disabled:opacity-50 text-foreground font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 flex items-center justify-center gap-2 font-medium"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Start Processing
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}