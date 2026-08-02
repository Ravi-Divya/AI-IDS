import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { Layout } from '@/components/layout/Layout'
import Landing from '@/pages/Landing'
import Login from '@/pages/Login'
import SignUp from '@/pages/SignUp'
import CompanySetup from '@/pages/CompanySetup'
import Dashboard from '@/pages/Dashboard'
import Packets from '@/pages/Packets'
import Flows from '@/pages/Flows'
import Threats from '@/pages/Threats'
import Alerts from '@/pages/Alerts'
import Analytics from '@/pages/Analytics'
import ML from '@/pages/ML'
import Users from '@/pages/Users'
import Settings from '@/pages/Settings'
import Logs from '@/pages/Logs'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <>{children}</>
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  if (isAuthenticated) return <Navigate to="/dashboard" replace />
  return <>{children}</>
}

export default function App() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const user = useAuthStore((s) => s.user)
  const needsCompanySetup = isAuthenticated && user && !user.company_name

  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
      <Route path="/signup" element={<PublicRoute><SignUp /></PublicRoute>} />
      <Route path="/setup-company" element={
        isAuthenticated ? (
          needsCompanySetup ? <CompanySetup /> : <Navigate to="/dashboard" replace />
        ) : (
          <Navigate to="/login" replace />
        )
      } />
      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={
          needsCompanySetup ? <Navigate to="/setup-company" replace /> : <Dashboard />
        } />
        <Route path="/packets" element={
          needsCompanySetup ? <Navigate to="/setup-company" replace /> : <Packets />
        } />
        <Route path="/flows" element={
          needsCompanySetup ? <Navigate to="/setup-company" replace /> : <Flows />
        } />
        <Route path="/threats" element={
          needsCompanySetup ? <Navigate to="/setup-company" replace /> : <Threats />
        } />
        <Route path="/alerts" element={
          needsCompanySetup ? <Navigate to="/setup-company" replace /> : <Alerts />
        } />
        <Route path="/analytics" element={
          needsCompanySetup ? <Navigate to="/setup-company" replace /> : <Analytics />
        } />
        <Route path="/ml" element={
          needsCompanySetup ? <Navigate to="/setup-company" replace /> : <ML />
        } />
        <Route path="/users" element={
          needsCompanySetup ? <Navigate to="/setup-company" replace /> : <Users />
        } />
        <Route path="/settings" element={
          needsCompanySetup ? <Navigate to="/setup-company" replace /> : <Settings />
        } />
        <Route path="/logs" element={
          needsCompanySetup ? <Navigate to="/setup-company" replace /> : <Logs />
        } />
      </Route>
      <Route path="*" element={<Navigate to={isAuthenticated ? '/dashboard' : '/'} replace />} />
    </Routes>
  )
}
