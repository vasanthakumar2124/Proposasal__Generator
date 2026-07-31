export interface User {
  _id: string
  email: string
  name: string
  organization_id: string
  role: 'admin' | 'editor' | 'viewer'
  avatar_url: string
  status: string
  created_at: string
  updated_at: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  expires_in: number
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  name: string
  email: string
  password: string
  company_name: string
}

export interface UserUpdateRequest {
  name?: string
  avatar_url?: string
}
