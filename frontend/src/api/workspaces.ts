import apiClient from './client'
import type { Workspace, WorkspaceCreateRequest, WorkspaceUpdateRequest } from '../types/workspace'
import type { PaginatedResponse, MessageResponse } from '../types/common'

export const workspacesApi = {
  list: (skip = 0, limit = 100) =>
    apiClient.get<PaginatedResponse<Workspace>>('/workspaces', { params: { skip, limit } }),

  get: (id: string) =>
    apiClient.get<Workspace>(`/workspaces/${id}`),

  create: (data: WorkspaceCreateRequest) =>
    apiClient.post<Workspace>('/workspaces', data),

  update: (id: string, data: WorkspaceUpdateRequest) =>
    apiClient.put<Workspace>(`/workspaces/${id}`, data),

  delete: (id: string) =>
    apiClient.delete<MessageResponse>(`/workspaces/${id}`),

  addMember: (id: string, userId: string) =>
    apiClient.post<Workspace>(`/workspaces/${id}/members/${userId}`),

  removeMember: (id: string, userId: string) =>
    apiClient.delete<Workspace>(`/workspaces/${id}/members/${userId}`),
}
