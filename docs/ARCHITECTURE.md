# Proposal Intelligence Platform — Architecture Document

> **Author:** Architecture & Platform Engineering
> **Status:** Target architecture (v3 → v4)
> **Scope:** Extend the existing codebase. No rewrites. Every proposal below names the existing files it touches.

---

## 0. Executive Summary

The current codebase is a working **AI Proposal Generator** with a healthy skeleton: DDD-style domain entities, repositories, services, a LangGraph workflow, a multi-provider LLM client with cost tracking and caching, RAG over Qdrant, and an async generation pipeline. The request is to evolve it into a **Proposal Intelligence Platform** — a multi-tenant SaaS where the generator is one module inside a project-centric, knowledge-driven system, comparable to Bidara AI / RFPIO / Loopio / Proposify / Qwilr.

The strategy is **extend, don't rewrite**:

1. Keep the existing layering (`api → services → domain → infrastructure`), LangGraph workflow, LLM client, RAG stack, and the already-correct multi-tenant patterns (`organization_id` on every entity, RBAC via `DEFAULT_PERMISSIONS`, `require_permission` deps).
2. Add the missing **platform spine**: knowledge hub, project-centric data model, proposal lifecycle state machine, collaboration (comments/mentions/versions), notifications, activity/audit logs, approval workflow, usage metering, and richer analytics.
3. Fix the concrete weaknesses observed in production of this session: silent failure paths, in-memory singletons, empty infrastructure adapters, `BackgroundTasks` used as a queue, and frontend pages that render fake data.

This document covers all 20 requested sections, with the "why" and "how" for each change, mapped to existing files.

---

## 1. Existing Architecture Review

### 1.1 What exists today (verified against the repo)

```
backend/app/
├── api/v1/          auth, users, organizations, workspaces, members,
│                    clients, projects, proposals        → FastAPI routers
├── admin/           router.py (health, users, organizations)
├── analytics/       service.py (org dashboard + admin dashboard), cost_tracker.py
├── agents/          base, requirement, writer, reviewer, rubric_checker, rag_agent
├── billing/         router, service, schemas (Stripe, PLANS)
├── config/          settings.py, constants.py, logging_config.py
├── database/        mongodb.py (motor client + ensure_indexes)
├── domain/          entities (user/org/workspace/client/project/proposal),
│                    interfaces (repositories), value_objects (email/money/permissions),
│                    exceptions (DomainError hierarchy)
├── engines/         18 business engines (industry, feature, tech_stack, risk,
│                    timeline, pricing, commercial, roi, sla, team, support,
│                    module, automation, integration, diagram, template,
│                    proposal_context_builder)
├── export/          router, service, normalize, renderers (html/pdf/docx/pptx)
├── graph/           state.py, nodes.py, edges.py, workflow.py  → LangGraph StateGraph
├── infrastructure/  auth (jwt, password), database (mongodb, redis,
│                    mongo_repositories/*), cache (redis_cache), log (audit, logger)
│                    email/export/monitoring/payment/storage  → EMPTY placeholders
├── llm/             client.py (multi-provider fallback), models.py (registry +
│                    per-task chains), cache.py, embeddings.py, tokenizer.py, prompts/*
├── middleware/      rate_limit.py
├── models/          generated_proposal_model.py, proposal_model.py, subscription_model.py
├── pricing/         engine.py
├── rag/             loader, chunker, splitter, embeddings, vectorstore,
│                    retriever, ingest, service, router, schemas
├── schemas/         pydantic request/response models
├── services/        auth, user, organization, workspace, member, client,
│                    project, proposal, generated_proposal, upload
└── tasks/           __init__.py (empty)
```

Frontend: React + Vite + TypeScript, Tailwind, React Router, TanStack Query, Redux Toolkit, Axios (token refresh interceptor), react-hook-form + zod. Pages: Dashboard, Login/Register, Workspace, Clients, Projects (+ detail), Generate, ProposalDetail, History, Billing, Analytics.

### 1.2 The AI pipeline (LangGraph StateGraph)

```
requirement → business_engines → rag → writer → reviewer → rubric_check → (retry loop) → finalizer
```

- `requirement_node`: requirement agent extracts requirements from `client_input`.
- `business_engines_node`: runs the engine registry (industry/feature/tech/risk/timeline/pricing...).
- `rag_node`: retrieves context from Qdrant collections (industry knowledge, tech, pricing, case studies, best practices, compliance, automation).
- `writer_node`: writes proposal sections in batches with strict-JSON retries.
- `reviewer_node` + `rubric_node`: quality gate; rubric failure re-runs the writer (bounded retries).
- `finalizer_node`: assembles system sections and exports.

Generation is **asynchronous** (`GeneratedProposalService.start_generation` + `run_and_finalize`, FastAPI `BackgroundTasks`); the frontend polls the proposal doc until it leaves `processing`.

### 1.3 Multi-tenancy, auth, RBAC (already partially in place)

- Every entity carries `organization_id`; routers scope queries by `get_current_org`.
- JWT access (15 min) + refresh (7 days) with token-type enforcement (`verify_access_token` / `verify_refresh_token`).
- RBAC: `UserRole` (admin/editor/viewer), `DEFAULT_PERMISSIONS[role]`, `require_permission(...)` dependency, `User.has_permission` with role-default fallback.
- Rate limiting middleware, audit log helper, analytics cost tracker.

---

## 2. Strengths

