import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import api from '../services/api'
import { authService } from '../services/authService'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => authService.getStoredUser())
  const [loading, setLoading] = useState(false)

  const login = async (username, password) => {
    const data = await authService.login(username, password)
    setUser(data.user)
    return data.user
  }

  const logout = () => {
    authService.logout()
    setUser(null)
    window.location.href = '/login'
  }

  const refreshMe = async () => {
    try {
      const { data } = await api.get('/auth/me/')
      const stored = authService.getStoredUser() || {}
      const merged = { ...stored, ...data.user }
      setUser(merged)
      localStorage.setItem('user', JSON.stringify(merged))
      return merged
    } catch (e) {
      // ignore — interceptor handles token refresh
    }
  }

  useEffect(() => {
    refreshMe()
  }, [])

  const value = useMemo(
    () => ({ user, setUser, login, logout, refreshMe, loading }),
    [user, loading],
  )
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => useContext(AuthContext)