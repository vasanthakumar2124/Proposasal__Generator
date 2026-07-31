# ProposalCraft AI — Production Architecture

## 1. Product Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Landing  │  │  Dashboard│  │Proposal  │  │  Admin   │   │
│  │   Page   │  │          │  │  Viewer  │  │  Panel   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            React SPA (Vite + TypeScript)              │   │
│  └──────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    API Gateway (FastAPI)                      │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐   │
│  │ Auth │ │Proposal│ │  AI  │ │  Org  │ │Billing│ │Admin │   │
│  │ API  │ │  API  │ │  API  │ │  API  │ │  API  │ │  API  │   │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘   │
├─────────────────────────────────────────────────────────────┤
│                    Service Layer                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │Auth Service│ │Proposal  │ │  Org     │ │Billing   │      │
│  │          │ │Service   │ │ Service  │ │ Service  │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
├─────────────────────────────────────────────────────────────┤
│                    Business Engine Layer                      │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │
│  │Industry│ │Module  │ │Feature │ │Pricing │ │Timeline │   │
│  │ Engine │ │ Engine │ │ Engine │ │ Engine │ │ Engine  │   │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘   │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │
│  │  ROI   │ │  Risk  │ │  Team  │ │Diagram │ │Template│   │
│  │ Engine │ │ Engine │ │ Engine │ │ Engine │ │ Engine  │   │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    AI Agent Layer                             │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐   │
│  │ Requirement │  │Proposal     │  │ Proposal Review   │   │
│  │   Agent     │  │ Writer Agent │  │    Agent         │   │
│  └──────┬──────┘  └──────┬──────┘  └──────────────────┘   │
│         │                │                                   │
│         └──────┬─────────┘                                   │
│                ▼                                              │
│         ┌─────────────┐                                       │
│         │  RAG Agent  │                                       │
│         └──────┬──────┘                                       │
│                ▼                                              │
│         ┌─────────────┐                                       │
│         │    Cache    │                                       │
│         └─────────────┘                                       │
├─────────────────────────────────────────────────────────────┤
│                    Data Layer                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ MongoDB  │  │  Qdrant  │  │  Redis   │  │   S3    │   │
│  │(Primary) │  │(Vector)  │  │ (Cache)  │  │(Files)  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 2. System Design — Component Diagram

### Core Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| API Gateway | FastAPI | Auth, routing, rate limiting, request validation |
| Auth Service | JWT + OAuth | Authentication, RBAC, session management |
| Proposal Service | FastAPI | CRUD, versioning, collaboration |
| AI Service | LangGraph | Agent orchestration pipeline |
| Business Engines | Python | Deterministic proposal calculations |
| RAG Engine | Qdrant + Transformers | Vector search, context retrieval |
| Export Service | WeasyPrint/Puppeteer | PDF, DOCX, PPTX generation |
| Diagram Engine | Mermaid + Graphviz | Dynamic diagram generation |
| Background Jobs | Celery + Redis | Async processing, email, exports |
| Billing | Stripe | Subscription management, payments |
| Analytics | Custom + MongoDB | Usage tracking, proposal analytics |

## 3. Clean Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                  API Layer (routes/)                      │
│  FastAPI routers — thin controllers, no business logic   │
├─────────────────────────────────────────────────────────┤
│                  Service Layer (services/)                │
│  Orchestration, coordination, transaction management     │
├─────────────────────────────────────────────────────────┤
│                  Domain Layer (domain/)                   │
│  Entities, value objects, business rules, interfaces     │
├─────────────────────────────────────────────────────────┤
│               Infrastructure Layer (infrastructure/)      │
│  DB adapters, external APIs, cache, file storage         │
├─────────────────────────────────────────────────────────┤
│               Engine Layer (engines/)                     │
│  Pure Python business logic, no I/O                      │
├─────────────────────────────────────────────────────────┤
│               AI Agent Layer (agents/)                    │
│  LLM orchestration via LangGraph                         │
└─────────────────────────────────────────────────────────┘
```

### Dependency Rule
- API Layer → Service Layer → Domain Layer ← Infrastructure Layer
- Engines are stateless — called by Service Layer
- Agents are stateful — orchestrated by LangGraph workflows

## 4. Database Design — MongoDB Collections

### Core Collections

```json
// organizations
{
  "_id": ObjectId,
  "name": "Acme Corp",
  "slug": "acme-corp",
  "plan": "enterprise",         // free | starter | professional | enterprise
  "features": ["white_label", "api_access"],
  "branding": { "logo": "", "primary_color": "", "secondary_color": "" },
  "settings": { "default_locale": "en", "timezone": "UTC" },
  "status": "active",
  "created_at": ISODate,
  "updated_at": ISODate
}

// users
{
  "_id": ObjectId,
  "email": "user@acme.com",
  "password_hash": "...",
  "name": "John Doe",
  "organization_id": ObjectId,
  "role": "admin",              // admin | member | viewer
  "permissions": ["proposal:create", "proposal:edit", ...],
  "auth_provider": "email",     // email | google | github
  "auth_provider_id": "",
  "status": "active",
  "last_login": ISODate,
  "created_at": ISODate,
  "updated_at": ISODate
}

// workspaces
{
  "_id": ObjectId,
  "organization_id": ObjectId,
  "name": "Q1 Proposals",
  "description": "",
  "created_by": ObjectId,
  "members": [ObjectId, ...],
  "created_at": ISODate,
  "updated_at": ISODate
}

// clients
{
  "_id": ObjectId,
  "organization_id": ObjectId,
  "name": "TechCorp Inc.",
  "industry": "healthcare",
  "contact_name": "Sarah Lee",
  "contact_email": "sarah@techcorp.com",
  "contact_phone": "",
  "address": "",
  "notes": "",
  "created_by": ObjectId,
  "created_at": ISODate,
  "updated_at": ISODate
}

// projects
{
  "_id": ObjectId,
  "organization_id": ObjectId,
  "workspace_id": ObjectId,
  "client_id": ObjectId,
  "name": "Healthcare CRM Platform",
  "description": "",
  "industry": "healthcare",
  "project_type": "crm",
  "status": "draft",
  "proposal_ids": [ObjectId, ...],
  "created_by": ObjectId,
  "created_at": ISODate,
  "updated_at": ISODate
}

