import { useParams, useNavigate } from 'react-router-dom'
import { useProposal } from '../hooks/useProposals'
import { useExportProposal } from '../hooks/useExportProposal'
import { useToast } from '../hooks/useToast'
import { Toast } from '../components/ui/Toast'
import { Button } from '../components/ui/Button'
import { Badge } from '../components/ui/Badge'
import { Skeleton } from '../components/ui/Skeleton'
import { ArrowLeft, FileText, Download, FileDown, AlertTriangle } from 'lucide-react'

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

function SVGInline({ svg }: { svg: string }) {
  if (!svg) return null
  return <div className="my-4 flex justify-center" dangerouslySetInnerHTML={{ __html: svg }} />
}

function SectionRenderer({ data, depth = 0 }: { data: unknown; depth?: number }) {
  if (data === null || data === undefined) return null
  if (typeof data === 'string') return data.includes('<svg') ? <SVGInline svg={data} /> : <p className="text-gray-700 mb-2">{data}</p>
  if (typeof data === 'boolean' || typeof data === 'number') return <span>{String(data)}</span>

  if (Array.isArray(data)) {
    if (data.length === 0) return <p className="text-gray-400 italic text-sm">None</p>
    return (
      <ul className="space-y-1 ml-4">
        {data.map((item, i) => (
          <li key={i} className="text-gray-700">
            {typeof item === 'object' ? <SectionRenderer data={item} depth={depth + 1} /> : String(item)}
          </li>
        ))}
      </ul>
    )
  }

  if (typeof data === 'object') {
    const entries = Object.entries(data as Record<string, unknown>).filter(([, v]) => v)
    if (entries.length === 0) return <p className="text-gray-400 italic text-sm">No data</p>
    return (
      <div className={`space-y-3 ${depth > 0 ? 'ml-4' : ''}`}>
        {entries.map(([key, value]) => (
          <div key={key}>
            <h4 className="text-sm font-semibold text-gray-800 capitalize mb-1">
              {key.replace(/_/g, ' ')}
            </h4>
            <SectionRenderer data={value} depth={depth + 1} />
          </div>
        ))}
      </div>
    )
  }

  return null
}

export default function ProposalDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data, isLoading, error } = useProposal(id!)
  const { exportProposal, exporting, exportError, setExportError } = useExportProposal()
  const { toasts, addToast, removeToast } = useToast()

  const proposal = data?.data
  const sections = proposal?.sections || {}
  const isErrorProposal = proposal?.status === 'error'

  const handleExport = async (fmt: 'html' | 'pdf' | 'docx' | 'pptx') => {
    try {
      await exportProposal(id!, fmt, proposal?.title)
    } catch (err) {
      addToast((err as Error)?.message || 'Export failed')
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64" />
      </div>
    )
  }

  if (!proposal || error) {
    return (
      <div className="text-center py-20">
        <p className="text-gray-500 text-lg">Proposal not found</p>
        <Button variant="outline" onClick={() => navigate('/history')} className="mt-4">
          View All Proposals
        </Button>
      </div>
    )
  }

  if (isErrorProposal) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex items-center gap-3">
          <Button variant="ghost" onClick={() => navigate('/history')}>
            <ArrowLeft className="h-4 w-4 mr-2" /> Back
          </Button>
          <h1 className="text-2xl font-bold">{proposal.title}</h1>
        </div>
        <div className="bg-red-50 border border-red-300 rounded-lg p-6 text-center">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-3" />
          <h2 className="text-xl font-bold text-red-700 mb-2">Generation Failed</h2>
          <p className="text-red-600 mb-4">
            {proposal.generation_metadata?.error as string || 'The proposal could not be generated. Please try again.'}
          </p>
          <Button variant="outline" onClick={() => navigate('/generate')}>
            Try Again
          </Button>
        </div>
      </div>
    )
  }

  const diagramData = (sections as Record<string, unknown>)['diagram_data'] as Record<string, string> | undefined

  const displaySections = Object.entries(sections).filter(
    ([key]) => !['metadata', 'cover_page', 'table_of_contents', 'diagram_data'].includes(key)
  )

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {toasts.map((t) => (
        <Toast key={t.id} id={t.id} message={t.message} type={t.type} onClose={removeToast} />
      ))}

      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-3">
          <Button variant="ghost" onClick={() => navigate('/history')}>
            <ArrowLeft className="h-4 w-4 mr-2" /> Back
          </Button>
          <div>
            <h1 className="text-2xl font-bold">{proposal.title}</h1>
            <p className="text-sm text-gray-500">
              v{proposal.version} &middot; {new Date(proposal.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>
        <Badge className={STATUS_COLORS[proposal.status] || ''}>
          {proposal.status}
        </Badge>
      </div>

      <div className="flex flex-wrap gap-2">
        <Button variant="outline" size="sm" onClick={() => handleExport('html')} disabled={exporting === 'html'}>
          <FileText className="h-4 w-4 mr-1" /> HTML
        </Button>
        <Button variant="outline" size="sm" onClick={() => handleExport('pdf')} disabled={exporting === 'pdf'}>
          <Download className="h-4 w-4 mr-1" /> PDF
        </Button>
        <Button variant="outline" size="sm" onClick={() => handleExport('docx')} disabled={exporting === 'docx'}>
          <FileDown className="h-4 w-4 mr-1" /> DOCX
        </Button>
        <Button variant="outline" size="sm" onClick={() => handleExport('pptx')} disabled={exporting === 'pptx'}>
          <FileDown className="h-4 w-4 mr-1" /> PPTX
        </Button>
      </div>

      {exportError && (
        <div className="bg-red-50 border border-red-300 rounded-lg p-4 text-red-700 text-sm">
          {exportError}
          <button onClick={() => setExportError(null)} className="ml-2 underline">Dismiss</button>
        </div>
      )}

      {diagramData && (
        <div className="space-y-8">
          {diagramData.workflow_svg && (
            <div className="bg-white rounded-lg border p-6">
              <h2 className="text-xl font-bold text-blue-700 border-b pb-2 mb-4">Solution Workflow</h2>
              <SVGInline svg={diagramData.workflow_svg} />
            </div>
          )}
          {diagramData.architecture_svg && (
            <div className="bg-white rounded-lg border p-6">
              <h2 className="text-xl font-bold text-blue-700 border-b pb-2 mb-4">System Architecture</h2>
              <SVGInline svg={diagramData.architecture_svg} />
            </div>
          )}
          {diagramData.timeline_svg && (
            <div className="bg-white rounded-lg border p-6">
              <h2 className="text-xl font-bold text-blue-700 border-b pb-2 mb-4">Project Timeline</h2>
              <SVGInline svg={diagramData.timeline_svg} />
            </div>
          )}
        </div>
      )}

      <div className="space-y-8">
        {displaySections.length === 0 ? (
          <p className="text-gray-400 italic text-center py-10">No proposal content yet.</p>
        ) : (
          displaySections.map(([key, value]) => (
            <div key={key} className="bg-white rounded-lg border p-6">
              <h2 className="text-xl font-bold text-blue-700 border-b pb-2 mb-4 capitalize">
                {key.replace(/_/g, ' ')}
              </h2>
              <SectionRenderer data={value} />
            </div>
          ))
        )}
      </div>
    </div>
  )
}
