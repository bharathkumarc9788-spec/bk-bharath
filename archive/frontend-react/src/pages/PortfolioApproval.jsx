import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { portfolioService } from '../services/portfolioService'
import { Skeleton } from '../components/Loading'
import { EmptyState } from '../components/EmptyState'
import { StatusBadge } from '../components/StatusBadge'
import { Modal } from '../components/Modal'
import { useToast } from '../context/ToastContext'
import { errorMessage } from '../services/api'

const STATUS_ORDER = ['SUBMITTED', 'UNDER_REVIEW', 'APPROVED', 'REVISION_REQUIRED', 'REJECTED', 'PUBLISHED']

function PortfolioApproval() {
  const [params] = useSearchParams()
  const toast = useToast()
  const [portfolios, setPortfolios] = useState([])
  const [loading, setLoading] = useState(true)
  const [active, setActive] = useState(Number(params.get('portfolio')) || null)
  const [detail, setDetail] = useState(null)
  const [reviewModal, setReviewModal] = useState(null)
  const [comment, setComment] = useState('')
  const [filter, setFilter] = useState('')

  const load = () => {
    portfolioService.list().then((d) => setPortfolios(d)).finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
    if (params.get('portfolio')) {
      setActive(Number(params.get('portfolio')))
      portfolioService.get(Number(params.get('portfolio'))).then(setDetail)
    }
  }, [])

  const select = async (p) => {
    setActive(p.id)
    setDetail(await portfolioService.get(p.id))
  }

  const act = async (fn, label) => {
    try {
      await fn(active)
      toast.success(`${label} — done`)
      setDetail(await portfolioService.get(active))
      load()
    } catch (err) {
      toast.error(errorMessage(err, `${label} failed`))
    }
  }

  const submitReview = async () => {
    if (!reviewModal || !active) return
    const fn = reviewModal.type === 'approve'
      ? portfolioService.approve
      : reviewModal.type === 'reject'
        ? portfolioService.reject
        : portfolioService.revision
    const payload = reviewModal.type === 'revision' ? { revision_reason: comment } : { comments: comment }
    try {
      await fn(active, payload.comments || payload.revision_reason)
      toast.success(`Review submitted (${reviewModal.type})`)
      setReviewModal(null)
      setComment('')
      setDetail(await portfolioService.get(active))
      load()
    } catch (err) {
      toast.error(errorMessage(err, 'Review failed'))
    }
  }

  const filtered = filter ? portfolios.filter((p) => p.status === filter) : portfolios

  return (
    <div className="grid-2">
      <div className="card">
        <div className="card-title">
          <h3>Approval Queue</h3>
          <select value={filter} onChange={(e) => setFilter(e.target.value)}
                  style={{ padding: 8, border: '1px solid var(--border)', borderRadius: 8 }}>
            <option value="">All Statuses</option>
            {STATUS_ORDER.map((s) => <option key={s} value={s}>{s.replace(/_/g, ' ')}</option>)}
          </select>
        </div>
        {loading ? <Skeleton rows={4} /> : (
          !filtered.length ? (
            <EmptyState icon="🕵️" title="No portfolios in this queue" sub="Submit portfolios from the generator to build a queue." />
          ) : (
            filtered.map((p) => (
              <div key={p.id} className="list-item"
                   style={{ cursor: 'pointer', borderColor: active === p.id ? 'var(--primary)' : 'var(--border)', marginBottom: 8 }}
                   onClick={() => select(p)}>
                <div>
                  <h4>{p.student_name}</h4>
                  <div className="muted">{p.register_number} · {p.completion_percentage}% complete</div>
                </div>
                <StatusBadge status={p.status} />
              </div>
            ))
          )
        )}
      </div>

      <ReviewPanel detail={detail} setReviewModal={setReviewModal} act={act} />
      <Modal open={!!reviewModal} title={reviewModal?.title} onClose={() => setReviewModal(null)}>
        <div className="form-group mb">
          <label>Comments / Reason</label>
          <textarea value={comment} onChange={(e) => setComment(e.target.value)} placeholder="Add a note for the student…" />
        </div>
        <div className="row">
          <button className="btn btn-primary" onClick={submitReview}>Submit Review</button>
          <button className="btn" onClick={() => setReviewModal(null)}>Cancel</button>
        </div>
      </Modal>
    </div>
  )
}

function ReviewPanel({ detail, setReviewModal, act }) {
  if (!detail) return <div className="card"><EmptyState icon="🕵️" title="Select a portfolio to review." /></div>
  return (
    <div className="card">
      <div className="row-between">
        <div>
          <h3>{detail.student_name}'s Portfolio</h3>
          <div className="muted">{detail.register_number} · {detail.title}</div>
        </div>
        <StatusBadge status={detail.status} />
      </div>

      <div className="row mt">
        <button className="btn btn-primary btn-sm" onClick={() => setReviewModal({ type: 'approve', title: 'Approve Portfolio' })}>✅ Approve</button>
        <button className="btn btn-warning btn-sm" onClick={() => setReviewModal({ type: 'revision', title: 'Request Revision' })}>✏️ Request Changes</button>
        <button className="btn btn-danger btn-sm" onClick={() => setReviewModal({ type: 'reject', title: 'Reject Portfolio' })}>❌ Reject</button>
        <button className="btn btn-success btn-sm" onClick={() => act(portfolioService.publish, 'Publish')} disabled={detail.status !== 'APPROVED'}>🌐 Publish</button>
        <button className="btn btn-sm" onClick={() => window.open(`/portfolio/${detail.id}/preview`, '_blank')}>👁 Preview</button>
      </div>

      <div className="mt"><b>Completion:</b> {detail.completion_percentage}%</div>

      <div className="mt">
        <h4 style={{ marginBottom: 8 }}>Approval History</h4>
        {(detail.approvals || []).map((a) => (
          <div key={a.id} className="list-item" style={{ display: 'block', padding: 10 }}>
            <div className="row-between">
              <b>{a.status.replace(/_/g, ' ')}</b>
              <span className="muted" style={{ fontSize: 12 }}>by {a.reviewer_name || 'auto'} · {new Date(a.created_at).toLocaleString()}</span>
            </div>
            {a.comments && <div className="muted mt">{a.comments}</div>}
          </div>
        ))}
      </div>

      <div className="mt">
        <h4 style={{ marginBottom: 8 }}>Versions</h4>
        {(detail.versions || []).map((v) => (
          <div key={v.id} className="muted" style={{ fontSize: 13, marginBottom: 6 }}>
            v{v.version_no} — {v.comment || 'Generated'} ({new Date(v.created_at).toLocaleString()})
          </div>
        ))}
      </div>
    </div>
  )
}

export default PortfolioApproval