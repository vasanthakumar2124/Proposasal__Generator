export interface Proposal {
  _id: string
  organization_id: string
  project_id: string | null
  client_id: string | null
  workspace_id: string | null
  version: number
  status: 'draft' | 'processing' | 'generating' | 'review' | 'approved' | 'rejected' | 'sent' | 'error'
  title: string
  sections: Record<string, unknown>
  ai_generated: boolean
  generation_metadata: Record<string, unknown>
  created_by: string
  approved_by: string | null
  created_at: string
  updated_at: string
}

export interface ProposalCreateRequest {
  title: string
  project_id?: string | null
  client_id?: string | null
  workspace_id?: string | null
}

export interface ProposalUpdateRequest {
  title?: string
  status?: string
}
