# UI Implementation Guide

This document contains all the remaining components needed to complete the UI enhancement.

## ✅ Already Created
- `src/components/Sidebar.tsx` - Navigation sidebar
- `src/components/Layout.tsx` - App layout wrapper
- Dependencies installed: react-markdown, react-hot-toast

## 📝 Files to Create

### 1. Shared Components

#### `src/components/StatusBadge.tsx`
```typescript
interface StatusBadgeProps {
  status: string
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const colors = {
    completed: 'bg-green-100 text-green-800 border-green-200',
    failed: 'bg-red-100 text-red-800 border-red-200',
    processing: 'bg-blue-100 text-blue-800 border-blue-200',
    pending: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${colors[status] || colors.pending}`}>
      {status}
    </span>
  )
}
```

#### `src/components/SourceTypeIcon.tsx`
```typescript
import { FileText, Film, Globe } from 'lucide-react'

interface SourceTypeIconProps {
  type: string
  className?: string
}

export default function SourceTypeIcon({ type, className = "w-5 h-5" }: SourceTypeIconProps) {
  const icons = {
    youtube: { Icon: Film, color: 'text-red-500' },
    pdf_url: { Icon: FileText, color: 'text-blue-500' },
    pdf_file: { Icon: FileText, color: 'text-blue-500' },
    web: { Icon: Globe, color: 'text-green-500' },
  }

  const { Icon, color } = icons[type] || icons.web
  return <Icon className={`${className} ${color}`} />
}
```

### 2. Content Components

#### `src/components/ContentCard.tsx`
```typescript
import { Link } from 'react-router-dom'
import { format } from 'date-fns'
import { ExternalLink, Eye, Sparkles, Trash2 } from 'lucide-react'
import SourceTypeIcon from './SourceTypeIcon'
import StatusBadge from './StatusBadge'

interface ContentCardProps {
  item: any
  onDelete: (id: string) => void
}

export default function ContentCard({ item, onDelete }: ContentCardProps) {
  const title = item.metadata?.title || 'Untitled'
  const charCount = item.metadata?.char_count || 0

  return (
    <div className="bg-card border border-border rounded-lg p-5 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <SourceTypeIcon type={item.source_type} />
          <span className="text-xs font-medium capitalize text-muted-foreground">
            {item.source_type.replace('_', ' ')}
          </span>
        </div>
        <StatusBadge status={item.processing_status} />
      </div>

      <h3 className="font-semibold text-lg mb-2 line-clamp-2">{title}</h3>

      {item.source_url && (
        <a
          href={item.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-muted-foreground hover:text-primary flex items-center gap-1 mb-3"
        >
          <ExternalLink className="w-3 h-3" />
          <span className="truncate">{item.source_url}</span>
        </a>
      )}

      <div className="flex items-center gap-4 text-xs text-muted-foreground mb-4">
        <span>{charCount.toLocaleString()} chars</span>
        <span>{format(new Date(item.created_at), 'MMM d, yyyy')}</span>
      </div>

      <div className="flex gap-2">
        <Link
          to={`/content/${item.id}`}
          className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90 text-sm"
        >
          <Eye className="w-4 h-4" />
          View
        </Link>
        <Link
          to={`/content/${item.id}?action=process`}
          className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-secondary text-secondary-foreground rounded hover:bg-secondary/80 text-sm"
        >
          <Sparkles className="w-4 h-4" />
          Process
        </Link>
        <button
          onClick={() => onDelete(item.id)}
          className="px-3 py-2 bg-destructive/10 text-destructive rounded hover:bg-destructive/20"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
```

### 3. Update App.tsx

Replace the existing App.tsx with:

```typescript
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import './lib/api-config'
import ContentPage from './pages/ContentPage'
import JobsPage from './pages/JobsPage'
import ContentDetailPage from './pages/ContentDetailPage'
import JobDetailPage from './pages/JobDetailPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 30000,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/content" replace />} />
            <Route path="/content" element={<ContentPage />} />
            <Route path="/content/:id" element={<ContentDetailPage />} />
            <Route path="/jobs" element={<JobsPage />} />
            <Route path="/jobs/:id" element={<JobDetailPage />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
```

### 4. Update ContentPage.tsx

Replace with grid layout:

```typescript
import { useState } from 'react'
import { useContentList, useDeleteContent } from '@/hooks/useContent'
import { Loader2, Plus } from 'lucide-react'
import ContentCard from '@/components/ContentCard'
import toast from 'react-hot-toast'

export default function ContentPage() {
  const [page, setPage] = useState(1)
  const { data, isLoading, error } = useContentList(page, 20)
  const deleteContent = useDeleteContent()

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
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold">Content Library</h1>
            <p className="text-muted-foreground mt-2">
              {data?.total || 0} items • Browse and process your content
            </p>
          </div>
        </div>

        {data && data.items.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-muted-foreground text-lg mb-4">No content yet</p>
            <p className="text-sm text-muted-foreground">
              Send YouTube links, PDFs, or web pages to the Telegram bot to get started!
            </p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              {data?.items.map((item) => (
                <ContentCard key={item.id} item={item} onDelete={handleDelete} />
              ))}
            </div>

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
    </div>
  )
}
```

## 🚀 Next Steps

1. Create the remaining component files from this guide
2. Create the detail pages (ContentDetailPage, JobDetailPage)
3. Create processing hooks
4. Test the UI with the bot

The implementation is now 40% complete with the foundation in place!