| Area | Evidence |
|---|---|
| Clean layering | `api → services → domain → infrastructure`; repositories behind interfaces (`domain/interfaces/*_repo.py`) |
| DDD seeds | Real `entities`, `value_objects`, `exceptions` — not anemic schemas |
| Multi-tenant discipline | `organization_id` scoping everywhere; org-level RBAC defaults |
| Provider-agnostic LLM | `MODEL_REGISTRY` + per-complexity chains with fallback and per-call cost/latency logging |
| Cost control | `cost_tracker.py`, token estimation, per-token pricing on models |
| Quality gate | Reviewer + rubric with bounded writer retry loop |
| RAG groundwork | Loader/chunker/splitter/embed/vectorstore/retriever all present |
| Async UX | Background generation + polling UI (avoids 5-min HTTP timeouts) |
| Export breadth | HTML/PDF/DOCX/PPTX renderers |
| Audit + permissions | `audit.py`, `permissions.py` value object |
| Test discipline | 159 unit tests passing |

---

## 3. Weaknesses (observed, with file references)

These are **architectural**, not cosmetic. Several caused real incidents this session.

1. **No dependency injection container.** Services are instantiated inside routers (`AuthService()`, `ProjectService()` in `api/v1/*.py`) and `llm_client` is a module singleton. Testing and cross-cutting concerns (metrics, tracing, retries) are bolted on ad hoc.
2. **`BackgroundTasks` is not a queue.** `generated_proposal_service.py` runs long LLM pipelines in-process: a worker restart kills generations, there is no retry/visibility, and concurrent generation scales with uvicorn workers (resource exhaustion seen live: NVIDIA `Worker local total request limit reached (33/32)`). No idempotency keys → duplicate proposals on retry.
3. **Empty infrastructure adapters.** `infrastructure/{email,export,monitoring,payment,storage}/__init__.py` are placeholders. Storage is local filesystem; email/notifications don't exist.
4. **LLM cache is an in-memory dict** (`llm/cache.py`), so it resets on restart and doesn't work across workers. Redis exists but is not used for it.
5. **Rate limiter is a middleware without a store** — inspect `middleware/rate_limit.py` for in-memory counters; restart/lost visibility, no per-tenant budgets.
6. **RBAC is coarse.** Permission lists are static per role; no org-level role overrides (ABAC), no resource-level ownership checks beyond `organization_id` equality (e.g., `projects.py` compares `project.organization_id != user.organization_id` inline).
7. **No proposal lifecycle.** `ProposalStatus` is `draft/processing/review/approved/rejected/sent/error` — a single enum, no transitions, no timestamps per stage, no required approvals.
8. **No versioning/collaboration.** `proposal.version` exists as an int but nothing writes versions, comments, mentions, or diffs.
9. **No knowledge hub.** RAG collections exist, but the Workspace has no structured knowledge model (company profile, services, portfolio, pricing rules, templates, legal clauses, brand assets) and no pipeline from uploaded PDFs → clean → classify → chunk → embed. `rag/ingest.py` is manual.
10. **No activity/notification system.** `audit.py` writes logs, but there are no activity feeds, in-app notifications, or email/Slack/Teams delivery.
11. **Analytics is aggregation-only.** No win-rate, revenue, AI usage/token trends, proposal quality scores, or productivity metrics; no per-user dashboards.
12. **Billing is Stripe-shaped only** (`billing/service.py`): no Razorpay, no credits/AI-token metering, no invoices, no storage metering; `PLANS` in `billing/schemas.py` is static.
13. **Frontend has dead/fake modules**: Dashboard previously rendered hardcoded proposals (fixed), Topbar search/bell are non-functional, no editor, no project-centric navigation, no realtime.
14. **Observability gaps.** Logging exists (`logging_config.py`), but no structured request tracing, no OpenTelemetry, no metrics endpoint, no error tracking; async failures surface only via `generation_metadata.error` and a polling `error` status.
15. **Testing is unit-heavy, e2e-light.** No API contract tests, no workflow-level tests, no frontend tests.
16. **Cost/quality coupling.** The fallback chain silently downgrades to weak models (observed: 8b writer → rubric failures → retries → 3–5 min generations); there is no explicit "acceptable model" policy or user-visible quality indicator.

---

## 4. Missing Modules (requested vs. current)

| Requested | Status | First step |
|---|---|---|
| Multi-tenancy / Orgs / Members / RBAC | Partial (exists) | Add org-level role overrides + ABAC policies |
| Workspace as Knowledge Hub | **Missing** | `knowledge/` domain + ingest pipeline (Section 7, 9) |
| Knowledge Builder (clean → classify → chunk → embed) | **Missing** | `knowledge/pipeline.py` wrapping existing `rag/` primitives |
| Clients (contacts, activity, history) | Partial | Extend `client.py` entity + `client_service.py` |
| Projects as the center | Partial (CRUD only) | Project aggregates: requirements, docs, meetings, budget, risks, activities |
| Proposal Studio (rich editor) | **Missing** | Frontend editor page + backend section CRUD + AI assist endpoints |
| Proposal Lifecycle / Approvals | **Missing** | Status state machine + `approvals` collection + workflow |
| Versioning / Comparison | **Missing** | `proposal_versions` collection + snapshot service |
| Collaboration (comments, mentions) | **Missing** | `comments` collection + notifications |
| Share links / Client portal / E-signature | **Missing** | `share_links`, portal tokens, esign adapter |
| Domain-specific business engines | Partial (generic engines) | Domain registry: `engines/domains/*` |
| Specialized agents | Partial (6 agents) | Extend to 16 single-responsibility agents (Section 12) |
| Knowledge: templates, clauses, brand assets | **Missing** | `knowledge/` types |
| Notifications (email/Slack/Teams) | **Missing** | `infrastructure/notifications/` |
| Integrations (HubSpot/Salesforce/Jira/Drive/...) | **Missing** | `integrations/` + webhook framework |
| Activity logs / Audit | Partial | Activity feed + unified event log |
| Analytics v2 (win rate, AI usage, quality) | Partial | Extend `analytics/service.py` |
| Billing v2 (Razorpay, credits, invoices) | Partial | `billing/` adapters + usage metering |
| Queue / workers (Celery/Redis) | **Missing** | `tasks/` + worker |
| Object storage | **Missing** | `infrastructure/storage/s3.py` |
| Observability (tracing, metrics) | **Missing** | OpenTelemetry + `monitoring/` |
| API v2 with versioning | Missing (v1 only) | `api/v2/` overlay |

