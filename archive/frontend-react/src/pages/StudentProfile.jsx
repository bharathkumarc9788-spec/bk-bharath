import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import studentService from '../services/studentService'
import { useToast } from '../context/ToastContext'
import { useAuth } from '../context/AuthContext'
import { Loading, ProgressBar } from '../components/Index'

/* ---------- small building blocks ---------- */

function Field({ f, value, onChange }) {
  const label = f.label || f.key.replace(/_/g, ' ')
  if (f.type === 'textarea') {
    return (
      <div className="form-group">
        <label>{label}</label>
        <textarea value={value || ''} onChange={(e) => onChange(f.key, e.target.value)} />
      </div>
    )
  }
  if (f.type === 'select') {
    return (
      <div className="form-group">
        <label>{label}</label>
        <select value={value || ''} onChange={(e) => onChange(f.key, e.target.value)}>
          <option value="">— Select —</option>
          {(f.options || []).map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>
    )
  }
  return (
    <div className="form-group">
      <label>{label}</label>
      <input type={f.type || 'text'} placeholder={f.placeholder || ''}
             value={value || ''} onChange={(e) => onChange(f.key, e.target.value)} />
    </div>
  )
}

function ItemList({ items, render, onDelete }) {
  if (!items?.length) return <div className="empty"><div className="big">📭</div>Nothing added yet</div>
  return (
    <div>
      {items.map((item) => (
        <div key={item.id} className="list-item">
          <div style={{ flex: 1 }}>{render(item)}</div>
          <button className="btn btn-sm btn-danger" onClick={() => onDelete(item)}>✕</button>
        </div>
      ))}
    </div>
  )
}

function SectionForm({ schema, onSubmit, onCancel }) {
  const [form, setForm] = useState({})
  return (
    <form onSubmit={(e) => { e.preventDefault(); onSubmit(form) }}
          style={{ border: '1px dashed var(--border)', borderRadius: 12, padding: 16, marginBottom: 14, background: '#f8fafc' }}>
      <div className="form-grid">
        {schema.map((f) => <Field key={f.key} f={f} value={form[f.key]} onChange={(k, v) => setForm({ ...form, [k]: v })} />)}
      </div>
      <div className="row mt">
        <button className="btn btn-primary btn-sm" type="submit">Add</button>
        <button className="btn btn-sm" type="button" onClick={onCancel}>Cancel</button>
      </div>
    </form>
  )
}

function SectionManager({ api, schema, render, addLabel }) {
  const toast = useToast()
  const [items, setItems] = useState([])
  const [open, setOpen] = useState(false)
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    api.list().then((d) => { setItems(d); setLoaded(true) }).catch(() => setLoaded(true))
  }, [api])

  const add = async (form) => {
    try {
      const created = await api.create(form)
      setItems([created, ...items])
      setOpen(false)
      toast.success('Added successfully')
    } catch (err) {
      toast.error(err.response?.data ? Object.values(err.response.data)[0]?.[0] : 'Failed to add')
    }
  }

  const remove = async (item) => {
    if (!window.confirm('Delete this entry?')) return
    try {
      await api.remove(item.id)
      setItems(items.filter((i) => i.id !== item.id))
      toast.success('Deleted')
    } catch (err) {
      toast.error('Failed to delete')
    }
  }

  if (!loaded) return <Loading label="Loading…" />
  return (
    <div>
      <div className="row-between mb">
        <h4 style={{ color: 'var(--muted)', fontSize: 14 }}>{items.length} record(s)</h4>
        <button className="btn btn-primary btn-sm" onClick={() => setOpen(!open)}>+ {addLabel}</button>
      </div>
      {open && <SectionForm schema={schema} onSubmit={add} onCancel={() => setOpen(false)} />}
      <ItemList items={items} render={render} onDelete={remove} />
    </div>
  )
}
/* ---------- section schemas ---------- */
const SKILL_CATEGORIES = ['PROGRAMMING', 'TECHNICAL', 'FRAMEWORK', 'DATABASE', 'CLOUD', 'TOOL', 'SOFT', 'OTHER']
const ACTIVITY_TYPES = ['HACKATHON', 'WORKSHOP', 'SEMINAR', 'CLUB', 'VOLUNTEERING', 'COMPETITION', 'EVENT', 'CO_CURRICULAR', 'SPORTS', 'OTHER']

