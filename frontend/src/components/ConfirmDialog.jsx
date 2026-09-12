import { Modal } from './Modal'

/** Simple confirm dialog built on Modal. */
export function ConfirmDialog({ open, title = 'Are you sure?', message, confirmLabel = 'Confirm', danger = false, onConfirm, onCancel }) {
  return (
    <Modal open={open} title={title} onClose={onCancel}>
      <p className="muted">{message}</p>
      <div className="row mt">
        <button className={`btn ${danger ? 'btn-danger' : 'btn-primary'}`} onClick={onConfirm}>
          {confirmLabel}
        </button>
        <button className="btn" onClick={onCancel}>Cancel</button>
      </div>
    </Modal>
  )
}

export default ConfirmDialog