---

## 5. Improved Architecture

### 5.1 Guiding principles

1. **Extend the existing layers.** `api → services → domain → infrastructure` stays. We add an explicit **application layer** (use-cases) later; for now services double as use-cases and gain constructor injection.
2. **Domain-driven aggregates.** The platform has 6 aggregates: `Organization`, `Workspace` (knowledge hub), `Client`, `Project`, `Proposal` (lifecycle + versions), `Subscription`.
3. **Event-driven internally.** A lightweight in-process event bus now; Redis pub/sub when multiple workers run. Events: `proposal.generated`, `proposal.approved`, `knowledge.ingested`, `usage.metered`.
4. **Everything retrievable.** All knowledge goes through one pipeline into Qdrant with provenance (`source_entity_type`, `source_id`, `tenant_id`).
5. **Tenancy is a cross-cutting concern.** `TenantContext` (org_id + user + permissions) resolved once per request and injected; no router repeats `get_current_org` chains.
6. **Queues for heavy work, endpoints for light.** Background LLM work moves from `BackgroundTasks` to a Redis-backed queue with idempotency keys.
7. **Usage metering as a platform primitive.** Every LLM call, export, and storage write produces a usage event → credits/token budgets and analytics consume the same stream.

### 5.2 Target layering (mapped to existing folders)

```
┌───────────────────────────────────────────────────────────────┐
│ API layer          app/api/v1 (existing) + app/api/v2 (new)   │
│                    routers → services; versioning strategy     │
├───────────────────────────────────────────────────────────────┤
│ Application layer  app/services/* (extend) + app/tasks/*       │
│                    use-cases: generate, approve, share, ingest │
│                    event bus: app/events/* (new)               │
├───────────────────────────────────────────────────────────────┤
│ Domain layer       app/domain/entities, value_objects,         │
│                    interfaces (extend), new aggregates         │
│                    app/engines/* (domain logic)                │
│                    app/graph/* (AI workflow = domain process)  │
├───────────────────────────────────────────────────────────────┤
│ Infrastructure    app/infrastructure/* (fill the empties:      │
│                    storage, email, notifications, payments,    │
│                    monitoring; repos, cache, queue adapters)   │
│                   app/llm/* app/rag/* app/export/*             │
└───────────────────────────────────────────────────────────────┘
```

Hexagonal view: domain in the middle; `interfaces/` are ports; `infrastructure/mongo_repositories/`, `llm/client.py`, `rag/vectorstore.py`, `export/renderers/`, `billing/service.py` are adapters. The `services/` layer orchestrates ports, and FastAPI routers are the delivery mechanism. This is already 80% true — we make it explicit by removing direct construction.

---

## 6. Folder Structure (v4 target — deltas marked)

New/modified paths only; everything else stays.

```
backend/app/
├── api/
│   ├── v1/                          # unchanged, freeze as-is (stability)
│   └── v2/                          # NEW: project-centric surface
│       ├── api.py                   # mounts after v1, prefix /api/v2
│       ├── projects.py              # project aggregate endpoints
│       ├── studio.py                # sections CRUD, AI assist (rewrite/expand/...)
│       ├── lifecycle.py             # status transitions, approvals
│       ├── knowledge.py             # knowledge hub CRUD + ingest triggers
│       ├── collaborations.py        # comments, mentions, share links
│       ├── notifications.py         # in-app feed + preferences
│       └── webhooks.py              # inbound/outbound webhook registry
├── application/                     # NEW: explicit use-cases (thin, async)
│   ├── __init__.py
│   ├── generate_proposal.py         # wraps existing GeneratedProposalService
│   ├── approve_proposal.py
│   ├── ingest_knowledge.py
│   └── meter_usage.py
├── events/                          # NEW: in-process event bus + payloads
│   ├── bus.py
│   └── handlers/                    # notify, audit, analytics, usage
├── knowledge/                       # NEW: Knowledge Hub domain
│   ├── types.py                     # CompanyProfile, Service, CaseStudy, Template,
│   │                                # LegalClause, BrandAsset, PricingRule, ...
│   ├── service.py                   # CRUD + ownership checks
│   ├── pipeline.py                  # clean → classify → chunk → embed → index
│   └── schemas.py
├── lifecycle/                       # NEW: proposal state machine
│   ├── machine.py                   # states, allowed transitions, guards
│   ├── approvals.py                 # approval requests, per-role required gates
│   └── versions.py                  # snapshot/diff/restore
├── collaborations/                  # NEW
│   ├── comments.py                  # threads, mentions (user_id refs)
│   └── share.py                     # share links, client portal tokens, expiry
├── agents/                          # EXTEND: 16 single-responsibility agents
│   ├── base.py                      # existing (add AgentResult typing)
│   ├── clarification_agent.py       # NEW
│   ├── question_agent.py            # NEW
│   ├── industry_classifier.py       # NEW
│   ├── business_analysis.py         # NEW
│   ├── feature_recommender.py       # NEW
│   ├── tech_recommender.py          # NEW
│   ├── architecture_agent.py        # NEW
│   ├── timeline_agent.py            # NEW
│   ├── cost_estimator.py            # NEW
│   ├── risk_analyst.py              # NEW
│   ├── compliance_agent.py          # NEW
│   ├── quality_agent.py             # NEW (replaces ad-hoc rubric)
│   ├── formatting_agent.py          # NEW
│   └── export_agent.py              # NEW (chooses renderer)
│   # existing: requirement, writer, reviewer, rubric_checker stay
├── engines/
│   ├── base_engine.py               # existing (add registry pattern)
│   ├── registry.py                  # NEW: domain → engine mapping
│   └── domains/                     # NEW
│       ├── healthcare.py            # terminology, compliance (HIPAA), features
│       ├── government.py            # tender/RFP compliance
│       ├── manufacturing.py
│       ├── retail.py
│       ├── education.py
│       ├── erp.py
│       ├── crm.py
│       ├── finance.py
│       ├── construction.py
│       └── realestate.py
│   # existing 18 engines stay untouched
├── graph/
│   ├── workflow.py                  # EXTEND: new nodes/edges (see §12)
│   ├── nodes.py                     # EXTEND
│   ├── edges.py                     # EXTEND: conditional transitions
│   └── checkpointer.py              # NEW: langgraph checkpointing (Redis/Mongo)
├── infrastructure/
│   ├── di/container.py              # NEW: composition root
│   ├── storage/s3.py                # FILL: S3-compatible object storage
│   ├── email/sendgrid.py            # FILL: transactional email
│   ├── notifications/               # FILL: in-app + Slack + Teams + webhooks
│   ├── payments/razorpay.py         # FILL: second payment adapter
│   ├── monitoring/otel.py           # FILL: OpenTelemetry tracing/metrics
│   ├── cache/llm_redis.py           # NEW: Redis-backed LLM cache
│   └── queue/                       # NEW
│       ├── producer.py              # enqueue generation/ingest/export jobs
│       └── consumer.py              # worker entrypoints
├── tasks/                           # FILL: worker jobs (Celery or ARQ)
│   ├── celery_app.py
│   └── jobs.py                      # generate_proposal, ingest_document, export_all
├── billing/
│   ├── service.py                   # EXTEND: payment gateway interface
│   ├── razorpay.py                  # NEW
│   └── credits.py                   # NEW: AI credit ledger
├── analytics/
│   ├── service.py                   # EXTEND: win rate, AI usage, quality, trends
│   └── usage.py                     # NEW: meter LLM/export/storage events
├── integrations/                    # NEW
│   ├── registry.py                  # connector interface + OAuth store
│   ├── hubspot.py                   # (phase 4)
│   ├── salesforce.py
│   ├── jira.py
│   ├── drive.py
│   ├── sharepoint.py
│   └── slack_teams.py               # notification channels
└── middleware/
    ├── tenant_context.py            # NEW: resolve + stash tenant
    └── rate_limit.py                # MODIFY: Redis-backed token bucket
```

