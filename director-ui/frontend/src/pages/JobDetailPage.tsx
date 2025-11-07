import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Loader2, RefreshCw, Calendar, Clock, FileText, Hash, ExternalLink, Package } from 'lucide-react'
import { useJobWithResult, useRetryJob } from '@/hooks/useJobs'
import { useBundle } from '@/hooks/useBundler'
import { format } from 'date-fns'
import toast from 'react-hot-toast'
import TextViewer from '@/components/TextViewer'
import StatusBadge from '@/components/StatusBadge'
import { BundleConfigModal } from '@/components/BundleConfigModal'
import { useState } from 'react'

export default function JobDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { data: job, isLoading, error } = useJobWithResult(id!)
  const retryJob = useRetryJob()
  const [showBundleModal, setShowBundleModal] = useState(false)

  // Fetch bundle details if this is a bundle job
  const { data: bundle } = useBundle(job?.bundle_id || undefined)

  const handleRetry = async () => {
    if (!id) return

    try {
      await retryJob.mutateAsync(id)
      toast.success('Job retry initiated!')
    } catch (err) {
      toast.error('Failed to retry job')
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

  if (error || !job) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-5xl mx-auto">
          <Link to="/jobs" className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground mb-6">
            <ArrowLeft className="w-4 h-4" />
            Back to Jobs
          </Link>
          <div className="bg-destructive/10 border border-destructive text-destructive px-4 py-3 rounded">
            Error loading job
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-5xl mx-auto">
        <Link to="/jobs" className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground mb-6">
          <ArrowLeft className="w-4 h-4" />
          Back to Jobs
        </Link>

        {/* Header */}
        <div className="bg-card border border-border rounded-lg p-6 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold capitalize">
                {job.processing_type.replace('_', ' ')}
              </h1>
              <p className="text-sm text-muted-foreground mt-1">
                Job ID: {job.id.slice(0, 8)}
              </p>
            </div>
            <StatusBadge status={job.status} />
          </div>

          <div className="grid grid-cols-2 gap-4 text-sm mb-4">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Calendar className="w-4 h-4" />
              <span>Created: {format(new Date(job.created_at), 'MMM d, yyyy HH:mm')}</span>
            </div>
            {job.completed_at && (
              <div className="flex items-center gap-2 text-muted-foreground">
                <Clock className="w-4 h-4" />
                <span>Completed: {format(new Date(job.completed_at), 'MMM d, yyyy HH:mm')}</span>
              </div>
            )}
            <div className="flex items-center gap-2 text-muted-foreground">
              <Hash className="w-4 h-4" />
              <span>Language: {job.output_language.toUpperCase()}</span>
            </div>
            {job.content_id && (
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-muted-foreground" />
                <Link
                  to={`/content/${job.content_id}`}
                  className="text-primary hover:underline"
                >
                  View Source Content
                </Link>
              </div>
            )}
            {job.bundle_id && (
              <div className="flex items-center gap-2">
                <Package className="w-4 h-4 text-muted-foreground" />
                <Link
                  to={`/bundles/${job.bundle_id}`}
                  className="text-primary hover:underline"
                >
                  View Bundle
                </Link>
              </div>
            )}
          </div>

          {/* Bundle Content Items */}
          {job.bundle_id && bundle && (
            <div className="bg-muted/30 rounded-lg p-4 mb-4">
              <h3 className="text-sm font-medium mb-3 flex items-center gap-2">
                <Package className="w-4 h-4" />
                Bundle Contents ({bundle.content_ids?.length || 0} items)
              </h3>
              <div className="space-y-2">
                {bundle.content_items && bundle.content_items.length > 0 ? (
                  bundle.content_items.map((item: any, index: number) => (
                    <div key={item.id} className="flex items-center gap-2 text-sm bg-background/50 rounded px-3 py-2">
                      <span className="text-muted-foreground">#{index + 1}</span>
                      <span className="text-xs px-2 py-0.5 bg-primary/10 text-primary rounded">
                        {item.source_type}
                      </span>
                      <span className="flex-1 truncate">
                        {item.metadata?.title || item.metadata?.url || 'Untitled'}
                      </span>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-muted-foreground">Loading bundle contents...</p>
                )}
              </div>
            </div>
          )}

          {job.custom_prompt && (
            <div className="bg-muted/50 rounded-lg p-4 mb-4">
              <h3 className="text-sm font-medium mb-2">Custom Instructions</h3>
              <p className="text-sm text-muted-foreground">{job.custom_prompt}</p>
            </div>
          )}

          {job.status === 'failed' && job.error_message && (
            <div className="bg-destructive/10 border border-destructive text-destructive px-4 py-3 rounded mb-4">
              <p className="font-medium mb-1">Error</p>
              <p className="text-sm">{job.error_message}</p>
            </div>
          )}

          {(job.status === 'failed' || job.status === 'completed') && (
            <div className="flex gap-2">
              <button
                onClick={handleRetry}
                disabled={retryJob.isPending}
                className="flex items-center gap-2 px-4 py-2 border border-border rounded-lg hover:bg-muted disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 ${retryJob.isPending ? 'animate-spin' : ''}`} />
                {retryJob.isPending ? 'Retrying...' : 'Retry Job'}
              </button>

              {job.bundle_id && bundle && (
                <button
                  onClick={() => setShowBundleModal(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90"
                >
                  <Package className="w-4 h-4" />
                  Process Bundle Again
                </button>
              )}
            </div>
          )}
        </div>

        {/* Result */}
        {job.result && (
          <div>
            <h2 className="text-xl font-semibold mb-4">AI Generated Result</h2>
            <TextViewer text={job.result} isMarkdown={true} />
          </div>
        )}

        {job.status === 'pending' && (
          <div className="text-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-primary mx-auto mb-4" />
            <p className="text-muted-foreground">Job is queued and waiting to be processed...</p>
          </div>
        )}

        {job.status === 'processing' && (
          <div className="text-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-primary mx-auto mb-4" />
            <p className="text-muted-foreground">AI is processing your content...</p>
          </div>
        )}
      </div>

      {/* Bundle Config Modal */}
      {showBundleModal && job.bundle_id && bundle && (
        <BundleConfigModal
          contentIds={bundle.content_ids}
          bundleId={job.bundle_id}
          onClose={() => setShowBundleModal(false)}
        />
      )}
    </div>
  )
}