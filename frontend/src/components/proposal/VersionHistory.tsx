import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { proposalLifecycleApi, type ProposalVersion } from '../../api/v2'
import { Button } from '../ui/Button'
import { Badge } from '../ui/Badge'
import { History, RotateCcw, ChevronDown, ChevronUp } from 'lucide-react'

function prettyJson(value: unknown): string {
  if (typeof value === 'string') return value
  try {
    return JSON.stringify(value, null, 2)
  } catch {
    return String(value)
  }
}

function DiffView({
  proposalId,
  fromVersion,
  toVersion,
  onClose,
}: {
  proposalId: string
  fromVersion: string
  toVersion: string
  onClose: () => void
}) {
  const { data, isLoading } = useQuery({
    queryKey: ['version-diff', proposalId, fromVersion, toVersion],
    queryFn: () => proposalLifecycleApi.diffVersions(proposalId, fromVersion, toVersion),
  })

  if (isLoading) return <p className="text-sm text-gray-500 py-3">Loading diff...</p>
  const changes = data?.data?.changes || {}

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium">
          Diff v{data?.data?.from_version} → v{data?.data?.to_version}
        </p>
        <Button variant="ghost" size="sm" onClick={onClose}>Close</Button>
      </div>
      {Object.keys(changes).length === 0 ? (
        <p className="text-sm text-gray-400 italic">No section differences.</p>
      ) : (
        Object.entries(changes).map(([section, change]) => {
          const from = (change as { from: unknown }).from
          const to = (change as { to: unknown }).to
          return (
          <div key={section} className="border rounded-lg overflow-hidden">
            <div className="bg-gray-100 px-3 py-1.5 text-sm font-semibold capitalize border-b">
              {section.replace(/_/g, ' ')}
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 divide-y sm:divide-y-0 sm:divide-x">
              <div className="p-3">
                <p className="text-xs font-medium text-red-600 mb-1">Before (v{data?.data?.from_version})</p>
                <pre className="text-xs whitespace-pre-wrap font-sans text-gray-600 max-h-48 overflow-y-auto">
                  {prettyJson(from)}
                </pre>
              </div>
              <div className="p-3">
                <p className="text-xs font-medium text-green-600 mb-1">After (v{data?.data?.to_version})</p>
                <pre className="text-xs whitespace-pre-wrap font-sans text-gray-600 max-h-48 overflow-y-auto">
                  {prettyJson(to)}
                </pre>
              </div>
            </div>
          </div>
          )
        })
      )}
    </div>
  )
}

export default function VersionHistory({ proposalId }: { proposalId: string }) {
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [diffing, setDiffing] = useState<{ from: string; to: string } | null>(null)
  const [restored, setRestored] = useState<string | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['proposal-versions', proposalId],
    queryFn: () => proposalLifecycleApi.listVersions(proposalId),
    enabled: open,
  })

  const versions: ProposalVersion[] = data?.data?.versions || []

  const restoreMutation = useMutation({
    mutationFn: (versionId: string) => proposalLifecycleApi.restoreVersion(proposalId, versionId),
    onSuccess: (res) => {
      setRestored(`Restored to version ${res.data.parent_version} (now v${res.data.version})`)
      queryClient.invalidateQueries({ queryKey: ['proposal-versions', proposalId] })
      queryClient.invalidateQueries({ queryKey: ['proposals', proposalId] })
      queryClient.invalidateQueries({ queryKey: ['proposals'] })
    },
  })

  const openDiff = (v: ProposalVersion) => {
    const older = versions.find((x) => x.version < v.version)
    if (!older) return
    setDiffing({ from: older._id, to: v._id })
  }

  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold flex items-center gap-2">
          <History className="h-5 w-5 text-blue-600" /> Version History
        </h2>
        <Button variant="outline" size="sm" onClick={() => setOpen(!open)}>
          {open ? <ChevronUp className="h-4 w-4 mr-1" /> : <ChevronDown className="h-4 w-4 mr-1" />}
          {open ? 'Hide' : 'Show'}
        </Button>
      </div>

      {restored && (
        <p className="mt-3 bg-green-50 border border-green-200 rounded-lg px-3 py-2 text-sm text-green-700">
          {restored}
        </p>
      )}

      {open && (
        <div className="mt-4 space-y-4">
          {isLoading ? (
            <p className="text-sm text-gray-500">Loading versions...</p>
          ) : versions.length === 0 ? (
            <p className="text-sm text-gray-400 italic">No versions recorded yet.</p>
          ) : (
            <ul className="space-y-2">
              {versions.map((v) => (
                <li key={v._id} className="border rounded-lg p-3 flex items-center justify-between gap-3">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">v{v.version}</Badge>
                      <span className="text-sm font-medium truncate">{v.title}</span>
                      <Badge>{v.status}</Badge>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {v.note || 'snapshot'} &middot; {new Date(v.created_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex gap-2 shrink-0">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => openDiff(v)}
                      disabled={!versions.some((x) => x.version < v.version)}
                    >
                      Diff
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => restoreMutation.mutate(v._id)}
                      disabled={restoreMutation.isPending}
                    >
                      <RotateCcw className="h-3.5 w-3.5 mr-1" /> Restore
                    </Button>
                  </div>
                </li>
              ))}
            </ul>
          )}

          {diffing && (
            <DiffView
              proposalId={proposalId}
              fromVersion={diffing.from}
              toVersion={diffing.to}
              onClose={() => setDiffing(null)}
            />
          )}
        </div>
      )}
    </div>
  )
}
