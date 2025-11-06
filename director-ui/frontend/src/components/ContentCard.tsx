import { useNavigate } from 'react-router-dom'
import { format } from 'date-fns'
import { ExternalLink, Eye, Sparkles, Trash2, FolderPlus, Check } from 'lucide-react'
import SourceTypeIcon from './SourceTypeIcon'
import StatusBadge from './StatusBadge'
import LanguageBadge from './LanguageBadge'
import TagBadge from './TagBadge'
import { useBundlerContext } from '../context/BundlerContext'

interface ContentCardProps {
  item: any
  onDelete: (id: string) => void
}

export default function ContentCard({ item, onDelete }: ContentCardProps) {
  const navigate = useNavigate()
  const title = item.metadata?.title || 'Untitled'
  const charCount = item.metadata?.char_count || 0
  const { addItem, removeItem, hasItem, openPanel } = useBundlerContext()
  const inBundle = hasItem(item.id)

  const handleCardClick = () => {
    navigate(`/content/${item.id}`)
  }

  const handleProcess = (e: React.MouseEvent) => {
    e.stopPropagation()
    navigate(`/content/${item.id}?action=process`)
  }

  const handleToggleBundle = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (inBundle) {
      removeItem(item.id)
    } else {
      addItem(item)
      openPanel()
    }
  }

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation()
    onDelete(item.id)
  }

  const handleSourceClick = (e: React.MouseEvent) => {
    e.stopPropagation()
  }

  return (
    <div
      onClick={handleCardClick}
      className="bg-card border border-border rounded-lg p-5 hover:shadow-lg transition-shadow cursor-pointer flex flex-col h-full"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <SourceTypeIcon type={item.source_type} />
          <span className="text-xs font-medium capitalize text-muted-foreground">
            {item.source_type.replace('_', ' ')}
          </span>
          {item.detected_language && <LanguageBadge language={item.detected_language} />}
        </div>
        <StatusBadge status={item.processing_status} />
      </div>

      <div className="flex-1 flex flex-col">
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

        <div className="flex items-center gap-4 text-xs text-muted-foreground mb-3">
          <span>{charCount.toLocaleString()} chars</span>
          <span>{format(new Date(item.created_at), 'MMM d, yyyy')}</span>
        </div>

        {item.tags && item.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-4">
            {item.tags.slice(0, 3).map((tag: string) => (
              <TagBadge key={tag} tag={tag} />
            ))}
            {item.tags.length > 3 && (
              <span className="text-xs text-muted-foreground self-center">+{item.tags.length - 3} more</span>
            )}
          </div>
        )}
      </div>

      <div className="flex gap-2 mt-auto">
        <button
          onClick={handleProcess}
          className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90 hover:shadow-md text-sm transition-all duration-200 cursor-pointer"
        >
          <Sparkles className="w-4 h-4" />
          Process
        </button>
        <button
          onClick={handleToggleBundle}
          className={`px-3 py-2 rounded transition-all duration-200 hover:shadow-md cursor-pointer ${
            inBundle
              ? 'bg-green-600/10 text-green-700 hover:bg-green-600/20 border border-green-600/30'
              : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
          }`}
          title={inBundle ? 'Remove from bundle' : 'Add to bundle'}
        >
          {inBundle ? <Check className="w-4 h-4" /> : <FolderPlus className="w-4 h-4" />}
        </button>
        <button
          onClick={handleDelete}
          className="px-3 py-2 bg-destructive/10 text-destructive rounded hover:bg-destructive/20 hover:shadow-md transition-all duration-200 cursor-pointer"
          title="Delete content"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}