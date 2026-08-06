import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { activityApi } from '../api/activity'
import { Button } from '../components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Skeleton } from '../components/ui/Skeleton'
import {
  UserPlus,
  Building2,
  FolderPlus,
  Boxes,
  FilePlus2,
  CheckCircle2,
  XCircle,
  Activity as ActivityIcon,
} from 'lucide-react'

const EVENT_META: Record<string, { icon: typeof UserPlus; label: string; color: string }> = {
  'user.registered': { icon: UserPlus, label: 'User registered', color: 'bg-blue-100 text-blue-700' },
  'client.created': { icon: Building2, label: 'Client created', color: 'bg-green-100 text-green-700' },
  'project.created': { icon: FolderPlus, label: 'Project created', color: 'bg-purple-100 text-purple-700' },
  'workspace.created': { icon: Boxes, label: 'Workspace created', color: 'bg-indigo-100 text-indigo-700' },
  'proposal.created': { icon: FilePlus2, label: 'Proposal created', color: 'bg-amber-100 text-amber-700' },
  'proposal.generated': { icon: CheckCircle2, label: 'Proposal generated', color: 'bg-emerald-100 text-emerald-700' },
  'proposal.failed': { icon: XCircle, label: 'Proposal failed', color: 'bg-red-100 text-red-700' },
}

const FILTERS = [
  { value: '', label: 'All' },
  { value: 'proposal.generated', label: 'Generated' },
  { value: 'proposal.failed', label: 'Failed' },
  { value: 'client.created', label: 'Clients' },
  { value: 'project.created', label: 'Projects' },
]

function timeAgo(iso: string): string {
  const seconds = Math.floor((Date.now() - new Date(iso).getTime()) / 1000)
  if (seconds < 60) return 'just now'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

export default function ActivityPage() {
  const [eventType, setEventType] = useState('')
  const [skip, setSkip] = useState(0)
  const pageSize = 50

  const { data, isLoading } = useQuery({
    queryKey: ['activity', eventType, skip],
    queryFn: () => activityApi.list({ skip, limit: pageSize, event_type: eventType || undefined }),
  })

  const items = data?.data?.items || []
  const total = data?.data?.total || items.length

  const changeFilter = (value: string) => {
    setEventType(value)
    setSkip(0)
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <ActivityIcon className="h-6 w-6 text-blue-600" /> Activity
        </h1>
        <p className="text-gray-500">Recent activity across your workspace</p>
      </div>

      <div className="flex flex-wrap gap-2">
        {FILTERS.map((f) => (
          <Button
            key={f.value}
            variant={eventType === f.value ? 'default' : 'outline'}
            size="sm"
            onClick={() => changeFilter(f.value)}
          >
            {f.label}
          </Button>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Feed</CardTitle>
          <CardDescription>{total} event{total === 1 ? '' : 's'}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-1">
          {isLoading ? (
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => <Skeleton key={i} className="h-14" />)}
            </div>
          ) : items.length === 0 ? (
            <p className="text-sm text-gray-500 py-8 text-center">No activity yet</p>
          ) : (
            items.map((item: { _id: string; event_type: string; payload?: Record<string, unknown>; occurred_at: string }) => {
              const meta = EVENT_META[item.event_type] || {
                icon: ActivityIcon,
                label: item.event_type,
                color: 'bg-gray-100 text-gray-700',
              }
              const Icon = meta.icon
              const title = item.payload?.title || item.payload?.name || meta.label
              return (
                <div key={item._id} className="flex items-start gap-3 rounded-lg p-3 hover:bg-gray-50">
                  <div className={`flex h-9 w-9 items-center justify-center rounded-full ${meta.color} shrink-0`}>
                    <Icon className="h-4 w-4" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium truncate">{String(title)}</p>
                    <p className="text-xs text-gray-500">{meta.label} · {timeAgo(item.occurred_at)}</p>
                  </div>
                  {item.event_type === 'proposal.failed' && (
                    <Badge variant="destructive" className="shrink-0">{String(item.payload?.error || 'failed')}</Badge>
                  )}
                </div>
              )
            })
          )}
          {!isLoading && items.length > 0 && skip + pageSize < total && (
            <div className="pt-3">
              <Button variant="outline" size="sm" className="w-full" onClick={() => setSkip(skip + pageSize)}>
                Load more
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