// requirements
{
  "_id": ObjectId,
  "organization_id": ObjectId,
  "project_id": ObjectId,
  "raw_text": "Client needs a CRM for healthcare...",
  "structured": {
    "project_name": "HealthCRM",
    "domain": "healthcare",
    "objective": "",
    "target_users": [],
    "functional_requirements": [],
    "non_functional_requirements": []
  },
  "created_by": ObjectId,
  "created_at": ISODate,
  "updated_at": ISODate
}

// proposal_contexts
{
  "_id": ObjectId,
  "organization_id": ObjectId,
  "project_id": ObjectId,
  "requirement_id": ObjectId,
  "industry_data": {},
  "module_data": {},
  "feature_data": {},
  "automation_data": {},
  "tech_stack_data": {},
  "pricing_data": {},
  "timeline_data": {},
  "team_data": {},
  "risk_data": {},
  "roi_data": {},
  "created_at": ISODate,
  "updated_at": ISODate
}

// proposals
{
  "_id": ObjectId,
  "organization_id": ObjectId,
  "project_id": ObjectId,
  "client_id": ObjectId,
  "workspace_id": ObjectId,
  "version": 1,
  "status": "draft",           // draft | review | approved | rejected | sent
  "sections": {
    "cover_page": {},
    "executive_summary": {},
    "client_understanding": {},
    "proposed_solution": {},
    "modules": [],
    "features": {},
    "technology_stack": {},
    "architecture": {},
    "workflow": {},
    "timeline": {},
    "pricing": {},
    "commercials": {},
    "roi": {},
    "risks": [],
    "sla": {},
    "support": {},
    "conclusion": {}
  },
  "ai_generated": true,
  "generation_metadata": {
    "model": "llama-3.3-70b",
    "tokens_used": 4500,
    "cost": 0.0027,
    "duration_ms": 12000
  },
  "created_by": ObjectId,
  "approved_by": null,
  "created_at": ISODate,
  "updated_at": ISODate
}

// proposal_versions
{
  "_id": ObjectId,
  "proposal_id": ObjectId,
  "version": 2,
  "sections": {},
  "changes_summary": "Updated pricing section",
  "created_by": ObjectId,
  "created_at": ISODate
}

// templates
{
  "_id": ObjectId,
  "organization_id": ObjectId,  // null = system template
  "name": "Enterprise Software Proposal",
  "description": "",
  "industry": null,
  "sections_config": {
    "executive_summary": {"enabled": true, "order": 1},
    "client_understanding": {"enabled": true, "order": 2},
    ...
  },
  "styling": {},
  "is_system": true,
  "created_at": ISODate,
  "updated_at": ISODate
}

// knowledge_base
{
  "_id": ObjectId,
  "organization_id": ObjectId,
  "type": "case_study",         // case_study | best_practice | technology | pricing | industry
  "title": "",
  "content": "",
  "metadata": {
    "industry": "healthcare",
    "tags": ["crm", "hipaa"]
  },
  "embedding_id": "qdrant-uuid",
  "created_by": ObjectId,
  "created_at": ISODate,
  "updated_at": ISODate
}

// subscriptions
{
  "_id": ObjectId,
  "organization_id": ObjectId,
  "stripe_customer_id": "",
  "stripe_subscription_id": "",
  "plan": "professional",
  "status": "active",
  "current_period_start": ISODate,
  "current_period_end": ISODate,
  "seats": 5,
  "created_at": ISODate,
  "updated_at": ISODate
}

// usage
{
  "_id": ObjectId,
  "organization_id": ObjectId,
  "user_id": ObjectId,
  "action": "proposal_generate",
  "tokens_used": 4500,
  "cost": 0.0027,
  "metadata": {"proposal_id": ObjectId, "model": "llama-3.3-70b"},
  "created_at": ISODate
}