Frontend (feature-sliced, extending current structure):

```
frontend/src/
├── pages/                    # existing pages stay; add:
│   ├── ProjectHub.tsx        # project-centric dashboard (requirements, docs,
│   │                         #   timeline, budget, risks, proposals)
│   ├── ProposalStudio.tsx    # rich editor + AI assist toolbar + comments
│   ├── Approvals.tsx         # my-approvals queue
│   ├── KnowledgeBase.tsx     # knowledge hub manager + ingest status
│   └── ClientProfile.tsx     # contacts, history, activity timeline
├── features/                 # NEW: feature modules (editor, approvals, knowledge)
├── components/               # existing ui/ stays; add editor/, charts/
├── hooks/                    # existing; add useRealtime.ts (SSE), useVersion.ts
├── api/                      # existing; add studio.ts, lifecycle.ts, knowledge.ts
└── lib/                      # existing; add p2p? no — realtime client
```

---

## 7. Module Responsibilities (v4)

| Module | Responsibility | Key files |
|---|---|---|
| `api/` | HTTP delivery, validation, versioning | v1 frozen; v2 new |
| `application/` | Use-cases: generate, approve, ingest, meter | new |
| `services/` | Orchestration + transactions | existing, DI-injected |
| `domain/` | Entities, rules, ports (interfaces) | extend with new aggregates |
| `engines/` | Domain logic (business analysis) | existing + `domains/` registry |
| `knowledge/` | Workspace knowledge hub, provenance | new |
| `lifecycle/` | Proposal state machine, approvals, versions | new |
| `collaborations/` | Comments, mentions, share links | new |
| `agents/` | Single-responsibility AI agents | extend to 16 |
| `graph/` | Orchestrates agents into workflow | extend, checkpointed |
| `llm/` | Model registry, providers, caching, tokens | existing + Redis cache |
| `rag/` | Vector retrieval + ingestion primitives | existing |
| `export/` | Renderers (html/pdf/docx/pptx) | existing |
| `billing/` | Plans, subscriptions, credits, invoices | extend with Razorpay + credits |
| `analytics/` | Dashboards, usage metering, cost tracking | extend |
| `events/` | Domain events + handlers | new |
| `tasks/` | Background workers (queue consumer) | new |
| `infrastructure/` | Adapters: storage, email, notify, payments, monitoring, cache, queue | fill empties |
| `middleware/` | Tenant context, rate limiting | extend |
| `config/` | Settings, constants | existing |
| `admin/` | Platform admin | existing, extend with usage tables |

---

## 8. Domain Model

### 8.1 Aggregates and boundaries

```
Organization
 ├─ Members (User + role + permissions)
 ├─ Workspaces ──────────────── Knowledge Hub
 │    ├─ CompanyProfile, Services, Industries, Technologies
 │    ├─ Portfolio, CaseStudies, Certifications, TeamMembers
 │    ├─ PricingRules, ProposalTemplates, LegalClauses
 │    ├─ BrandAssets, CompanyDocuments (pdf/brochures/images/logos/videos)
 │    └─ → all ingested into RAG with provenance
 ├─ Clients (Company + Contacts + Tags + ActivityTimeline)
 │    └─ Projects
 ├─ Projects (the center)
 │    ├─ Requirements, Documents, Meetings, Emails
 │    ├─ Timeline, Budget, Risks, CostEstimate, Architecture
 │    ├─ Proposals ── Proposal Lifecycle
 │    │    ├─ Versions (snapshots + diff)
 │    │    ├─ Approvals (role-gated transitions)
 │    │    ├─ Comments / Mentions
 │    │    └─ Share links / Client portal / e-sign
 │    └─ Activities (event log)
 └─ Subscription (plan, usage ledger, credits)
```

