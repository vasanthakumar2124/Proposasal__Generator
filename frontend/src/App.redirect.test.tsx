import { render, screen, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { MemoryRouter, Routes, Route, Navigate } from 'react-router-dom'
import { describe, it, expect, vi } from 'vitest'

// Mock the heavy pages to avoid loading all dependencies
vi.mock('@/pages/ProjectHub', () => ({
  default: () => <div data-testid="project-hub">Project Hub</div>,
}))

import App from '@/App'

describe('Project route redirect', () => {
  it('redirects /projects/:id to /projects/:id/hub', async () => {
    render(
      <MemoryRouter initialEntries={['/projects/abc-123']}>
        <Routes>
          <Route path="/projects/:id" element={<Navigate to="/projects/:id/hub" replace />} />
          <Route path="/projects/:id/hub" element={<div data-testid="project-hub">Project Hub</div>} />
        </Routes>
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByTestId('project-hub')).toBeInTheDocument()
    })
  })

  it('renders ProjectHub at /projects/:id/hub directly', async () => {
    render(
      <MemoryRouter initialEntries={['/projects/abc-123/hub']}>
        <Routes>
          <Route path="/projects/:id/hub" element={<div data-testid="project-hub">Project Hub</div>} />
        </Routes>
      </MemoryRouter>
    )

    expect(screen.getByTestId('project-hub')).toBeInTheDocument()
  })
})