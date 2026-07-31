export interface Client {
  _id: string
  organization_id: string
  name: string
  industry: string
  contact_name: string
  contact_email: string
  contact_phone: string
  address: string
  notes: string
  created_by: string
  status: string
  created_at: string
  updated_at: string
}

export interface ClientCreateRequest {
  name: string
  industry?: string
  contact_name?: string
  contact_email?: string
  contact_phone?: string
  address?: string
  notes?: string
}

export interface ClientUpdateRequest {
  name?: string
  industry?: string
  contact_name?: string
  contact_email?: string
  contact_phone?: string
  address?: string
  notes?: string
}