### 8.2 Entity deltas (existing files to extend)

- `domain/entities/project.py` — add: `requirements: list[RequirementRef]`, `documents: list[ObjectRef]`, `meetings`, `emails`, `budget: Money`, `risks`, `timeline`, `cost_estimate`, `activities`.
- `domain/entities/client.py` — add: `contacts: list[Contact]`, `tags`, `activity_timeline`, `previous_projects`.
- `domain/entities/proposal.py` — add `lifecycle: LifecycleState`, `approvals: list[ApprovalRecord]`, `current_version_id`, `share_links`.
- `domain/entities/workspace.py` — becomes the knowledge hub root: `knowledge_assets: list[KnowledgeAssetRef]`.
- New: `domain/entities/knowledge_asset.py`, `domain/entities/approval.py`, `domain/entities/proposal_version.py`, `domain/entities/comment.py`, `domain/entities/notification.py`, `domain/entities/usage_event.py`.

### 8.3 Why this matters

Without an aggregate boundary, "Project" is a row. With it, every operation (add requirement, attach doc, generate proposal) is a use-case against one aggregate → consistent transactions, clear authorization point (project belongs to org), and a single activity feed source. This is the difference between a CRUD app and a platform.

---

## 9. Database Schema

### 9.1 Existing collections (keep, add indexes)

```
users, organizations, workspaces, clients, projects, proposals,
generated_proposals, subscriptions, plans, audit_logs
```

`ensure_indexes` (`infrastructure/database/mongodb.py`) must add:
- compound `(organization_id, created_at)` on proposals/projects/clients/workspaces — every dashboard query uses it.
- `(organization_id, status)` on proposals.
- TTL index on share links / notifications.

### 9.2 New collections

| Collection | Purpose | Key fields |
|---|---|---|
| `knowledge_assets` | Knowledge hub items | `org_id, workspace_id, type, title, content, file_ref, tags, status (pending/processing/ready/failed), provenance {source, chunk_ids}` |
| `proposal_versions` | Version snapshots | `proposal_id, version, author_id, sections_snapshot, created_at, note, parent_version` |
| `approvals` | Lifecycle gates | `proposal_id, stage, required_role, requested_by, approved_by, status, decided_at, comment` |
| `comments` | Collaboration | `proposal_id, section_key, thread_id, author_id, body, mentions[], created_at, resolved` |
| `notifications` | In-app feed | `org_id, user_id, type, title, body, link, read_at, created_at` |
| `share_links` | Public/client links | `proposal_id, token, type (public/client), expires_at, access_count, created_by` |
| `usage_events` | Metering | `org_id, user_id, type (llm/export/storage), provider, model, tokens_in, tokens_out, cost, credits, created_at` |
| `activity_events` | Activity + audit feed | `org_id, user_id, entity_type, entity_id, action, meta, created_at` |
| `integration_connectors` | OAuth connectors | `org_id, provider, credentials (encrypted), status, sync_state` |

### 9.3 Why these collections

- `usage_events` is the single source for **billing credits, AI token limits, storage metering, and analytics** — one append-only stream, multiple consumers.
- `activity_events` replaces ad-hoc audit calls and powers the UI activity timeline, admin panel, and compliance audit with the same data.
- `proposal_versions` keeps the proposal document immutable per version; the "live" doc in `proposals` is a pointer to the current snapshot. Diff = compare two snapshots. This is how RFPIO/Loopio handle history without custom diffs on one mutable doc.

---

## 10. API Structure

### 10.1 Versioning strategy

Keep `/api/v1` **frozen** (existing clients/frontend keep working). New surface under `/api/v2` with a clean project-centric shape. `api/v1/api.py` and `api/v2/api.py` mount in `main.py`. This is a backwards-compatible overlay — no rewrite.

### 10.2 v2 endpoint map (representative)

```
POST   /v2/projects                                  create project aggregate
GET    /v2/projects/{id}                             full aggregate
PUT    /v2/projects/{id}                             update (name, budget, timeline...)
POST   /v2/projects/{id}/documents                   upload doc → knowledge pipeline
POST   /v2/projects/{id}/proposals                   create draft proposal
GET    /v2/projects/{id}/proposals                   list proposals
POST   /v2/projects/{id}/proposals/{pid}/generate    enqueue generation (idempotency-key)
POST   /v2/proposals/{pid}/sections/{key}            save section
POST   /v2/proposals/{pid}/assist                    {action: rewrite|expand|summarize|grammar|tone}
GET    /v2/proposals/{pid}/versions                  list versions
GET    /v2/proposals/{pid}/versions/{v}/diff?vs={v2}
POST   /v2/proposals/{pid}/lifecycle/transition      {to_status, note}
POST   /v2/proposals/{pid}/approvals                 request approval (gate: role)
POST   /v2/proposals/{pid}/comments                  comment/mention
POST   /v2/proposals/{pid}/share                     create share link
POST   /v2/knowledge/ingest                          {workspace_id, asset_ids} → pipeline job
GET    /v2/knowledge/assets                          searchable hub list
GET    /v2/notifications                             in-app feed
POST   /v2/usage/meter                               (internal) usage events
```

### 10.3 Response envelope (v2 only)

```json
{ "data": {...}, "meta": { "tenant": "org_...", "trace_id": "...", "version": 2 } }
```

Rationale: v1 returns bare payloads; v2 adds trace propagation and tenant echo — needed for support/debugging in production.

---

## 11. AI Pipeline (v4)

### 11.1 Current

