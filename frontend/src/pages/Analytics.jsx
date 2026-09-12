import { useEffect, useState } from 'react'
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid,
  PieChart, Pie, Cell, Legend, LineChart, Line,
} from 'recharts'
import { dashboardService } from '../services/portfolioService'
import { Skeleton } from '../components/Loading'
import { StatCard } from '../components/StatCard'

const PIE_COLORS = ['#4f46e5', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#64748b']

function Analytics() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    dashboardService.analytics().then(setData).catch(() => setError('Failed to load analytics'))
  }, [])

  if (error) return <div className="empty"><div className="big">⚠️</div>{error}</div>
  if (!data) return <Skeleton rows={6} />

  const views = data.views_30_days || []
  const status = data.portfolio_status || []
  const bins = data.completion_bins || []

  const totalViews = data.total_views_30_days || 0
  const uniqueVisitors = views.reduce((a, v) => a + v.views, 0)
  const published = data.published_by_department?.reduce((a, d) => a + d.count, 0) || 0
  const avgCompletion = data.avg_completion_by_department?.length
    ? Math.round(data.avg_completion_by_department.reduce((a, d) => a + d.avg_completion, 0) / data.avg_completion_by_department.length)
    : 0
  const mostViewedDept = (data.published_by_department || [])[0]?.department || '—'

  return (
    <div>
      <div className="stat-grid">
        <StatCard icon="👁️" label="Total Portfolio Views" value={totalViews} color="#4f46e5" />
        <StatCard icon="👤" label="Unique Visitors (30d)" value={uniqueVisitors} color="#0ea5e9" />
        <StatCard icon="🌐" label="Published Portfolios" value={published} color="#22c55e" />
        <StatCard icon="📊" label="Average Completion" value={`${avgCompletion}%`} color="#f59e0b" />
        <StatCard icon="🏫" label="Most Viewed Department" value={mostViewedDept} color="#8b5cf6" />
      </div>

      <div className="grid-2">
        <div className="card">
          <h3>Portfolio Views — last 30 days</h3>
          {views.length ? (
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={views}>
                <CartesianGrid strokeDasharray="3 3" stroke="#eef2f7" />
                <XAxis dataKey="date" fontSize={11} />
                <YAxis allowDecimals={false} fontSize={12} />
                <Tooltip />
                <Line type="monotone" dataKey="views" stroke="#4f46e5" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          ) : <div className="empty">No views yet — share a public portfolio URL!</div>}
        </div>

        <div className="card">
          <h3>Average Completion by Department</h3>
          {(data.avg_completion_by_department || []).length ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={data.avg_completion_by_department} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#eef2f7" />
                <XAxis type="number" domain={[0, 100]} fontSize={12} />
                <YAxis type="category" dataKey="department" width={130} fontSize={12} />
                <Tooltip />
                <Bar dataKey="avg_completion" name="Avg %" fill="#0ea5e9" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : <div className="empty">No data</div>}
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <h3>Portfolio Status</h3>
          {status.length ? (
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={status} dataKey="count" nameKey="status" outerRadius={90} label>
                  {status.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : <div className="empty">No portfolios</div>}
        </div>

        <div className="card">
          <h3>Published Portfolios by Department</h3>
          {(data.published_by_department || []).length ? (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={data.published_by_department}>
                <CartesianGrid strokeDasharray="3 3" stroke="#eef2f7" />
                <XAxis dataKey="department" fontSize={11} />
                <YAxis allowDecimals={false} fontSize={12} />
                <Tooltip />
                <Bar dataKey="count" name="Published" fill="#8b5cf6" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : <div className="empty">Nothing published yet</div>}
        </div>
      </div>

      <div className="card">
        <h3>Completion Percentage Distribution</h3>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={bins}>
            <CartesianGrid strokeDasharray="3 3" stroke="#eef2f7" />
            <XAxis dataKey="label" fontSize={12} />
            <YAxis allowDecimals={false} fontSize={12} />
            <Tooltip />
            <Bar dataKey="value" name="Students" fill="#22c55e" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default Analytics