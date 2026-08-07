import apiClient from './client'
import type { Proposal, ProposalCreateRequest, ProposalUpdateRequest } from '../types/proposal'
import type { PaginatedResponse, MessageResponse } from '../types/common'

export const proposalsApi = {
  list: (skip = 0, limit = 100, status?: string) =>
    apiClient.get<PaginatedResponse<Proposal>>('/proposals', {
      params: { skip, limit, status },
    }),

  get: (id: string) =>
    apiClient.get<Proposal>(`/proposals/${id}`),

  create: (data: ProposalCreateRequest) =>
    apiClient.post<Proposal>('/proposals', data),

  update: (id: string, data: ProposalUpdateRequest) =>
    apiClient.put<Proposal>(`/proposals/${id}`, data),

  delete: (id: string) =>
    apiClient.delete<MessageResponse>(`/proposals/${id}`),

  updateSection: (id: string, sectionName: string, content: Record<string, unknown>) =>
    apiClient.put<Proposal>(`/proposals/${id}/sections/${sectionName}`, content),

  generate: (data: { client_input: string; domain?: string; project_type?: string; project_id?: string }, idempotencyKey?: string) =>
    apiClient.post<Proposal>('/proposals/generate', data, {
      headers: idempotencyKey ? { 'Idempotency-Key': idempotencyKey } : undefined,
    }),

  exportProposal: (id: string, fmt: string) =>
    apiClient.get(`/proposals/${id}/export/${fmt}`, { responseType: 'blob' }),
}
