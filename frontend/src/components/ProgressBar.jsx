export function ProgressBar({ percent, suffix = '%', tone = '' }) {
  const p = Math.max(0, Math.min(100, Number(percent) || 0))
  return (
    <div className="row">
      <div className="progress-bar" style={{ flex: 1 }}>
        <div className={`progress-fill ${tone}`} style={{ width: `${p}%` }} />
      </div>
      <span style={{ fontSize: 12.5, minWidth: 42 }}>{p}{suffix}</span>
    </div>
  )
}

export default ProgressBar