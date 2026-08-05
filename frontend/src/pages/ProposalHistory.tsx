import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useProposals, useDeleteProposal } from '../hooks/useProposals'
import { Button } from '../components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Input } from '../components/ui/Input'
import { Skeleton } from '../components/ui/Skeleton'
import { Plus, Search, Trash2, Eye, FileText } from 'lucide-react'

const STATUS_COLORS: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-800',
  generating: 'bg-yellow-100 text-yellow-800',
  processing: 'bg-yellow-100 text-yellow-800',
  review: 'bg-blue-100 text-blue-800',
  approved: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
  sent: 'bg-purple-100 text-purple-800',
  error: 'bg-red-100 text-red-800',
}

const STATUS_FILTERS = ['all', 'draft', 'review', 'approved', 'sent']

export default function ProposalHistory() {
  const navigate = useNavigate()
  const [statusFilter, setStatusFilter] = useState('all')
  const [search, setSearch] = useState('')
  const { data, isLoading } = useProposals(statusFilter !== 'all' ? statusFilter : undefined)
  const deleteProposal = useDeleteProposal()

  const proposals = data?.data?.items || []
  const filtered = search
    ? proposals.filter((p: { title: string }) =>
        p.title.toLowerCase().includes(search.toLowerCase()))
    : proposals

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <h1 className="text-2xl font-bold">Proposals</h1>
        <Button onClick={() => navigate('/generate')}>
          <Plus className="h-4 w-4 mr-2" /> New Proposal
        </Button>
      </div>

      <div className="flex flex-wrap gap-3 items-center">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search proposals..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <div className="flex gap-1">
          {STATUS_FILTERS.map((s) => (
            <Button
              key={s}
              variant={statusFilter === s ? 'default' : 'outline'}
              size="sm"
              onClick={() => setStatusFilter(s)}
            >
              {s.charAt(0).toUpperCase() + s.slice(1)}
            </Button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-20" />)}
        </div>
      ) : filtered.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <FileText className="h-12 w-12 mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500 text-lg">No proposals found</p>
            <Button onClick={() => navigate('/generate')} className="mt-4">
              Generate Your First Proposal
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {filtered.map((proposal: {
            _id: string; title: string; status: string; version: number; created_at: string
          }) => (
            <Card key={proposal._id} className="hover:shadow-md transition-shadow">
              <CardContent className="flex items-center justify-between p-4">
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold truncate">{proposal.title}</h3>
                  <div className="flex items-center gap-3 mt-1 text-sm text-gray-500">
                    <Badge className={STATUS_COLORS[proposal.status] || ''}>
                      {proposal.status}
                    </Badge>
                    <span>v{proposal.version}</span>
                    <span>{new Date(proposal.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <Button variant="outline" size="sm" onClick={() => navigate(`/proposals/${proposal._id}`)}>
                    <Eye className="h-4 w-4 mr-1" /> View
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => { if (confirm('Delete this proposal?')) deleteProposal.mutate(proposal._id) }}
                  >
                    <Trash2 className="h-4 w-4 text-red-500" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
