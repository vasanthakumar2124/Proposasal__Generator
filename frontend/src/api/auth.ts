import apiClient from './client'
import type { AuthResponse, TokenResponse, LoginRequest, RegisterRequest, UserUpdateRequest, User } from '../types/auth'

export const authApi = {
  register: (data: RegisterRequest) =>
    apiClient.post<AuthResponse>('/auth/register', data),

  login: (data: LoginRequest) =>
    apiClient.post<AuthResponse>('/auth/login', data),

  refresh: (refreshToken: string) =>
    apiClient.post<TokenResponse>('/auth/refresh', { refresh_token: refreshToken }),

  getMe: () =>
    apiClient.get<User>('/auth/me'),

  updateMe: (data: UserUpdateRequest) =>
    apiClient.put<User>('/auth/me', data),

  logout: () =>
    apiClient.post<{ message: string }>('/auth/logout'),
}
