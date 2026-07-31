import { useEffect, useState } from 'react'
import { useAppDispatch, useAppSelector } from '../../store/hooks'
import { fetchWorkspaces, setCurrentWorkspace } from '../../store/slices/workspaceSlice'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../../components/ui/Select'
import { Plus } from 'lucide-react'
import { Button } from '../../components/ui/Button'

export function WorkspaceSwitcher() {
  const dispatch = useAppDispatch()
  const { workspaces, currentWorkspace } = useAppSelector((state) => state.workspace)

  useEffect(() => {
    dispatch(fetchWorkspaces())
  }, [dispatch])

  useEffect(() => {
    if (!currentWorkspace && workspaces.length > 0) {
      const saved = localStorage.getItem('current_workspace_id')
      const found = saved ? workspaces.find((w) => w._id === saved) : null
      dispatch(setCurrentWorkspace(found || workspaces[0]))
    }
  }, [workspaces, currentWorkspace, dispatch])

  const handleChange = (id: string) => {
    const ws = workspaces.find((w) => w._id === id)
    if (ws) {
      dispatch(setCurrentWorkspace(ws))
      localStorage.setItem('current_workspace_id', id)
    }
  }

  return (
    <div className="flex items-center gap-2">
      <Select value={currentWorkspace?._id} onValueChange={handleChange}>
        <SelectTrigger className="w-[200px]">
          <SelectValue placeholder="Select workspace" />
        </SelectTrigger>
        <SelectContent>
          {workspaces.map((ws) => (
            <SelectItem key={ws._id} value={ws._id}>
              {ws.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Button variant="ghost" size="icon">
        <Plus className="h-4 w-4" />
      </Button>
    </div>
  )
}
