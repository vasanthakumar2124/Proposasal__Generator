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