// audit_logs
{
  "_id": ObjectId,
  "organization_id": ObjectId,
  "user_id": ObjectId,
  "action": "proposal.create",
  "resource_type": "proposal",
  "resource_id": ObjectId,
  "details": {},
  "ip_address": "",
  "user_agent": "",
  "created_at": ISODate
}
```

## 5. AI Architecture — LangGraph Agents

### Agent Pipeline

```
User Input (requirement text)
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  Requirement Agent (LLM — 1 call)                        │
│  Extracts structured info from raw requirement text      │
│  Output: requirement_json (Pydantic model)               │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  RAG Agent (LLM — 1 call only when needed)              │
│  Queries Qdrant with hybrid search                      │
│  Reranks results with CrossEncoder                      │
│  Compresses context (removes duplicates, low relevance) │
│  Output: compressed_context                             │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  Business Engines (Python — 0 LLM calls)                │
│  IndustryEngine → ModuleEngine → FeatureEngine          │
│  AutomationEngine → IntegrationEngine                   │
│  TechStackEngine → TimelineEngine                       │
│  PricingEngine → TeamEngine → ROIEngine                 │
│  RiskEngine → CommercialEngine → SupportEngine          │
│  SLAEngine → DiagramEngine                              │
│  Output: proposal_context (fully structured)            │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  Proposal Writer Agent (LLM — 1 call)                   │
│  Takes structured context + engines output              │
│  Generates full proposal text with all sections         │
│  Output: proposal_content (markdown + structured)       │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  Proposal Reviewer Agent (LLM — 1 call)                 │
│  Reviews grammar, tone, completeness, formatting        │
│  Suggests improvements                                  │
│  Output: review_feedback + final_proposal               │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  Export Engine (Python — 0 LLM calls)                  │
│  Generates HTML, PDF, DOCX, PPTX                       │
│  Applies branding, watermark, page numbers             │
│  Generates diagrams via Mermaid                        │
└─────────────────────────────────────────────────────────┘
```

**Total LLM calls per proposal: 3-4 (Requirement + RAG + Writer + optional Review)**

## 6. Business Engines (0 LLM calls)

| Engine | Responsibility | Data Source |
|--------|---------------|-------------|
| IndustryEngine | Maps project domain to industry patterns, compliance needs | MongoDB `industries` collection |
| ModuleEngine | Recommends modules based on industry + project type | Module knowledge base |
| FeatureEngine | Generates feature matrix from modules + industry standards | Feature patterns library |
| AutomationEngine | Identifies automation opportunities per industry | Automation patterns |
| IntegrationEngine | Recommends integrations (ERP, CRM, payment, etc.) | Integration catalog |
| TechStackEngine | Recommends technology stack per project type | Tech stack knowledge base |
| TimelineEngine | Generates timeline with phases, milestones, dependencies | Effort estimation data |
| PricingEngine | Calculates pricing based on modules, effort, complexity | Pricing rules + hourly rates |
| TeamEngine | Recommends team composition per project scope | Resource profiles |
| ROIEngine | Calculates ROI, payback period, TCO | Industry benchmarks |
| RiskEngine | Identifies risks per industry + project type | Risk patterns |
| CommercialEngine | Generates payment terms, commercials | Pricing config |
| SupportEngine | Generates support plan tiers | Support packages |
| SLAEngine | Generates SLA tiers based on project criticality | SLA templates |
| DiagramEngine | Generates all diagrams via Mermaid | Context data |
| TemplateEngine | Applies proposal template styling | Template config |
| ProposalContextBuilder | Assembles final context for LLM writer | All engine outputs |

## 7. RAG Architecture

### Collections (Qdrant)

| Collection | Content | Chunk Size | Embedding Model |
|-----------|---------|------------|-----------------|
| proposal_examples | High-quality proposal examples | 512 tokens | BAAI/bge-base-en-v1.5 |
| industry_knowledge | Industry-specific patterns | 384 tokens | BAAI/bge-small-en-v1.5 |
| technology_knowledge | Tech stack descriptions | 256 tokens | BAAI/bge-small-en-v1.5 |
| pricing_data | Pricing benchmarks | 256 tokens | BAAI/bge-small-en-v1.5 |
| case_studies | Implementation case studies | 512 tokens | BAAI/bge-base-en-v1.5 |
| best_practices | Development best practices | 384 tokens | BAAI/bge-small-en-v1.5 |
| automation_patterns | Automation opportunities | 256 tokens | BAAI/bge-small-en-v1.5 |
| compliance_standards | Government/industry compliance | 512 tokens | BAAI/bge-base-en-v1.5 |

### Search Pipeline

```
Query → Embedding → Hybrid Search (Dense + Sparse)
    → Metadata Filtering (industry, project_type)
    → CrossEncoder Reranking (top 20 → top 5)
    → Context Compression (remove redundant chunks)
    → Final Context (≤2000 tokens for LLM)
```

## 8. API Design — RESTful Endpoints

### Authentication
```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout
GET    /api/v1/auth/me
PUT    /api/v1/auth/me
POST   /api/v1/auth/forgot-password
POST   /api/v1/auth/reset-password
POST   /api/v1/auth/google
```

### Organizations
```
GET    /api/v1/orgs
GET    /api/v1/orgs/{id}
PUT    /api/v1/orgs/{id}
GET    /api/v1/orgs/{id}/members
POST   /api/v1/orgs/{id}/members
PUT    /api/v1/orgs/{id}/members/{userId}
DELETE /api/v1/orgs/{id}/members/{userId}
```

### Workspaces
```
GET    /api/v1/workspaces
POST   /api/v1/workspaces
GET    /api/v1/workspaces/{id}
PUT    /api/v1/workspaces/{id}
DELETE /api/v1/workspaces/{id}
```

### Clients
```
GET    /api/v1/clients
POST   /api/v1/clients
GET    /api/v1/clients/{id}
PUT    /api/v1/clients/{id}
DELETE /api/v1/clients/{id}
```

### Projects
```
GET    /api/v1/projects
POST   /api/v1/projects
GET    /api/v1/projects/{id}
PUT    /api/v1/projects/{id}
DELETE /api/v1/projects/{id}
```

### Requirements
```
POST   /api/v1/requirements/analyze    (LLM)
GET    /api/v1/requirements/{id}
PUT    /api/v1/requirements/{id}
```

### Proposals
```
GET    /api/v1/proposals
POST   /api/v1/proposals
GET    /api/v1/proposals/{id}
PUT    /api/v1/proposals/{id}
DELETE /api/v1/proposals/{id}
POST   /api/v1/proposals/{id}/generate    (triggers AI pipeline)
POST   /api/v1/proposals/{id}/duplicate
POST   /api/v1/proposals/{id}/archive
PUT    /api/v1/proposals/{id}/sections/{section}
GET    /api/v1/proposals/{id}/versions
GET    /api/v1/proposals/{id}/versions/{versionId}
POST   /api/v1/proposals/{id}/restore/{versionId}
POST   /api/v1/proposals/{id}/approve
POST   /api/v1/proposals/{id}/submit
POST   /api/v1/proposals/{id}/share
```

### AI Features
```
POST   /api/v1/ai/generate          (full pipeline)
POST   /api/v1/ai/rewrite           (rewrite section)
POST   /api/v1/ai/improve           (improve section)
POST   /api/v1/ai/summarize         (summarize proposal)
POST   /api/v1/ai/translate         (translate proposal)
POST   /api/v1/ai/review            (review proposal)
POST   /api/v1/ai/score             (score proposal)
POST   /api/v1/ai/optimize          (optimize section)
POST   /api/v1/ai/compare           (compare versions)
```

### Exports
```
POST   /api/v1/exports/pdf
POST   /api/v1/exports/docx
POST   /api/v1/exports/html
POST   /api/v1/exports/pptx
GET    /api/v1/exports/{id}/download
```

### Templates
```
GET    /api/v1/templates
POST   /api/v1/templates
GET    /api/v1/templates/{id}
PUT    /api/v1/templates/{id}
DELETE /api/v1/templates/{id}
```

### Knowledge Base
```
GET    /api/v1/knowledge
POST   /api/v1/knowledge/upload
GET    /api/v1/knowledge/{id}
DELETE /api/v1/knowledge/{id}
POST   /api/v1/knowledge/search
POST   /api/v1/knowledge/ingest
```

### Billing
```
GET    /api/v1/billing/plan
GET    /api/v1/billing/invoices
POST   /api/v1/billing/create-checkout-session
POST   /api/v1/billing/cancel
POST   /api/v1/billing/webhook
```

### Admin
```
GET    /api/v1/admin/orgs
GET    /api/v1/admin/orgs/{id}
PUT    /api/v1/admin/orgs/{id}
GET    /api/v1/admin/usage
GET    /api/v1/admin/analytics
GET    /api/v1/admin/logs
```

### Analytics
```
GET    /api/v1/analytics/proposals
GET    /api/v1/analytics/usage
GET    /api/v1/analytics/users
GET    /api/v1/analytics/revenue
GET    /api/v1/analytics/dashboard
```

## 9. Frontend Architecture

### Component Tree
```
App
├── Layout
│   ├── Sidebar
│   │   ├── NavLinks
│   │   ├── WorkspaceSwitcher
│   │   └── UserMenu
│   ├── Topbar
│   │   ├── Search
│   │   ├── Notifications
│   │   └── ProfileDropdown
│   └── MainContent
├── Pages
│   ├── Landing
│   │   ├── Hero
│   │   ├── Features
│   │   ├── Templates
│   │   ├── Pricing
│   │   └── Footer
│   ├── Auth
│   │   ├── LoginForm
│   │   ├── RegisterForm
│   │   └── ForgotPassword
│   ├── Dashboard
│   │   ├── StatsCards
│   │   ├── RecentProposals
│   │   ├── ActivityFeed
│   │   └── QuickActions
│   ├── Workspace
│   │   ├── ProjectList
│   │   ├── ClientList
│   │   └── KanbanBoard
│   ├── ProposalGenerator
│   │   ├── RequirementForm
│   │   ├── ClientSelect
│   │   ├── TemplateSelect
│   │   ├── ProgressStepper
│   │   └── GenerationPreview
│   ├── ProposalViewer
│   │   ├── ProposalNav
│   │   ├── SectionRenderer
│   │   ├── DiagramRenderer (Mermaid)
│   │   ├── ChartRenderer (Recharts)
│   │   ├── PricingTable
│   │   └── ExportMenu
│   ├── ProposalEditor
│   │   ├── RichTextEditor
│   │   ├── SectionEditor
│   │   ├── DragDropSection
│   │   └── AIAssistant
│   ├── Settings
│   │   ├── Profile
│   │   ├── Organization
│   │   ├── Branding
│   │   ├── Billing
│   │   └── Members
│   ├── KnowledgeBase
│   │   ├── DocumentList
│   │   ├── UploadForm
│   │   └── SearchResults
│   └── Admin
│       ├── OrganizationList
│       ├── UsageDashboard
│       ├── AuditLogs
│       └── SystemHealth
└── Shared Components
    ├── DataTable
    ├── Modal
    ├── Toast
    ├── LoadingSpinner
    ├── EmptyState
    ├── ErrorBoundary
    ├── ConfirmDialog
    └── FileUpload
