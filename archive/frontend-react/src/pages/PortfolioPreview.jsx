import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { portfolioService } from '../services/portfolioService'
import { useToast } from '../context/ToastContext'
import { StatusBadge } from '../components/StatusBadge'
import { Skeleton } from '../components/Loading'
import { errorMessage } from '../services/api'

function PortfolioPreview() {
  const { id } = useParams()
  const navigate = useNavigate()
  const toast = useToast()
  const [portfolio, setPortfolio] = useState(null)
  const [busy, setBusy] = useState('')

  useEffect(() => {
    portfolioService.get(id).then(setPortfolio).catch((e) => toast.error(errorMessage(e, 'Could not load portfolio')))
  }, [id])

  if (!portfolio) return <Skeleton rows={6} />
  const data = portfolio.data || {}

  const act = async (fn, label) => {
    setBusy(label)
    try {
      await fn(portfolio.id)
      const fresh = await portfolioService.get(portfolio.id)
      setPortfolio(fresh)
      toast.success(`${label} done`)
    } catch (err) {
      toast.error(errorMessage(err, `${label} failed`))
    } finally {
      setBusy('')
    }
  }

  const section = (label, children) => (
    <div style={{ marginTop: 20 }}>
      <div className="section-title">{label}</div>
      {children}
    </div>
  )

  return (
    <div>
      <div className="card">
        <div className="card-title">
          <div className="row">
            <h3>{portfolio.student_name}'s Portfolio — Preview</h3>
            <StatusBadge status={portfolio.status} />
          </div>
          <div className="row">
            <button className="btn btn-sm" onClick={() => navigate(`/students/${portfolio.student}`)}>✏️ Edit</button>
            <button className="btn btn-sm" onClick={() => navigate('/portfolio/templates')}>🎨 Change Template</button>
            <button className="btn btn-sm" onClick={() => navigate('/portfolio/generator')}>💾 Save Draft</button>
            <button className="btn btn-primary btn-sm" onClick={() => act(portfolioService.submit, 'Submit')} disabled={!!busy}>📤 Submit for Approval</button>
            {portfolio.status === 'APPROVED' && (
              <button className="btn btn-success btn-sm" onClick={() => act(portfolioService.publish, 'Publish')} disabled={!!busy}>🌐 Publish</button>
            )}
            <button className="btn btn-sm" onClick={() => navigate('/portfolio/generator')}>← Back</button>
          </div>
        </div>
      </div>

      <div className="card">
        <div style={{ border: '1px solid var(--border)', borderRadius: 12, overflow: 'hidden' }}>
          <div style={{ background: 'linear-gradient(135deg,#1e1b4b,#4f46e5)', color: '#fff', padding: 40, textAlign: 'center' }}>
            {data.personal?.profile_photo
              ? <img src={data.personal.profile_photo} alt="" style={{ width: 110, height: 110, borderRadius: '50%', border: '4px solid #fff', objectFit: 'cover' }} />
              : <div style={{ width: 110, height: 110, borderRadius: '50%', background: 'rgba(255,255,255,0.2)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: 40 }}>{(data.personal?.name || '?')[0]}</div>}
            <h1 style={{ marginTop: 12, fontSize: 30 }}>{data.personal?.name}</h1>
            <div style={{ opacity: 0.9, fontSize: 17 }}>{data.personal?.department} · {data.education?.[0]?.degree}</div>
            <div className="contact-bar">
              {data.personal?.email && <a href={`mailto:${data.personal.email}`}>✉️ {data.personal.email}</a>}
              {data.personal?.phone && <span>📞 {data.personal.phone}</span>}
              {data.personal?.github_url && <a href={data.personal.github_url} target="_blank" rel="noreferrer">GitHub</a>}
              {data.personal?.linkedin_url && <a href={data.personal.linkedin_url} target="_blank" rel="noreferrer">LinkedIn</a>}
            </div>
          </div>
          <div style={{ padding: 24 }}>
            {data.personal?.professional_summary && <p className="muted">{data.personal.professional_summary}</p>}
            {section('Education', (data.education || []).map((e) => (
              <div key={e.id} className="list-item"><div><b>{e.degree}</b><span className="muted"> · {e.college || ''}</span></div></div>
            )))}
{section('Projects', (data.projects || []).map((p) => (
              <div key={p.id} className="list-item">
                <div>
                  <b>{p.name}</b>
                  <div className="muted">{p.description || ''}</div>
                  {p.technologies && <div className="mt">{p.technologies.split(',').map((t) => <span key={t.trim()} className="skill-chip">{t.trim()}</span>)}</div>}
                </div>
              </div>
            )))}
            {section('Internship', (data.internships || []).map((i) => (
              <div key={i.id} className="list-item"><b>{i.role_name} @ {i.company}</b></div>
            )))}
            {section('Certifications', (data.certifications || []).map((c) => (
              <div key={c.id} className="list-item"><b>{c.name}</b><span className="muted"> · {c.issuing_organization}</span></div>
            )))}
            {section('Achievements', (data.achievements || []).map((a) => (
              <div key={a.id} className="list-item"><b>{a.title}</b><span className="badge badge-violet">{a.level}</span></div>
            )))}
            {section('360° Feedback', (data.feedback?.teacher || []).map((f) => (
              <div key={f.id} className="list-item">
                <div><b>{f.teacher_name}</b><div className="muted">{f.remarks}</div></div>
                <span className="badge badge-blue">Rating {f.overall_rating}/5</span>
              </div>
            )))}
            {section('Goals', (data.goals || []).map((g) => (
              <div key={g.id} className="list-item"><b>{g.title}</b><span className="badge badge-amber">{g.status.replace(/_/g, ' ')}</span></div>
            )))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default PortfolioPreview
            {section('Skills', (data.skills || []).map((s) => <span key={s.id} className="skill-chip">{s.name}</span>))}