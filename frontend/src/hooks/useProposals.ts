import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { proposalsApi } from '../api/proposals'

export function useProposals(status?: string) {
  return useQuery({
    queryKey: ['proposals', status],
    queryFn: () => proposalsApi.list(0, 100, status),
  })
}

export function useProposal(id: string) {
  return useQuery({
    queryKey: ['proposals', id],
    queryFn: () => proposalsApi.get(id),
    enabled: !!id,
  })
}

export function useDeleteProposal() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => proposalsApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['proposals'] }),
  })
}

export function useGenerateProposal() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (args: { data: { client_input: string; domain?: string; project_type?: string; project_id?: string }; idempotencyKey?: string }) =>
      proposalsApi.generate(args.data, args.idempotencyKey),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['proposals'] }),
  })
}