```

### State Management (Redux Toolkit)
```
store/
├── authSlice         — user, token, org
├── workspaceSlice    — current workspace, projects
├── proposalSlice     — proposals, current proposal
├── clientSlice       — clients
├── templateSlice     — templates
├── notificationSlice — notifications
├── uiSlice           — sidebar, modals, theme
└── adminSlice        — admin data
```

### Data Fetching (React Query)
```
Query keys:
  ['workspaces']
  ['projects', workspaceId]
  ['clients', orgId]
  ['proposals', projectId]
  ['proposal', proposalId]
  ['proposal', proposalId, 'versions']
  ['templates']
  ['knowledge', query]
  ['analytics', dashboard]
  ['usage']

Mutations:
  generateProposal
  updateProposal
  deleteProposal
  exportProposal
  uploadDocument
  ...
```

## 10. Folder Structure — Production Ready

### Backend (backend/)
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                          # FastAPI app factory
│   ├── dependencies.py                   # Global DI
│   │
│   ├── api/                             # API Layer
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── api.py                   # Router aggregator
│   │   │   ├── auth.py                  # Auth endpoints
│   │   │   ├── users.py                 # User endpoints
│   │   │   ├── organizations.py         # Org endpoints
│   │   │   ├── workspaces.py            # Workspace endpoints
│   │   │   ├── clients.py               # Client endpoints
│   │   │   ├── projects.py              # Project endpoints
│   │   │   ├── proposals.py             # Proposal CRUD
│   │   │   ├── proposal_ai.py           # AI generation endpoints
│   │   │   ├── proposal_export.py       # Export endpoints
│   │   │   ├── templates.py             # Template endpoints
│   │   │   ├── knowledge.py             # Knowledge base endpoints
│   │   │   ├── billing.py               # Billing endpoints
│   │   │   ├── admin.py                 # Admin endpoints
│   │   │   ├── analytics.py             # Analytics endpoints
│   │   │   └── webhooks.py              # Stripe webhooks
│   │   └── deps.py                      # Route dependencies
│   │
│   ├── schemas/                         # Pydantic request/response
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── organization.py
│   │   ├── workspace.py
│   │   ├── client.py
│   │   ├── project.py
│   │   ├── proposal.py
│   │   ├── template.py
│   │   ├── knowledge.py
│   │   ├── billing.py
│   │   ├── analytics.py
│   │   ├── ai.py                        # AI request/response schemas
│   │   └── common.py                    # Pagination, filters, etc.
│   │
│   ├── domain/                          # Domain Layer (business entities)
│   │   ├── __init__.py
│   │   ├── entities/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── organization.py
│   │   │   ├── workspace.py
│   │   │   ├── client.py
│   │   │   ├── project.py
│   │   │   ├── proposal.py
│   │   │   ├── template.py
│   │   │   └── knowledge.py
│   │   ├── value_objects/
│   │   │   ├── __init__.py
│   │   │   ├── money.py
│   │   │   ├── address.py
│   │   │   ├── email.py
│   │   │   ├── phone.py
│   │   │   ├── date_range.py
│   │   │   └── permissions.py
│   │   ├── interfaces/                  # Repository interfaces
│   │   │   ├── __init__.py
│   │   │   ├── user_repo.py
│   │   │   ├── org_repo.py
│   │   │   ├── proposal_repo.py
│   │   │   └── ...
│   │   └── exceptions.py
│   │
│   ├── services/                        # Service Layer
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── organization_service.py
│   │   ├── workspace_service.py
│   │   ├── client_service.py
│   │   ├── project_service.py
│   │   ├── proposal_service.py
│   │   ├── proposal_generation_service.py
│   │   ├── export_service.py
│   │   ├── template_service.py
│   │   ├── knowledge_service.py
│   │   ├── billing_service.py
│   │   ├── analytics_service.py
│   │   └── notification_service.py
│   │
│   ├── engines/                         # Business Engines (Pure Python)
│   │   ├── __init__.py
│   │   ├── base_engine.py               # Abstract base
│   │   ├── industry_engine.py
│   │   ├── module_engine.py
│   │   ├── feature_engine.py
│   │   ├── automation_engine.py
│   │   ├── integration_engine.py
│   │   ├── tech_stack_engine.py
│   │   ├── timeline_engine.py
│   │   ├── pricing_engine.py
│   │   ├── team_engine.py
│   │   ├── roi_engine.py
│   │   ├── risk_engine.py
│   │   ├── commercial_engine.py
│   │   ├── support_engine.py
│   │   ├── sla_engine.py
│   │   ├── diagram_engine.py
│   │   ├── template_engine.py
│   │   └── proposal_context_builder.py
│   │
│   ├── agents/                          # AI Agent Layer
│   │   ├── __init__.py
│   │   ├── requirement_agent.py
│   │   ├── rag_agent.py
│   │   ├── proposal_writer_agent.py
│   │   └── proposal_reviewer_agent.py
│   │
│   ├── graph/                           # LangGraph Workflow
│   │   ├── __init__.py
│   │   ├── state.py
│   │   ├── nodes.py
│   │   ├── edges.py
│   │   └── workflow.py
│   │
│   ├── llm/                             # LLM Infrastructure
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── cache.py
│   │   ├── models.py                    # Model configs, cost mapping
│   │   ├── tokenizer.py                 # Token counting
│   │   └── prompts/
│   │       ├── __init__.py
│   │       ├── requirement.txt
│   │       ├── rag_formatter.txt
│   │       ├── proposal_writer.txt
│   │       ├── proposal_reviewer.txt
│   │       ├── rewrite.txt
│   │       ├── improve.txt
│   │       ├── summarize.txt
│   │       └── translate.txt
│   │
│   ├── rag/                             # RAG Infrastructure
│   │   ├── __init__.py
│   │   ├── client.py                    # Qdrant client
│   │   ├── embeddings.py                # Embedding models
│   │   ├── retriever.py                 # Search + rerank + compress
│   │   ├── ingestor.py                  # Document ingestion pipeline
│   │   ├── chunker.py                   # Text splitting strategies
│   │   ├── reranker.py                  # CrossEncoder reranker
│   │   └── collections.py              # Collection configs
│   │
│   ├── infrastructure/                  # Infrastructure Layer
│   │   ├── __init__.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── mongodb.py               # Motor client
│   │   │   ├── redis.py                 # Redis client
│   │   │   └── mongo_repositories/      # Repository implementations
│   │   │       ├── __init__.py
│   │   │       ├── user_repo.py
│   │   │       ├── org_repo.py
│   │   │       ├── proposal_repo.py
│   │   │       └── ...
│   │   ├── cache/
│   │   │   ├── __init__.py
│   │   │   ├── redis_cache.py
│   │   │   └── memory_cache.py
│   │   ├── storage/
│   │   │   ├── __init__.py
│   │   │   ├── local.py
│   │   │   ├── s3.py
│   │   │   └── interfaces.py
│   │   ├── payment/
│   │   │   ├── __init__.py
│   │   │   ├── stripe_client.py
│   │   │   └── interfaces.py
│   │   ├── email/
│   │   │   ├── __init__.py
│   │   │   ├── sendgrid_client.py
│   │   │   └── templates/
│   │   ├── export/
│   │   │   ├── __init__.py
│   │   │   ├── pdf_exporter.py
│   │   │   ├── docx_exporter.py
│   │   │   ├── html_exporter.py
│   │   │   ├── pptx_exporter.py
│   │   │   └── base.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── jwt.py
│   │   │   ├── oauth.py
│   │   │   └── password.py
│   │   ├── logging/
│   │   │   ├── __init__.py
│   │   │   ├── logger.py
│   │   │   └── audit.py
│   │   └── monitoring/
│   │       ├── __init__.py
│   │       ├── metrics.py
│   │       └── tracing.py
│   │
│   ├── tasks/                           # Celery Tasks
│   │   ├── __init__.py
│   │   ├── celery_app.py
│   │   ├── proposal_tasks.py
│   │   ├── export_tasks.py
│   │   ├── email_tasks.py
│   │   ├── knowledge_tasks.py
│   │   └── cleanup_tasks.py
│   │
│   └── config/                          # Configuration
│       ├── __init__.py
│       ├── settings.py
│       ├── logging_config.py
│       └── constants.py
│
├── data/                                # Data files
│   ├── knowledge/                       # Seed knowledge base
│   │   ├── industries/
│   │   ├── technologies/
│   │   ├── pricing/
│   │   ├── case_studies/
│   │   └── templates/
│   └── migrations/                      # MongoDB migrations
│       └── 001_initial_indexes.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── engines/
│   │   ├── services/
│   │   └── domain/
│   ├── integration/
│   │   ├── api/
│   │   └── repositories/
│   └── fixtures/
│       ├── users.json
│       ├── proposals.json
│       └── knowledge.json
│
├── scripts/
│   ├── seed_knowledge.py
│   ├── create_indexes.py
│   └── migrate.py
│
├── alembic/                             # For DB migrations (if needed)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── Makefile
└── .env.example
```

