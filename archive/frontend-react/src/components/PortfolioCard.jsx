import { StatusBadge } from './StatusBadge'

export function PortfolioCard({ portfolio, onOpen }) {
  return (
    <div className="card" style={{ marginBottom: 14 }}>
      <div className="row-between">
        <div className="row">
          <img
            className="avatar-sm"
            src={portfolio.profile_photo || ''}
            alt=""
            style={portfolio.profile_photo ? {} : { display: 'none' }}
          />
          <div>
            <h4 style={{ fontSize: 16 }}>{portfolio.student_name}</h4>
            <div className="muted">{portfolio.register_number} · {portfolio.title}</div>
          </div>
        </div>
        <StatusBadge status={portfolio.status} />
      </div>
      <div className="row mt">
        <div className="progress-bar" style={{ width: 200 }}>
          <div className="progress-fill" style={{ width: `${portfolio.completion_percentage || 0}%` }} />
        </div>
        <span className="muted">{portfolio.completion_percentage || 0}% complete</span>
        {onOpen && <button className="btn btn-sm" onClick={() => onOpen(portfolio)}>Open →</button>}
      </div>
    </div>
  )
}

export default PortfolioCard