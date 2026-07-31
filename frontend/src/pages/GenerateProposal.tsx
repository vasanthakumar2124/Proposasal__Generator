import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useGenerateProposal } from '../hooks/useProposals'
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!clientInput.trim()) return

    try {
      const result = await generate.mutateAsync({
        client_input: clientInput,
        domain: domain || undefined,
        project_type: projectType || undefined,
      })
      navigate(`/proposals/${result.data._id}`)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || (err as Error)?.message || 'Generation failed'
      alert(msg)
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
              disabled={!clientInput.trim() || generate.isPending}
              className="w-full"
              size="lg"
            >
              {generate.isPending ? (
                <><Loader2 className="h-5 w-5 mr-2 animate-spin" /> Generating Proposal...</>
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
