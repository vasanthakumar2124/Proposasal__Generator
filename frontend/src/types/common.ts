export interface PaginatedResponse<T> {
  items: T[]
  total: number
  skip: number
  limit: number
  has_more: boolean
}

export interface MessageResponse {
  message: string
  status: string
}

export interface ApiError {
  detail: string
  error_code?: string
  status?: number
}
