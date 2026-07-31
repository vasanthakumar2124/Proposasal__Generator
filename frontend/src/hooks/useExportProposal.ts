import { useCallback, useState } from 'react'
import apiClient from '../api/client'

type ExportFormat = 'html' | 'pdf' | 'docx' | 'pptx'

export function useExportProposal() {
  const [exporting, setExporting] = useState<ExportFormat | null>(null)
  const [exportError, setExportError] = useState<string | null>(null)

  const exportProposal = useCallback(async (id: string, fmt: ExportFormat, title?: string) => {
    setExporting(fmt)
    setExportError(null)
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL || '/api/v1'}/proposals/${id}/export/${fmt}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
      })
      if (!res.ok) {
        let detail = 'Export failed'
        try {
          const err = await res.json()
          detail = err.detail || detail
        } catch {}
        throw new Error(detail)
      }
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${title || 'proposal'}.${fmt}`
      a.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      const msg = (err as Error)?.message || 'Export failed'
      setExportError(msg)
      throw err
    } finally {
      setExporting(null)
    }
  }, [])

  return { exportProposal, exporting, exportError, setExportError }
}
