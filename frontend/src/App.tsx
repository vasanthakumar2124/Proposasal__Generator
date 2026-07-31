import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Provider } from 'react-redux'
import { store } from './store'
import { ThemeProvider } from './providers/ThemeProvider'
import { AuthProvider } from './providers/AuthProvider'
import { QueryProvider } from './providers/QueryProvider'
import { ProtectedRoute } from './components/auth/ProtectedRoute'
import { PublicRoute } from './components/auth/PublicRoute'
import { AppLayout } from './components/layout/AppLayout'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import WorkspacePage from './pages/Workspace'
import Clients from './pages/Clients'
import Projects from './pages/Projects'
import ProjectDetail from './pages/ProjectDetail'
import GenerateProposal from './pages/GenerateProposal'
import ProposalDetail from './pages/ProposalDetail'
import ProposalHistory from './pages/ProposalHistory'
import BillingPage from './pages/Billing'
import AnalyticsPage from './pages/Analytics'

function App() {
  return (
    <Provider store={store}>
      <QueryProvider>
        <ThemeProvider>
          <BrowserRouter>
            <AuthProvider>
              <Routes>
                <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
                <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />

                <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/workspace" element={<WorkspacePage />} />
                  <Route path="/clients" element={<Clients />} />
                  <Route path="/projects" element={<Projects />} />
                  <Route path="/projects/:id" element={<ProjectDetail />} />
                  <Route path="/generate" element={<GenerateProposal />} />
                  <Route path="/proposals/:id" element={<ProposalDetail />} />
                  <Route path="/history" element={<ProposalHistory />} />
                  <Route path="/billing" element={<BillingPage />} />
                  <Route path="/analytics" element={<AnalyticsPage />} />
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                </Route>

                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </AuthProvider>
          </BrowserRouter>
        </ThemeProvider>
      </QueryProvider>
    </Provider>
  )
}

export default App
