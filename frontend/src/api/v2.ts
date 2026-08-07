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

export interface ProposalVersion {
  _id: string
  proposal_id: string
  version: number
  author_id: string
  title: string
  sections_snapshot: Record<string, unknown>
  status: string
  note: string | null
  parent_version: number | null
  created_at: string
}

export interface VersionDiff {
  proposal_id: string
  from_version: number
  to_version: number
  changes: Record<string, { from: unknown; to: unknown }>
}

export const proposalLifecycleApi = {
  changeStatus: (proposalId: string, target: string) =>
    v2Client.post<{ _id: string; status: string }>(`/proposals/${proposalId}/status`, { target }),
  listVersions: (proposalId: string) =>
    v2Client.get<{ proposal_id: string; versions: ProposalVersion[] }>(`/proposals/${proposalId}/versions`),
  diffVersions: (proposalId: string, fromVersion: string, toVersion: string) =>
    v2Client.get<VersionDiff>(`/proposals/${proposalId}/versions/diff`, {
      params: { from_version: fromVersion, to_version: toVersion },
    }),
  restoreVersion: (proposalId: string, versionId: string) =>
    v2Client.post<ProposalVersion>(`/proposals/${proposalId}/versions/${versionId}/restore`),
}

export type RestoreResponse = ProposalVersion
