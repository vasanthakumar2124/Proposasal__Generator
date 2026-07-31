import apiClient from './client'
import type { Member } from '../types/organization'
import type { PaginatedResponse, MessageResponse } from '../types/common'

export const membersApi = {
  list: (skip = 0, limit = 100) =>
    apiClient.get<PaginatedResponse<Member>>('/members', { params: { skip, limit } }),

  invite: (data: { email: string; role: string }) =>
    apiClient.post('/members', data),

  updateRole: (userId: string, role: string) =>
    apiClient.put<Member>(`/members/${userId}/role`, { role }),

  remove: (userId: string) =>
    apiClient.delete<MessageResponse>(`/members/${userId}`),
}
