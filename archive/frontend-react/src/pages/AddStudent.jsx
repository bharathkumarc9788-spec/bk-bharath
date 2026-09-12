import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import studentService from '../services/studentService'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { Skeleton } from '../components/Loading'
import { errorMessage } from '../services/api'

const EMPTY = {
  register_number: '', name: '', student_id: '', admission_number: '',
  email: '', phone: '', gender: 'MALE', date_of_birth: '',
  address: '', city: '', state: '', department: '',
  github_url: '', linkedin_url: '', professional_summary: '',
}

const EMAIL_RE = /^\S+@\S+\.\S+$/
const URL_RE = /^https?:\/\//

export function validate(schema, form) {
  const errors = {}
  for (const f of schema) {
    const raw = form[f.key] || ''
    const v = typeof raw === 'string' ? raw.trim() : raw
    if (f.required && !v) { errors[f.key] = `${f.label} is required`; continue }
    if (!v) continue
    if (f.type === 'email' && !EMAIL_RE.test(v)) errors[f.key] = 'Enter a valid email'
    if (f.type === 'url' && !URL_RE.test(v)) errors[f.key] = 'Enter a valid URL (https://…)'
    if (f.type === 'number' && f.min && Number(v) < f.min) errors[f.key] = `Must be at least ${f.min}`
    if (f.type === 'number' && f.max && Number(v) > f.max) errors[f.key] = `Must be at most ${f.max}`
    if (f.key === 'cgpa' && v !== '' && (Number(v) < 0 || Number(v) > 10)) errors[f.key] = 'CGPA must be 0–10'
    if (f.key === 'percentage' && v !== '' && (Number(v) < 0 || Number(v) > 100)) errors[f.key] = 'Percentage must be 0–100'
  }
  return errors
}

