import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { errorMessage } from '../services/api'

function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('admin123')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const onSubmit = async (e) => {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      await login(username.trim(), password)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setError(errorMessage(err, 'Invalid credentials. Try again.'))
    } finally {
      setBusy(false)
    }
  }

  const fill = (u, p) => { setUsername(u); setPassword(p); setError('') }

  return (
    <div className="login-page">
      <div className="login-card">
        <div style={{ textAlign: 'center', marginBottom: 16 }}>
          <div style={{ fontSize: 44 }}>🎒</div>
        </div>
        <h1 style={{ textAlign: 'center' }}>Student Portfolio Automation System</h1>
        <p className="sub" style={{ textAlign: 'center' }}>360° digital portfolios with approval, publishing &amp; QR.</p>

        <form onSubmit={onSubmit}>
          <div className="form-group mb">
            <label>Username / Email</label>
            <input value={username} onChange={(e) => setUsername(e.target.value)} required autoFocus />
          </div>
          <div className="form-group mb">
            <label>Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          {error && <div className="form-error mb">{error}</div>}
          <button className="btn btn-primary" type="submit" disabled={busy} style={{ width: '100%', justifyContent: 'center' }}>
            {busy ? 'Signing in…' : 'Login'}
          </button>
        </form>

        <div className="mt" style={{ textAlign: 'center' }}>
          <Link to="/reset-password" className="muted" style={{ fontSize: 13 }}>Forgot Password?</Link>
        </div>

        <div className="demo-box">
          <b>Demo accounts</b><br />
          👩‍💼 HR / Super Admin — admin / admin123<br />
          👨‍🏫 Teacher — teacher / teacher123<br />
          👨‍👩‍👧 Parent — parent / parent123
          <div className="mt">
            <button className="btn btn-sm" onClick={() => fill('admin', 'admin123')}>Admin</button>{' '}
            <button className="btn btn-sm" onClick={() => fill('teacher', 'teacher123')}>Teacher</button>{' '}
            <button className="btn btn-sm" onClick={() => fill('parent', 'parent123')}>Parent</button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login