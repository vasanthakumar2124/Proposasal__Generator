import apiClient from './client'
import type { Project, ProjectCreateRequest, ProjectUpdateRequest } from '../types/project'
import type { PaginatedResponse, MessageResponse } from '../types/common'

export const projectsApi = {
  list: (skip = 0, limit = 100, workspace_id?: string) =>
    apiClient.get<PaginatedResponse<Project>>('/projects', {
      params: { skip, limit, workspace_id },
    }),

  get: (id: string) =>
    apiClient.get<Project>(`/projects/${id}`),

  create: (data: ProjectCreateRequest) =>
    apiClient.post<Project>('/projects', data),

  update: (id: string, data: ProjectUpdateRequest) =>
    apiClient.put<Project>(`/projects/${id}`, data),

  delete: (id: string) =>
    apiClient.delete<MessageResponse>(`/projects/${id}`),
}