const EDUCATION_SCHEMA = [
  { key: 'college', label: 'College / School' }, { key: 'degree', label: 'Degree' },
  { key: 'department', label: 'Department' }, { key: 'academic_year', label: 'Academic Year' },
  { key: 'year_of_study', label: 'Year of Study' }, { key: 'klass', label: 'Class' },
  { key: 'section', label: 'Section' }, { key: 'board', label: 'Board' },
  { key: 'cgpa', label: 'CGPA', type: 'number', step: '0.01' },
  { key: 'percentage', label: 'Percentage', type: 'number', step: '0.01' },
  { key: 'start_year', label: 'Start Year' }, { key: 'end_year', label: 'End Year' },
  { key: 'history', label: 'Academic History', type: 'textarea' },
]

const SKILL_SCHEMA = [
  { key: 'name', label: 'Skill Name' },
  { key: 'category', label: 'Category', type: 'select', options: SKILL_CATEGORIES.map((c) => ({ value: c, label: c })) },
  { key: 'proficiency', label: 'Proficiency (1-5)', type: 'number' },
]

const PROJECT_SCHEMA = [
  { key: 'name', label: 'Project Name' }, { key: 'description', label: 'Description', type: 'textarea' },
  { key: 'problem_statement', label: 'Problem Statement', type: 'textarea' },
  { key: 'technologies', label: 'Technologies (comma separated)' }, { key: 'student_role', label: 'Your Role' },
  { key: 'start_date', label: 'Start Date', type: 'date' }, { key: 'end_date', label: 'End Date', type: 'date' },
  { key: 'github_url', label: 'GitHub URL', type: 'url' }, { key: 'live_url', label: 'Live URL', type: 'url' },
  { key: 'key_features', label: 'Key Features', type: 'textarea' },
]

const INTERNSHIP_SCHEMA = [
  { key: 'company', label: 'Company' }, { key: 'role_name', label: 'Role / Designation' },
  { key: 'start_date', label: 'Start Date', type: 'date' }, { key: 'end_date', label: 'End Date', type: 'date' },
  { key: 'technologies', label: 'Technologies' },
  { key: 'responsibilities', label: 'Responsibilities', type: 'textarea' },
  { key: 'description', label: 'Description', type: 'textarea' },
]

const CERTIFICATION_SCHEMA = [
  { key: 'name', label: 'Certificate Name' }, { key: 'issuing_organization', label: 'Issuing Organization' },
  { key: 'issue_date', label: 'Issue Date', type: 'date' }, { key: 'expiry_date', label: 'Expiry Date', type: 'date' },
  { key: 'credential_id', label: 'Credential ID' }, { key: 'url', label: 'Certificate URL', type: 'url' },
]

const ACHIEVEMENT_SCHEMA = [
  { key: 'title', label: 'Achievement' }, { key: 'organization', label: 'Organization' },
  { key: 'date', label: 'Date', type: 'date' },
  { key: 'level', label: 'Level', type: 'select', options: ['COLLEGE', 'DISTRICT', 'STATE', 'NATIONAL', 'INTERNATIONAL'].map((l) => ({ value: l, label: l })) },
  { key: 'description', label: 'Description', type: 'textarea' },
]

const ACTIVITY_SCHEMA = [
  { key: 'title', label: 'Title' },
  { key: 'activity_type', label: 'Type', type: 'select', options: ACTIVITY_TYPES.map((t) => ({ value: t, label: t })) },
  { key: 'organization', label: 'Organization' }, { key: 'role', label: 'Your Role' },
  { key: 'date', label: 'Date', type: 'date' }, { key: 'description', label: 'Description', type: 'textarea' },
]

