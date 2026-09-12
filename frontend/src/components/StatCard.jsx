export function StatCard({ icon, label, value, sub, color = 'var(--primary)' }) {
  return (
    <div className="stat-card">
      <div className="icon" style={{ background: `${color}1a`, color }}>
        {icon}
      </div>
      <div>
        <div className="value">{value != null ? value : '—'}</div>
        <div className="label">{label}</div>
        {sub && <div className="kpi-sub">{sub}</div>}
      </div>
    </div>
  )
}

export default StatCard