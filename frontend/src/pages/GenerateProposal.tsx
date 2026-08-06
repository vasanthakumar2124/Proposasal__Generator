import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useGenerateProposal } from '../hooks/useProposals'
import { proposalsApi } from '../api/proposals'
import { Button } from '../components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card'
import { Input } from '../components/ui/Input'
import { Loader2, Sparkles, ArrowLeft } from 'lucide-react'

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

export default function GenerateProposal() {
  const navigate = useNavigate()
  const generate = useGenerateProposal()
  const [clientInput, setClientInput] = useState('')
  const [domain, setDomain] = useState('')
  const [projectType, setProjectType] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!clientInput.trim() || isGenerating) return

    try {
      setIsGenerating(true)
      const result = await generate.mutateAsync({
        client_input: clientInput,
        domain: domain || undefined,
        project_type: projectType || undefined,
      })
      const id = result.data._id
      const deadline = Date.now() + 15 * 60 * 1000

      const waitViaSSE = () =>
        new Promise<{ status: string; error?: string } | null>((resolve) => {
          const token = localStorage.getItem('access_token')
          const base = import.meta.env.VITE_API_URL || '/api/v1'
          const es = new EventSource(
            `${base}/realtime/proposals/${id}/events?token=${encodeURIComponent(token || '')}`
          )
          const timer = setTimeout(() => {
            es.close()
            resolve(null)
          }, Math.max(0, deadline - Date.now()))

          const done = (status: string, error?: string) => {
            clearTimeout(timer)
            es.close()
            resolve({ status, error })
          }

          es.addEventListener('connected', (ev) => {
            try {
              const data = JSON.parse((ev as MessageEvent).data)
              if (data.status !== 'processing') done(data.status, data.error)
            } catch { /* ignore */ }
          })
          es.addEventListener('status', (ev) => {
            try {
              const data = JSON.parse((ev as MessageEvent).data)
              if (data.status !== 'processing') done(data.status, data.error)
            } catch { /* ignore */ }
          })
          es.onerror = () => {
            clearTimeout(timer)
            es.close()
            resolve(null)
          }
        })

      let outcome = await waitViaSSE()
      if (!outcome) {
        while (Date.now() < deadline) {
          await new Promise((r) => setTimeout(r, 3000))
          const p = await proposalsApi.get(id)
          const status = p.data.status
          if (status === 'processing') continue
          outcome = { status, error: (p.data as { generation_metadata?: { error?: string } }).generation_metadata?.error }
          break
        }
      }
      if (!outcome || outcome.status === 'processing') {
        throw new Error('Generation timed out after 15 minutes')
      }
      if (outcome.status === 'error') {
        throw new Error(outcome.error || 'Generation failed')
      }
      navigate(`/proposals/${id}`)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || (err as Error)?.message || 'Generation failed'
      alert(msg)
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <Button variant="ghost" onClick={() => navigate('/dashboard')} className="mb-2">
        <ArrowLeft className="h-4 w-4 mr-2" /> Back to Dashboard
      </Button>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-2xl">
            <Sparkles className="h-6 w-6 text-blue-600" />
            Generate Proposal
          </CardTitle>
          <CardDescription>
            Describe your project in detail. Our AI will analyze your requirements
            and generate a comprehensive professional proposal.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <label className="text-sm font-medium">Project Description *</label>
              <textarea
                className="w-full min-h-[200px] rounded-lg border border-gray-300 bg-white p-3 text-sm text-gray-900 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none resize-y"
                placeholder="Describe your project, goals, target audience, key features, timeline, and any other relevant details..."
                value={clientInput}
                onChange={(e) => setClientInput(e.target.value)}
                required
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Industry / Domain</label>
                <select
                  className="w-full rounded-lg border border-gray-300 bg-white p-2.5 text-sm text-gray-900 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                  value={domain}
                  onChange={(e) => setDomain(e.target.value)}
                >
                  {DOMAINS.map((d) => (
                    <option key={d.value} value={d.value} className="text-gray-900">{d.label}</option>
                  ))}
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Project Type</label>
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
            </div>

            <Button
              type="submit"
              disabled={!clientInput.trim() || isGenerating}
              className="w-full"
              size="lg"
            >
              {isGenerating ? (
                <><Loader2 className="h-5 w-5 mr-2 animate-spin" /> Generating Proposal... This can take a few minutes.</>
              ) : (
                <><Sparkles className="h-5 w-5 mr-2" /> Generate Proposal</>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
