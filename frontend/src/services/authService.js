import api from './api'

export const authService = {
  async login(username, password) {
    const { data } = await api.post('/auth/login/', { username, password })
    localStorage.setItem('access', data.access)
    localStorage.setItem('refresh', data.refresh)
    localStorage.setItem('user', JSON.stringify(data.user))
    return data
  },
  logout() {
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')
    localStorage.removeItem('user')
  },
  getStoredUser() {
    try {
      return JSON.parse(localStorage.getItem('user'))
    } catch (e) {
      return null
    }
  },
  me: () => api.get('/auth/me/').then((r) => r.data),
  updateMe: (data) => api.patch('/auth/me/', data).then((r) => r.data),
  changePassword: (oldPassword, newPassword) =>
    api.post('/auth/change-password/', { old_password: oldPassword, new_password: newPassword }).then((r) => r.data),
}