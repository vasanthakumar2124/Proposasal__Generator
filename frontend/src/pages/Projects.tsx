import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { projectsApi } from '../api/projects'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Badge } from '../components/ui/Badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/Dialog'
import { Skeleton } from '../components/ui/Skeleton'
import { Plus, FileText, Search, LayoutDashboard } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import type { Project, ProjectCreateRequest } from '../types/project'

const projectSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  description: z.string().optional(),
  project_type: z.string().optional(),
})

export default function Projects() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [searchParams] = useSearchParams()
  const workspaceId = searchParams.get('workspace') || undefined
  const [open, setOpen] = useState(false)
  const [search, setSearch] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['projects', workspaceId],
    queryFn: () => projectsApi.list(0, 100, workspaceId),
  })

  const createMutation = useMutation({
    mutationFn: (data: ProjectCreateRequest) => projectsApi.create({ ...data, workspace_id: workspaceId || null }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      setOpen(false)
    },
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Projects</h1>
          <p className="text-muted-foreground">Manage your proposal projects</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />New Project</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Create Project</DialogTitle></DialogHeader>
            <ProjectForm onSubmit={(d) => createMutation.mutate(d)} loading={createMutation.isPending} />
          </DialogContent>
        </Dialog>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
        <Input placeholder="Search projects..." className="pl-9" value={search} onChange={(e) => setSearch(e.target.value)} />
      </div>

      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Card key={i} className="animate-pulse"><CardContent className="h-32" /></Card>
          ))}
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {(data?.data?.items ?? []).filter((p: { name: string }) =>
            (p.name ?? '').toLowerCase().includes(search.toLowerCase())
          ).map((project: Project) => (
              <Card
                key={project._id}
                className="cursor-pointer transition-colors hover:border-primary"
                onClick={() => navigate(`/projects/${project._id}`)}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-lg flex items-center gap-2">
                      <FileText className="h-5 w-5 text-primary" />
                      {project.name}
                    </CardTitle>
                    <div className="flex items-center gap-1">
                      <Badge variant={project.status === 'active' ? 'success' : 'secondary'}>
                        {project.status}
                      </Badge>
                      <Button
                        variant="outline"
                        size="icon"
                        title="Open Project Hub"
                        onClick={(e) => {
                          e.stopPropagation()
                          navigate(`/projects/${project._id}/hub`)
                        }}
                      >
                        <LayoutDashboard className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {project.description || 'No description'}
                  </p>
                  <div className="mt-3 flex gap-2">
                    <Badge variant="outline">{project.industry}</Badge>
                    <Badge variant="outline">{project.project_type}</Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
        </div>
      )}
    </div>
  )
}

function ProjectForm({ onSubmit, loading }: { onSubmit: (d: ProjectCreateRequest) => void; loading: boolean }) {
  const { register, handleSubmit, formState: { errors } } = useForm<ProjectCreateRequest>({
    resolver: zodResolver(projectSchema),
  })

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 pt-4">
      <div className="space-y-2">
        <label className="text-sm font-medium">Project Name *</label>
        <Input placeholder="e.g. Healthcare CRM" {...register('name')} />
        {errors.name && <p className="text-xs text-destructive">{errors.name.message}</p>}
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium">Description</label>
        <Input placeholder="Brief project description" {...register('description')} />
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium">Project Type</label>
        <Input placeholder="e.g. CRM, ERP, Mobile App" {...register('project_type')} />
      </div>
      <Button type="submit" className="w-full" disabled={loading}>
        {loading ? 'Creating...' : 'Create Project'}
      </Button>
    </form>
  )
}
