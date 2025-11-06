import { ReactNode } from 'react'
import Sidebar from './Sidebar'
import { Toaster } from 'react-hot-toast'
import { useBundlerContext } from '../context/BundlerContext'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const { isOpen } = useBundlerContext()

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className={`flex-1 overflow-auto transition-all duration-300 ${isOpen ? 'mr-80' : 'mr-0'}`}>
        {children}
      </main>
      <Toaster position="top-right" />
    </div>
  )
}