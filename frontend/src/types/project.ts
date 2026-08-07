export interface Project {
  _id: string
  organization_id: string
  workspace_id: string | null
  client_id: string | null
  name: string
  description: string
  industry: string
  project_type: string
  status: string
  proposal_ids: string[]
  goal?: string
  budget?: number | null
  currency?: string
  timeline?: string | null
  key_features?: string[]
  notes?: string
  created_by: string
  created_at: string
  updated_at: string
}

export interface ProjectCreateRequest {
  name: string
  description?: string
  industry?: string
  project_type?: string
  workspace_id?: string | null
  client_id?: string | null
}

export interface ProjectUpdateRequest {
  name?: string
  description?: string
  industry?: string
  project_type?: string
  workspace_id?: string | null
  client_id?: string | null
}

export interface HubProposal {
  _id: string
  proposal_id: string
  title: string
  status: string
  error: string | null
  created_at: string | null
}

export interface HubActivityEvent {
  _id: string
  event_type: string
  resource_type: string
  resource_id: string
  occurred_at: string
  payload?: Record<string, unknown> | null
}

export interface ProjectHub {
  project: Project
  proposals: HubProposal[]
  activity: HubActivityEvent[]
}

export interface ProjectHubUpdate {
  goal?: string
  budget?: number | null
  currency?: string
  timeline?: string | null
  key_features?: string[]
  notes?: string
  status?: string
}
