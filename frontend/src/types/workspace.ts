export interface Workspace {
  _id: string
  organization_id: string
  name: string
  description: string
  created_by: string
  members: string[]
  status: string
  created_at: string
  updated_at: string
}

export interface WorkspaceCreateRequest {
  name: string
  description?: string
}

export interface WorkspaceUpdateRequest {
  name?: string
  description?: string
}
