interface LanguageBadgeProps {
  language: string | null | undefined
  size?: 'sm' | 'md'
}

const getLanguageConfig = (lang: string | null | undefined) => {
  const normalized = lang?.toLowerCase()

  switch (normalized) {
    case 'en':
      return {
        label: 'EN',
        colorClass: 'bg-blue-100 text-blue-700 border-blue-200'
      }
    case 'ru':
      return {
        label: 'RU',
        colorClass: 'bg-red-100 text-red-700 border-red-200'
      }
    case 'es':
      return {
        label: 'ES',
        colorClass: 'bg-yellow-100 text-yellow-700 border-yellow-200'
      }
    default:
      return {
        label: lang?.toUpperCase() || 'N/A',
        colorClass: 'bg-gray-100 text-gray-700 border-gray-200'
      }
  }
}

export default function LanguageBadge({ language, size = 'sm' }: LanguageBadgeProps) {
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
  }

  const { label, colorClass } = getLanguageConfig(language)

  return (
    <span className={`inline-flex items-center rounded-full border font-medium ${sizeClasses[size]} ${colorClass}`}>
      {label}
    </span>
  )
}
