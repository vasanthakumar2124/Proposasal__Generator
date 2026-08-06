import apiClient from './client'

export interface CollectionInfo {
  name: string
  vectors_count: number
  dimensions: number
}

export interface SearchResult {
  content: string
  score: number
  metadata: Record<string, unknown>
  collection_name: string
}

export interface IngestResponse {
  ingested: number
  point_ids: string[]
  source?: string
}

export const knowledgeApi = {
  listCollections: () =>
    apiClient.get<CollectionInfo[]>('/rag/collections'),

  search: (query: string, collectionName = 'industry_knowledge', topK = 5) =>
    apiClient.post<SearchResult[]>('/rag/search', {
      query,
      collection_name: collectionName,
      top_k: topK,
    }),

  ingestText: (content: string, collectionName = 'industry_knowledge') =>
    apiClient.post<IngestResponse>('/rag/ingest', {
      content,
      collection_name: collectionName,
    }),

  ingestFile: (file: File, collectionName = 'industry_knowledge') => {
    const form = new FormData()
    form.append('file', file)
    form.append('collection_name', collectionName)
    return apiClient.post<IngestResponse>('/rag/ingest/file', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  deleteDocument: (collectionName: string, pointId: string) =>
    apiClient.delete<{ deleted: boolean }>(`/rag/documents/${collectionName}/${pointId}`),
}
