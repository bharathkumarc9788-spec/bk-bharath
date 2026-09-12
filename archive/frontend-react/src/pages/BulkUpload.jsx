import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api, { errorMessage } from '../services/api'
import { useToast } from '../context/ToastContext'

function BulkUpload() {
  const navigate = useNavigate()
  const toast = useToast()
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [report, setReport] = useState(null)
  const [busy, setBusy] = useState(false)
  const [dragOver, setDragOver] = useState(false)

  const upload = async () => {
    if (!file) { toast.error('Choose a CSV or Excel file first'); return }
    setBusy(true)
    setReport(null)
    try {
      const form = new FormData()
      form.append('file', file)
      const { data } = await api.post('/students/bulk-upload/', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setPreview(data)
      toast.success(`Parsed ${data.valid.length} valid records`)
    } catch (err) {
      toast.error(errorMessage(err, 'Could not parse file'))
      if (err.response?.data?.invalid) setPreview({ valid: [], invalid: err.response.data.invalid, total: err.response.data.total })
    } finally {
      setBusy(false)
    }
  }

  const confirmImport = async () => {
    setBusy(true)
    try {
      const { data } = await api.post('/students/bulk-upload/', { preview: false, rows: preview.valid })
      setReport(data.report)
      toast.success(`Imported ${data.report.valid} students`)
    } catch (err) {
      toast.error('Import failed')
    } finally {
      setBusy(false)
    }
  }

  const downloadTemplate = () => {
    const csv = 'register_number,name,email,phone,gender,department,admission_number\n' +
      '21CSE100,John Doe,john@college.edu,+919800000000,MALE,Computer Science,ADM-21CSE100\n'
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'students-upload-template.csv'
    a.click()
  }

  return (
    <div>
      <div className="card">
        <div className="card-title">
          <h3>Bulk Student Upload</h3>
          <button className="btn btn-sm" onClick={downloadTemplate}>⬇️ Download Template</button>
        </div>
        <p className="muted mb">Header row: register_number, name, email, phone, gender, department, admission_number. Upload .csv or .xlsx.</p>
        <div
          className={`dropzone ${dragOver ? 'dragover' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => { e.preventDefault(); setDragOver(false); if (e.data.files?.length) setFile(e.data.files[0]) }}
        >
          <div style={{ fontSize: 34, textAlign: 'center' }}>📄</div>
          <p style={{ textAlign: 'center', color: 'var(--muted)', marginTop: 6 }}>Drag &amp; Drop File here, or</p>
          <div className="row" style={{ justifyContent: 'center' }}>
            <input type="file" accept=".csv,.xlsx" onChange={(e) => setFile(e.target.files[0])} />
            {file && <span className="badge badge-blue">{file.name}</span>}
          </div>
          <div className="row mt" style={{ justifyContent: 'center' }}>
            <button className="btn btn-primary" onClick={upload} disabled={busy}>{busy ? 'Processing…' : '📂 Parse File'}</button>
            <button className="btn btn-sm" onClick={() => navigate('/students')}>← Back to Students</button>
          </div>
        </div>
      </div>

      {preview && !report && (
        <div className="card">
          <div className="card-title">
            <h3>Preview — {preview.total} records ({preview.valid.length} valid, {preview.invalid.length} invalid)</h3>
          </div>
          {preview.valid.length > 0 && (
            <div className="table-wrap mb">
              <table>
                <thead><tr><th>Register No</th><th>Name</th><th>Email</th><th>Department</th></tr></thead>
                <tbody>
                  {preview.valid.slice(0, 20).map((r, i) => (
                    <tr key={i}><td>{r.register_number}</td><td>{r.name}</td><td>{r.email || '—'}</td><td>{r.department || '—'}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {preview.invalid.length > 0 && (
            <div className="mb">
              <b className="muted">Invalid rows:</b>
              {preview.invalid.map((r, i) => (
                <div key={i} className="badge badge-red" style={{ margin: 3, padding: '6px 10px' }}>{r.reason || 'invalid'}</div>
              ))}
            </div>
          )}
          <button className="btn btn-success" onClick={confirmImport} disabled={busy || !preview.valid.length}>
            {busy ? 'Importing…' : `✔ Import Valid Records (${preview.valid.length})`}
          </button>
        </div>
      )}

      {report && (
        <div className="card">
          <h3>Import Report</h3>
          <div className="stat-grid">
            <div className="stat-card"><div><div className="value">{report.total}</div><div className="label">Total Records</div></div></div>
            <div className="stat-card"><div><div className="value" style={{ color: 'var(--success)' }}>{report.valid}</div><div className="label">Valid / Created</div></div></div>
            <div className="stat-card"><div><div className="value" style={{ color: 'var(--danger)' }}>{report.invalid}</div><div className="label">Invalid / Skipped</div></div></div>
          </div>
          {(report.failed || []).length > 0 && (
            <div className="mb">
              <b>Errors:</b>
              {report.failed.map((f, i) => <div key={i} className="muted" style={{ fontSize: 13 }}>• {f.reason}</div>)}
            </div>
          )}
          <button className="btn btn-primary" onClick={() => navigate('/students')}>View Students</button>
        </div>
      )}
    </div>
  )
}

export default BulkUpload