const SCHEMAS = {
  education: [
    { key: 'college', label: 'College / School', required: true },
    { key: 'degree', label: 'Degree', required: true },
    { key: 'department', label: 'Department' },
    { key: 'academic_year', label: 'Academic Year' },
    { key: 'year_of_study', label: 'Year of Study' },
    { key: 'klass', label: 'Class' },
    { key: 'section', label: 'Section' },
    { key: 'board', label: 'Board' },
    { key: 'cgpa', label: 'CGPA', type: 'number', step: '0.01' },
    { key: 'percentage', label: 'Percentage', type: 'number', step: '0.01' },
    { key: 'start_year', label: 'Start Year' },
    { key: 'end_year', label: 'End Year' },
    { key: 'history', label: 'Academic History', type: 'textarea' },
  ],
  skills: [
    { key: 'name', label: 'Skill Name', required: true },
    { key: 'category', label: 'Category', type: 'select', options: ['PROGRAMMING', 'TECHNICAL', 'FRAMEWORK', 'DATABASE', 'CLOUD', 'TOOL', 'SOFT', 'OTHER'].map((c) => ({ value: c, label: c })) },
    { key: 'proficiency', label: 'Proficiency (1-5)', type: 'number', min: 1, max: 5 },
  ],
  projects: [
    { key: 'name', label: 'Project Name', required: true },
    { key: 'description', label: 'Description', type: 'textarea' },
    { key: 'problem_statement', label: 'Problem Statement', type: 'textarea' },
    { key: 'technologies', label: 'Technologies (comma separated)' },
    { key: 'student_role', label: 'Your Role' },
    { key: 'start_date', label: 'Start Date', type: 'date' },
    { key: 'end_date', label: 'End Date', type: 'date' },
    { key: 'github_url', label: 'GitHub URL', type: 'url' },
    { key: 'live_url', label: 'Live URL', type: 'url' },
    { key: 'key_features', label: 'Key Features', type: 'textarea' },
  ],
  internships: [
    { key: 'company', label: 'Company', required: true },
    { key: 'role_name', label: 'Role / Designation' },
    { key: 'start_date', label: 'Start Date', type: 'date' },
    { key: 'end_date', label: 'End Date', type: 'date' },
    { key: 'technologies', label: 'Technologies' },
    { key: 'responsibilities', label: 'Responsibilities', type: 'textarea' },
    { key: 'description', label: 'Description', type: 'textarea' },
  ],
  certifications: [
    { key: 'name', label: 'Certificate Name', required: true },
    { key: 'issuing_organization', label: 'Issuing Organization' },
    { key: 'issue_date', label: 'Issue Date', type: 'date' },
    { key: 'expiry_date', label: 'Expiry Date', type: 'date' },
    { key: 'credential_id', label: 'Credential ID' },
    { key: 'url', label: 'Certificate URL', type: 'url' },
  ],
  achievements: [
    { key: 'title', label: 'Achievement', required: true },
    { key: 'organization', label: 'Organization' },
    { key: 'date', label: 'Date', type: 'date' },
    { key: 'level', label: 'Level', type: 'select', options: ['COLLEGE', 'DISTRICT', 'STATE', 'NATIONAL', 'INTERNATIONAL'].map((l) => ({ value: l, label: l })) },
    { key: 'description', label: 'Description', type: 'textarea' },
  ],
  activities: [
    { key: 'title', label: 'Title', required: true },
    { key: 'activity_type', label: 'Type', type: 'select', options: ['HACKATHON', 'WORKSHOP', 'SEMINAR', 'CLUB', 'VOLUNTEERING', 'COMPETITION', 'EVENT', 'CO_CURRICULAR', 'SPORTS', 'OTHER'].map((t) => ({ value: t, label: t })) },
    { key: 'organization', label: 'Organization' },
    { key: 'role', label: 'Your Role' },
    { key: 'date', label: 'Date', type: 'date' },
    { key: 'description', label: 'Description', type: 'textarea' },
  ],
  goals: [
    { key: 'title', label: 'Goal', required: true },
    { key: 'category', label: 'Category', type: 'select', options: [{ value: 'SHORT_TERM', label: 'Short Term' }, { value: 'LONG_TERM', label: 'Long Term' }] },
    { key: 'target_date', label: 'Target Date', type: 'date' },
    { key: 'status', label: 'Status', type: 'select', options: [{ value: 'NOT_STARTED', label: 'Not Started' }, { value: 'IN_PROGRESS', label: 'In Progress' }, { value: 'ACHIEVED', label: 'Achieved' }] },
    { key: 'description', label: 'Description', type: 'textarea' },
  ],
}
function F({ f, value, onChange, errors }) {
  const label = f.label
  const err = errors?.[f.key]
  if (f.type === 'textarea') {
    return (
      <div className="form-group">
        <label>{label}{f.required ? ' *' : ''}</label>
        <textarea value={value || ''} onChange={(e) => onChange(f.key, e.target.value)} />
        {err && <div className="field-error">⚠ {err}</div>}
      </div>
    )
  }
  if (f.type === 'select') {
    return (
      <div className="form-group">
        <label>{label}{f.required ? ' *' : ''}</label>
        <select value={value || ''} onChange={(e) => onChange(f.key, e.target.value)}>
          <option value="">— Select —</option>
          {(f.options || []).map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
        {err && <div className="field-error">⚠ {err}</div>}
      </div>
    )
  }
  return (
    <div className="form-group">
      <label>{label}{f.required ? ' *' : ''}</label>
      <input type={f.type || 'text'} step={f.step} placeholder={f.placeholder || ''} value={value || ''} onChange={(e) => onChange(f.key, e.target.value)} min={f.min} max={f.max} />
      {err && <div className="field-error">⚠ {err}</div>}
    </div>
  )
}

const STEP_ORDER = ['personal', 'education', 'skills', 'projects', 'internships', 'certifications', 'achievements', 'activities', 'goals', 'review']

function SectionCollector({ section, title, onData }) {
  // Collects multiple rows for a section before moving on.
  const toast = useToast()
  const [rows, setRows] = useState([])
  const [form, setForm] = useState({})
  const [errors, setErrors] = useState({})
  const [open, setOpen] = useState(true)
  const schema = SCHEMAS[section]

  const add = () => {
    const errs = validate(schema, form)
    setErrors(errs)
    if (Object.keys(errs).length) { toast.error('Please fix the highlighted fields'); return }
    // convert empties → nulls so API doesn't complain
    const clean = {}
    for (const f of schema) clean[f.key] = (form[f.key] || '').trim() || null
    setRows([...rows, clean])
    setForm({})
  }
  useEffect(() => { onData(section, rows) }, [rows])

  return (
    <div>
      <h4 style={{ marginBottom: 6 }}>{title}</h4>
      <div className="row-between">
        {rows.length
          ? <span className="badge badge-green">✓ {rows.length} record(s)</span>
          : <span className="muted">No records yet</span>}
        <button className="btn btn-primary btn-sm" onClick={add}>+ Add</button>
      </div>
      {open && (
        <div className="mt form-grid">
          {schema.map((f) => <F key={f.key} f={f} value={form[f.key]} onChange={(k, v) => setForm({ ...form, [k]: v })} errors={errors} />)}
        </div>
      )}
      <div className="mt">
        {rows.map((r, i) => (
          <div key={i} className="badge badge-blue" style={{ margin: 3, padding: '6px 10px' }}>
            {schema.find((f) => f.key === 'name' || f.key === 'title' || f.key === 'company' || f.key === 'college')?.key
              ? (r[schema.find((f) => f.key === 'name' || f.key === 'title' || f.key === 'company' || f.key === 'college').key] || `Row ${i + 1}`)
              : `Row ${i + 1}`}
            <button className="btn btn-sm" style={{ marginLeft: 6, padding: '0 5px' }} onClick={() => setRows(rows.filter((_, j) => j !== i))}>✕</button>
          </div>
        ))}
      </div>
    </div>
  )
}
function AddStudent() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const toast = useToast()
  const [step, setStep] = useState(0)
  const [form, setForm] = useState(EMPTY)
  const [errors, setErrors] = useState({})
  const [busy, setBusy] = useState(false)
  const [sectionData, setSectionData] = useState({})
  const [createdId, setCreatedId] = useState(null)

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })

  const PERSONAL_FIELDS = [
    ['register_number', 'Register Number', 'text', true],
    ['name', 'Full Name', 'text', true],
    ['student_id', 'Student ID', null, false],
    ['admission_number', 'Admission Number', null, false],
    ['email', 'Email', 'email', false],
    ['phone', 'Phone', null, false],
    ['gender', 'Gender', 'select', false],
    ['date_of_birth', 'Date of Birth', 'date', false],
    ['department', 'Department', null, false],
    ['address', 'Address', null, false],
    ['city', 'City', null, false],
    ['state', 'State', null, false],
    ['github_url', 'GitHub URL', 'url', false],
    ['linkedin_url', 'LinkedIn URL', 'url', false],
    ['professional_summary', 'Professional Summary', 'textarea', false],
  ]

  const goNext = () => {
    if (step === 0) {
      const errs = {}
      if (!form.register_number.trim()) errs.register_number = 'Register number is required'
      if (!form.name.trim()) errs.name = 'Full name is required'
      if (form.email.trim() && !EMAIL_RE.test(form.email.trim())) errs.email = 'Enter a valid email'
      if (form.github_url.trim() && !URL_RE.test(form.github_url.trim())) errs.github_url = 'Enter a valid URL'
      if (form.linkedin_url.trim() && !URL_RE.test(form.linkedin_url.trim())) errs.linkedin_url = 'Enter a valid URL'
      setErrors(errs)
      if (Object.keys(errs).length) { toast.error('Please fix the highlighted fields'); return }
    }
    setErrors({})
    setStep(Math.min(step + 1, STEP_ORDER.length - 1))
  }

  const saveAll = async () => {
    setBusy(true)
    try {
      let student
      try {
        student = await studentService.create(form)
      } catch (err) {
        toast.error(errorMessage(err, 'Could not create student — check register number is unique'))
        setBusy(false)
        setStep(0)
        return
      }
      setCreatedId(student.id)
      for (const [section, rows] of Object.entries(sectionData)) {
        const api = studentService.sections(student.id)[section]
        for (const row of rows) {
          try { await api.create(row) } catch (e) { /* best-effort */ }
        }
      }
      toast.success(`Student ${student.name} created with ${Object.values(sectionData).reduce((a, b) => a + b.length, 0)} section record(s)!`)
      navigate(`/students/${student.id}`)
    } finally {
      setBusy(false)
    }
  }

  const pct = Math.round(((step + 1) / STEP_ORDER.length) * 100)
