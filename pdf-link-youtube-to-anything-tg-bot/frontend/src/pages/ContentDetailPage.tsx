import { useState, useEffect, useMemo } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, Loader2, Sparkles, FileText, Calendar, Hash, ExternalLink, Globe, RefreshCw, Package } from 'lucide-react'
import { useContentWithText, useReprocessContent, useUpdateContentLanguage } from '@/hooks/useContent'
import { useCreateJob, useJobsList } from '@/hooks/useJobs'
import { useListBundles } from '@/hooks/useBundler'
import { format } from 'date-fns'
import toast from 'react-hot-toast'
import TextViewer from '@/components/TextViewer'
import ProcessingModal from '@/components/ProcessingModal'
import type { ProcessingParams } from '@/components/ProcessingModal'
import ReextractModal from '@/components/ReextractModal'
import type { ReextractParams } from '@/components/ReextractModal'
import SourceTypeIcon from '@/components/SourceTypeIcon'
import StatusBadge from '@/components/StatusBadge'
import LanguageBadge from '@/components/LanguageBadge'
import TagBadge from '@/components/TagBadge'

export default function ContentDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [isProcessingModalOpen, setIsProcessingModalOpen] = useState(false)
  const [isReextractModalOpen, setIsReextractModalOpen] = useState(false)
  const [activeTab, setActiveTab] = useState<'text' | 'metadata'>('text')
  const [selectedLanguage, setSelectedLanguage] = useState<string | undefined>()

  const { data: content, isLoading, error, refetch } = useContentWithText(id!, selectedLanguage)
  const { data: jobsData } = useJobsList(1, 5, undefined, id)
  const { data: bundlesData } = useListBundles(1, 100) // Fetch bundles to filter client-side
  const createJob = useCreateJob()
  const reprocessContent = useReprocessContent()
  const updateLanguage = useUpdateContentLanguage()

  // Filter bundles that contain this content (limit to 5)
  const contentBundles = useMemo(() => {
    if (!bundlesData?.items || !id) return []
    return bundlesData.items
      .filter(bundle => bundle.content_ids?.includes(id))
      .slice(0, 5)
  }, [bundlesData, id])

  // Extract available languages from content
  const availableLanguages = content?.extracted_text_paths ? Object.keys(content.extracted_text_paths) : []
  const hasMultipleLanguages = availableLanguages.length > 1

  // Set initial language when content loads
  useEffect(() => {
    if (content && !selectedLanguage) {
      setSelectedLanguage(content.detected_language || availableLanguages[0])
    }
  }, [content, selectedLanguage, availableLanguages])

  // Refetch when language changes
  useEffect(() => {
    if (selectedLanguage && id) {
      refetch()
    }
  }, [selectedLanguage, id, refetch])

  const handleProcess = async (params: ProcessingParams) => {
    if (!id) return

    try {
      const job = await createJob.mutateAsync({
        content_id: id,
        processing_type: params.processingType,
        output_language: params.language,
        user_prompt: params.customPrompt,
      })

      toast.success('Processing job created!')
      setIsProcessingModalOpen(false)

      // Navigate to job detail page
      navigate(`/jobs/${job.id}`)
    } catch (err) {
      toast.error('Failed to create processing job')
      console.error(err)
    }
  }

  const handleReextract = async (params: ReextractParams) => {
    if (!content?.source_url) {
      toast.error('No source URL available for re-extraction')
      return
    }

    try {
      await reprocessContent.mutateAsync({
        url: content.source_url,
        sourceType: content.source_type,
        targetLanguage: params.targetLanguage,
      })
      toast.success('Content re-extracted successfully! Tags and language updated.')
      setIsReextractModalOpen(false)
    } catch (err) {
      toast.error('Failed to re-extract content')
      console.error(err)
    }
  }

  const handleLanguageChange = async (newLanguage: string) => {
    if (!id || newLanguage === content?.detected_language) {
      return
    }

    try {
      await updateLanguage.mutateAsync({
        contentId: id,
        language: newLanguage,
      })
      toast.success(`Language updated to ${newLanguage.toUpperCase()}`)
    } catch (err) {
      toast.error('Failed to update language')
      console.error(err)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen p-8 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    )
  }

  if (error || !content) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-5xl mx-auto">
          <Link to="/content" className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground mb-6">
            <ArrowLeft className="w-4 h-4" />
            Back to Library
          </Link>
          <div className="bg-destructive/10 border border-destructive text-destructive px-4 py-3 rounded">
            Error loading content
          </div>
        </div>
      </div>
    )
  }

  const title = content.metadata?.title || 'Untitled'
  const charCount = content.metadata?.char_count || 0

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-5xl mx-auto">
        <Link to="/content" className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground mb-6">
          <ArrowLeft className="w-4 h-4" />
          Back to Library
        </Link>

        {/* Header */}
        <div className="bg-card border border-border rounded-lg p-6 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <SourceTypeIcon type={content.source_type} className="w-6 h-6" />
              <div>
                <h1 className="text-2xl font-bold">{title}</h1>
                <p className="text-sm text-muted-foreground mt-1 capitalize">
                  {content.source_type.replace('_', ' ')}
                </p>
              </div>
            </div>
            <StatusBadge status={content.processing_status} />
          </div>

          {content.source_url && (
            <a
              href={content.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-muted-foreground hover:text-primary flex items-center gap-2 mb-4"
            >
              <ExternalLink className="w-4 h-4" />
              {content.source_url}
            </a>
          )}

          <div className="flex items-center gap-6 text-sm text-muted-foreground mb-4">
            <span className="flex items-center gap-2">
              <FileText className="w-4 h-4" />
              {charCount.toLocaleString()} characters
            </span>
            <span className="flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              {format(new Date(content.created_at), 'MMM d, yyyy HH:mm')}
            </span>
            <span className="flex items-center gap-2">
              <Hash className="w-4 h-4" />
              {content.id.slice(0, 8)}
            </span>
            {content.detected_language && (
              <span className="flex items-center gap-2">
                <Globe className="w-4 h-4" />
                <select
                  value={content.detected_language}
                  onChange={(e) => handleLanguageChange(e.target.value)}
                  className="px-2 py-1 rounded-md text-sm border border-border bg-background hover:bg-accent cursor-pointer"
                >
                  <option value="en">🇬🇧 English</option>
                  <option value="ru">🇷🇺 Русский</option>
                  <option value="es">🇪🇸 Español</option>
                </select>
              </span>
            )}
          </div>

          {content.tags && content.tags.length > 0 && (
            <div className="mb-6">
              <h4 className="text-sm font-medium text-muted-foreground mb-2">Tags</h4>
              <div className="flex flex-wrap gap-2">
                {content.tags.map((tag: string) => (
                  <TagBadge key={tag} tag={tag} size="md" />
                ))}
              </div>
            </div>
          )}

          <div className="flex gap-3">
            <button
              onClick={() => setIsProcessingModalOpen(true)}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 font-medium"
            >
              <Sparkles className="w-5 h-5" />
              Process with AI
            </button>
            {content.source_url && (
              <button
                onClick={() => setIsReextractModalOpen(true)}
                className="flex items-center justify-center gap-2 px-4 py-3 border border-border rounded-lg hover:bg-accent font-medium"
                title="Re-extract content to update tags and language detection"
              >
                <RefreshCw className="w-5 h-5" />
                Re-extract
              </button>
            )}
          </div>
        </div>

        {/* Bundles containing this content */}
        {contentBundles.length > 0 && (
          <div className="mb-6">
            <h3 className="text-sm font-semibold mb-3 flex items-center gap-2 text-muted-foreground">
              <Package className="w-4 h-4" />
              Bundles ({contentBundles.length})
            </h3>
            <div className="space-y-1.5">
              {contentBundles.map((bundle) => (
                <Link
                  key={bundle.id}
                  to={`/bundles/${bundle.id}`}
                  className="block bg-card border border-border rounded-md p-2.5 hover:border-primary transition-colors"
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">
                        {bundle.name || 'Unnamed Bundle'}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {bundle.content_ids.length} items • {bundle.attempt_count || 0} attempts • {format(new Date(bundle.created_at), 'MMM d, yyyy')}
                      </p>
                    </div>
                    <Package className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Recent Jobs */}
        {jobsData && jobsData.items.length > 0 && (
          <div className="mb-6">
            <h3 className="font-semibold mb-4">Recent Processing Jobs</h3>
            <div className="space-y-2">
              {jobsData.items.map((job) => (
                <Link
                  key={job.id}
                  to={`/jobs/${job.id}`}
                  className="block bg-card border border-border rounded-lg p-4 hover:border-primary transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium capitalize">
                        {job.processing_type.replace('_', ' ')}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {format(new Date(job.created_at), 'MMM d, yyyy HH:mm')}
                      </p>
                    </div>
                    <StatusBadge status={job.status} />
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="border-b border-border mb-6">
          <div className="flex gap-6">
            <button
              onClick={() => setActiveTab('text')}
              className={`pb-3 px-2 font-medium transition-colors ${
                activeTab === 'text'
                  ? 'border-b-2 border-primary text-primary'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              Extracted Text
            </button>
            <button
              onClick={() => setActiveTab('metadata')}
              className={`pb-3 px-2 font-medium transition-colors ${
                activeTab === 'metadata'
                  ? 'border-b-2 border-primary text-primary'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              Metadata
            </button>
          </div>
        </div>

        {/* Content Area */}
        {activeTab === 'text' && (
          <>
            {/* Language Switcher - only show if multiple languages available */}
            {hasMultipleLanguages && (
              <div className="mb-4 flex items-center gap-3">
                <span className="text-sm text-muted-foreground font-medium">Language:</span>
                <div className="flex gap-2">
                  {availableLanguages.map((lang) => (
                    <button
                      key={lang}
                      onClick={() => setSelectedLanguage(lang)}
                      className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                        selectedLanguage === lang
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted text-muted-foreground hover:bg-accent'
                      }`}
                    >
                      <LanguageBadge language={lang} size="sm" />
                    </button>
                  ))}
                </div>
              </div>
            )}

            {content.extracted_text && (
              <TextViewer text={content.extracted_text} />
            )}
          </>
        )}

        {activeTab === 'metadata' && (
          <div className="bg-card border border-border rounded-lg p-6">
            <h3 className="font-semibold mb-4">Content Metadata</h3>
            <div className="space-y-3">
              {Object.entries(content.metadata || {}).map(([key, value]) => (
                <div key={key} className="flex items-start gap-4">
                  <span className="text-muted-foreground min-w-32 capitalize">
                    {key.replace(/_/g, ' ')}:
                  </span>
                  <span className="font-mono text-sm">
                    {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Processing Modal */}
        <ProcessingModal
          isOpen={isProcessingModalOpen}
          onClose={() => setIsProcessingModalOpen(false)}
          onSubmit={handleProcess}
          isLoading={createJob.isPending}
        />

        {/* Re-extract Modal */}
        <ReextractModal
          isOpen={isReextractModalOpen}
          onClose={() => setIsReextractModalOpen(false)}
          onSubmit={handleReextract}
          isLoading={reprocessContent.isPending}
          currentLanguage={content?.detected_language}
        />
      </div>
    </div>
  )
}