import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { portfolioService } from '../services/portfolioService'
import { Skeleton } from '../components/Loading'
import { useToast } from '../context/ToastContext'

const TEMPLATE_PALETTES = {
  navy: { bg: 'linear-gradient(135deg, #1e293b, #334155)', color: '#fff' },
  indigo: { bg: 'linear-gradient(135deg, #312e81, #4f46e5)', color: '#fff' },
  dark: { bg: 'linear-gradient(135deg, #0a0a0a, #1f2937)', color: '#34d399' },
  violet: { bg: 'linear-gradient(135deg, #4c1d95, #7c3aed)', color: '#fff' },
  gray: { bg: 'linear-gradient(135deg, #475569, #64748b)', color: '#fff' },
}

function PortfolioTemplates() {
  const navigate = useNavigate()
  const toast = useToast()
  const [templates, setTemplates] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    portfolioService.templates().then((t) => { setTemplates(t); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  const pick = (t) => {
    toast.success(`Template "${t.name}" selected — use it in the generator!`)
    navigate(`/portfolio/generator?template=${t.id}`)
  }

  if (loading) return <Skeleton rows={3} />
  return (
    <div>
      <div className="card">
        <h3>Portfolio Templates</h3>
        <p className="muted">Choose a template to shape your portfolio's look &amp; feel. Select one and it will be pre-loaded in the generator.</p>
        <div className="grid-3">
          {templates.map((t) => {
            const palette = TEMPLATE_PALETTES[t.color_scheme] || TEMPLATE_PALETTES.indigo
            return (
              <div key={t.id} className="card" style={{ padding: 0, overflow: 'hidden' }}>
                <div style={{ ...palette, padding: 40, textAlign: 'center' }}>
                  <div style={{ fontSize: 30 }}>{t.name === 'Developer' ? '👨‍💻' : t.name === 'Creative' ? '🎨' : t.name === 'Minimal' ? '⬜' : t.name === 'Modern' ? '✨' : '💼'}</div>
                  <h3 style={{ marginTop: 8, color: palette.color === '#fff' ? '#fff' : '#0f172a' }}>{t.name}</h3>
                  {t.is_default && <span className="badge badge-green">Default</span>}
                </div>
                <div style={{ padding: 16 }}>
                  <p className="muted" style={{ fontSize: 13 }}>{t.description || 'Custom portfolio template.'}</p>
                  <div className="muted" style={{ fontSize: 12, marginBottom: 10 }}>
                    Font: {t.font} · {t.layout}
                  </div>
                  <button className="btn btn-primary btn-sm" onClick={() => pick(t)}>Use Template</button>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default PortfolioTemplates