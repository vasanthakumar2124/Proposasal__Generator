import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { projectHubApi } from '../api/v2'
import { proposalsApi } from '../api/proposals'
import { Button } from '../components/ui/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card'
import { Input } from '../components/ui/Input'
import { Badge } from '../components/ui/Badge'
import { ArrowLeft, FileText, History, LayoutDashboard, Loader2, Save, Sparkles } from 'lucide-react'
import type { ProjectHubUpdate } from '../types/project'

const DOMAINS = [
  { value: '', label: 'Auto-detect' },
  { value: 'healthcare', label: 'Healthcare' },
  { value: 'erp', label: 'ERP' },
  { value: 'fintech', label: 'Fintech' },
  { value: 'edtech', label: 'EdTech' },
  { value: 'ecommerce', label: 'E-Commerce' },
  { value: 'logistics', label: 'Logistics' },
  { value: 'realestate', label: 'Real Estate' },
  { value: 'saas', label: 'SaaS' },
  { value: 'custom', label: 'Custom / Other' },
]

const PROJECT_TYPES = [
  { value: '', label: 'Auto-detect' },
  { value: 'web_app', label: 'Web Application' },
  { value: 'mobile_app', label: 'Mobile Application' },
  { value: 'saas_platform', label: 'SaaS Platform' },
  { value: 'ecommerce', label: 'E-Commerce' },
  { value: 'custom', label: 'Custom' },
]

