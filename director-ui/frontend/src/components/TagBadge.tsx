import { X } from 'lucide-react'

interface TagBadgeProps {
  tag: string
  size?: 'sm' | 'md'
  onClick?: () => void
  onRemove?: () => void
  variant?: 'default' | 'outline'
}

// Hash string to consistent color index
const hashToColor = (str: string): string => {
  const colors = [
    'bg-blue-100 text-blue-700 border-blue-200',
    'bg-green-100 text-green-700 border-green-200',
    'bg-purple-100 text-purple-700 border-purple-200',
    'bg-orange-100 text-orange-700 border-orange-200',
    'bg-pink-100 text-pink-700 border-pink-200',
    'bg-cyan-100 text-cyan-700 border-cyan-200',
    'bg-indigo-100 text-indigo-700 border-indigo-200',
  ]

  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

export default function TagBadge({ tag, size = 'sm', onClick, onRemove, variant = 'default' }: TagBadgeProps) {
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
  }

  const colorClass = variant === 'default' ? hashToColor(tag) : 'bg-transparent text-muted-foreground border-border'
  const interactiveClass = onClick ? 'cursor-pointer hover:opacity-80 transition-opacity' : ''

  return (
    <span
      onClick={onClick}
      className={`inline-flex items-center gap-1 rounded-full border font-medium ${sizeClasses[size]} ${colorClass} ${interactiveClass}`}
    >
      {tag}
      {onRemove && (
        <button
          onClick={(e) => {
            e.stopPropagation()
            onRemove()
          }}
          className="hover:bg-black/10 rounded-full p-0.5 transition-colors"
        >
          <X className="w-3 h-3" />
        </button>
      )}
    </span>
  )
}