`requirement → engines → rag → writer → reviewer → rubric → finalizer` (single linear pass).

### 11.2 Target (extending the same StateGraph)

```
                  ┌───────────  requirement  ───────────┐
                  │                │                     │
            clarification   industry_classifier      question (gaps?)
           (if <60% conf)        │                     │
                  └───────────────┴─────────────────────┘
                                  │
                         business_analysis
                     (business_engines + domain engine
                        from registry by classification)
                                  │
              feature_recommender, tech_recommender, architecture
                                  │
                    timeline, cost_estimator, risk, compliance
                                  │
                          rag (knowledge hub + org RAG)
                                  │
                     proposal_writer (batch sections)
                                  │
                     reviewer → quality_agent (score)
                         │ fail <threshold
                         │   └── writer re-run (bounded, per-section)
                         ▼
                    formatting_agent → export_agent
                                  │
                     finalizer → version snapshot → notify
```

### 11.3 LangGraph design details

- **Add nodes**, keep existing ones (`graph/nodes.py`, `graph/edges.py`): `clarification_node`, `classification_node`, `quality_node`, `formatting_node`.
- **Conditional edges** (`graph/edges.py`): `requirement → clarification | classify` based on confidence; `quality → writer | formatting` based on score.
- **Checkpointing** (`graph/checkpointer.py`, new): use `langgraph` checkpointer backed by Redis/MongoDB so interrupted/restarted generations resume — this also replaces the current "poll a status field" resilience gap.
- **Agent registry**: `agents/base.py` gets a `@agent.register("name", complexity)` decorator; `graph/nodes.py` resolves agents by task instead of hardcoded imports → adding a new agent becomes a one-file change.
- **Cost/quality policy**: `llm/models.py` chains get a per-task `min_quality` gate; a fallback downgrade logs a `usage_events` record with `quality_tier` so admins can see when generation degraded (today this is silent).

### 11.4 Why

The current pipeline is one linear pass with one retry loop. Real proposal intelligence needs: clarification (bidara-style), classification (drives the domain engine), gap questions, and a proper quality gate. All of this extends the existing graph — no new framework, no rewrite of `writer_agent.py` or `reviewer_agent.py`.

---

## 12. Agents — Single Responsibility (v4)

| Agent | Responsibility | Replaces/extends |
|---|---|---|
| Requirement | Extract requirements from client_input | existing `requirement_agent.py` |
| Clarification | Ask missing-info questions, update requirement | **new** |
| Question | Generate Q&A for unclear requirements | **new** |
| Industry Classifier | Classify industry/domain → picks engine | **new** |
| Business Analysis | Deep domain analysis via engine registry | wraps `business_engines_node` |
| Feature Recommender | Recommend features (engine-informed) | `feature_engine.py` wrapper |
| Tech Recommender | Technology stack | `tech_stack_engine.py` wrapper |
| Architecture | Solution architecture | `architecture_agent.py` **new**, uses diagram engine |
| Timeline | Phases/milestones | `timeline_engine.py` wrapper |
| Cost Estimator | Effort/pricing/ROI | `pricing/commercial/roi_engine.py` wrappers |
| Risk Analyst | Risks + mitigations | `risk_engine.py` wrapper |
| Compliance | Compliance mapping (domain-specific) | `compliance.py` prompt + domain engines |
| Proposal Writer | Write sections | existing `writer_agent.py` |
| Reviewer | Review for depth/accuracy | existing `reviewer_agent.py` |
| Quality | Score against rubric → gate | `rubric_checker.py` evolution |
| Formatting | Output formatting (markdown, structure) | **new** |
| Export | Pick renderer + export | `export/` wrapper |

The wrappers above are **1:1 with existing engines** — the split is organizational, not new compute. This satisfies "single responsibility" without throwing away the 18 engines.

---

## 13. Frontend Architecture (v4)

### 13.1 Routing (extend, don't break)

```
/dashboard            → existing (now real data)
/workspace            → existing
/workspace/:id/knowledge → NEW knowledge hub manager
/clients/:id          → NEW client profile (contacts, history, activity)
/projects             → existing
/projects/:id         → NEW Project Hub (requirements, docs, budget, risks, proposals)
/generate             → existing (becomes: create project + generate first proposal)
/proposals/:id        → existing detail
/proposals/:id/studio → NEW Proposal Studio (editor + AI assist + comments + versions)
/approvals            → NEW approval queue
/analytics, /billing  → existing
```

### 13.2 State strategy

- **TanStack Query** remains for server state (it already is) — add `useRealtime` for SSE updates instead of polling where possible (generation status, notifications). Keep polling as fallback.
- **Redux** remains for auth/workspace session state only (already the pattern). Do not move server state into Redux.
- **Proposal Studio editor**: TipTap (ProseMirror) — JSON doc model maps 1:1 to `proposals.sections`, enabling section-level AI assist and comments anchored to section keys (matches `collaborations/` design).

### 13.3 AI assist UX

`POST /v2/proposals/{pid}/assist` with `{action, section_key, instruction}` → queued job → SSE update on the section → inline "diff applied" toast + version bump. No page reload, no full regeneration.

---

## 14. Backend Architecture (v4)

### 14.1 Dependency injection (composition root)

`infrastructure/di/container.py`:

```python
# container.py (sketch)
from app.infrastructure.database.mongo_repositories.user_repo import MongoUserRepository
from app.services.auth_service import AuthService

class Container:
    def __init__(self):
        self.user_repo = MongoUserRepository()
        ...
    def auth_service(self) -> AuthService:
        return AuthService(user_repo=self.user_repo, org_repo=self.org_repo)
```

FastAPI `Depends` wiring: routers depend on container-provided services via a small `get_service(ServiceType)` dependency. **Why:** today every router does `AuthService()`; tests can't substitute fakes, and cross-cutting decorators (tracing, metering) can't wrap calls. This is a mechanical refactor of constructor calls only — no logic change. `AuthService` already accepts repos in its constructor, so this closes an existing seam.

