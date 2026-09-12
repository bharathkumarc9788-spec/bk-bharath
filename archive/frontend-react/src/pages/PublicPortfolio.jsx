import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { portfolioService } from '../services/portfolioService'
import { Loading } from '../components/Loading'

const fmtDate = (d) => (d ? new Date(d).toLocaleDateString('en-IN', { year: 'numeric', month: 'short' }) : '—')
const fmtLong = (d) => (d ? new Date(d).toLocaleString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : '—')

function PublicPortfolio() {
  const { slug } = useParams()
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    portfolioService.publicBySlug(slug)
      .then(setData)
      .catch((e) => setError(e.response?.data?.detail || 'Could not load portfolio'))
  }, [slug])

  if (error) return (
    <div className="login-page">
      <div className="login-card" style={{ textAlign: 'center' }}>
        <div style={{ fontSize: 42 }}>🔒</div>
        <h1>Portfolio not available</h1>
        <p className="sub">{error}</p>
      </div>
    </div>
  )
  if (!data) return <div className="public-shell"><Loading label="Opening public portfolio…" /></div>

  const p = data.personal || {}
  const completion = data.completion?.overall ?? 0

  const Blk = ({ label, children }) => (
    <div className="card">
      <div className="section-title">{label}</div>
      {children}
    </div>
  )

  return (
    <div className="public-shell">
      <div className="public-hero">
        {p.profile_photo
          ? <img className="avatar-lg" src={p.profile_photo} alt={p.name} />
          : <div className="avatar-lg" style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: 40 }}>{(p.name || '?')[0]}</div>}
        <h1 style={{ marginTop: 12, fontSize: 30 }}>{String(data.title || '').replace(' — Digital Portfolio', '') || p.name}</h1>
        <div style={{ opacity: 0.85, fontSize: 17 }}>{p.department}{data.education?.[0]?.degree ? ` · ${data.education[0].degree}` : ''}</div>
        {p.professional_summary && (
          <p style={{ maxWidth: 600, margin: '14px auto 0', opacity: 0.9, fontSize: 14 }}>{p.professional_summary}</p>
        )}
        <div className="contact-bar">
          {p.email && <a href={`mailto:${p.email}`}>✉️ {p.email}</a>}
          {p.phone && <span>📞 {p.phone}</span>}
          {p.github_url && <a href={p.github_url} target="_blank" rel="noreferrer">🐙 GitHub</a>}
          {p.linkedin_url && <a href={p.linkedin_url} target="_blank" rel="noreferrer">💼 LinkedIn</a>}
        </div>
        <div style={{ marginTop: 14, fontSize: 12.5, opacity: 0.7 }}>👁️ {data.views_count} views · Profile {completion}% complete</div>
      </div>

      <div className="public-body">
        <Blk label="About">
          <p className="muted" style={{ lineHeight: 1.7 }}>{p.professional_summary || 'No summary available.'}</p>
        </Blk>

        <Blk label="Education">
          {(data.education || []).map((e) => (
            <div key={e.id} className="list-item">
              <div>
                <b>{e.degree || 'Degree'}</b>
                <div className="muted">{e.college}</div>
                {e.history && <div className="muted mt">{e.history}</div>}
              </div>
              <div style={{ textAlign: 'right' }} className="muted">
                {e.cgpa && <div>CGPA {e.cgpa}</div>}
                {e.percentage && <div>{e.percentage}%</div>}
                {e.start_year && <div>{e.start_year} – {e.end_year}</div>}
              </div>
            </div>
          ))}
          {!data.education?.length && <div className="empty">No education</div>}
        </Blk>

        <Blk label="Skills">
          {(data.skills || []).map((s) => <span key={s.id} className="skill-chip">{s.name}</span>)}
          {!data.skills?.length && <div className="empty">No skills</div>}
        </Blk>

        <Blk label="Projects">
          {(data.projects || []).map((pr) => (
            <div key={pr.id} className="list-item">
              <div>
                <b>{pr.name}</b>
                {pr.student_role && <span className="muted"> · Role: {pr.student_role}</span>}
                <div className="muted mt">{pr.description || ''}</div>
                {pr.technologies && (
                  <div className="mt">{pr.technologies.split(',').map((t) => <span key={t.trim()} className="skill-chip">{t.trim()}</span>)}</div>
                )}
              </div>
              {pr.live_url && <a href={pr.live_url} target="_blank" rel="noreferrer">Live Demo ↗</a>}
            </div>
          ))}
          {!data.projects?.length && <div className="empty">No projects</div>}
        </Blk>

        <Blk label="Internship">
          {(data.internships || []).map((i) => (
            <div key={i.id} className="list-item">
              <div>
                <b>{i.role_name || 'Intern'} @ {i.company}</b>
                <div className="muted">{fmtDate(i.start_date)} → {fmtDate(i.end_date)}</div>
                <div className="muted mt">{i.description || i.responsibilities}</div>
              </div>
            </div>
          ))}
          {!data.internships?.length && <div className="empty">No internships</div>}
        </Blk>

        <Blk label="Certifications">
          {(data.certifications || []).map((c) => (
            <div key={c.id} className="list-item">
              <div>
                <b>{c.name}</b>
                <div className="muted">{c.issuing_organization} · {fmtDate(c.issue_date)}</div>
              </div>
              {c.url && <a href={c.url} target="_blank" rel="noreferrer">Verify ↗</a>}
            </div>
          ))}
          {!data.certifications?.length && <div className="empty">No certifications</div>}
        </Blk>

        <Blk label="Achievements">
          {(data.achievements || []).map((a) => (
            <div key={a.id} className="list-item">
              <div>
                <b>🏆 {a.title}</b>
                <div className="muted">{a.organization} · {fmtDate(a.date)}</div>
              </div>
              <span className="badge badge-violet">{a.level}</span>
            </div>
          ))}
          {!data.achievements?.length && <div className="empty">No achievements</div>}
        </Blk>

        <Blk label="Activities">
          {(data.activities || []).map((a) => (
            <div key={a.id} className="list-item">
              <div>
                <b>{a.title}</b>
                <div className="muted">{a.activity_type_display} · {a.organization}{a.role ? ` · ${a.role}` : ''}</div>
              </div>
            </div>
          ))}
          {!data.activities?.length && <div className="empty">No activities</div>}
        </Blk>

        <Blk label="360° Feedback">
          {(data.feedback_teacher || []).map((f) => (
            <div key={f.id} className="list-item">
              <div>
                <b>{f.teacher_name}</b> <span className="muted">· Teacher</span>
                <div className="muted mt">{f.academic_performance || f.communication || f.remarks}</div>
              </div>
              <span className="badge badge-blue">Rating {f.overall_rating}/5</span>
            </div>
          ))}
          {!data.feedback_teacher?.length && <div className="empty">No feedback yet</div>}
        </Blk>

        <Blk label="Goals">
          {(data.goals || []).map((g) => (
            <div key={g.id} className="list-item">
              <div>
                <b>{g.title}</b>
                <div className="muted">{g.description}</div>
              </div>
              <span className="badge badge-amber">{g.status.replace(/_/g, ' ')}</span>
            </div>
          ))}
          {!data.goals?.length && <div className="empty">No goals</div>}
        </Blk>

        <Blk label="Contact">
          <div className="row" style={{ gap: 12 }}>
            {p.email && <a href={`mailto:${p.email}`}>✉️ {p.email}</a>}
            {p.phone && <span>📞 {p.phone}</span>}
            {p.github_url && <a href={p.github_url} target="_blank" rel="noreferrer">🐙 GitHub</a>}
            {p.linkedin_url && <a href={p.linkedin_url} target="_blank" rel="noreferrer">💼 LinkedIn</a>}
          </div>
          {p.address && (
            <div className="muted mt">📍 {p.address}{p.city ? `, ${p.city}` : ''}{p.state ? `, ${p.state}` : ''}</div>
          )}
        </Blk>

        <div className="muted" style={{ textAlign: 'center', padding: '20px 0 40px', fontSize: 12.5 }}>
          Published {data.published_at ? fmtLong(data.published_at) : '—'} · Student Portfolio Automation System
        </div>
      </div>
    </div>
  )
}

export default PublicPortfolio