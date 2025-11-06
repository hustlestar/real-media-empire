import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { FileText, Briefcase, Settings, Plus, Package } from 'lucide-react'
import AddContentModal from './AddContentModal'

export default function Sidebar() {
  const location = useLocation()
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)

  const navLinks = [
    { to: '/content', label: 'Content Library', icon: FileText },
    { to: '/bundles', label: 'Bundles', icon: Package },
    { to: '/jobs', label: 'Processing Jobs', icon: Briefcase },
  ]

  const isActive = (path: string) => location.pathname.startsWith(path)

  return (
    <aside className="w-64 bg-card border-r border-border min-h-screen flex flex-col">
      <div className="p-6 border-b border-border">
        <h1 className="text-2xl font-bold text-primary">Content AI</h1>
        <p className="text-sm text-muted-foreground mt-1">Process & Analyze</p>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        <button
          onClick={() => setIsAddModalOpen(true)}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 hover:shadow-md transition-all duration-200 font-medium mb-4 cursor-pointer"
        >
          <Plus className="w-5 h-5" />
          <span>Add Content</span>
        </button>
        {navLinks.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              isActive(link.to)
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:bg-muted hover:text-foreground'
            }`}
          >
            <link.icon className="w-5 h-5" />
            <span className="font-medium">{link.label}</span>
          </Link>
        ))}
      </nav>

      <div className="p-4 border-t border-border">
        <div className="text-xs text-muted-foreground">
          <p>User ID: 66395090</p>
          <p className="mt-1">v1.0.0</p>
        </div>
      </div>

      <AddContentModal isOpen={isAddModalOpen} onClose={() => setIsAddModalOpen(false)} />
    </aside>
  )
}