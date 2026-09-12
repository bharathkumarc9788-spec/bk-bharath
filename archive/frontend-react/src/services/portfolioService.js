import api from './api'

export const portfolioService = {
  templates: () => api.get('/portfolio/templates/').then((r) => r.data),
  list: () => api.get('/portfolio/').then((r) => r.data),
  get: (id) => api.get(`/portfolio/${id}/`).then((r) => r.data),
  generate: (studentId, templateId) =>
    api.post('/portfolio/generate/', { student_id: studentId, template_id: templateId }).then((r) => r.data),
  submit: (id) => api.post(`/portfolio/${id}/submit/`).then((r) => r.data),
  startReview: (id) => api.post(`/portfolio/${id}/start_review/`).then((r) => r.data),
  approve: (id, comments) => api.post(`/portfolio/${id}/approve/`, { comments }).then((r) => r.data),
  reject: (id, comments) => api.post(`/portfolio/${id}/reject/`, { comments }).then((r) => r.data),
  revision: (id, revisionReason) => api.post(`/portfolio/${id}/revision/`, { revision_reason: revisionReason }).then((r) => r.data),
  publish: (id) => api.post(`/portfolio/${id}/publish/`).then((r) => r.data),
  saveDraft: (id, data) => api.patch(`/portfolio/${id}/`, data).then((r) => r.data),
  publicUrl: (id) => api.get(`/portfolio/${id}/public_url/`).then((r) => r.data),
  publicBySlug: (slug) => api.get(`/portfolio/public/${slug}/`).then((r) => r.data),
  qr: (id) => api.get(`/portfolio/${id}/qr/`, { responseType: 'blob' }),
}

export const dashboardService = {
  data: () => api.get('/dashboard/').then((r) => r.data),
  analytics: () => api.get('/dashboard/data/').then((r) => r.data),
}

export const notificationService = {
  list: () => api.get('/notifications/').then((r) => r.data),
  markAllRead: () => api.post('/notifications/mark_all_read/'),
  remove: (id) => api.delete(`/notifications/${id}/`),
}