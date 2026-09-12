export function ErrorState({ message = 'Could not load data.', onRetry }) {
  return (
    <div className="empty">
      <div className="big">⚠️</div>
      {message}
      {onRetry && (
        <div className="mt">
          <button className="btn btn-primary btn-sm" onClick={onRetry}>↻ Retry</button>
        </div>
      )}
    </div>
  )
}

export default ErrorState