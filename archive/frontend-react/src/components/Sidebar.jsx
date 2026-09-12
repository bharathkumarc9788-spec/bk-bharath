import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, GraduationCap, UserRound, FileCog, Palette, BadgeCheck,
  Globe, ChartColumnBig, Upload, Bell, Settings, ShieldCheck, LifeBuoy, LogOut,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { authService } from '../services/authService'

function sidebarToggle(open) {
  const shell = document.getElementById('app-shell')
  if (shell) shell.classList.toggle('sidebar-open', open)
}

export function closeSidebar() {
  sidebarToggle(false)
}

function Sidebar() {
  const { user } = useAuth()

  const primary = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/students', label: 'Students', icon: GraduationCap },
    { to: '/students', label: 'Student Profiles', icon: UserRound },
    ...(user?.role === 'HR'
      ? [{ to: '/students/add', label: 'Add Student', icon: GraduationCap }]
      : []),
    { to: '/portfolio/generator', label: 'Portfolio Generator', icon: FileCog },
    { to: '/portfolio/templates', label: 'Portfolio Templates', icon: Palette },
  ]

  const review = user?.role === 'HR' || user?.role === 'TEACHER'
    ? [
        { to: '/portfolio/approval', label: 'Portfolio Approval', icon: BadgeCheck },
        { to: '/portfolio/published', label: 'Published Portfolios', icon: Globe },
        { to: '/analytics', label: 'Analytics', icon: ChartColumnBig },
      ]
    : []

  const common = [
    ...(user?.role === 'HR' ? [{ to: '/bulk-upload', label: 'Bulk Upload', icon: Upload }] : []),
    { to: '/notifications', label: 'Notifications', icon: Bell },
    { to: '/settings', label: 'Settings', icon: Settings },
  ]

  const item = (it) => {
    const Icon = it.icon
    return (
      <NavLink key={it.to + it.label} to={it.to} className={({ isActive }) => (isActive ? 'active' : '')} onClick={() => sidebarToggle(false)}>
        <Icon size={17} />
        {it.label}
      </NavLink>
    )
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <span className="logo">🎒</span>
        <span>Student Portfolio</span>
      </div>
      <nav>
        <div className="nav-group">Main</div>
        {primary.map(item)}
        {review.length > 0 && <div className="nav-group">Review & Reports</div>}
        {review.map(item)}
        <div className="nav-group">System</div>
        {common.map(item)}
      </nav>
      <div className="sidebar-user">
        <div className="row-between">
          <div>
            <b>{user?.first_name ? `${user.first_name} ${user.last_name}` : user?.username}</b>
            <div className="muted" style={{ fontSize: 12 }}>
              {user?.is_superuser ? 'Super Admin' : user?.role_display || user?.role}
            </div>
          </div>
          <span className={`badge ${user?.role === 'HR' ? 'badge-violet' : 'badge-gray'}`}>{user?.role || 'User'}</span>
        </div>
      </div>
      <div className="sidebar-footer">
        <div className="row" style={{ gap: 8 }}>
          <a className="footer-link" href="#help" onClick={(e) => e.preventDefault()}>
            <LifeBuoy size={15} /> Help & Support
          </a>
          <a className="footer-link" href="/admin/" target="_blank" rel="noreferrer">
            <ShieldCheck size={15} /> Admin
          </a>
        </div>
        <button
          className="btn btn-sm footer-logout"
          onClick={() => { authService.logout(); window.location.href = '/login' }}
          style={{ width: '100%', justifyContent: 'flex-start', marginTop: 8 }}
        >
          <LogOut size={15} /> Logout
        </button>
        <div style={{ marginTop: 10, fontSize: 11, color: '#6b7280' }}>
          Student Portfolio Automation System v2.0
        </div>
      </div>
    </aside>
  )
}

export default Sidebar