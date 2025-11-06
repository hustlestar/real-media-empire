import { FileText, Film, Globe } from 'lucide-react'
import { ComponentType } from 'react'

interface SourceTypeIconProps {
  type: string
  className?: string
}

export default function SourceTypeIcon({ type, className = "w-5 h-5" }: SourceTypeIconProps) {
  const icons: Record<string, { Icon: ComponentType<{ className?: string }>; color: string }> = {
    youtube: { Icon: Film, color: 'text-red-500' },
    pdf_url: { Icon: FileText, color: 'text-blue-500' },
    pdf_file: { Icon: FileText, color: 'text-blue-500' },
    web: { Icon: Globe, color: 'text-green-500' },
  }

  const { Icon, color } = icons[type] || icons.web
  return <Icon className={`${className} ${color}`} />
}