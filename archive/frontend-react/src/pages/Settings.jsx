import { useEffect, useState } from 'react'
import api from '../services/api'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'

function Settings() {
  const { user, refreshMe } = useAuth()
  const toast = useToast()
  const [tab, setTab] = useState('profile')
  const [profile, setProfile] = useState(null)
  const [savingProfile, setSavingProfile] = useState(false)
  const [password, setPassword] = useState({ current: '', next: '', confirm: '' })
  const [savingPassword, setSavingPassword] = useState(false)

  useEffect(() => {
    refreshMe().then((u) => setProfile({
      first_name: u.first_name, last_name: u.last_name, email: u.email,
      phone: u.phone || '', address: u.address || '',
    }))
  }, [])

  const saveProfile = async () => {
    setSavingProfile(true)
    try {
      const { data } = await api.patch('/auth/me/', profile)
      localStorage.setItem('user', JSON.stringify({ ...user, ...data }))
      refreshMe()
      toast.success('Profile settings saved')
    } catch (err) {
      toast.error('Could not save profile settings')
    } finally {
      setSavingProfile(false)
    }
  }

  const savePassword = async () => {
    if (password.next.length < 8) { toast.error('New password must be at least 8 characters'); return }
    if (password.next !== password.confirm) { toast.error('Passwords do not match'); return }
    setSavingPassword(true)
    try {
      const { data } = await api.post('/auth/change-password/', {
        old_password: password.current, new_password: password.next,
      })
      toast.success('Password changed')
      setPassword({ current: '', next: '', confirm: '' })
    } catch (err) {
      toast.error('Could not change password — check your current password')
    } finally {
      setSavingPassword(false)
    }
  }

  const SectionCard = ({ title, children }) => (
    <div className="card">
      <h3>{title}</h3>
      {children}
    </div>
  )

  const set = (k) => (e) => setProfile({ ...(profile || {}), [k]: e.target.value })

  return (
    <div>
      <div className="tabs">
        {[['profile', 'Profile'], ['account', 'Account & Security'], ['notifications', 'Notification Settings'], ['portfolio', 'Portfolio & Templates']].map(([key, label]) => (
          <button key={key} className={`tab-btn ${tab === key ? 'active' : ''}`} onClick={() => setTab(key)}>{label}</button>
        ))}
      </div>

      {tab === 'profile' && (
        <SectionCard title="Profile">
          <div className="muted mb">Manage your display name, email and contact details.</div>
          <div className="form-grid">
            <div className="form-group"><label>First Name</label><input value={profile?.first_name || ''} onChange={set('first_name')} /></div>
            <div className="form-group"><label>Last Name</label><input value={profile?.last_name || ''} onChange={set('last_name')} /></div>
            <div className="form-group"><label>Email</label><input value={profile?.email || ''} onChange={set('email')} /></div>
            <div className="form-group"><label>Phone</label><input value={profile?.phone || ''} onChange={set('phone')} /></div>
            <div className="form-group" style={{ gridColumn: '1 / -1' }}><label>Address</label><textarea value={profile?.address || ''} onChange={set('address')} /></div>
          </div>
          <button className="btn btn-primary mt" onClick={saveProfile} disabled={savingProfile}>{savingProfile ? 'Saving…' : 'Save Profile'}</button>
        </SectionCard>
      )}

      {tab === 'account' && (
        <SectionCard title="Account & Security">
          <div className="muted mb">Your role: <b>{user?.is_superuser ? 'Super Admin' : user?.role_display || user?.role}</b> · username <b>{user?.username}</b></div>
          <h4 style={{ marginTop: 14 }}>Change Password</h4>
          <div className="form-grid">
            <div className="form-group"><label>Current Password</label><input type="password" value={password.current} onChange={(e) => setPassword({ ...password, current: e.target.value })} /></div>
            <div className="form-group"><label>New Password (min 8)</label><input type="password" value={password.next} onChange={(e) => setPassword({ ...password, next: e.target.value })} /></div>
            <div className="form-group"><label>Confirm New Password</label><input type="password" value={password.confirm} onChange={(e) => setPassword({ ...password, confirm: e.target.value })} /></div>
          </div>
          <button className="btn btn-primary mt" onClick={savePassword} disabled={savingPassword}>{savingPassword ? 'Updating…' : 'Update Password'}</button>
        </SectionCard>
      )}

      {tab === 'notifications' && (
        <SectionCard title="Notification Settings">
          <div className="muted mb">Notification preferences are managed per-event on the server and via the admin panel.</div>
          <div className="list-item"><div><b>Email me for portfolio events</b><div className="muted">Approve / reject / publish notifications are delivered in-app.</div></div></div>
        </SectionCard>
      )}

      {tab === 'portfolio' && (
        <SectionCard title="Portfolio & Templates">
          <div className="muted">Choose templates in the Portfolio Templates page. Profile completion dictates portfolio readiness.</div>
          <div className="row mt">
            <a className="btn btn-primary" href="/portfolio/templates">Open Templates</a>
            <a className="btn" href="/portfolio/generator">Open Generator</a>
          </div>
        </SectionCard>
      )}
    </div>
  )
}

export default Settings