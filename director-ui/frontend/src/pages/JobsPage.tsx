import { useState } from 'react'
import { useJobsList, useRetryJob } from '@/hooks/useJobs'
import { Link } from 'react-router-dom'
import { format } from 'date-fns'
import { FileText, RefreshCw, Loader2, CheckCircle, XCircle, Clock } from 'lucide-react'

export default function JobsPage() {
  const [page, setPage] = useState(1)
  const { data, isLoading, error } = useJobsList(page, 20)
  const retryJob = useRetryJob()

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-600" />
      case 'processing':
        return <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
      default:
        return <Clock className="w-5 h-5 text-yellow-600" />
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'summary':
        return 'bg-blue-100 text-blue-700 border-blue-200'
      case 'mvp_plan':
        return 'bg-purple-100 text-purple-700 border-purple-200'
      case 'content_ideas':
        return 'bg-green-100 text-green-700 border-green-200'
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200'
    }
  }

  const handleRetry = async (jobId: string) => {
    if (window.confirm('Retry this job?')) {
      await retryJob.mutateAsync(jobId)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background p-8 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold mb-8">Processing Jobs</h1>
          <div className="bg-destructive/10 border border-destructive text-destructive px-4 py-3 rounded">
            Error loading jobs: {error.message}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold">Processing Jobs</h1>
          <Link
            to="/content"
            className="px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90"
          >
            View Content
          </Link>
        </div>

        {data?.items?.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground">
            <p>No jobs yet. Create a processing job from the content library!</p>
          </div>
        ) : (
          <>
            <div className="bg-card rounded-lg border overflow-hidden">
              <table className="w-full">
                <thead className="bg-muted">
                  <tr>
                    <th className="px-4 py-3 text-left font-medium">Status</th>
                    <th className="px-4 py-3 text-left font-medium">Type</th>
                    <th className="px-4 py-3 text-left font-medium">Content</th>
                    <th className="px-4 py-3 text-left font-medium">Lang</th>
                    <th className="px-4 py-3 text-left font-medium">Created</th>
                    <th className="px-4 py-3 text-left font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {data?.items.map((job: any) => (
                    <tr key={job.id} className="border-t hover:bg-muted/50">
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(job.status)}
                          <span className="capitalize text-sm">{job.status}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`text-xs px-2 py-1 rounded border ${getTypeColor(job.processing_type)}`}>
                          {job.processing_type.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-4 py-3 max-w-xs">
                        <div className="truncate text-sm">
                          {job.content_title || 'Untitled'}
                        </div>
                      </td>
                      <td className="px-4 py-3 uppercase text-sm">{job.output_language}</td>
                      <td className="px-4 py-3 text-sm text-muted-foreground">
                        {format(new Date(job.created_at), 'MMM d, HH:mm')}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <Link
                            to={`/jobs/${job.id}`}
                            className="p-2 hover:bg-primary/10 rounded text-primary"
                            title="View job details"
                          >
                            <FileText className="w-4 h-4" />
                          </Link>
                          {job.status === 'failed' && (
                            <button
                              onClick={() => handleRetry(job.id)}
                              disabled={retryJob.isPending}
                              className="p-2 hover:bg-primary/10 rounded text-primary disabled:opacity-50"
                              title="Retry job"
                            >
                              <RefreshCw className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {data?.total && (
              <div className="mt-4 flex items-center justify-between">
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
                    disabled={!data?.total || page * 20 >= data.total}
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
    </div>
  )
}