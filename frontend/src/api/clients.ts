import apiClient from './client'
import type { Client, ClientCreateRequest, ClientUpdateRequest } from '../types/client'
import type { PaginatedResponse, MessageResponse } from '../types/common'

export const clientsApi = {
  list: (skip = 0, limit = 100) =>
    apiClient.get<PaginatedResponse<Client>>('/clients', { params: { skip, limit } }),

  get: (id: string) =>
    apiClient.get<Client>(`/clients/${id}`),

  create: (data: ClientCreateRequest) =>
    apiClient.post<Client>('/clients', data),

  update: (id: string, data: ClientUpdateRequest) =>
    apiClient.put<Client>(`/clients/${id}`, data),

  delete: (id: string) =>
    apiClient.delete<MessageResponse>(`/clients/${id}`),
}
