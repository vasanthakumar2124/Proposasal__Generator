import { useRef, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { knowledgeApi, type SearchResult, type CollectionInfo } from '../api/knowledge'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Badge } from '../components/ui/Badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/Select'
import { Skeleton } from '../components/ui/Skeleton'
import { Upload, Search, BookOpen, FileText, Loader2 } from 'lucide-react'

const COLLECTION_LABELS: Record<string, string> = {
  industry_knowledge: 'Industry Knowledge',
  best_practices: 'Best Practices',
  case_studies: 'Case Studies',
  technology_knowledge: 'Technology',
  pricing_data: 'Pricing',
  proposal_examples: 'Proposal Examples',
  compliance_standards: 'Compliance',
  automation_patterns: 'Automation',
}

function labelFor(name: string): string {
  return COLLECTION_LABELS[name] ?? name
}

export default function KnowledgeBase() {
  const queryClient = useQueryClient()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [collection, setCollection] = useState('industry_knowledge')
  const [query, setQuery] = useState('')
  const [searched, setSearched] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const { data: collections, isLoading: loadingCollections } = useQuery({
    queryKey: ['knowledge-collections'],
    queryFn: () => knowledgeApi.listCollections(),
  })

  const uploadMutation = useMutation({
    mutationFn: (file: File) => knowledgeApi.ingestFile(file, collection),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['knowledge-collections'] })
      setSelectedFile(null)
      if (fileInputRef.current) fileInputRef.current.value = ''
    },
  })

  const searchMutation = useMutation({
    mutationFn: ({ q, c }: { q: string; c: string }) => knowledgeApi.search(q, c),
    onSuccess: (resp) => setResults(resp.data),
  })

  const runSearch = () => {
    if (!query.trim()) return
    setSearched(query)
    searchMutation.mutate({ q: query, c: collection })
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Knowledge Base</h1>
        <p className="text-muted-foreground">Upload documents and search your org's knowledge</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-4 w-4" /> Upload Document
          </CardTitle>
          <CardDescription>PDF, DOCX, TXT or Markdown — parsed and indexed into vector search</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-end gap-3">
            <div className="space-y-2">
              <label className="text-sm font-medium">Target collection</label>
              <Select value={collection} onValueChange={setCollection}>
                <SelectTrigger className="w-56">
                  <SelectValue placeholder="Collection" />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(COLLECTION_LABELS).map(([value, label]) => (
                    <SelectItem key={value} value={value}>{label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2 flex-1">
              <label className="text-sm font-medium">File</label>
              <Input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.txt,.md"
                onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
              />
            </div>
            <Button
              onClick={() => selectedFile && uploadMutation.mutate(selectedFile)}
              disabled={!selectedFile || uploadMutation.isPending}
            >
              {uploadMutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Upload className="mr-2 h-4 w-4" />}
              {uploadMutation.isPending ? 'Uploading...' : 'Upload'}
            </Button>
          </div>
          {uploadMutation.isError && (
            <p className="text-sm text-destructive">Upload failed: {(uploadMutation.error as Error).message}</p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-4 w-4" /> Test Search
          </CardTitle>
          <CardDescription>Semantic search over your org's uploaded knowledge</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-3">
            <Input
              placeholder="e.g. pricing benchmarks for ERP migration"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && runSearch()}
            />
            <Button onClick={runSearch} disabled={searchMutation.isPending || !query.trim()}>
              {searchMutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Search className="mr-2 h-4 w-4" />}
              Search
            </Button>
          </div>
          {searched && (
            <div className="space-y-2">
              {searchMutation.isPending ? (
                <div className="space-y-2">{['w-full', 'w-3/4', 'w-5/6'].map((w, i) => <Skeleton key={i} className={`h-10 ${w}`} />)}</div>
              ) : (
                results.map((r, i) => (
                  <div key={i} className="rounded-lg border p-3">
                    <div className="flex items-center justify-between">
                      <Badge variant="secondary">{labelFor(r.collection_name)}</Badge>
                      <span className="text-xs text-muted-foreground">score {r.score.toFixed(2)}</span>
                    </div>
                    <p className="mt-2 text-sm text-muted-foreground">{r.content}</p>
                  </div>
                ))
              )}
              {!searchMutation.isPending && results.length === 0 && (
                <p className="text-sm text-muted-foreground">No results found.</p>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="h-4 w-4" /> Collections
          </CardTitle>
          <CardDescription>Documents indexed per collection</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          {loadingCollections ? (
            <div className="space-y-3 p-4">
              {[1, 2, 3].map((i) => <Skeleton key={i} className="h-12 w-full" />)}
            </div>
          ) : (
            <div className="divide-y">
              {(collections?.data ?? []).map((c: CollectionInfo) => (
                <div key={c.name} className="flex items-center justify-between p-4">
                  <div className="flex items-center gap-3">
                    <FileText className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium">{labelFor(c.name)}</p>
                      <p className="text-xs text-muted-foreground">{c.vectors_count} chunks · {c.dimensions}d vectors</p>
                    </div>
                  </div>
                </div>
              ))}
              {(collections?.data ?? []).length === 0 && (
                <p className="p-4 text-sm text-muted-foreground">No collections yet — upload your first document.</p>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
