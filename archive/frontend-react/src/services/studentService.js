import api from './api'

const studentService = {
  list: (params) => api.get('/students/', { params }).then((r) => r.data),
  get: (id) => api.get(`/students/${id}/`).then((r) => r.data),
  create: (data) => api.post('/students/', data).then((r) => r.data),
  update: (id, data) => api.patch(`/students/${id}/`, data).then((r) => r.data),
  remove: (id) => api.delete(`/students/${id}/`).then((r) => r.data),

  // Section endpoints (real API calls)
  sections: (studentId) => ({
    education: {
      list: () => api.get(`/students/${studentId}/education/`).then((r) => r.data),
      create: (data) => api.post(`/students/${studentId}/education/`, { ...data, student: studentId }).then((r) => r.data),
      remove: (id) => api.delete(`/students/${studentId}/education/${id}/`),
    },
    skills: {
      list: () => api.get(`/students/${studentId}/skills/`).then((r) => r.data),
      create: (data) => api.post(`/students/${studentId}/skills/`, { ...data, student: studentId }).then((r) => r.data),
      remove: (id) => api.delete(`/students/${studentId}/skills/${id}/`),
    },
    projects: {
      list: () => api.get(`/students/${studentId}/projects/`).then((r) => r.data),
      create: (data) => api.post(`/students/${studentId}/projects/`, { ...data, student: studentId }).then((r) => r.data),
      remove: (id) => api.delete(`/students/${studentId}/projects/${id}/`),
    },
    internships: {
      list: () => api.get(`/students/${studentId}/internships/`).then((r) => r.data),
      create: (data) => api.post(`/students/${studentId}/internships/`, { ...data, student: studentId }).then((r) => r.data),
      remove: (id) => api.delete(`/students/${studentId}/internships/${id}/`),
    },
    certifications: {
      list: () => api.get(`/students/${studentId}/certifications/`).then((r) => r.data),
      create: (data) => api.post(`/students/${studentId}/certifications/`, { ...data, student: studentId }).then((r) => r.data),
      remove: (id) => api.delete(`/students/${studentId}/certifications/${id}/`),
    },
    achievements: {
      list: () => api.get(`/students/${studentId}/achievements/`).then((r) => r.data),
      create: (data) => api.post(`/students/${studentId}/achievements/`, { ...data, student: studentId }).then((r) => r.data),
      remove: (id) => api.delete(`/students/${studentId}/achievements/${id}/`),
    },
    activities: {
      list: () => api.get(`/students/${studentId}/activities/`).then((r) => r.data),
      create: (data) => api.post(`/students/${studentId}/activities/`, { ...data, student: studentId }).then((r) => r.data),
      remove: (id) => api.delete(`/students/${studentId}/activities/${id}/`),
    },
    goals: {
      list: () => api.get('/goals/', { params: { student_id: studentId } }).then((r) => r.data),
      create: (data) => api.post('/goals/', { ...data, student: studentId }).then((r) => r.data),
      remove: (id) => api.delete(`/goals/${id}/`),
    },
    feedback: {
      teacher: () => api.get('/feedback/teacher-feedback/', { params: { student_id: studentId } }).then((r) => r.data),
      createTeacher: (data) => api.post('/feedback/teacher-feedback/create_feedback/', { ...data, student: studentId }).then((r) => r.data),
      parent: () => api.get('/feedback/parent-feedback/', { params: { student_id: studentId } }).then((r) => r.data),
    },
  }),
}

export default studentService