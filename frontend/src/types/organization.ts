export interface Branding {
  logo_url: string
  primary_color: string
  secondary_color: string
  font_family: string
  accent_color: string
}

export interface Organization {
  _id: string
  name: string
  slug: string
  plan: 'free' | 'starter' | 'professional' | 'enterprise'
  features: string[]
  branding: Branding
  settings: Record<string, unknown>
  status: string
  created_at: string
  updated_at: string
}

export interface Member {
  id: string
  name: string
  email: string
  role: string
  status: string
  last_login: string | null
}