### Frontend (frontend/)
```
frontend/
├── public/
│   ├── favicon.svg
│   └── icons.svg
│
├── src/
│   ├── main.tsx                          # Entry point
│   ├── App.tsx                           # Router + providers
│   ├── vite-env.d.ts
│   │
│   ├── api/                              # API layer
│   │   ├── client.ts                     # Axios instance with interceptors
│   │   ├── auth.ts                       # Auth API calls
│   │   ├── proposals.ts                  # Proposal API calls
│   │   ├── clients.ts
│   │   ├── workspaces.ts
│   │   ├── templates.ts
│   │   ├── knowledge.ts
│   │   ├── billing.ts
│   │   ├── admin.ts
│   │   ├── analytics.ts
│   │   ├── exports.ts
│   │   └── ai.ts                         # AI feature API calls
│   │
│   ├── store/                            # Redux Toolkit
│   │   ├── index.ts
│   │   ├── slices/
│   │   │   ├── authSlice.ts
│   │   │   ├── workspaceSlice.ts
│   │   │   ├── proposalSlice.ts
│   │   │   ├── clientSlice.ts
│   │   │   ├── templateSlice.ts
│   │   │   ├── notificationSlice.ts
│   │   │   ├── uiSlice.ts
│   │   │   └── adminSlice.ts
│   │   └── hooks.ts
│   │
│   ├── hooks/                            # Custom hooks
│   │   ├── useAuth.ts
│   │   ├── useProposals.ts
│   │   ├── useClients.ts
│   │   ├── useWorkspaces.ts
│   │   ├── useDebounce.ts
│   │   ├── useMediaQuery.ts
│   │   └── useOnClickOutside.ts
│   │
│   ├── lib/                              # Utility functions
│   │   ├── utils.ts
│   │   ├── format.ts
│   │   ├── validators.ts
│   │   └── constants.ts
│   │
│   ├── types/                            # TypeScript types
│   │   ├── index.ts
│   │   ├── auth.ts
│   │   ├── proposal.ts
│   │   ├── client.ts
│   │   ├── workspace.ts
│   │   ├── template.ts
│   │   ├── knowledge.ts
│   │   ├── billing.ts
│   │   ├── analytics.ts
│   │   ├── api.ts                        # API response types
│   │   └── common.ts                     # Pagination, etc.
│   │
│   ├── pages/
│   │   ├── Landing.tsx
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── ForgotPassword.tsx
│   │   ├── Dashboard.tsx
│   │   ├── Workspace.tsx
│   │   ├── Projects.tsx
│   │   ├── ProjectDetail.tsx
│   │   ├── Clients.tsx
│   │   ├── GenerateProposal.tsx
│   │   ├── ProposalViewer.tsx
│   │   ├── ProposalEditor.tsx
│   │   ├── ProposalHistory.tsx
│   │   ├── Templates.tsx
│   │   ├── KnowledgeBase.tsx
│   │   ├── Settings.tsx
│   │   ├── Billing.tsx
│   │   ├── Admin.tsx
│   │   ├── HelpCenter.tsx
│   │   └── NotFound.tsx
│   │
│   ├── components/
│   │   ├── ui/                           # Shadcn UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Select.tsx
│   │   │   ├── Table.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Tabs.tsx
│   │   │   ├── Badge.tsx
│   │   │   ├── Avatar.tsx
│   │   │   ├── DropdownMenu.tsx
│   │   │   ├── Dialog.tsx
│   │   │   ├── Toast.tsx
│   │   │   ├── Tooltip.tsx
│   │   │   ├── Progress.tsx
│   │   │   ├── Skeleton.tsx
│   │   │   ├── Spinner.tsx
│   │   │   └── EmptyState.tsx
│   │   │
│   │   ├── layout/
│   │   │   ├── AppLayout.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Topbar.tsx
│   │   │   ├── WorkspaceSwitcher.tsx
│   │   │   ├── UserMenu.tsx
│   │   │   ├── NotificationBell.tsx
│   │   │   └── Footer.tsx
│   │   │
│   │   ├── proposal/
│   │   │   ├── ProposalCard.tsx
│   │   │   ├── ProposalTable.tsx
│   │   │   ├── ProposalRenderer.tsx
│   │   │   ├── ProposalSection.tsx
│   │   │   ├── ProposalSidebar.tsx
│   │   │   ├── ProposalStepper.tsx
│   │   │   ├── ProposalVersionHistory.tsx
│   │   │   ├── ProposalComparison.tsx
│   │   │   └── ProposalScore.tsx
│   │   │
│   │   ├── generator/
│   │   │   ├── RequirementForm.tsx
│   │   │   ├── ClientSelector.tsx
│   │   │   ├── TemplateSelector.tsx
│   │   │   ├── GenerationProgress.tsx
│   │   │   └── GenerationPreview.tsx
│   │   │
│   │   ├── editor/
│   │   │   ├── RichTextEditor.tsx
│   │   │   ├── SectionEditor.tsx
│   │   │   ├── DragDropSections.tsx
│   │   │   ├── EditorToolbar.tsx
│   │   │   └── AIAssistant.tsx
│   │   │
│   │   ├── diagrams/
│   │   │   ├── MermaidRenderer.tsx
│   │   │   ├── ArchitectureDiagram.tsx
│   │   │   ├── WorkflowDiagram.tsx
│   │   │   ├── ModuleDiagram.tsx
│   │   │   ├── OrgChart.tsx
│   │   │   ├── GanttChart.tsx
│   │   │   ├── Timeline.tsx
│   │   │   └── DeploymentDiagram.tsx
│   │   │
│   │   ├── charts/
│   │   │   ├── PricingChart.tsx
│   │   │   ├── ROIChart.tsx
│   │   │   ├── TimelineChart.tsx
│   │   │   └── BudgetBreakdown.tsx
│   │   │
│   │   ├── knowledge/
│   │   │   ├── DocumentCard.tsx
│   │   │   ├── DocumentUploader.tsx
│   │   │   ├── KnowledgeSearch.tsx
│   │   │   └── KnowledgeCategory.tsx
│   │   │
│   │   ├── billing/
│   │   │   ├── PlanCard.tsx
│   │   │   ├── InvoiceTable.tsx
│   │   │   └── PaymentMethod.tsx
│   │   │
│   │   ├── settings/
│   │   │   ├── ProfileForm.tsx
│   │   │   ├── OrganizationForm.tsx
│   │   │   ├── BrandingForm.tsx
│   │   │   ├── TeamMembers.tsx
│   │   │   └── ApiKeys.tsx
│   │   │
│   │   ├── landing/
│   │   │   ├── Hero.tsx
│   │   │   ├── FeaturesSection.tsx
│   │   │   ├── TemplatesSection.tsx
│   │   │   ├── PricingSection.tsx
│   │   │   └── CTASection.tsx
│   │   │
│   │   ├── auth/
│   │   │   ├── ProtectedRoute.tsx
│   │   │   ├── PublicRoute.tsx
│   │   │   └── AuthGuard.tsx
│   │   │
│   │   └── shared/
│   │       ├── DataTable.tsx
│   │       ├── SearchBar.tsx
│   │       ├── Pagination.tsx
│   │       ├── ConfirmDialog.tsx
│   │       ├── ErrorBoundary.tsx
│   │       ├── LoadingOverlay.tsx
│   │       ├── EmptyState.tsx
│   │       ├── FileUpload.tsx
│   │       ├── ColorPicker.tsx
│   │       └── IconPicker.tsx
│   │
│   ├── styles/
│   │   ├── globals.css                    # Tailwind imports + custom vars
│   │   └── proposal.css                   # Proposal print styles
│   │
│   └── providers/
│       ├── AuthProvider.tsx
│       ├── ThemeProvider.tsx
│       └── QueryProvider.tsx
│
├── index.html
├── vite.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── tsconfig.node.json
├── postcss.config.js
├── components.json                       # Shadcn config
├── package.json
├── .eslintrc.cjs
├── .prettierrc
└── README.md
```

