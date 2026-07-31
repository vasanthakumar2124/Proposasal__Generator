import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { projectsApi } from '../api/projects'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Badge } from '../components/ui/Badge'
import { Skeleton } from '../components/ui/Skeleton'
import { ArrowLeft, Plus, Sparkles } from 'lucide-react'

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const { data: project, isLoading } = useQuery({
    queryKey: ['project', id],
    queryFn: () => projectsApi.get(id!),
    enabled: !!id,
  })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-32 w-full" />
      </div>
    )
  }

  if (!project) {
    return <div>Project not found</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate('/projects')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold tracking-tight">{project.data?.name}</h1>
          <p className="text-muted-foreground">{project.data?.description}</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Plus className="mr-2 h-4 w-4" />Add Proposal
          </Button>
          <Button>
            <Sparkles className="mr-2 h-4 w-4" />Generate Proposal
          </Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Industry</CardTitle></CardHeader>
          <CardContent><p className="text-lg font-semibold capitalize">{project.data?.industry}</p></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Type</CardTitle></CardHeader>
          <CardContent><p className="text-lg font-semibold capitalize">{project.data?.project_type}</p></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Status</CardTitle></CardHeader>
          <CardContent><Badge variant="success">{project.data?.status}</Badge></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Proposals</CardTitle></CardHeader>
          <CardContent><p className="text-lg font-semibold">{project.data?.proposal_ids?.length ?? 0}</p></CardContent>
        </Card>
      </div>

      {(project.data?.proposal_ids?.length ?? 0) === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Sparkles className="mb-4 h-12 w-12 text-muted-foreground" />
            <p className="text-lg font-medium">No proposals yet</p>
            <p className="text-sm text-muted-foreground">Generate your first proposal for this project</p>
            <Button className="mt-4">
              <Sparkles className="mr-2 h-4 w-4" />Generate Proposal
            </Button>
          </CardContent>
        </Card>
      ) : null}
    </div>
  )
}
