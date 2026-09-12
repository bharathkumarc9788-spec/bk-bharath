import { useNavigate } from 'react-router-dom'

function ResetPassword() {
  const navigate = useNavigate()
  return (
    <div className="login-page">
      <div className="login-card">
        <h1>Password Reset</h1>
        <p className="sub">In this demo, passwords are set by HR or via the admin panel. Please contact your administrator.</p>
        <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center' }} onClick={() => navigate('/login')}>
          Back to Login
        </button>
      </div>
    </div>
  )
}

export default ResetPassword