const GOAL_SCHEMA = [
  { key: 'title', label: 'Goal' },
  { key: 'category', label: 'Category', type: 'select', options: [{ value: 'SHORT_TERM', label: 'Short Term' }, { value: 'LONG_TERM', label: 'Long Term' }] },
  { key: 'target_date', label: 'Target Date', type: 'date' },
  { key: 'status', label: 'Status', type: 'select', options: [{ value: 'NOT_STARTED', label: 'Not Started' }, { value: 'IN_PROGRESS', label: 'In Progress' }, { value: 'ACHIEVED', label: 'Achieved' }] },
  { key: 'description', label: 'Description', type: 'textarea' },
]

const FEEDBACK_SCHEMA = [
  { key: 'academic_performance', label: 'Academic Performance', type: 'textarea' },
  { key: 'behaviour', label: 'Behaviour', type: 'select', options: ['Excellent', 'Good', 'Average', 'Poor'].map((x) => ({ value: x, label: x })) },
  { key: 'communication', label: 'Communication Evaluation', type: 'textarea' },
  { key: 'leadership', label: 'Leadership Evaluation', type: 'textarea' },
  { key: 'creativity', label: 'Creativity', type: 'textarea' },
  { key: 'sports_pet', label: 'Sports / PET', type: 'textarea' },
  { key: 'participation', label: 'Participation / Activities', type: 'textarea' },
  { key: 'overall_rating', label: 'Rating (1-5)', type: 'number' },
  { key: 'remarks', label: 'Remarks', type: 'textarea' },
]

/* ---------- render helpers ---------- */
const fmtDate = (d) => (d ? new Date(d).toLocaleDateString('en-IN', { year: 'numeric', month: 'short' }) : '—')
const TABS = [
  ['overview', 'Overview'], ['personal', 'Personal'], ['education', 'Education'],
  ['skills', 'Skills'], ['projects', 'Projects'], ['internships', 'Internships'],
  ['certifications', 'Certifications'], ['achievements', 'Achievements'],
  ['activities', 'Activities'], ['feedback', '360° Feedback'], ['goals', 'Goals'],
  ['completion', 'Completion'],
]

function TeacherFeedbackView({ api }) {
  const [feedbacks, setFeedbacks] = useState([])
  const [loaded, setLoaded] = useState(false)
  useEffect(() => {
    api().then((d) => { setFeedbacks(d); setLoaded(true) }).catch(() => setLoaded(true))
  }, [api])
  if (!loaded) return <Loading label="Loading feedback…" />
  if (!feedbacks.length) return <div className="empty"><div className="big">💬</div>No teacher feedback yet</div>
  return (
    <div>
      {feedbacks.map((f) => (
        <div key={f.id} className="list-item" style={{ display: 'block' }}>
          <div className="row-between">
            <b>{f.teacher_name}</b>
            <span className="badge badge-blue">Rating {f.overall_rating}/5</span>
          </div>
          {f.academic_performance && <p className="muted mt" style={{ marginBottom: 4 }}>📘 {f.academic_performance}</p>}
          {f.behaviour && <p className="muted" style={{ marginBottom: 4 }}>🎯 Behaviour: {f.behaviour}</p>}
          {f.communication && <p className="muted" style={{ marginBottom: 4 }}>🗣️ {f.communication}</p>}
          {f.leadership && <p className="muted" style={{ marginBottom: 4 }}>👥 {f.leadership}</p>}
          {f.creativity && <p className="muted" style={{ marginBottom: 4 }}>💡 {f.creativity}</p>}
          {f.remarks && <p className="mt"><b>Remarks:</b> {f.remarks}</p>}
        </div>
      ))}
    </div>
  )
}

