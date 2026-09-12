import { StatusBadge } from './StatusBadge'

function fmtDate(d) {
  if (!d) return '—'
  const dt = new Date(d)
  return isNaN(dt.getTime()) ? '—' : dt.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
}

/**
 * Students table with real API-backed actions.
 * Optional callbacks: onRowClick, onEdit, onGenerate, onDelete, onView.
 */
export function StudentTable({ students, onRowClick, onEdit, onGenerate, onDelete, canDelete = false }) {
  if (!students?.length) {
    return (
      <div className="empty">
        <div className="big">🎓</div>
        No students found.
      </div>
    )
  }
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Profile</th>
            <th>Register No</th>
            <th>Department</th>
            <th>Year</th>
            <th>Completion</th>
            <th>Portfolio Status</th>
            <th>Last Updated</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {students.map((s) => (
            <tr key={s.id}>
              <td>
                <div className="row">
                  {s.profile_photo
                    ? <img className="avatar-sm" src={s.profile_photo} alt={s.name} />
                    : <span className="avatar-sm">{s.name?.[0]}</span>}
                  <a className="link-strong" onClick={() => onRowClick?.(s)} href="#">{s.name}</a>
                </div>
              </td>
              <td>{s.register_number}</td>
              <td>{s.department || '—'}</td>
              <td>{s.year || '—'}</td>
              <td style={{ width: 150 }}>
                <div className="row">
                  <div className="progress-bar" style={{ flex: 1, width: 80 }}>
                    <div className="progress-fill" style={{ width: `${s.completion ?? 0}%` }} />
                  </div>
                  <span style={{ fontSize: 12.5 }}>{s.completion ?? 0}%</span>
                </div>
              </td>
              <td>
                {s.status
                  ? <StatusBadge status={s.status} />
                  : <span className="muted">No portfolio</span>}
              </td>
              <td><span className="muted" style={{ whiteSpace: 'nowrap', fontSize: 12.5 }}>{fmtDate(s.updated_at || s.created_at)}</span></td>
              <td>
                <div className="row actions-cell">
                  <button className="btn btn-sm" title="View" onClick={() => onRowClick?.(s)}>View</button>
                  {onEdit && (
                    <button className="btn btn-sm" title="Edit" onClick={() => onEdit(s)}>Edit</button>
                  )}
                  {onGenerate && (
                    <button className="btn btn-sm btn-primary" title="Generate Portfolio" onClick={() => onGenerate(s)}>Generate</button>
                  )}
                  {onDelete && canDelete && (
                    <button className="btn btn-sm btn-danger" title="Delete" onClick={() => onDelete(s)}>🗑</button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default StudentTable