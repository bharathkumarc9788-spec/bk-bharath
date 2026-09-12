import { Link } from 'react-router-dom'
import { Menu, Bell, Settings, LogOut } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

function Header({ title, subtitle }) {
  const { user, logout } = useAuth()
  const initials = user ? (user.first_name?.[0] || '') + (user.last_name?.[0] || '') : '?'

  return (
    <header className="topbar">
      <div className="topbar-left">
        <button className="btn btn-sm hamburger" aria-label="Menu" onClick={() => {
          const shell = document.getElementById('app-shell')
          if (shell) shell.classList.toggle('sidebar-open')
        }}>
          <Menu size={18} />
        </button>
        <div>
          <h2>{title || 'Dashboard'}</h2>
          {subtitle && <div className="muted" style={{ fontSize: 13 }}>{subtitle}</div>}
        </div>
      </div>
      <div className="topbar-right">
        <Link to="/notifications" className="btn btn-sm" title="Notifications">
          <Bell size={16} />
        </Link>
        <Link to="/settings" className="btn btn-sm" title="Settings">
          <Settings size={16} />
        </Link>
        <div className="topbar-user">
          <span className="avatar">{initials || 'U'}</span>
          <div>
            <div>{user?.first_name ? `${user.first_name} ${user.last_name}` : user?.username}</div>
            <div className="muted" style={{ fontSize: 12 }}>
              {user?.is_superuser ? 'Super Admin' : user?.role_display || user?.role}
            </div>
          </div>
        </div>
        <button className="btn btn-sm" onClick={logout} title="Logout"><LogOut size={16} /></button>
      </div>
    </header>
  )
}

export default Header