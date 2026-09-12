import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import DashboardLayout from '../layouts/DashboardLayout'

import Login from '../pages/Login'
import ResetPassword from '../pages/ResetPassword'
import PublicPortfolio from '../pages/PublicPortfolio'
import Dashboard from '../pages/Dashboard'
import Students from '../pages/Students'
import AddStudent from '../pages/AddStudent'
import EditStudent from '../pages/EditStudent'
import StudentProfile from '../pages/StudentProfile'
import BulkUpload from '../pages/BulkUpload'
import PortfolioGenerator from '../pages/PortfolioGenerator'
import PortfolioTemplates from '../pages/PortfolioTemplates'
import PortfolioPreview from '../pages/PortfolioPreview'
import PortfolioApproval from '../pages/PortfolioApproval'
import PublishedPortfolios from '../pages/PublishedPortfolios'
import Analytics from '../pages/Analytics'
import Notifications from '../pages/Notifications'
import Settings from '../pages/Settings'

function Protected({ children, roles }) {
  const { user } = useAuth()
  const location = useLocation()
  if (!user) return <Navigate to="/login" state={{ from: location }} replace />
  if (roles && !roles.includes(user.role)) return <Navigate to="/dashboard" replace />
  return children
}

function AppRoutes() {
  return (
    <Routes>
      {/* Public pages */}
      <Route path="/login" element={<Login />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route path="/portfolio/public/:slug" element={<PublicPortfolio />} />

      {/* Protected dashboard shell */}
      <Route
        path="/"
        element={
          <Protected>
            <DashboardLayout />
          </Protected>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="students" element={<Students />} />
        <Route path="students/add" element={<AddStudent />} />
        <Route path="students/new" element={<Navigate to="/students/add" replace />} />
        <Route path="students/:id/edit" element={<EditStudent />} />
        <Route path="students/:id" element={<StudentProfile />} />
        <Route path="bulk-upload" element={<Protected roles={['HR']}><BulkUpload /></Protected>} />
        <Route path="portfolio/generator" element={<PortfolioGenerator />} />
        <Route path="portfolio/templates" element={<PortfolioTemplates />} />
        <Route path="portfolio/:id/preview" element={<PortfolioPreview />} />
        <Route path="portfolio/approval" element={<Protected roles={['HR', 'TEACHER']}><PortfolioApproval /></Protected>} />
        <Route path="portfolio/published" element={<PublishedPortfolios />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="notifications" element={<Notifications />} />
        <Route path="settings" element={<Settings />} />
      </Route>

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default AppRoutes