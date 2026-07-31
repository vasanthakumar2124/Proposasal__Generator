import apiClient from './client'

export const analyticsApi = {
  getDashboard: () => apiClient.get('/analytics/dashboard'),

  getAdminDashboard: () => apiClient.get('/analytics/admin/dashboard'),
}

export const adminApi = {
  getHealth: () => apiClient.get('/admin/health'),

  listUsers: () => apiClient.get('/admin/users'),

  listOrganizations: () => apiClient.get('/admin/organizations'),
}
