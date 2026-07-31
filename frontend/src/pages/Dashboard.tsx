import { useNavigate } from 'react-router-dom'
import { useAppSelector } from '../store/hooks'
import { Button } from '../components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { FileText, Users, TrendingUp, Clock, Plus, Sparkles } from 'lucide-react'

const stats = [
  { label: 'Total Proposals', value: '12', icon: FileText, change: '+2 this week' },
  { label: 'Active Clients', value: '8', icon: Users, change: '+1 this month' },
  { label: 'Win Rate', value: '75%', icon: TrendingUp, change: '+5% vs last quarter' },
  { label: 'In Review', value: '3', icon: Clock, change: '2 pending approval' },
]

const recentProposals = [
  { id: '1', name: 'Healthcare CRM Platform', client: 'MediCorp', status: 'completed', date: '2026-07-28' },
  { id: '2', name: 'ERP Modernization', client: 'BuildWell Inc.', status: 'generating', date: '2026-07-27' },
  { id: '3', name: 'Mobile Banking App', client: 'FinSecure', status: 'draft', date: '2026-07-25' },
  { id: '4', name: 'E-Learning Platform', client: 'EduGlobal', status: 'review', date: '2026-07-22' },
  { id: '5', name: 'Retail POS System', client: 'ShopMax', status: 'sent', date: '2026-07-20' },
]

export default function Dashboard() {
  const navigate = useNavigate()
  const { user } = useAppSelector((state) => state.auth)

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

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
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

      <Card>
        <CardHeader>
          <CardTitle>Recent Proposals</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {recentProposals.map((proposal) => (
              <div
                key={proposal.id}
                className="flex items-center justify-between rounded-lg border p-3 transition-colors hover:bg-muted/50 cursor-pointer"
                onClick={() => navigate(`/proposals/${proposal.id}`)}
              >
                <div className="flex-1">
                  <p className="font-medium">{proposal.name}</p>
                  <p className="text-sm text-muted-foreground">{proposal.client}</p>
                </div>
                <div className="flex items-center gap-3">
                  <Badge
                    variant={
                      proposal.status === 'completed' ? 'success' :
                      proposal.status === 'generating' ? 'warning' :
                      proposal.status === 'review' ? 'default' :
                      proposal.status === 'sent' ? 'secondary' :
                      'outline'
                    }
                  >
                    {proposal.status}
                  </Badge>
                  <span className="text-sm text-muted-foreground">{proposal.date}</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
