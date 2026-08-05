import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useAppSelector } from '../store/hooks'
import { analyticsApi } from '../api/analytics'
import { proposalsApi } from '../api/proposals'
import { Button } from '../components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Skeleton } from '../components/ui/Skeleton'
import { FileText, Users, TrendingUp, FolderOpen, Plus, Sparkles } from 'lucide-react'

const STATUS_VARIANTS: Record<string, 'success' | 'warning' | 'default' | 'secondary' | 'outline'> = {
  completed: 'success',
  approved: 'success',
  sent: 'secondary',
  draft: 'outline',
  review: 'default',
  generating: 'warning',
  processing: 'warning',
  error: 'warning',
}

export default function Dashboard() {
  const navigate = useNavigate()
  const { user } = useAppSelector((state) => state.auth)

  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ['analytics-dashboard'],
    queryFn: () => analyticsApi.getDashboard(),
  })

  const { data: proposalsData, isLoading: proposalsLoading } = useQuery({
    queryKey: ['proposals', undefined],
    queryFn: () => proposalsApi.list(0, 10),
  })

  const stats = analytics?.data?.stats || analytics?.data?.data?.stats || {}
  const recentProposals = proposalsData?.data?.items || []

  const statCards = [
    { label: 'Total Proposals', value: stats.total_proposals ?? 0, icon: FileText, change: 'All time' },
    { label: 'Recent (30d)', value: stats.recent_proposals_30d ?? 0, icon: TrendingUp, change: 'Last 30 days' },
    { label: 'Active Clients', value: stats.total_clients ?? 0, icon: Users, change: 'All time' },
    { label: 'Projects', value: stats.total_projects ?? 0, icon: FolderOpen, change: 'All time' },
  ]

  const loading = analyticsLoading && proposalsLoading

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Welcome, {user?.name?.split(' ')[0]}
          </h1>
          <p className="text-muted-foreground">
            Here&apos;s your proposal overview
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => navigate('/generate')}>
            <Sparkles className="mr-2 h-4 w-4" />
            New Proposal
          </Button>
          <Button variant="outline" onClick={() => navigate('/projects')}>
            <Plus className="mr-2 h-4 w-4" />
            New Project
          </Button>
        </div>
      </div>

      {loading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-28" />
          ))}
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {statCards.map((stat) => (
            <Card key={stat.label}>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.label}
                </CardTitle>
                <stat.icon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground">{stat.change}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Recent Proposals</CardTitle>
        </CardHeader>
        <CardContent>
          {proposalsLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-14" />
              ))}
            </div>
          ) : recentProposals.length === 0 ? (
            <div className="py-8 text-center">
              <p className="text-muted-foreground">No proposals yet. Generate your first one!</p>
              <Button onClick={() => navigate('/generate')} className="mt-4">
                <Sparkles className="mr-2 h-4 w-4" />
                Generate Proposal
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {recentProposals.map((proposal: {
                _id: string; title: string; status: string; created_at: string
              }) => (
                <div
                  key={proposal._id}
                  className="flex items-center justify-between rounded-lg border p-3 transition-colors hover:bg-muted/50 cursor-pointer"
                  onClick={() => navigate(`/proposals/${proposal._id}`)}
                >
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{proposal.title}</p>
                    <p className="text-sm text-muted-foreground">
                      {new Date(proposal.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <Badge variant={STATUS_VARIANTS[proposal.status] || 'outline'}>
                    {proposal.status}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
