import apiClient from './client'

export const analyticsApi = {
  getDashboard: () => apiClient.get('/analytics/dashboard'),

  getAdminDashboard: () => apiClient.get('/analytics/admin/dashboard'),
}
