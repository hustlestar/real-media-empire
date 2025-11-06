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
            </Routes>
          </Layout>
          <BundlerPanel />
        </BrowserRouter>
      </BundlerProvider>
    </QueryClientProvider>
  )
}

export default App