function FeedbackForm({ studentId, onSaved }) {
  const toast = useToast()
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState({})
  const save = async () => {
    try {
      await studentService.sections(studentId).feedback.createTeacher(form)
      setOpen(false)
      onSaved()
    } catch (err) {
      toast.error(err.response?.data ? Object.values(err.response.data)[0]?.[0] : 'Failed to save')
    }
  }
  return (
    <div className="mb">
      <button className="btn btn-primary btn-sm" onClick={() => setOpen(!open)}>+ Add Teacher Feedback</button>
      {open && (
        <form onSubmit={(e) => { e.preventDefault(); save() }} style={{ border: '1px dashed var(--border)', borderRadius: 12, padding: 16, marginTop: 12, background: '#f8fafc' }}>
          <div className="form-grid">
            {FEEDBACK_SCHEMA.map((f) => <Field key={f.key} f={f} value={form[f.key]} onChange={(k, v) => setForm({ ...form, [k]: v })} />)}
          </div>
          <div className="row mt">
            <button className="btn btn-primary btn-sm" type="submit">Save Feedback</button>
            <button className="btn btn-sm" type="button" onClick={() => setOpen(false)}>Cancel</button>
          </div>
        </form>
      )}
    </div>
  )
}
/* ---------- main page ---------- */
function StudentProfile() {
  const { id } = useParams()
  const navigate = useNavigate()
  const toast = useToast()
  const { user } = useAuth()
  const [student, setStudent] = useState(null)
  const [tab, setTab] = useState('overview')
  const [savingPersonal, setSavingPersonal] = useState(false)
  const [personal, setPersonal] = useState({})

  const canEdit = user?.role === 'HR' || (user?.role === 'STUDENT' && student?.user_id === user?.id)
  const sections = id ? studentService.sections(id) : null

  useEffect(() => {
    studentService.get(id).then((s) => {
      setStudent(s)
      setPersonal({
        name: s.name, register_number: s.register_number, student_id: s.student_id,
        admission_number: s.admission_number, email: s.email, phone: s.phone,
        gender: s.gender, date_of_birth: s.date_of_birth, department: s.department,
        address: s.address, city: s.city, state: s.state,
        github_url: s.github_url, linkedin_url: s.linkedin_url,
        professional_summary: s.professional_summary,
      })
    }).catch(() => toast.error('Student not found'))
  }, [id])

  const savePersonal = async () => {
    setSavingPersonal(true)
    try {
      const updated = await studentService.update(id, personal)
      setStudent({ ...student, ...updated })
      toast.success('Personal information saved')
    } catch (err) {
      toast.error('Could not save — check required fields')
    } finally {
      setSavingPersonal(false)
    }
  }

  if (!student) return <Loading label="Loading profile…" />
  const completion = student.completion_overview?.overall ?? 0

  return (
    <div>
      <div className="card" style={{ display: 'flex', gap: 18, alignItems: 'center', flexWrap: 'wrap' }}>
        {student.profile_photo
          ? <img className="avatar-sm" src={student.profile_photo} alt={student.name} style={{ width: 72, height: 72, borderRadius: '50%', objectFit: 'cover' }} />
          : <div style={{ width: 72, height: 72, borderRadius: '50%', background: 'var(--primary-light)', color: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 28 }}>{student.name?.[0]}</div>}
        <div style={{ flex: 1 }}>
          <div className="row-between">
            <div>
              <h2 style={{ fontSize: 22 }}>{student.name}</h2>
              <div className="muted">{student.register_number} · {student.department || 'No department'} · {student.email}</div>
            </div>
            <div className="row">
              <button className="btn btn-primary btn-sm" onClick={() => navigate(`/portfolio/generator?student=${student.id}`)}>🔗 Portfolio</button>
              <button className="btn btn-sm" onClick={() => navigate(-1)}>← Back</button>
            </div>
          </div>
          <div className="mt row">
            <div style={{ width: 200 }}><ProgressBar percent={completion} /></div>
            <span className="muted" style={{ fontSize: 13 }}>Profile completion</span>
          </div>
        </div>
      </div>

      <div className="tabs">
        {TABS.map(([key, label]) => (
          <button key={key} className={`tab-btn ${tab === key ? 'active' : ''}`} onClick={() => setTab(key)}>
            {label}
          </button>
        ))}
      </div>

      <div className="card">
        {tab === 'overview' && <OverviewTab student={student} completion={completion} />}
        {tab === 'personal' && <PersonalTab personal={personal} setPersonal={setPersonal} canEdit={canEdit} saving={savingPersonal} onSave={savePersonal} />}
{tab === 'education' && sections && (
          <SectionManager api={sections.education} schema={EDUCATION_SCHEMA} addLabel="Add Education"
            render={(e) => (
              <div>
                <h4>{e.degree || 'Degree not set'}</h4>
                <span className="muted">{e.college} · {e.year_of_study ? `Year ${e.year_of_study}` : ''} {e.cgpa ? `· CGPA ${e.cgpa}` : ''} {e.percentage ? `· ${e.percentage}%` : ''}</span>
              </div>
            )} />
        )}
        {tab === 'skills' && sections && (
          <SectionManager api={sections.skills} schema={SKILL_SCHEMA} addLabel="Add Skill"
            render={(s) => (
              <div className="row-between">
                <b>{s.name}</b>
                <div className="row"><span className="badge badge-blue">{s.category}</span><span className="muted">Level {s.proficiency}/5</span></div>
              </div>
            )} />
        )}
        {tab === 'projects' && sections && (
          <SectionManager api={sections.projects} schema={PROJECT_SCHEMA} addLabel="Add Project"
            render={(p) => (
              <div>
                <h4>{p.name}</h4>
                <div className="muted">{p.description || 'No description'}</div>
                {p.technologies && <div className="mt">{p.technologies.split(',').map((t) => <span key={t} className="skill-chip">{t.trim()}</span>)}</div>}
                <div className="row mt muted" style={{ fontSize: 13 }}>
                  <span>{p.student_role ? `Role: ${p.student_role}` : ''}</span>
                  {p.github_url && <a href={p.github_url} target="_blank" rel="noreferrer">GitHub</a>}
                  {p.live_url && <a href={p.live_url} target="_blank" rel="noreferrer">Live</a>}
                </div>
              </div>
            )} />
        )}
        {tab === 'internships' && sections && (
          <SectionManager api={sections.internships} schema={INTERNSHIP_SCHEMA} addLabel="Add Internship"
            render={(i) => (
              <div>
                <h4>{i.role_name || 'Intern'} @ {i.company}</h4>
                <div className="muted">{fmtDate(i.start_date)} → {fmtDate(i.end_date)}</div>
                <div className="muted">{i.description || i.responsibilities}</div>
              </div>
            )} />
        )}
        {tab === 'certifications' && sections && (
          <SectionManager api={sections.certifications} schema={CERTIFICATION_SCHEMA} addLabel="Add Certification"
            render={(c) => (
              <div>
                <h4>{c.name}</h4>
                <div className="muted">{c.issuing_organization} · {fmtDate(c.issue_date)}</div>
                {c.credential_id && <div className="muted">Credential: {c.credential_id}</div>}
                {c.url && <a href={c.url} target="_blank" rel="noreferrer">Verify →</a>}
              </div>
            )} />
        )}
        {tab === 'achievements' && sections && (
          <SectionManager api={sections.achievements} schema={ACHIEVEMENT_SCHEMA} addLabel="Add Achievement"
            render={(a) => (
              <div className="row-between">
                <div>
                  <h4>{a.title}</h4>
                  <div className="muted">{a.organization} · {fmtDate(a.date)}</div>
                  {a.description && <div className="muted mt">{a.description}</div>}
                </div>
                <span className="badge badge-violet">{a.level}</span>
              </div>
            )} />
        )}
{tab === 'activities' && sections && (
          <SectionManager api={sections.activities} schema={ACTIVITY_SCHEMA} addLabel="Add Activity"
            render={(a) => (
              <div className="row-between">
                <div>
                  <h4>{a.title}</h4>
                  <div className="muted">{a.activity_type_display || a.activity_type} · {a.organization || ''} {a.role ? `· ${a.role}` : ''} · {fmtDate(a.date)}</div>
                </div>
              </div>
            )} />
        )}
        {tab === 'feedback' && sections && (
          <div>
            <h3 className="mb">360° Teacher Feedback</h3>
            {(user?.role === 'TEACHER' || user?.role === 'HR') && (
              <FeedbackForm studentId={id} onSaved={() => toast.success('Feedback saved')} />
            )}
            <TeacherFeedbackView api={sections.feedback.teacher} />
          </div>
        )}
        {tab === 'goals' && sections && (
          <SectionManager api={sections.goals} schema={GOAL_SCHEMA} addLabel="Add Goal"
            render={(g) => (
              <div className="row-between">
                <div>
                  <h4>{g.title}</h4>
                  <div className="muted">{g.description} · Target {fmtDate(g.target_date)}</div>
                </div>
                <span className="badge badge-amber">{g.status.replace(/_/g, ' ')}</span>
              </div>
            )} />
        )}
        {tab === 'completion' && (
          <div>
            <h3 className="mb">Profile Completion</h3>
            <div className="mb" style={{ maxWidth: 420 }}><ProgressBar percent={completion} /></div>
            {(student.completion_overview?.sections || []).map((s) => (
              <div key={s.section} className="completion-row">
                <span className="section-name">{s.section}</span>
                <div className="bar"><ProgressBar percent={s.percent} /></div>
                <span className="muted" style={{ fontSize: 12 }}>
                  {s.percent >= 100 ? '✓ Complete' : (s.count ?? '')}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function OverviewTab({ student, completion }) {
  return (
    <div>
      <h3 className="mb">Summary</h3>
      <p className="muted">{student.professional_summary || 'No professional summary yet.'}</p>
      <div className="grid-3 mt">
        <div className="list-item" style={{ display: 'block' }}>
          <div className="kpi-value">{completion}%</div><div className="kpi-sub">Profile completion</div>
        </div>
        <div className="list-item" style={{ display: 'block' }}>
          <div className="kpi-value">{student.completion_overview?.sections?.filter((s) => s.complete).length || 0}/{student.completion_overview?.sections?.length || 10}</div>
          <div className="kpi-sub">Sections completed</div>
        </div>
        <div className="list-item" style={{ display: 'block' }}>
          <div className="kpi-value">{student.completion_overview?.missing?.length || 0}</div>
          <div className="kpi-sub">Sections to improve</div>
        </div>
      </div>
      <div className="mt">
        <b>Contact</b>
        <div className="row mt">
          {student.email && <a href={`mailto:${student.email}`}>✉️ {student.email}</a>}
          {student.phone && <span>📞 {student.phone}</span>}
          {student.github_url && <a href={student.github_url} target="_blank" rel="noreferrer">🐙 GitHub</a>}
          {student.linkedin_url && <a href={student.linkedin_url} target="_blank" rel="noreferrer">💼 LinkedIn</a>}
        </div>
      </div>
    </div>
  )
}

function PersonalTab({ personal, setPersonal, canEdit, saving, onSave }) {
  const P = ({ k, label, type }) => (
    <div className="form-group">
      <label>{label}</label>
      <input type={type || 'text'} value={personal[k] || ''} readOnly={!canEdit}
             onChange={(e) => setPersonal({ ...personal, [k]: e.target.value })} />
    </div>
  )
  return (
    <div>
      <div className="form-grid">
        <P k="name" label="Name" />
        <P k="register_number" label="Register Number" />
        <P k="student_id" label="Student ID" />
        <P k="admission_number" label="Admission Number" />
        <P k="email" label="Email" type="email" />
        <P k="phone" label="Phone" />
        <P k="gender" label="Gender" />
        <P k="date_of_birth" label="Date of Birth" type="date" />
        <P k="department" label="Department" />
        <P k="address" label="Address" />
        <P k="city" label="City" />
        <P k="state" label="State" />
        <P k="github_url" label="GitHub URL" />
        <P k="linkedin_url" label="LinkedIn URL" />
        <div className="form-group" style={{ gridColumn: '1 / -1' }}>
          <label>Professional Summary</label>
          <textarea value={personal.professional_summary || ''} readOnly={!canEdit}
                    onChange={(e) => setPersonal({ ...personal, professional_summary: e.target.value })} />
        </div>
      </div>
      {canEdit && <button className="btn btn-primary mt" onClick={onSave} disabled={saving}>{saving ? 'Saving…' : 'Save Personal Information'}</button>}
    </div>
  )
}

export default StudentProfile