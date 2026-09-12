const STATUS_STYLE = {
  DRAFT: 'badge-gray',
  SUBMITTED: 'badge-blue',
  UNDER_REVIEW: 'badge-amber',
  APPROVED: 'badge-green',
  REJECTED: 'badge-red',
  REVISION_REQUIRED: 'badge-red',
  PUBLISHED: 'badge-violet',
}

export function StatusBadge({ status }) {
  if (!status) return null
  return <span className={`badge ${STATUS_STYLE[status] || 'badge-gray'}`}>{String(status).replace('_', ' ')}</span>
}

export default StatusBadge