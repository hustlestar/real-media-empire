import { useState, useEffect, useRef } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { FileText, Briefcase, Package, Film, Presentation, Image, Users, Upload, Video, Send, Sparkles, Camera, Grid, ChevronDown, Plus } from 'lucide-react'
import { useWorkspace } from '../contexts/WorkspaceContext'
import CreateWorkspaceModal from './CreateWorkspaceModal'

export default function Sidebar() {
  const location = useLocation()
  const { currentWorkspace, workspaces, setCurrentWorkspace, refreshWorkspaces } = useWorkspace()
  const [isWorkspaceDropdownOpen, setIsWorkspaceDropdownOpen] = useState(false)
  const [isCreateWorkspaceModalOpen, setIsCreateWorkspaceModalOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsWorkspaceDropdownOpen(false)
      }
    }

    if (isWorkspaceDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isWorkspaceDropdownOpen])

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
        { to: '/shot-studio', label: 'Shot Studio', icon: Camera },
        { to: '/storyboard', label: 'Storyboard', icon: Grid },
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
      {/* Header */}
      <div className="p-6 border-b border-border">
        <h1 className="text-2xl font-bold text-primary">Media Empire</h1>
        <p className="text-sm text-muted-foreground mt-1">Create & Publish</p>
      </div>

      {/* Workspace Selector */}
      <div className="p-4 border-b border-border">
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setIsWorkspaceDropdownOpen(!isWorkspaceDropdownOpen)}
            className="w-full flex items-center justify-between px-4 py-3 rounded-lg bg-muted hover:bg-muted/80 transition-colors"
          >
            <div className="flex flex-col items-start">
              <span className="text-xs text-muted-foreground mb-1">WORKSPACE</span>
              <span className="font-semibold text-sm truncate max-w-[160px]">
                {currentWorkspace?.name || 'No Workspace'}
              </span>
            </div>
            <ChevronDown className={`w-4 h-4 transition-transform ${isWorkspaceDropdownOpen ? 'rotate-180' : ''}`} />
          </button>

          {/* Workspace Dropdown */}
          {isWorkspaceDropdownOpen && (
            <div className="absolute top-full left-0 right-0 mt-2 bg-card border border-border rounded-lg shadow-lg z-50 max-h-64 overflow-y-auto">
              {workspaces.map((workspace) => (
                <button
                  key={workspace.id}
                  onClick={() => {
                    setCurrentWorkspace(workspace)
                    setIsWorkspaceDropdownOpen(false)
                  }}
                  className={`w-full text-left px-4 py-3 hover:bg-muted transition-colors ${
                    currentWorkspace?.id === workspace.id ? 'bg-muted' : ''
                  }`}
                >
                  <div className="font-medium text-sm">{workspace.name}</div>
                  <div className="text-xs text-muted-foreground mt-1">{workspace.slug}</div>
                </button>
              ))}

              {/* Create New Workspace Button */}
              <button
                onClick={() => {
                  setIsWorkspaceDropdownOpen(false)
                  setIsCreateWorkspaceModalOpen(true)
                }}
                className="w-full text-left px-4 py-3 border-t border-border hover:bg-muted transition-colors flex items-center gap-2 text-primary font-medium"
              >
                <Plus className="w-4 h-4" />
                <span className="text-sm">Create New Workspace</span>
              </button>
            </div>
          )}
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-6 overflow-y-auto">

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

      <CreateWorkspaceModal
        isOpen={isCreateWorkspaceModalOpen}
        onClose={() => setIsCreateWorkspaceModalOpen(false)}
        onSuccess={refreshWorkspaces}
      />
    </aside>
  )
}
