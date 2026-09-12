import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import studentService from '../services/studentService'
import { portfolioService } from '../services/portfolioService'
import { useToast } from '../context/ToastContext'
import { StatusBadge } from '../components/StatusBadge'
import { errorMessage } from '../services/api'

const GEN_STEPS = [
  'Preparing student data...',
  'Loading education...',
  'Loading skills...',
  'Loading projects...',
  'Loading internship...',
  'Loading certificates...',
  'Loading achievements...',
  'Generating portfolio...',
]

function PortfolioGenerator() {
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const toast = useToast()
  const [students, setStudents] = useState([])
  const [studentId, setStudentId] = useState(params.get('student') || '')
  const [templates, setTemplates] = useState([])
  const [templateId, setTemplateId] = useState(params.get('template') || '')
  const [portfolio, setPortfolio] = useState(null)
  const [missing, setMissing] = useState([])
  const [steps, setSteps] = useState([])
  const [generating, setGenerating] = useState(false)
  const [busy, setBusy] = useState('')
  const [publicUrl, setPublicUrl] = useState('')

  useEffect(() => {
    portfolioService.templates().then(setTemplates)
    studentService.list().then(setStudents)
  }, [])

  const generate = async () => {
    if (!studentId) { toast.error('Please select a student first'); return }
    setGenerating(true)
    setSteps([])
    setPortfolio(null)
    setPublicUrl('')
    for (const step of GEN_STEPS) {
      setSteps((s) => [...s, step])
      await new Promise((r) => setTimeout(r, 240))
    }
    try {
      const res = await portfolioService.generate(studentId, templateId || null)
      setPortfolio(res.portfolio)
      setMissing(res.missing_required || [])
      toast.success('Portfolio generated successfully!')
    } catch (err) {
      toast.error(errorMessage(err, 'Generation failed'))
    } finally {
      setGenerating(false)
    }
  }

  const action = async (fn, label) => {
    if (!portfolio) return
    setBusy(label)
    try {
      await fn(portfolio.id)
      const fresh = await portfolioService.get(portfolio.id)
      setPortfolio(fresh)
      toast.success(`${label} done`)
      if (fresh.status === 'PUBLISHED') {
        const url = await portfolioService.publicUrl(fresh.id)
        setPublicUrl(url.public_url)
      }
    } catch (err) {
      toast.error(errorMessage(err, `${label} failed`))
    } finally {
      setBusy('')
    }
  }

  const downloadQr = async () => {
    try {
      const blob = await portfolioService.qr(portfolio.id)
      const url = window.URL.createObjectURL(blob.data || blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `portfolio-qr-${portfolio.slug}.png`
      a.click()
      toast.success('QR code downloaded')
    } catch (err) {
      toast.error('QR only available for published portfolios')
    }
  }

  return (
    <div>
      <div className="card">
        <div className="card-title"><h3>Portfolio Generator</h3></div>
        <div className="row">
          <select value={studentId} onChange={(e) => setStudentId(e.target.value)} style={{ flex: 1, padding: 10 }}>
            <option value="">— Search & Select Student —</option>
            {students.map((s) => <option key={s.id} value={s.id}>{s.name} ({s.register_number})</option>)}
          </select>
          <select value={templateId} onChange={(e) => setTemplateId(e.target.value)} style={{ flex: 1, padding: 10 }}>
            <option value="">Default Template</option>
            {templates.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
          </select>
          <button className="btn btn-primary" onClick={generate} disabled={generating}>
            {generating ? 'Generating…' : '⚙️ Generate Portfolio'}
          </button>
        </div>
        {generating && (
          <div className="mt card" style={{ background: '#0f172a', color: '#34d399', fontFamily: 'monospace', fontSize: 14 }}>
            {steps.map((s, i) => <div key={i}>{i === steps.length - 1 ? `${s} ✓` : s}</div>)}
          </div>
        )}
      </div>

      {portfolio && (
        <div className="card">
          <div className="row-between">
            <div className="row">
              <h3>{portfolio.student_name}'s Portfolio</h3>
              <StatusBadge status={portfolio.status} />
            </div>
            <div className="row">
              <button className="btn btn-primary btn-sm" onClick={() => navigate(`/portfolio/${portfolio.id}/preview`)}>👁️ Preview</button>
              <button className="btn btn-primary btn-sm" onClick={() => action(portfolioService.submit, 'Submit')} disabled={!!busy}>
                📤 Submit for Approval
              </button>
              <button className="btn btn-success btn-sm" onClick={() => action(portfolioService.publish, 'Publish')}
                      disabled={!!busy || portfolio.status !== 'APPROVED'}>
                🌐 Publish
              </button>
              <button className="btn btn-sm" onClick={downloadQr} disabled={portfolio.status !== 'PUBLISHED'}>
                🏷️ Download QR
              </button>
            </div>
          </div>
          {missing?.length > 0 && (
            <div className="mt">
              {missing.map((m) => <span key={m} className="badge badge-amber" style={{ margin: 3 }}>Missing: {m}</span>)}
            </div>
          )}
          {publicUrl && (
            <div className="row mt">
              <span className="badge badge-green">🔗 Public URL</span>
              <a href={publicUrl} target="_blank" rel="noreferrer">{publicUrl}</a>
            </div>
          )}
          <div className="mt" style={{ fontSize: 14 }}>
            <b>Profile completion:</b> {portfolio.completion_percentage}% &nbsp;·&nbsp;
            <b>Template:</b> {portfolio.template_name || 'Default'} &nbsp;·&nbsp;
            <b>Version:</b> {portfolio.versions?.[0]?.version_no || 1}
          </div>
        </div>
      )}
      {portfolio && <PortfolioPreview data={portfolio.data} />}
    </div>
  )
}
function PortfolioPreview({ data }) {
  if (!data) return <div className="empty">No portfolio data</div>
  const p = data.personal || {}
  const section = (label, children) => (
    <div style={{ marginTop: 20 }}>
      <div className="section-title">{label}</div>
      {children}
    </div>
  )
  return (
    <div className="card">
      <h3>Portfolio Preview</h3>
      <div style={{ border: '1px solid var(--border)', borderRadius: 12, overflow: 'hidden' }}>
        <div style={{ background: 'linear-gradient(135deg,#1e1b4b,#4f46e5)', color: '#fff', padding: 30, textAlign: 'center' }}>
          {p.profile_photo
            ? <img src={p.profile_photo} alt="" style={{ width: 88, height: 88, borderRadius: '50%', border: '3px solid #fff', objectFit: 'cover' }} />
            : <div style={{ width: 88, height: 88, borderRadius: '50%', background: 'rgba(255,255,255,0.2)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: 34 }}>{(p.name || '?')[0]}</div>}
          <h2 style={{ marginTop: 10 }}>{p.name}</h2>
          <div style={{ opacity: 0.9 }}>{p.department} · {data?.education?.[0]?.degree}</div>
          <div className="contact-bar">
            {p.email && <a href={`mailto:${p.email}`}>✉️ {p.email}</a>}
            {p.phone && <span>📞 {p.phone}</span>}
            {p.github_url && <a href={p.github_url} target="_blank" rel="noreferrer">GitHub</a>}
            {p.linkedin_url && <a href={p.linkedin_url} target="_blank" rel="noreferrer">LinkedIn</a>}
          </div>
        </div>
        <div style={{ padding: 24 }}>
          {p.professional_summary && <p className="muted">{p.professional_summary}</p>}
          {section('Education', (data.education || []).map((e) => (
            <div key={e.id} className="list-item"><div><b>{e.degree}</b><span className="muted"> · {e.college || ''}</span></div></div>
          )))}
          {section('Skills', (data.skills || []).map((s) => <span key={s.id} className="skill-chip">{s.name}</span>))}
          {section('Projects', (data.projects || []).map((pr) => (
            <div key={pr.id} className="list-item"><div><b>{pr.name}</b><div className="muted">{pr.description || ''}</div></div></div>
          )))}
          {section('Internships', (data.internships || []).map((i) => (
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
              <div><b>{f.teacher_name}</b><div className="muted">{f.academic_performance || f.communication || f.remarks}</div></div>
              <span className="badge badge-blue">Rating {f.overall_rating}/5</span>
            </div>
          )))}
          {section('Goals', (data.goals || []).map((g) => (
            <div key={g.id} className="list-item"><b>{g.title}</b><span className="badge badge-amber">{g.status.replace(/_/g, ' ')}</span></div>
          )))}
        </div>
      </div>
    </div>
  )
}

export default PortfolioGenerator