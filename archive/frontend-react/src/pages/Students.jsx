import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import studentService from '../services/studentService'
import { portfolioService } from '../services/portfolioService'
import { StudentTable } from '../components/StudentTable'
import { ConfirmDialog } from '../components/ConfirmDialog'
import { Skeleton } from '../components/Loading'
import { useToast } from '../context/ToastContext'
import { useAuth } from '../context/AuthContext'
import { errorMessage } from '../services/api'

const PAGE_SIZE = 10
const YEARS = ['', '1', '2', '3', '4', '5', '6']
const STATUS_FILTERS = ['', 'DRAFT', 'SUBMITTED', 'UNDER_REVIEW', 'APPROVED', 'REVISION_REQUIRED', 'REJECTED', 'PUBLISHED']

function Students() {
  const navigate = useNavigate()
  const toast = useToast()
  const { user } = useAuth()
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [department, setDepartment] = useState('')
  const [year, setYear] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [departments, setDepartments] = useState([])
  const [page, setPage] = useState(1)
  const [deleteTarget, setDeleteTarget] = useState(null)
  const [deleting, setDeleting] = useState(false)

  const canDelete = user?.role === 'HR'

  const fetchStudents = useCallback(async () => {
    setLoading(true)
    try {
      const params = {}
      if (search) params.search = search
      if (department) params.department = department
      if (year) params.year = year
      if (statusFilter) params.status = statusFilter
      const data = await studentService.list(params)
      setStudents(data)
      setPage(1)
      if (!departments.length) {
        setDepartments([...new Set(data.map((s) => s.department).filter(Boolean))])
      }
      return data
    } finally {
      setLoading(false)
    }
  }, [search, department, year, statusFilter])

  useEffect(() => {
    const t = setTimeout(fetchStudents, 250)
    return () => clearTimeout(t)
  }, [fetchStudents])

  // Portfolio status + year + last-updated enrichment from real API detail.
  const enrich = async (list) => {
    const enriched = []
    for (const s of list) {
      let year = null
      let updatedAt = s.created_at
      let status = null
      try {
        const detail = await studentService.get(s.id)
        updatedAt = detail.updated_at || detail.created_at
        const edu = detail.education_records || []
        if (edu.length) year = edu[0].year_of_study
        if (detail.portfolios?.length) status = detail.portfolios[0].status
      } catch (e) {
        // fall back to list fields
      }
      enriched.push({ ...s, year, updated_at: updatedAt, status })
    }
    return enriched
  }

  const handleDelete = async () => {
    if (!deleteTarget) return
    setDeleting(true)
    try {
      await studentService.remove(deleteTarget.id)
      toast.success(`Student ${deleteTarget.name} deleted.`)
      setDeleteTarget(null)
      fetchStudents()
    } catch (err) {
      toast.error(errorMessage(err, 'Failed to delete student.'))
    } finally {
      setDeleting(false)
    }
  }

  const totalPages = Math.max(1, Math.ceil(students.length / PAGE_SIZE))
  const pageStudents = students.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  // Enrich current page once loaded.
  useEffect(() => {
    if (pageStudents.length && !loading) {
      enrich(pageStudents).then((rows) => {
        const map = new Map(rows.map((r) => [r.id, r]))
        setStudents((prev) => prev.map((s) => ({ ...s, ...(map.get(s.id) || {}) })))
      })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, loading])

  return (
    <div>
      <div className="card">
        <div className="row-between">
          <h3>Students</h3>
          <div className="search-bar">
            <input
              placeholder="Search name / register / dept / skills…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ minWidth: 240 }}
            />
            <select value={department} onChange={(e) => setDepartment(e.target.value)}>
              <option value="">All Departments</option>
              {departments.map((d) => <option key={d} value={d}>{d}</option>)}
            </select>
            <select value={year} onChange={(e) => setYear(e.target.value)}>
              <option value="">All Years</option>
              {YEARS.filter(Boolean).map((y) => <option key={y} value={y}>Year {y}</option>)}
            </select>
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="">All Status</option>
              {STATUS_FILTERS.filter(Boolean).map((s) => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
            </select>
          </div>
        </div>
        <div className="row mt">
          {user?.role === 'HR' && (
            <>
              <button className="btn btn-primary" onClick={() => navigate('/students/add')}>+ Add Student</button>
              <button className="btn" onClick={() => navigate('/bulk-upload')}>📤 Upload Students</button>
            </>
          )}
        </div>
      </div>

      <div className="card">
        {loading ? (
          <Skeleton rows={6} />
        ) : (
          <>
            <StudentTable
              students={pageStudents}
              onRowClick={(s) => navigate(`/students/${s.id}`)}
              onEdit={(s) => navigate(`/students/${s.id}/edit`)}
              onGenerate={(s) => navigate(`/portfolio/generator?student=${s.id}`)}
              onDelete={(s) => setDeleteTarget(s)}
              canDelete={canDelete}
            />
            <div className="pagination mt">
              <button className="btn btn-sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>← Prev</button>
              <span className="muted">Page {page} of {totalPages} · {students.length} student(s)</span>
              <button className="btn btn-sm" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>Next →</button>
            </div>
          </>
        )}
      </div>

      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete student"
        message={deleteTarget ? `Delete ${deleteTarget.name} (${deleteTarget.register_number}) permanently?` : ''}
        confirmLabel={deleting ? 'Deleting…' : 'Delete'}
        danger
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  )
}

export default Students