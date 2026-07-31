import { useEffect, type ReactNode } from 'react'
import { useAppDispatch, useAppSelector } from '../store/hooks'
import { fetchCurrentUser } from '../store/slices/authSlice'

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const dispatch = useAppDispatch()
  const { accessToken, isAuthenticated } = useAppSelector((state) => state.auth)

  useEffect(() => {
    if (accessToken && isAuthenticated) {
      dispatch(fetchCurrentUser())
    }
  }, [dispatch, accessToken, isAuthenticated])

  return <>{children}</>
}