return (
    <div>
      <div className="card">
        <div className="card-title">
          <h3>Add New Student (multi-step)</h3>
          <button className="btn btn-sm" onClick={() => navigate('/students')}>← Back</button>
        </div>
        <div className="step-progress">
          <div className="muted" style={{ fontSize: 13 }}>Step {step + 1} of {STEP_ORDER.length} · {STEP_ORDER[step].replace('_', ' ')}</div>
          <div className="progress-bar" style={{ width: '100%', marginLeft: 10 }}>
            <div className="progress-fill" style={{ width: `${pct}%` }} />
          </div>
          <span className="muted" style={{ fontSize: 12.5, minWidth: 42 }}>{pct}%</span>
        </div>
      </div>

      <div className="card">
        {step === 0 && (
          <div className="form-grid">
            {PERSONAL_FIELDS.map(([key, label, type, required]) => (
              <div className="form-group" key={key} style={type === 'textarea' ? { gridColumn: '1 / -1' } : undefined}>
                <label>{label}{required ? ' *' : ''}</label>
                {type === 'textarea'
                  ? <textarea value={form[key]} onChange={set(key)} />
                  : type === 'select'
                    ? <select value={form[key]} onChange={set(key)}>
                        <option value="MALE">Male</option>
                        <option value="FEMALE">Female</option>
                        <option value="OTHER">Other</option>
                      </select>
                    : <input type={type || 'text'} value={form[key]} onChange={set(key)} />}
                {errors[key] && <div className="field-error">⚠ {errors[key]}</div>}
              </div>
            ))}
          </div>
        )}

        {step === 1 && <SectionCollector section="education" title="Education" onData={(s, d) => setSectionData({ ...sectionData, [s]: d })} />}
        {step === 2 && <SectionCollector section="skills" title="Skills" onData={(s, d) => setSectionData({ ...sectionData, [s]: d })} />}
        {step === 3 && <SectionCollector section="projects" title="Projects" onData={(s, d) => setSectionData({ ...sectionData, [s]: d })} />}
        {step === 4 && <SectionCollector section="internships" title="Internship" onData={(s, d) => setSectionData({ ...sectionData, [s]: d })} />}
        {step === 5 && <SectionCollector section="certifications" title="Certifications" onData={(s, d) => setSectionData({ ...sectionData, [s]: d })} />}
        {step === 6 && <SectionCollector section="achievements" title="Achievements" onData={(s, d) => setSectionData({ ...sectionData, [s]: d })} />}
        {step === 7 && <SectionCollector section="activities" title="Activities" onData={(s, d) => setSectionData({ ...sectionData, [s]: d })} />}
        {step === 8 && <SectionCollector section="goals" title="Goals" onData={(s, d) => setSectionData({ ...sectionData, [s]: d })} />}

        {step === 9 && (
          <div>
            <h4>Review & Save</h4>
            <div className="grid-2">
              <div className="card" style={{ padding: 14 }}><b>{form.name || '—'}</b><div className="muted">{form.register_number}</div></div>
              <div className="card" style={{ padding: 14 }}><b>{form.department || '—'}</b><div className="muted">{form.email || '—'}</div></div>
            </div>
            <div className="mt">
              {Object.keys(sectionData).map((s) => (
                <span key={s} className="badge badge-green" style={{ margin: 3 }}>
                  {s}: {sectionData[s].length} record(s)
                </span>
              ))}
              {!Object.keys(sectionData).length && <span className="badge badge-gray">No section records yet — you can add them later from the profile.</span>}
            </div>
          </div>
        )}

        <div className="row mt">
          <button className="btn" disabled={step === 0} onClick={() => setStep(step - 1)}>← Back</button>
          {step < STEP_ORDER.length - 1
            ? <button className="btn btn-primary" onClick={goNext}>Save & Continue →</button>
            : <button className="btn btn-success" disabled={busy} onClick={saveAll}>
                {busy ? 'Saving student…' : '✔ Save Student & Sections'}
              </button>}
        </div>
      </div>
    </div>
  )
}

export default AddStudent
const L = (key, label, type, extra) => ({ key, label, ...(type ? { type } : {}), ...(extra || {}) })