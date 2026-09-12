import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, PieChart, Pie, Cell, Legend,
} from 'recharts'
import { dashboardService } from '../services/portfolioService'
import { StatCard } from '../components/StatCard'
import { StatusBadge } from '../components/StatusBadge'
import { ProgressBar } from '../components/ProgressBar'
import { Skeleton } from '../components/Loading'
import { useAuth } from '../context/AuthContext'

const PIE_COLORS = ['#4f46e5', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#64748b']

function QuickActions({ user }) {
  const actions = [
    { to: '/students/add', icon: '➕', label: 'Add Student', show: user?.role === 'HR' },
    { to: '/bulk-upload', icon: '📤', label: 'Bulk Upload', show: user?.role === 'HR' },
    { to: '/portfolio/generator', icon: '⚙️', label: 'Generate Portfolio', show: true },
    { to: '/portfolio/templates', icon: '🎨', label: 'Templates', show: true },
    { to: '/portfolio/approval', icon: '✅', label: 'Approvals', show: user?.role === 'HR' || user?.role === 'TEACHER' },
    { to: '/analytics', icon: '📈', label: 'Analytics', show: user?.role === 'HR' || user?.role === 'TEACHER' },
    { to: '/notifications', icon: '🔔', label: 'Notifications', show: true },
    { to: '/settings', icon: '🛠️', label: 'Settings', show: true },
  ].filter((a) => a.show)
  return (
    <div className="quick-grid">
      {actions.map((a) => (
        <Link key={a.label} to={a.to} className="quick-action">
          <span className="quick-icon">{a.icon}</span>
          <span className="quick-label">{a.label}</span>
        </Link>
      ))}
    </div>
  )
}

function Dashboard() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const { user } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    dashboardService
      .data()
      .then(setData)
      .catch((e) => setError(e.response?.data?.detail || 'Failed to load dashboard'))
  }, [])

  if (error) return (
    <div className="empty">
      <div className="big">⚠️</div>
      Could not load dashboard. Is the backend running?
    </div>
  )
  if (!data) return <div className="grid-2"><Skeleton rows={4} /><Skeleton rows={4} /></div>

  const k = data.kpis || {}
  const completionSeries = (data.completion_bins || []).map((b) => ({ name: b.label, value: b.value }))
  const statusSeries = (data.portfolio_status || []).map((s) => ({ name: s.status, value: s.count }))

  const statCards = [
    { icon: '🎓', label: 'Total Students', value: k.total_students, color: '#4f46e5' },
    { icon: '📄', label: 'Portfolios Generated', value: k.portfolios_generated, color: '#0ea5e9' },
    { icon: '⏳', label: 'Pending Approval', value: k.pending_approval, color: '#f59e0b' },
    { icon: '🌐', label: 'Published Portfolios', value: k.published_portfolios, color: '#8b5cf6' },
    { icon: '🗂️', label: 'Incomplete Profiles', value: k.incomplete_profiles, color: '#ef4444' },
    { icon: '👁️', label: 'Portfolio Views', value: k.portfolio_views, color: '#22c55e' },
    { icon: '📊', label: 'Average Completion', value: `${k.avg_completion || 0}%`, color: '#0ea5e9' },
  ]

  const isTeacher = user?.role === 'TEACHER'

  return (
    <div>
      <div className="card welcome-card">
        <div className="row-between">
          <div>
            <h2 style={{ fontSize: 20 }}>Welcome back, {user?.first_name || user?.username} 👋</h2>
            <div className="muted">
              Here is what is happening with your {(isTeacher ? 'students' : 'student')} portfolios today.
            </div>
          </div>
          <div>
            <span className={`badge ${user?.is_superuser ? 'badge-violet' : 'badge-blue'}`}>
              {user?.is_superuser ? 'Super Admin' : user?.role_display || user?.role}
            </span>
          </div>
        </div>
      </div>

      <div className="stat-grid">
        {statCards.map((s) => <StatCard key={s.label} {...s} />)}
      </div>

      <div className="card">
        <h3>Quick Actions</h3>
        <QuickActions user={user} />
      </div>
<div className="grid-2">
        <div className="card">
          <h3>Profile Completion Distribution</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={completionSeries}>
              <CartesianGrid strokeDasharray="3 3" stroke="#eef2f7" />
              <XAxis dataKey="name" fontSize={12} />
              <YAxis allowDecimals={false} fontSize={12} />
              <Tooltip />
              <Bar dataKey="value" name="Students" fill="#4f46e5" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="card">
          <h3>Portfolio Status</h3>
          {statusSeries.length ? (
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={statusSeries} dataKey="value" nameKey="name" outerRadius={90} label>
                  {statusSeries.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : <div className="empty">No portfolios yet — generate one!</div>}
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <h3>Department Analysis</h3>
          {(data.department_analysis || []).length ? (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={data.department_analysis} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#eef2f7" />
                <XAxis type="number" fontSize={12} />
                <YAxis type="category" dataKey="department" width={130} fontSize={12} />
                <Tooltip />
                <Bar dataKey="count" name="Students" fill="#0ea5e9" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : <div className="empty">No department data</div>}
        </div>

        <div className="card">
          <div className="card-title">
            <h3>Students Requiring Support</h3>
            <Link to="/students">All students →</Link>
          </div>
          {(data.students_requiring_support || []).length ? (
            <div style={{ maxHeight: 300, overflowY: 'auto' }}>
              {data.students_requiring_support.map((s) => (
                <div key={s.id} className="list-item" style={{ cursor: 'pointer' }}
                     onClick={() => navigate(`/students/${s.id}`)}>
                  <div>
                    <h4>{s.name}</h4>
                    <div className="muted">{s.register_number} · {s.department || '—'}</div>
                    <div className="mt">
                      {(s.missing || []).map((m) => (
                        <span key={m} className="badge badge-amber" style={{ margin: 2 }}>{m}</span>
                      ))}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div className="kpi-value">{s.completion}%</div>
                    <div className="kpi-sub">complete</div>
                  </div>
                </div>
              ))}
            </div>
          ) : <div className="empty">Everyone looks complete 🎉</div>}
        </div>
      </div>
<div className="card">
        <div className="card-title">
          <h3>{isTeacher ? 'My Students' : 'Recent Students'}</h3>
          <Link to="/students">View all →</Link>
        </div>
        {(data.recent_students || []).length ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>Student</th><th>Register No</th><th>Department</th><th>Email</th><th>Completion</th></tr>
              </thead>
              <tbody>
                {data.recent_students.map((s) => (
                  <tr key={s.id} onClick={() => navigate(`/students/${s.id}`)} style={{ cursor: 'pointer' }}>
                    <td>
                      <div className="row">
                        {s.profile_photo
                          ? <img className="avatar-sm" src={s.profile_photo} alt={s.name} />
                          : <span className="avatar-sm">{s.name?.[0]}</span>}
                        <b>{s.name}</b>
                      </div>
                    </td>
                    <td>{s.register_number}</td>
                    <td>{s.department || '—'}</td>
                    <td>{s.email || '—'}</td>
                    <td style={{ width: 150 }}><ProgressBar percent={s.completion} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <div className="empty">No students yet</div>}
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-title">
            <h3>Approval Queue</h3>
            <Link to="/portfolio/approval">Review →</Link>
          </div>
          {(data.approval_queue || []).length ? (
            data.approval_queue.map((p) => (
              <div key={p.id} className="list-item" style={{ cursor: 'pointer' }}
                   onClick={() => navigate(`/portfolio/approval?portfolio=${p.id}`)}>
                <div>
                  <h4>{p.student_name}</h4>
                  <div className="muted">{p.completion}% complete</div>
                </div>
                <StatusBadge status={p.status} />
              </div>
            ))
          ) : <div className="empty">No portfolios pending approval</div>}
        </div>

        <div className="card">
          <h3>Recent Activity</h3>
          {(data.recent_activities || []).length ? (
            data.recent_activities.map((a) => (
              <div key={a.id} className="list-item">
                <div>
                  <b>{String(a.action).replace(/_/g, ' ')}</b>
                  <div className="muted">by {a.actor || 'system'}{a.details ? ` — ${a.details}` : ''}</div>
                </div>
              </div>
            ))
          ) : <div className="empty">No activity yet</div>}
        </div>
      </div>
    </div>
  )
}

export default Dashboard