import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import studentService from '../services/studentService'
import { useToast } from '../context/ToastContext'
import { useAuth } from '../context/AuthContext'
import { Skeleton } from '../components/Loading'
import { errorMessage } from '../services/api'

function EditStudent() {
  const { id } = useParams()
  const navigate = useNavigate()
  const toast = useToast()
  const { user } = useAuth()
  const [form, setForm] = useState(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    studentService.get(id).then((s) => {
      setForm({
        register_number: s.register_number, name: s.name, student_id: s.student_id,
        admission_number: s.admission_number, email: s.email, phone: s.phone,
        gender: s.gender, date_of_birth: s.date_of_birth, department: s.department,
        address: s.address, city: s.city, state: s.state,
        github_url: s.github_url, linkedin_url: s.linkedin_url,
        professional_summary: s.professional_summary,
      })
    }).catch((e) => toast.error(errorMessage(e, 'Student not found')))
  }, [id])

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })

  const onSubmit = async (e) => {
    e.preventDefault()
    setBusy(true)
    try {
      const updated = await studentService.update(id, form)
      toast.success(`Student ${updated.name} updated!`)
      navigate(`/students/${id}`)
    } catch (err) {
      toast.error(errorMessage(err, 'Failed to update student'))
    } finally {
      setBusy(false)
    }
  }

  if (!form) return <Skeleton rows={6} />

  return (
    <div>
      <div className="card">
        <div className="card-title">
          <h3>Edit Student</h3>
          <button className="btn btn-sm" onClick={() => navigate(`/students/${id}`)}>← Back to Profile</button>
        </div>
        <form onSubmit={onSubmit}>
          <div className="form-grid">
            <div className="form-group"><label>Register Number *</label><input value={form.register_number} onChange={set('register_number')} required /></div>
            <div className="form-group"><label>Full Name *</label><input value={form.name} onChange={set('name')} required /></div>
            <div className="form-group"><label>Student ID</label><input value={form.student_id} onChange={set('student_id')} /></div>
            <div className="form-group"><label>Admission Number</label><input value={form.admission_number} onChange={set('admission_number')} /></div>
            <div className="form-group"><label>Email</label><input type="email" value={form.email} onChange={set('email')} /></div>
            <div className="form-group"><label>Phone</label><input value={form.phone} onChange={set('phone')} /></div>
            <div className="form-group"><label>Gender</label>
              <select value={form.gender} onChange={set('gender')}>
                <option value="MALE">Male</option>
                <option value="FEMALE">Female</option>
                <option value="OTHER">Other</option>
              </select>
            </div>
            <div className="form-group"><label>Date of Birth</label><input type="date" value={form.date_of_birth} onChange={set('date_of_birth')} /></div>
            <div className="form-group"><label>Department</label><input value={form.department} onChange={set('department')} /></div>
            <div className="form-group"><label>Address</label><input value={form.address} onChange={set('address')} /></div>
            <div className="form-group"><label>City</label><input value={form.city} onChange={set('city')} /></div>
            <div className="form-group"><label>State</label><input value={form.state} onChange={set('state')} /></div>
            <div className="form-group"><label>GitHub URL</label><input value={form.github_url} onChange={set('github_url')} placeholder="https://github.com/…" /></div>
            <div className="form-group"><label>LinkedIn URL</label><input value={form.linkedin_url} onChange={set('linkedin_url')} placeholder="https://linkedin.com/in/…" /></div>
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label>Professional Summary</label>
              <textarea value={form.professional_summary} onChange={set('professional_summary')} />
            </div>
          </div>
          <div className="row mt">
            <button className="btn btn-primary" type="submit" disabled={busy}>{busy ? 'Saving…' : 'Save Changes'}</button>
            <button className="btn" type="button" onClick={() => navigate(`/students/${id}`)}>Cancel</button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default EditStudent