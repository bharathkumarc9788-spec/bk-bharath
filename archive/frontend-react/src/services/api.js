import axios from 'axios'

// Base API client — JWT access token attached automatically.
const api = axios.create({
  baseURL: '/api',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// On 401, try to refresh the token once.
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    const refresh = localStorage.getItem('refresh')
    if (error.response?.status === 401 && refresh && !original._retry) {
      original._retry = true
      try {
        const { data } = await axios.post('/api/auth/refresh/', { refresh })
        localStorage.setItem('access', data.access)
        original.headers.Authorization = `Bearer ${data.access}`
        return api(original)
      } catch (e) {
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
        localStorage.removeItem('user')
        window.location.href = '/login'
      }
    }
    if (error.response?.status === 401) {
      // No refresh token — session is over.
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      localStorage.removeItem('user')
      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)

/** Extract a human-readable message from an API error. */
export function errorMessage(err, fallback = 'Something went wrong. Please try again.') {
  const data = err?.response?.data
  if (!data) return fallback
  if (typeof data === 'string') return data
  if (data.detail) return data.detail
  for (const key of Object.keys(data)) {
    const v = data[key]
    if (Array.isArray(v) && v.length) return `${String(v[0])}`
    if (typeof v === 'string' && v) return v
  }
  return fallback
}

export default api