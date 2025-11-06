import { useState } from 'react'
import { X, RefreshCw, Loader2 } from 'lucide-react'

export interface ReextractParams {
  targetLanguage: string
}

interface ReextractModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (params: ReextractParams) => void
  isLoading?: boolean
  currentLanguage?: string | null
}

const languages = [
  { value: 'en', label: 'English', flag: '🇬🇧' },
  { value: 'ru', label: 'Русский', flag: '🇷🇺' },
  { value: 'es', label: 'Español', flag: '🇪🇸' },
]

export default function ReextractModal({
  isOpen,
  onClose,
  onSubmit,
  isLoading = false,
  currentLanguage,
}: ReextractModalProps) {
  const [targetLanguage, setTargetLanguage] = useState(currentLanguage || 'en')

  if (!isOpen) return null

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({ targetLanguage })
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-900 border border-border rounded-lg max-w-md w-full shadow-xl">
        <div className="flex items-center justify-between p-6 border-b border-border">
          <div className="flex items-center gap-2">
            <RefreshCw className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-bold">Re-extract Content</h2>
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
            <label className="block text-sm font-medium mb-3">Target Language</label>
            <p className="text-sm text-muted-foreground mb-4">
              Re-extract the content and regenerate tags and language detection. The AI will analyze
              the content in the selected language.
            </p>
            <div className="space-y-2">
              {languages.map((lang) => (
                <label
                  key={lang.value}
                  className={`flex items-center gap-3 p-3 border rounded-lg cursor-pointer transition-colors ${
                    targetLanguage === lang.value
                      ? 'border-primary bg-primary/5'
                      : 'border-border hover:border-primary/50'
                  }`}
                >
                  <input
                    type="radio"
                    name="targetLanguage"
                    value={lang.value}
                    checked={targetLanguage === lang.value}
                    onChange={(e) => setTargetLanguage(e.target.value)}
                    disabled={isLoading}
                    className="text-primary focus:ring-primary"
                  />
                  <span className="text-2xl">{lang.flag}</span>
                  <span className="font-medium">{lang.label}</span>
                  {currentLanguage === lang.value && (
                    <span className="ml-auto text-xs text-muted-foreground">(current)</span>
                  )}
                </label>
              ))}
            </div>
          </div>

          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
              className="flex-1 px-4 py-2 border border-border rounded-lg hover:bg-muted disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Re-extracting...
                </>
              ) : (
                <>
                  <RefreshCw className="w-4 h-4" />
                  Re-extract
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
