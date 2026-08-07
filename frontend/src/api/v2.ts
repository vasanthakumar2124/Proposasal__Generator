import { createApiClient } from './client'
import type { Project, ProjectHub, ProjectHubUpdate } from '../types/project'

const v2Client = createApiClient('/api/v2')

export interface GenerateForProjectInput {
  client_input: string
  domain?: string
  project_type?: string
}

export const projectHubApi = {
  getHub: (projectId: string) => v2Client.get<ProjectHub>(`/projects/${projectId}/hub`),
  updateFields: (projectId: string, data: ProjectHubUpdate) =>
    v2Client.patch<Project>(`/projects/${projectId}`, data),
  generate: (projectId: string, data: GenerateForProjectInput, idempotencyKey: string) =>
    v2Client.post<{ _id: string; status: string }>(`/projects/${projectId}/generate`, data, {
      headers: { 'Idempotency-Key': idempotencyKey },
    }),
}