## 11. Proposal Generation Flow — Detailed

```
1. User enters requirement text on GenerateProposal page
2. POST /api/v1/ai/generate { requirement, project_id, template_id }
3. ProposalService.startGeneration() creates proposal record (status: generating)
4. ProposalGenerationService invokes LangGraph workflow:

   STEP 1: Requirement Agent (LLM)
   - Takes raw text → structured requirement JSON
   - Cache: Check if same requirement was analyzed before
   - Output: requirement_json (Pydantic validated)

   STEP 2: RAG Agent (LLM — only if needed)
   - Creates multi-query search from requirement
   - Searches Qdrant (hybrid search across all collections)
   - Filters by industry + project_type metadata
   - Reranks results (CrossEncoder)
   - Compresses to ≤2000 tokens
   - Cache: Check query hash
   - Output: compressed_context

   STEP 3: Business Engines (Pure Python — parallel)
   - IndustryEngine: Lookup industry patterns
   - ModuleEngine: Recommend modules
   - FeatureEngine: Generate feature matrix
   - AutomationEngine: Find automation opportunities
   - IntegrationEngine: List integrations
   - TechStackEngine: Recommend stack
   - TimelineEngine: Generate phased timeline
   - PricingEngine: Calculate costs
   - TeamEngine: Recommend team
   - ROIEngine: Calculate ROI
   - RiskEngine: Identify risks
   - CommercialEngine: Generate terms
   - SupportEngine: Support tiers
   - SLAEngine: SLA tiers
   - DiagramEngine: Generate Mermaid code
   - ProposalContextBuilder: Assemble all into structured context

   STEP 4: Proposal Writer Agent (LLM — 1 call)
   - Takes requirement_json + compressed_context + engines_context
   - Generates full proposal text with all sections
   - Output follows strict JSON schema
   - Structured output per section (not free-form markdown)

   STEP 5: Proposal Reviewer Agent (LLM — 1 call, optional)
   - Reviews for grammar, tone, completeness
   - Checks all sections are present
   - Generates improvement suggestions
   - Output: review + final proposal

5. ProposalGenerationService saves result to MongoDB
6. Background task triggers export generation (PDF, HTML)
7. WebSocket notification sent to user: generation complete
8. User views proposal in ProposalViewer
```