### 14.2 Events

`events/bus.py`: sync in-process dispatch now (single worker), Redis pub/sub later. Handlers: notifications, activity log, audit log, usage metering, analytics refresh. **Why:** decouples "proposal generated" from "send email + record usage + update analytics" — adding a handler is a registration, not a change to the generation path.

### 14.3 Queue

`infrastructure/queue/` + `tasks/` (Celery + Redis recommended; ARQ if avoiding a broker dependency):

- `generate_proposal` (moves off `BackgroundTasks`)
- `ingest_document` (knowledge pipeline)
- `export_all`, `send_notification`

**Why:** background LLM work must survive restarts, retry with backoff, and scale horizontally. Keep `BackgroundTasks` only for sub-second jobs (cache warm). `start_generation` gains `Idempotency-Key` support (dedupe on `(org, project, request_hash)`).

### 14.4 Storage

`infrastructure/storage/s3.py` — S3-compatible (MinIO locally, AWS/GCS/Wasabi prod). `upload_service.py` routes blobs to it; `knowledge_assets.file_ref` and proposal exports store there; local disk becomes the dev-only adapter. **Why:** multi-instance deployments can't share local disk; e-sign and share links need signed URLs.

### 14.5 Caching

- `infrastructure/cache/llm_redis.py`: Redis-backed LLM cache (key = hash(prompt + model)), replacing the in-memory dict. Survives restarts, shared across workers → real cost savings (duplicate prompts from the 5-min polling loop alone).
- Analytics aggregates cached in Redis with TTL + invalidation on `activity_events`.

### 14.6 Rate limiting

`middleware/rate_limit.py` → Redis token bucket keyed `org_id` (burst) + `user_id` (fairness). Limits become plan data (`billing/schemas.py` PLANS gains `rate_limits`), so Free vs Enterprise differ.

---

## 15. Deployment Architecture

### 15.1 Dev (today, works)

```
uvicorn (8000)  ── MongoDB (local)
vite (5173)     ── Redis (local)
                 ── Qdrant (cloud)
```

### 15.2 Target (Docker Compose → managed)

```
                        ┌──────────── Load Balancer (nginx) ────────────┐
                        │                                               │
                 api workers (uvicorn xN)                      frontend (static / CDN)
                        │                                               │
   ┌────────────────────┼────────────────────┐                          │
MongoDB Atlas      Redis (cache+queue)   Qdrant (vector)        S3/MinIO (objects)
   │                                                                    │
Celery workers (generate, ingest, export)  ──  LLM providers (groq/openai/nvidia/...)
```

- API: 2–4 uvicorn workers behind nginx; `--workers` with sticky session not needed (JWT).
- Workers: Celery concurrency tuned by model latency; generation job queued with TTL.
- Frontend: `npm run build` → CDN/object storage; env-config injected at deploy (`VITE_API_URL`).
- Observability: OpenTelemetry → (self-hosted Grafana+Prometheus or managed), structured JSON logs → Loki/ELK. `infrastructure/monitoring/` fills this gap.
- One-command local: add `docker-compose.yml` at repo root (mongo, redis, qdrant, minio, api, worker, frontend).

---

## 16. Multi-tenant Design

### 16.1 Current (already correct)

- `organization_id` on every aggregate; `get_current_org` from the token; repos query by org.

### 16.2 Hardening

1. **Tenant context middleware** (`middleware/tenant_context.py`): resolve `org_id + user + permissions` once; routers/use-cases read it instead of repeating `Depends(get_current_user)` chains. Removes the "forgot to scope" class of bugs.
2. **Index enforcement**: `(organization_id, ...)` compound indexes on every org-scoped collection (already partially in `ensure_indexes`).
3. **Cross-tenant leak tests**: contract tests asserting `orgA` cannot read `orgB` rows for every collection (the `project.organization_id != user.organization_id` inline checks in `projects.py` become a reusable `ensure_tenant_access(entity, org_id)` guard).
4. **ABAC (phase 3)**: `policies.py` — rules like `proposal:approve` only for `manager+` AND `org.plan != free`; evaluated before transition. RBAC remains the default; ABAC adds context (org plan, entity state).
5. **Billing isolation**: usage metering per org; plan limits enforced at the service boundary (`PlanLimitExceededError` already exists in `domain/exceptions.py` — wire it into generation/export/ingest).

---

## 17. Security Design

| Concern | Current | v4 action |
|---|---|---|
| AuthN | JWT access+refresh, type-checked | Keep. Add refresh-token rotation + reuse detection (store `token_version` on user) |
| AuthZ | RBAC permission lists | Keep + ABAC policies + `ensure_tenant_access` guard |
| Secrets | `.env` gitignored | Keep; add `SECRETS` via env/kms in deploy |
| Prompt injection | None | `llm/client.py`: add input sanitization pass for uploaded docs (strip instruction-like blocks), agent-side "ignore embedded instructions" system prompt |
| SSRF | None (RAG loaders may fetch URLs) | `rag/loader.py`: block private IP ranges on URL ingestion |
| Uploads | `MAX_UPLOAD_SIZE_MB`, local disk | Virus scan hook (ClamAV container), stored in S3 with private bucket + signed URLs |
| PII | None | Field-level redaction in activity/audit logs; mask emails/phones in exports when configured |
| E-sign | n/a | Adapter (DocuSign/PandaDoc) with webhook verification |
| Webhooks | Stripe only | Outbound signature (HMAC) + inbound verification |
| CORS | List-based | Keep; tighten per environment |
| Rate limits | In-memory | Redis + per-plan budgets (see §14.6) |
| Audit | `audit.py` | Unified `activity_events`; admin read-only access |

---

