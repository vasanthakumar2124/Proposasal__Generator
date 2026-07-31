import { useEffect } from 'react'
import { X } from 'lucide-react'

interface ToastProps {
  id: string
  message: string
  type?: 'error' | 'success' | 'info'
  onClose: (id: string) => void
  duration?: number
}

const TYPE_STYLES = {
  error: 'bg-red-50 border-red-400 text-red-800',
  success: 'bg-green-50 border-green-400 text-green-800',
  info: 'bg-blue-50 border-blue-400 text-blue-800',
}

export function Toast({ id, message, type = 'error', onClose, duration = 6000 }: ToastProps) {
  useEffect(() => {
    const timer = setTimeout(() => onClose(id), duration)
    return () => clearTimeout(timer)
  }, [id, duration, onClose])

  return (
    <div className={`fixed top-4 right-4 z-50 flex items-center gap-3 border px-4 py-3 rounded-lg shadow-lg max-w-md ${TYPE_STYLES[type]}`}>
      <span className="text-sm flex-1">{message}</span>
      <button onClick={() => onClose(id)} className="shrink-0">
        <X className="h-4 w-4" />
      </button>
    </div>
  )
}