## 12. Cost Optimization Strategy

### LLM Cost per Proposal (~$0.01-0.05)

| Agent | Model | Tokens In | Tokens Out | Cost |
|-------|-------|-----------|------------|------|
| Requirement Agent | Groq Llama 3.3 70B (fast) | ~500 | ~300 | ~$0.0003 |
| RAG Agent | None (cache hit) or Groq fast | ~1000 | ~500 | ~$0.0006 |
| Proposal Writer | Groq Llama 3.3 70B | ~4000 | ~4000 | ~$0.0047 |
| Proposal Reviewer | Groq fast 8B | ~4000 | ~500 | ~$0.0004 |
| **Total** | | | | **~$0.006** |

### Optimization Techniques

1. **Prompt Compression**: Strip whitespace, redundant instructions from prompts
2. **Embedding Cache**: Cache all embeddings in Redis (key: text hash)
3. **LLM Response Cache**: Cache LLM responses by (prompt_hash, model) in Redis
4. **RAG Cache**: Cache search results by query hash + filters (TTL: 1 hour)
5. **Requirement Cache**: Cache requirement analysis by text hash (TTL: 24 hours)
6. **Proposal Cache**: Cache completed proposals by context hash (TTL: 7 days)
7. **Token Budgeting**: Count tokens before sending; truncate context to fit
8. **Dynamic Model Selection**: Simple tasks → fast cheap model; complex → full model
9. **Batch Embeddings**: Batch all embedding requests in RAG pipeline
10. **Background Processing**: LLM calls in background → user gets notification
11. **Streaming**: Stream proposal generation for real-time UX
12. **Knowledge Pre-computation**: Pre-compute common patterns, no LLM needed

### Annual Cost Projection (10,000 proposals/month)

| Item | Monthly | Annual |
|------|---------|--------|
| LLM API (Groq) | $60 | $720 |
| Qdrant Cloud | $25 | $300 |
| MongoDB Atlas | $57 | $684 |
| Redis Cloud | $15 | $180 |
| Server (2 × $40) | $80 | $960 |
| SendGrid | $15 | $180 |
| Stripe (2.9% + $0.30) | ~$290 | ~$3,480 |
| **Total** | **~$542** | **~$6,504** |

