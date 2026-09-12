import { useEffect, useState } from 'react'
import { notificationService } from '../services/portfolioService'
import { Skeleton } from '../components/Loading'

const EVENT_ICONS = {
  PORTFOLIO_SUBMITTED: '📤', PORTFOLIO_APPROVED: '✅', REVISION_REQUIRED: '✏️',
  PORTFOLIO_REJECTED: '❌', PORTFOLIO_PUBLISHED: '🌐', PROFILE_CREATED: '🎓', GENERIC: '🔔',
}

function Notifications() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)

  const load = () => {
    notificationService.list().then(setItems).finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const markAll = async () => {
    await notificationService.markAllRead()
    load()
  }

  const remove = async (id) => {
    await notificationService.remove(id)
    load()
  }

  if (loading) return <Skeleton rows={5} />
  return (
    <div>
      <div className="card">
        <div className="card-title">
          <h3>Notifications ({items.filter((n) => !n.is_read).length} unread)</h3>
          <button className="btn btn-sm" onClick={markAll}>Mark all read</button>
        </div>
        {!items.length ? (
          <div className="empty"><div className="big">🔕</div>No notifications yet. Submit a portfolio to trigger some!</div>
        ) : (
          items.map((n) => (
            <div key={n.id} className="list-item" style={{ opacity: n.is_read ? 0.6 : 1 }}>
              <div className="row" style={{ alignItems: 'flex-start', flex: 1 }}>
                <span style={{ fontSize: 22 }}>{EVENT_ICONS[n.event] || '🔔'}</span>
                <div>
                  <b>{n.event.replace(/_/g, ' ')}</b>
                  {!n.is_read && <span className="badge badge-blue" style={{ marginLeft: 8, padding: '1px 8px' }}>new</span>}
                  <div className="muted">{n.message}</div>
                  <div className="muted" style={{ fontSize: 12 }}>{new Date(n.created_at).toLocaleString()}</div>
                </div>
              </div>
              <button className="btn btn-sm btn-danger" onClick={() => remove(n.id)}>✕</button>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default Notifications