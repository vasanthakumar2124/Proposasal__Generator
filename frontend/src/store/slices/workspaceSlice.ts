import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import type { Workspace } from '../../types/workspace'
import { workspacesApi } from '../../api/workspaces'

interface WorkspaceState {
  workspaces: Workspace[]
  currentWorkspace: Workspace | null
  loading: boolean
  error: string | null
}

const initialState: WorkspaceState = {
  workspaces: [],
  currentWorkspace: null,
  loading: false,
  error: null,
}

export const fetchWorkspaces = createAsyncThunk(
  'workspace/fetchAll',
  async (_, { rejectWithValue }) => {
    try {
      const { data } = await workspacesApi.list()
      return data.items
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch workspaces')
    }
  }
)

export const createWorkspace = createAsyncThunk(
  'workspace/create',
  async (payload: { name: string; description?: string }, { rejectWithValue }) => {
    try {
      const { data } = await workspacesApi.create(payload)
      return data
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      return rejectWithValue(error.response?.data?.detail || 'Failed to create workspace')
    }
  }
)

const workspaceSlice = createSlice({
  name: 'workspace',
  initialState,
  reducers: {
    setCurrentWorkspace(state, action: PayloadAction<Workspace | null>) {
      state.currentWorkspace = action.payload
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchWorkspaces.pending, (state) => { state.loading = true; state.error = null })
      .addCase(fetchWorkspaces.fulfilled, (state, action) => {
        state.loading = false
        state.workspaces = action.payload
      })
      .addCase(fetchWorkspaces.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })
      .addCase(createWorkspace.fulfilled, (state, action) => {
        state.workspaces.unshift(action.payload)
      })
  },
})

export const { setCurrentWorkspace } = workspaceSlice.actions
export default workspaceSlice.reducer
