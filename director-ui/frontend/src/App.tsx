import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import './lib/api-config'
import ContentPage from './pages/ContentPage'
import JobsPage from './pages/JobsPage'
import ContentDetailPage from './pages/ContentDetailPage'
import JobDetailPage from './pages/JobDetailPage'
import { BundlesPage } from './pages/BundlesPage'
import { BundleDetailPage } from './pages/BundleDetailPage'
import FilmGenerationPage from './pages/FilmGenerationPage'
import PPTXGenerationPage from './pages/PPTXGenerationPage'
import AssetGalleryPage from './pages/AssetGalleryPage'
import PublishingDashboardPage from './pages/PublishingDashboardPage'
import CharacterLibraryPage from './pages/CharacterLibraryPage'
import { BundlerProvider } from './context/BundlerContext'
import { BundlerPanel } from './components/BundlerPanel'

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
      <BundlerProvider>
        <BrowserRouter>
          <Layout>
            <Routes>
              <Route path="/" element={<Navigate to="/content" replace />} />
              <Route path="/content" element={<ContentPage />} />
              <Route path="/content/:id" element={<ContentDetailPage />} />
              <Route path="/jobs" element={<JobsPage />} />
              <Route path="/jobs/:id" element={<JobDetailPage />} />
              <Route path="/bundles" element={<BundlesPage />} />
              <Route path="/bundles/:bundleId" element={<BundleDetailPage />} />

              {/* Creation Tools */}
              <Route path="/film-generation" element={<FilmGenerationPage />} />
              <Route path="/pptx-generation" element={<PPTXGenerationPage />} />

              {/* Library */}
              <Route path="/assets" element={<AssetGalleryPage />} />
              <Route path="/characters" element={<CharacterLibraryPage />} />

              {/* Publishing */}
              <Route path="/publishing" element={<PublishingDashboardPage />} />
            </Routes>
          </Layout>
          <BundlerPanel />
        </BrowserRouter>
      </BundlerProvider>
    </QueryClientProvider>
  )
}

export default App