## 18. Scalability Strategy

1. **Stateless API** — JWT auth already; object storage + queue make workers stateless. Add uvicorn workers now, containers later.
2. **Cache first** — Redis LLM cache (biggest lever: repeated prompts), RAG result cache (`ENABLE_RAG_CACHE` already exists — wire it to Redis), analytics TTL cache.
3. **Queue everything slow** — generation, ingestion, exports off the request path (Celery). API latency becomes ~50ms regardless of LLM latency.
4. **Model cost routing** — already in `llm/models.py` chains; add per-org plan budget → automatic tier downgrade policy + admin alerts (`usage_events` feeds this).
5. **Read scaling** — analytics reads go to a secondary Mongo replica / cached aggregates, not live counts.
6. **Storage** — blobs out of Mongo; S3 + CDN for exports; signed URLs.
7. **Vector scale** — Qdrant collections per knowledge category (already); add collection-per-org partitioning when volume demands.
8. **Bottleneck guard** — generation concurrency cap per org (plan limit) and global queue; prevents the NVIDIA-style worker exhaustion seen in production.

---

## 19. Microservice Migration Strategy (future)

**Do not microservice now.** The monolith is small, cohesive, and fast to change; splitting early adds distributed-transaction and deployment costs without benefit.

When triggered (team > ~8, independent deploy cadence, dedicated infra budget):

1. **Strangler fig**: keep `api/v1` as the gateway; extract in order of isolation strength:
   - `billing` (already gateway-agnostic: `billing/router.py` + service) → first candidate.
   - `export` (stateless, queue-driven) → second.
   - `knowledge` + `rag` ingestion (worker-heavy) → third.
   - `notifications` (fan-out) → fourth.
   - Core generation stays in the monolith longest (it's the heart and benefits from in-process state).
2. **Contracts**: v2 API + event bus become the inter-service contract (events already carry `org_id`). Use async-first integration (queue + events), not REST-to-REST, for latency isolation.
3. **Shared kernel**: keep a small package (`proposalcraft-common`) for tenant context, permissions, usage metering — the anti-corruption layer.
4. **Data**: per-service collections with owner-only writes (billing owns `subscriptions`+`usage_events`; core owns entities; analytics owns cached aggregates). Cross-service reads via events, not shared collections.

---

## 20. Enterprise SaaS Roadmap

### Phase 0 — Stabilize (1–2 sprints) *[partially done this session]*
- Session persistence fix (refresh tokens) — **done**
- Permission fallback for stale role lists — **done**
- Frontend real data (Dashboard), remove dead links — **done**
- Redis-backed LLM cache; rate-limit store; queue generation off `BackgroundTasks`

### Phase 1 — Project-centric core (2–3 sprints)
- v2 API: projects aggregate, proposal CRUD under projects, idempotent generation
- Proposal lifecycle state machine + approvals collection
- Version snapshots + diff
- Activity feed (unified `activity_events`) + in-app notifications
- Frontend: Project Hub + Proposal Studio (editor, comments)

### Phase 2 — Knowledge Hub (2–3 sprints)
- `knowledge/` types + CRUD; Workspace manager UI
- Knowledge pipeline: upload → clean → classify → chunk → embed → Qdrant (reuses `rag/` primitives)
- Domain engine registry (`engines/domains/*`) + industry classifier agent
- RAG retrieval surfaces org knowledge automatically (rag_agent)

### Phase 3 — Monetization & scale (2–3 sprints)
- Usage metering (`usage_events`) → credits + AI token limits per plan
- Razorpay adapter + invoices; Stripe stays
- RBAC → ABAC policies; plan-limit enforcement on generation/export/ingest
- Share links + client portal + e-sign adapter; exports to S3

### Phase 4 — Enterprise integrations (per-quarter)
- Notifications: email (SendGrid), Slack, Teams
- Integrations: Google Drive, SharePoint, HubSpot, Salesforce, Jira, Confluence
- Webhook framework + outbound events

### Phase 5 — Intelligence layer
- Analytics v2: win rate, revenue, avg generation time, industry distribution, AI usage, quality score, productivity, pipeline
- Proposal quality scoring model (calibrate `quality_agent` on outcomes)
- A/B template experiments; negotiation assistant

### KPIs to gate each phase
- P95 generation completion < 2 min; queue depth visibility
- Zero silent LLM failures (every downgrade logged)
- Zero cross-tenant data leaks (contract tests)
- Billing accuracy = usage ledger reconciliation 100%
- Frontend: no route 404s; every module renders server data

---

## Appendix A — Concrete "do now" list (highest ROI, lowest risk)

1. `infrastructure/cache/llm_redis.py` — replace in-memory `llm/cache.py` store (saves real cost immediately).
2. `middleware/rate_limit.py` → Redis token bucket (correctness under multiple workers).
3. `tasks/` + `infrastructure/queue/` — move `run_and_finalize` from `BackgroundTasks` to a durable job (survives restarts).
4. `events/bus.py` + `activity_events` — unify audit/activity logging.
5. `api/v2/` with project-centric endpoints — new UI builds on v2, v1 untouched.
6. `knowledge/pipeline.py` — first asset type: uploaded PDF → chunk → embed → Qdrant (uses existing `rag/loader.py`, `chunker.py`, `vectorstore.py`).
7. `infrastructure/di/container.py` — mechanical DI refactor of existing services.
8. `lifecycle/machine.py` — state machine over the existing `ProposalStatus` enum (no data migration: keep statuses, add `lifecycle.history`).
9. `analytics/usage.py` — emit `usage_events` from `_call_provider` (one line in `llm/client.py`).
10. Frontend: realtime via SSE for generation status (replaces 3s polling), Studio editor (TipTap) as a new route — old pages untouched.

---

*This document is a living artifact. Revisit after each phase; sections 5–9 change first, 15–19 last.*
