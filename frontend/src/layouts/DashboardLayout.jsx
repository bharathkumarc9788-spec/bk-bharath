import { Outlet } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'
import { ToastProvider } from '../context/ToastContext'

function DashboardLayout() {
  return (
    <div className="app-shell" id="app-shell">
      <div className="sidebar-backdrop" onClick={() => {
        const shell = document.getElementById('app-shell')
        if (shell) shell.classList.remove('sidebar-open')
      }} />
      <Sidebar />
      <div className="main">
        <Header />
        <main className="content">
          <ToastProvider>
            <Outlet />
          </ToastProvider>
        </main>
      </div>
    </div>
  )
}

export default DashboardLayout