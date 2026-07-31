import { useQuery } from '@tanstack/react-query'
import { analyticsApi } from '../api/analytics'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Skeleton } from '../components/ui/Skeleton'
import { FileText, Users, FolderOpen, Layers, TrendingUp, BarChart3 } from 'lucide-react'

function StatCard({
  title, value, icon: Icon, description,
}: {
  title: string; value: string | number; icon: React.ComponentType<{ className?: string }>; description?: string
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {description && <p className="text-xs text-muted-foreground mt-1">{description}</p>}
      </CardContent>
    </Card>
  )
}

export default function AnalyticsPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['analytics-dashboard'],
    queryFn: () => analyticsApi.getDashboard(),
  })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">Analytics</h1>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-28" />)}
        </div>
        <Skeleton className="h-64" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-20">
        <p className="text-red-500">Failed to load analytics. Connect to the backend to see data.</p>
      </div>
    )
  }

  const d = data?.data || data?.data?.data || {}
  const stats = d.stats || {}
  const proposalsByStatus = d.proposals_by_status || {}
  const recentProposals = d.recent_proposals || []
  const recentProjects = d.recent_projects || []
  const recentClients = d.recent_clients || []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Analytics</h1>
        <Badge variant="outline" className="capitalize">{stats.plan || 'free'}</Badge>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Total Proposals" value={stats.total_proposals ?? 0} icon={FileText} description="All time" />
        <StatCard title="Recent (30d)" value={stats.recent_proposals_30d ?? 0} icon={TrendingUp} description="Last 30 days" />
        <StatCard title="Clients" value={stats.total_clients ?? 0} icon={Users} description="All time" />
        <StatCard title="Projects" value={stats.total_projects ?? 0} icon={FolderOpen} description="All time" />
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle className="text-lg flex items-center gap-2"><BarChart3 className="h-5 w-5" /> Proposals by Status</CardTitle></CardHeader>
          <CardContent>
            {Object.keys(proposalsByStatus).length === 0 ? (
              <p className="text-gray-400 text-sm">No proposals yet</p>
            ) : (
              <div className="space-y-3">
                {Object.entries(proposalsByStatus).map(([status, count]) => (
                  <div key={status} className="flex items-center justify-between">
                    <span className="capitalize text-sm">{status}</span>
                    <div className="flex items-center gap-3">
                      <div className="w-32 h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-blue-600 rounded-full"
                          style={{ width: `${Math.min(100, ((count as number) / Math.max(...Object.values(proposalsByStatus) as number[])) * 100)}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium w-8 text-right">{count as number}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-lg flex items-center gap-2"><Layers className="h-5 w-5" /> Quick Stats</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium text-muted-foreground mb-2">Workspaces</h4>
                <p className="text-lg font-semibold">{stats.total_workspaces ?? 0}</p>
              </div>
              <div>
                <h4 className="text-sm font-medium text-muted-foreground mb-2">Plan</h4>
                <Badge className="capitalize">{stats.plan || 'free'}</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <Card>
          <CardHeader><CardTitle className="text-sm">Recent Proposals</CardTitle></CardHeader>
          <CardContent>
            {recentProposals.length === 0 ? (
              <p className="text-gray-400 text-sm">No proposals</p>
            ) : (
              <ul className="space-y-2">
                {recentProposals.map((p: { id: string; title: string; status: string }) => (
                  <li key={p.id} className="text-sm truncate flex items-center justify-between">
                    <span className="truncate">{p.title}</span>
                    <Badge variant="outline" className="text-xs ml-2 capitalize">{p.status}</Badge>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-sm">Recent Projects</CardTitle></CardHeader>
          <CardContent>
            {recentProjects.length === 0 ? (
              <p className="text-gray-400 text-sm">No projects</p>
            ) : (
              <ul className="space-y-2">
                {recentProjects.map((p: { id: string; name: string; status: string }) => (
                  <li key={p.id} className="text-sm truncate flex items-center justify-between">
                    <span className="truncate">{p.name}</span>
                    <Badge variant="outline" className="text-xs ml-2 capitalize">{p.status}</Badge>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-sm">Recent Clients</CardTitle></CardHeader>
          <CardContent>
            {recentClients.length === 0 ? (
              <p className="text-gray-400 text-sm">No clients</p>
            ) : (
              <ul className="space-y-2">
                {recentClients.map((c: { id: string; name: string; industry: string }) => (
                  <li key={c.id} className="text-sm truncate">{c.name}{c.industry ? ` (${c.industry})` : ''}</li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
