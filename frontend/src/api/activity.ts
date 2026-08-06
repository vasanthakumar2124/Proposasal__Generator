import apiClient from './client'

export const activityApi = {
  list: (params: { skip?: number; limit?: number; event_type?: string }) =>
    apiClient.get('/activity', { params }),
}
