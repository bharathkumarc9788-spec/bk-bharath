export function EmptyState({ icon = '📭', title = 'Nothing here yet', sub }) {
  return (
    <div className="empty">
      <div className="big">{icon}</div>
      {title}
      {sub && <div className="muted mt" style={{ fontSize: 13 }}>{sub}</div>}
    </div>
  )
}

export default EmptyState