import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { proposalLifecycleApi } from '../../api/v2'
import { Button } from '../ui/Button'

const TRANSITIONS: Record<string, string[]> = {
  draft: ['processing', 'review'],
  processing: ['draft', 'generating', 'review', 'rejected'],
  generating: ['draft', 'review'],
  review: ['draft', 'approved', 'rejected'],
  approved: ['draft', 'sent'],
  rejected: ['draft'],
  sent: [],
}

export default function StatusControl({ proposalId, status }: { proposalId: string; status: string }) {
  const [message, setMessage] = useState<string | null>(null)
  const mutation = useMutation({
    mutationFn: (target: string) => proposalLifecycleApi.changeStatus(proposalId, target),
    onSuccess: () => setMessage('Status updated'),
    onError: (err: unknown) => {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setMessage(typeof msg === 'string' ? msg : 'Transition failed')
    },
  })

  const targets = TRANSITIONS[status] || []

  if (targets.length === 0) return null

  return (
    <div className="flex items-center gap-2">
      {message && <span className="text-xs text-gray-500">{message}</span>}
      {targets.map((t) => (
        <Button
          key={t}
          variant="outline"
          size="sm"
          onClick={() => {
            setMessage(null)
            mutation.mutate(t)
          }}
          disabled={mutation.isPending}
        >
          {t}
        </Button>
      ))}
    </div>
  )
}
