import { useEffect, useState } from 'react'
import { portfolioService, dashboardService } from '../services/portfolioService'
import { Skeleton } from '../components/Loading'
import { StatusBadge } from '../components/StatusBadge'
import { Modal } from '../components/Modal'
import { useToast } from '../context/ToastContext'

function PublishedPortfolios() {
  const toast = useToast()
  const [portfolios, setPortfolios] = useState([])
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [qrTarget, setQrTarget] = useState(null)

  useEffect(() => {
    portfolioService.list().then((all) => {
      setPortfolios(all.filter((p) => p.status === 'PUBLISHED'))
    }).finally(() => setLoading(false))
    dashboardService.analytics().then(setAnalytics).catch(() => {})
  }, [])

  const copyUrl = (slug) => {
    const url = `${window.location.origin}/portfolio/public/${slug}`
    navigator.clipboard?.writeText(url).then(() => toast.success('URL copied!')).catch(() => {
      const a = document.createElement('textarea')
      a.value = url
      document.body.appendChild(a)
      a.select()
      document.execCommand('copy')
      document.body.removeChild(a)
      toast.success('URL copied!')
    })
  }

  if (loading) return <Skeleton rows={5} />
  return (
    <div>
      <div className="card">
        <div className="card-title">
          <h3>Published Portfolios</h3>
          <span className="muted">{portfolios.length} live</span>
        </div>
        {!portfolios.length ? (
          <div className="empty">
            <div className="big">🌐</div>
            No published portfolios yet.<br />Generate → Approve → Publish to go live.
          </div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>Student</th><th>Portfolio URL</th><th>Published Date</th><th>Views</th><th>Template</th><th>Status</th><th>Actions</th></tr>
              </thead>
              <tbody>
                {portfolios.map((p) => (
                  <tr key={p.id}>
                    <td><b>{p.student_name}</b><div className="muted" style={{ fontSize: 12 }}>{p.register_number}</div></td>
                    <td><a href={`/portfolio/public/${p.slug}`} target="_blank" rel="noreferrer">/portfolio/public/{p.slug}</a></td>
                    <td className="muted" style={{ whiteSpace: 'nowrap', fontSize: 12.5 }}>{p.published_at ? new Date(p.published_at).toLocaleDateString() : '—'}</td>
                    <td>👁️ {p.views_count}</td>
                    <td>{p.template_name || 'Default'}</td>
                    <td><StatusBadge status={p.status} /></td>
                    <td>
                      <div className="row" style={{ gap: 6 }}>
                        <a className="btn btn-sm" href={`/portfolio/public/${p.slug}`} target="_blank" rel="noreferrer">View</a>
                        <button className="btn btn-sm" onClick={() => copyUrl(p.slug)}>Copy URL</button>
                        <button className="btn btn-sm" onClick={() => setQrTarget(p)}>QR Code</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {analytics?.views_30_days?.length > 0 && (
        <div className="card">
          <h3 className="mb">Views — last 30 days</h3>
          <div className="row" style={{ gap: 8, alignItems: 'flex-end', minHeight: 140 }}>
            {analytics.views_30_days.slice(-14).map((d) => (
              <div key={d.date} style={{ textAlign: 'center', flex: 1 }}>
                <div style={{ background: 'var(--primary)', borderRadius: '6px 6px 0 0', height: `${Math.max(4, d.views * 12)}px`, minWidth: 18 }} title={`${d.date}: ${d.views}`} />
                <div style={{ fontSize: 11, color: 'var(--muted)', marginTop: 4 }}>{d.date.slice(5)}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      <Modal open={!!qrTarget} title="Your Portfolio is Live!" onClose={() => setQrTarget(null)}>
        {qrTarget && (
          <div className="qr-box">
            <div className="row">
              <span className="badge badge-green">🔗 Portfolio URL</span>
              <span className="muted" style={{ flex: 1, overflowWrap: 'anywhere' }}>/portfolio/public/{qrTarget.slug}</span>
              <button className="btn btn-sm" onClick={() => copyUrl(qrTarget.slug)}>Copy URL</button>
            </div>
            <div className="qr-code" style={{ textAlign: 'center', padding: '20px 0' }}>
              <div className="qr-placeholder">
                <a className="btn btn-primary" href={`/portfolio/${qrTarget.id}/qr/`} target="_blank">⬇️ Download QR Code</a>
                <p className="muted mt" style={{ fontSize: 12.5 }}>QR redirects to /portfolio/public/{qrTarget.slug}</p>
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}

export default PublishedPortfolios