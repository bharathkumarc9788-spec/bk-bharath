/** Spinner loader with optional label. */
export function Loading({ label = 'Loading…' }) {
  return (
    <div className="loading">
      <div className="spinner" />
      <span style={{ marginLeft: 14 }}>{label}</span>
    </div>
  )
}

/** Skeleton shimmer block (rows are always styleable via .skeleton). */
export function Skeleton({ rows = 3, height = "100%" }) {
  return (
    <div className="skeleton-block">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="skeleton" style={{ height }} />
      ))}
    </div>
  )
}