export default function ProjectHub() {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['project-hub', id],
    queryFn: () => projectHubApi.getHub(id as string),
    enabled: !!id,
  })

  const [form, setForm] = useState<ProjectHubUpdate>({})
  const [clientInput, setClientInput] = useState('')
  const [domain, setDomain] = useState('')
  const [projectType, setProjectType] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [featuresText, setFeaturesText] = useState('')

  const project = data?.data?.project
  const formKey = project?._id || ''
  const initialFormKey = `${formKey}:${project?.updated_at || ''}`
  const [loadedKey, setLoadedKey] = useState('')

  if (project && loadedKey !== initialFormKey) {
    setLoadedKey(initialFormKey)
    setFeaturesText((project.key_features ?? []).join(', '))
    setForm({
      goal: project.goal || '',
      budget: project.budget ?? null,
      currency: project.currency || 'USD',
      timeline: project.timeline || '',
      notes: project.notes || '',
      status: project.status,
    })
  }

  const saveMutation = useMutation({
    mutationFn: (payload: ProjectHubUpdate) => projectHubApi.updateFields(id as string, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project-hub', id] })
      alert('Project hub saved')
    },
  })

  const handleSave = () => {
    saveMutation.mutate({
      ...form,
      key_features: featuresText
        .split(',')
        .map((f) => f.trim())
        .filter(Boolean),
    })
  }

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!clientInput.trim() || isGenerating) return
    try {
      setIsGenerating(true)
      const result = await projectHubApi.generate(
        id as string,
        {
          client_input: clientInput,
          domain: domain || undefined,
          project_type: projectType || undefined,
        },
        crypto.randomUUID()
      )
      const genId = result.data._id
      const deadline = Date.now() + 15 * 60 * 1000
      let outcome: { status: string; error?: string } | null = null
      while (Date.now() < deadline) {
        await new Promise((r) => setTimeout(r, 3000))
        const p = await proposalsApi.get(genId)
        outcome = {
          status: p.data.status,
          error: (p.data as { generation_metadata?: { error?: string } }).generation_metadata?.error,
        }
        if (outcome.status !== 'processing') break
      }
      if (!outcome || outcome.status === 'processing') {
        throw new Error('Generation timed out after 15 minutes')
      }
      if (outcome.status === 'error') {
        throw new Error(outcome.error || 'Generation failed')
      }
      navigate(`/proposals/${genId}`)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || (err as Error)?.message || 'Generation failed'
      alert(msg)
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Button variant="ghost" onClick={() => (id ? navigate(`/projects/${id}`) : navigate('/projects'))} className="mb-2 -ml-3">
            <ArrowLeft className="h-4 w-4 mr-2" /> Back to Project
          </Button>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
              <LayoutDashboard className="h-7 w-7 text-primary" />
              {isLoading || !project ? 'Project Hub' : project.name}
            </h1>
            {project && <Badge variant={project.status === 'active' ? 'success' : 'secondary'}>{project.status}</Badge>}
          </div>
          <p className="text-muted-foreground">Overview, proposals, and activity for this project</p>
        </div>
      </div>

      {isLoading || !project ? (
        <div className="grid gap-4 md:grid-cols-2">
          {[1, 2].map((i) => (
            <Card key={i} className="animate-pulse"><CardContent className="h-40" /></Card>
          ))}
        </div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><LayoutDashboard className="h-5 w-5 text-primary" /> Project Overview</CardTitle>
              <CardDescription>Capture the goal, budget, and scope that AI should use when generating proposals.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Goal</label>
                <textarea
                  className="w-full min-h-[90px] rounded-lg border border-gray-300 bg-white p-3 text-sm text-gray-900 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none resize-y"
                  placeholder="What is the client trying to achieve?"
                  value={form.goal ?? ''}
                  onChange={(e) => setForm({ ...form, goal: e.target.value })}
                />
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Budget</label>
                  <Input
                    type="number"
                    min={0}
                    placeholder="e.g. 50000"
                    value={form.budget ?? ''}
                    onChange={(e) => setForm({ ...form, budget: e.target.value === '' ? null : Number(e.target.value) })}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Currency</label>
                  <Input
                    placeholder="USD"
                    maxLength={3}
                    value={form.currency ?? ''}
                    onChange={(e) => setForm({ ...form, currency: e.target.value.toUpperCase() })}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Timeline</label>
                  <Input
                    placeholder="e.g. 6 months"
                    value={form.timeline ?? ''}
                    onChange={(e) => setForm({ ...form, timeline: e.target.value })}
                  />
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Key Features (comma separated)</label>
                <Input
                  placeholder="e.g. Role-based access, Analytics dashboard, API"
                  value={featuresText}
                  onChange={(e) => setFeaturesText(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Notes</label>
                <textarea
                  className="w-full min-h-[70px] rounded-lg border border-gray-300 bg-white p-3 text-sm text-gray-900 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none resize-y"
                  placeholder="Internal notes for the team"
                  value={form.notes ?? ''}
                  onChange={(e) => setForm({ ...form, notes: e.target.value })}
                />
              </div>
              <Button onClick={handleSave} disabled={saveMutation.isPending}>
                {saveMutation.isPending ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Save className="h-4 w-4 mr-2" />}
                Save Hub
              </Button>
            </CardContent>
          </Card>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2"><Sparkles className="h-5 w-5 text-blue-600" /> Generate Proposal for this Project</CardTitle>
                <CardDescription>Link a new AI-generated proposal to this project.</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleGenerate} className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Project Description *</label>
                    <textarea
                      className="w-full min-h-[120px] rounded-lg border border-gray-300 bg-white p-3 text-sm text-gray-900 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none resize-y"
                      placeholder="Describe the engagement scope for this proposal..."
                      value={clientInput}
                      onChange={(e) => setClientInput(e.target.value)}
                      required
                    />
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <select
                      className="w-full rounded-lg border border-gray-300 bg-white p-2.5 text-sm text-gray-900 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                      value={domain}
                      onChange={(e) => setDomain(e.target.value)}
                    >
                      {DOMAINS.map((d) => (
                        <option key={d.value} value={d.value} className="text-gray-900">{d.label}</option>
                      ))}
                    </select>
                    <select
                      className="w-full rounded-lg border border-gray-300 bg-white p-2.5 text-sm text-gray-900 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                      value={projectType}
                      onChange={(e) => setProjectType(e.target.value)}
                    >
                      {PROJECT_TYPES.map((t) => (
                        <option key={t.value} value={t.value} className="text-gray-900">{t.label}</option>
                      ))}
                    </select>
                  </div>
                  <Button type="submit" disabled={!clientInput.trim() || isGenerating} className="w-full">
                    {isGenerating ? (
                      <><Loader2 className="h-5 w-5 mr-2 animate-spin" /> Generating... This can take a few minutes.</>
                    ) : (
                      <><Sparkles className="h-5 w-5 mr-2" /> Generate Proposal</>
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg"><FileText className="h-5 w-5 text-primary" /> Proposals ({data.data.proposals.length})</CardTitle>
              </CardHeader>
              <CardContent>
                {data.data.proposals.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No proposals linked to this project yet.</p>
                ) : (
                  <ul className="space-y-2">
                    {data.data.proposals.map((p) => (
                      <li key={p._id}>
                        <button
                          type="button"
                          onClick={() => navigate(`/proposals/${p._id}`)}
                          className="w-full flex items-center justify-between rounded-lg border border-gray-200 p-3 text-left hover:border-primary hover:bg-accent/50 transition-colors"
                        >
                          <div>
                            <p className="text-sm font-medium">{p.title}</p>
                            <p className="text-xs text-muted-foreground">{p.proposal_id}</p>
                          </div>
                          <Badge variant={p.status === 'draft' ? 'success' : p.status === 'error' ? 'destructive' : 'secondary'}>
                            {p.status}
                          </Badge>
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg"><History className="h-5 w-5 text-primary" /> Recent Activity</CardTitle>
              </CardHeader>
              <CardContent>
                {data.data.activity.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No activity for this project yet.</p>
                ) : (
                  <ul className="space-y-2">
                    {data.data.activity.map((ev) => (
                      <li key={ev._id} className="rounded-lg border border-gray-200 p-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium">{ev.event_type}</span>
                          <span className="text-xs text-muted-foreground">{new Date(ev.occurred_at).toLocaleString()}</span>
                        </div>
                        {ev.payload?.title ? <p className="text-xs text-muted-foreground mt-1">{String(ev.payload.title)}</p> : null}
                      </li>
                    ))}
                  </ul>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  )
}
