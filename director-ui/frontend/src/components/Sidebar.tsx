import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { FileText, Briefcase, Plus, Package, Film, Presentation, Image, Users, Upload, Video, Send, Sparkles } from 'lucide-react'
import AddContentModal from './AddContentModal'

export default function Sidebar() {
  const location = useLocation()
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)

  // Navigation sections with grouped links
  const navSections = [
    {
      title: 'LIBRARY',
      links: [
        { to: '/content', label: 'Content Library', icon: FileText },
        { to: '/assets', label: 'Asset Gallery', icon: Image },
        { to: '/characters', label: 'Characters', icon: Users },
      ]
    },
    {
      title: 'CREATION',
      links: [
        { to: '/script-writer', label: 'Script Writer', icon: Sparkles },
        { to: '/film-generation', label: 'Film Generator', icon: Film },
        { to: '/pptx-generation', label: 'PPTX Generator', icon: Presentation },
        { to: '/heygen-studio', label: 'HeyGen Studio', icon: Video },
      ]
    },
    {
      title: 'PUBLISHING',
      links: [
        { to: '/publishing', label: 'Publishing', icon: Upload },
        { to: '/publishing/postiz', label: 'Social Publishing', icon: Send },
        { to: '/jobs', label: 'Processing Jobs', icon: Briefcase },
      ]
    },
    {
      title: 'ORGANIZATION',
      links: [
        { to: '/bundles', label: 'Bundles', icon: Package },
      ]
    }
  ]

  const isActive = (path: string) => location.pathname.startsWith(path)

  return (
    <aside className="w-64 bg-card border-r border-border min-h-screen flex flex-col">
      <div className="p-6 border-b border-border">
        <h1 className="text-2xl font-bold text-primary">Media Empire</h1>
        <p className="text-sm text-muted-foreground mt-1">Create & Publish</p>
      </div>

      <nav className="flex-1 p-4 space-y-6 overflow-y-auto">
        <button
          onClick={() => setIsAddModalOpen(true)}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 hover:shadow-md transition-all duration-200 font-medium cursor-pointer"
        >
          <Plus className="w-5 h-5" />
          <span>Add Content</span>
        </button>

        {navSections.map((section) => (
          <div key={section.title} className="space-y-1">
            <h3 className="px-4 text-xs font-semibold text-muted-foreground mb-2">
              {section.title}
            </h3>
            {section.links.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={`flex items-center gap-3 px-4 py-2.5 rounded-lg transition-colors ${
                  isActive(link.to)
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                }`}
              >
                <link.icon className="w-5 h-5" />
                <span className="font-medium text-sm">{link.label}</span>
              </Link>
            ))}
          </div>
        ))}
      </nav>

      <div className="p-4 border-t border-border">
        <div className="text-xs text-muted-foreground">
          <p>User ID: 66395090</p>
          <p className="mt-1">v2.0.0</p>
        </div>
      </div>

      <AddContentModal isOpen={isAddModalOpen} onClose={() => setIsAddModalOpen(false)} />
    </aside>
  )
}