## 13. Security Architecture

```
┌─────────────────────────────────────────────┐
│          Request Flow                        │
│                                             │
│ Client → Rate Limiter → JWT Validation      │
│            → Multi-Tenant Isolation         │
│            → RBAC Check                     │
│            → Input Validation               │
│            → Rate Limit (per user/org)      │
│            → Audit Log                      │
│            → Controller                     │
└─────────────────────────────────────────────┘
```

- **JWT**: Access (15min) + Refresh (7 days) token pair
- **Password**: bcrypt with 12 rounds
- **Rate Limiting**: 100 req/min per user, 1000 req/min per org
- **Prompt Injection**: Input sanitization, pattern blocking
- **Encryption**: AES-256 at rest for sensitive fields
- **File Upload**: File type validation, size limits (10MB), scan
- **RBAC**: Role hierarchy: admin > editor > viewer
- **Multi-Tenant**: All queries filter by organization_id
- **Audit Log**: All CUD operations logged
- **CORS**: Whitelist allowed origins
- **Helmet**: Security headers (via middleware)
- **API Keys**: HMAC-signed keys for programmatic access

## 14. Performance Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Client     │────▶│   FastAPI    │────▶│   MongoDB    │
│   (React)    │     │  (Async)     │     │  (Indexed)   │
└──────┬───────┘     └──────┬───────┘     └──────────────┘
       │                    │                    │
       │                    │                    │
       ▼                    ▼                    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Redis Cache │     │  Redis Queue │     │   Qdrant     │
│  (API Cache) │     │  (Celery)    │     │  (Vector DB) │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  Background  │
                     │  Workers     │
                     │  (Celery)    │
                     └──────────────┘
```

- **Async I/O**: All I/O operations async (httpx, motor, aioredis)
- **Connection Pooling**: MongoDB (maxPoolSize=50), Redis (max connections)
- **Indexing**: All query patterns indexed in MongoDB
- **Pagination**: All list endpoints paginated (cursor or offset)
- **Lazy Loading**: Frontend loads sections on demand
- **Virtualization**: Long lists virtualized (react-window)
- **Bundle Splitting**: Route-based code splitting in frontend
- **Image Optimization**: WebP format, lazy loading
- **CDN**: Static assets served via CDN
- **Database Optimization**: Aggregation pipelines, covered queries
- **N+1 Prevention**: Batch loading, eager loading

## 15. Development Roadmap — 12 Phases

### Phase 1: Foundation (Week 1-2)
**Objective**: Project scaffolding, clean architecture base, auth

Files to create:
- Backend: Project structure, config, dependencies, domain entities, auth system
- Frontend: Vite + TS + Tailwind + Shadcn setup, auth pages, layout

### Phase 2: Multi-Tenant Core (Week 3)
**Objective**: Organizations, workspaces, user management, RBAC

### Phase 3: CRUD Services (Week 4)
**Objective**: Clients, projects, proposals CRUD with repository pattern

### Phase 4: Business Engines (Week 5-6)
**Objective**: All 17 business engines with comprehensive test coverage

### Phase 5: AI Agent Pipeline (Week 7-8)
**Objective**: LangGraph workflow, requirement agent, RAG agent, writer agent, reviewer agent

### Phase 6: RAG Infrastructure (Week 8-9)
**Objective**: Qdrant collections, embedding pipeline, hybrid search, reranking, ingestion

### Phase 7: Export System (Week 9-10)
**Objective**: PDF, DOCX, HTML, PPTX exporters with identical formatting

### Phase 8: Diagram Engine (Week 10)
**Objective**: Mermaid diagram generation for all diagram types

### Phase 9: Frontend Complete (Week 11-14)
**Objective**: All pages, components, proposal viewer, editor, generator

### Phase 10: Billing & Payments (Week 15)
**Objective**: Stripe integration, subscription plans, usage tracking

### Phase 11: Admin & Analytics (Week 16)
**Objective**: Admin panel, analytics dashboard, audit logs, monitoring

### Phase 12: Production Hardening (Week 17-18)
**Objective**: Docker, CI/CD, monitoring, load testing, security audit, documentation

## 16. Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Cloudflare CDN                        │
├─────────────────────────────────────────────────────────┤
│                   Load Balancer (HAProxy)                 │
├────────────────────┬────────────────────┬────────────────┤
│   FastAPI App 1    │   FastAPI App 2    │   FastAPI App 3│
│   (API Server)     │   (API Server)     │   (API Server) │
├────────────────────┴────────────────────┴────────────────┤
│                   Redis Cluster (Cache + Queue)           │
├────────────────────┬────────────────────┬────────────────┤
│   Celery Worker 1  │   Celery Worker 2  │  Celery Beat   │
├────────────────────┴────────────────────┴────────────────┤
│            MongoDB Replica Set (Primary + 2 Secondaries)  │
├──────────────────────────────────────────────────────────┤
│                    Qdrant Cluster                          │
├──────────────────────────────────────────────────────────┤
│                    S3 Compatible Storage                   │
└──────────────────────────────────────────────────────────┘
```

### Docker Services
```
services:
  api:        FastAPI app (3 replicas)
  worker:     Celery worker (2 replicas)
  beat:       Celery beat scheduler
  redis:      Redis cache + broker
  mongodb:    MongoDB replica set
  qdrant:     Qdrant vector DB
  nginx:      Reverse proxy
  frontend:   Nginx serving React SPA
```

## 17. Future Scalability Plan

### Horizontal Scaling
- API servers: Stateless → add more replicas
- Celery workers: Increase queue consumers
- MongoDB: Shard by organization_id
- Qdrant: Multi-node cluster with replication
- Redis: Cluster mode for cache

### Feature Scaling
- Real-time collaboration (WebSockets + CRDT)
- Team workspace with concurrent editing
- AI model fine-tuning on organization data
- Custom AI agents per organization
- Marketplace for proposal templates
- API for third-party integrations
- White-label SaaS offering
- Multi-language proposal generation
- Offline proposal editing (PWA)

---
*Architecture v1.0 — ProposalCraft AI*
