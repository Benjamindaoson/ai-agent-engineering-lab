# AgentLab Technology Selection v0.1

## 1. Executive Decision

AgentLab v0.1 should use a hybrid architecture:

```text
Next.js + Supabase for product experience and normal app data
FastAPI Review Service for Review / Evidence / Skill / Passport core writes
Redis + RQ for async jobs
Claude Agent SDK inside an isolated Agent Runner
Docker Sandbox for project execution checks
```

The key correction:

```text
Not every interface must go through FastAPI.
But every write that affects review, evidence, skill score, or Hiring Passport must go through the trusted Review Service.
```

## 2. Final Stack Summary

| Area | Selected Tech | Role | MVP Priority |
|---|---|---|---|
| Web App | Next.js + React + TypeScript | Product UI, BFF, public Passport pages | Required |
| Styling | Tailwind CSS + shadcn/ui | Fast, consistent app UI | Required |
| Frontend Server State | TanStack Query | API fetching, polling, cache invalidation | Required |
| Frontend Local State | Zustand | Lightweight UI state | Required |
| Forms | React Hook Form + Zod | Form handling and client validation | Required |
| Auth | Supabase Auth | Login, session, JWT | Required |
| Database | Supabase Postgres | Source of truth for structured data | Required |
| Storage | Supabase Storage | Reports, diagrams, videos, artifacts | Required |
| Vector Search | Supabase pgvector | JD, rubric, knowledge, project retrieval | Required |
| Review Service | FastAPI + Pydantic | Review, Evidence, Skill, Passport core writes | Required |
| ORM / Migrations | SQLModel or SQLAlchemy + Alembic | Schema and data access | Required |
| Async Queue | Redis + RQ | Review jobs and snapshot generation | Required |
| Agent Runtime | Claude Agent SDK | Repo/code/project-level review | Required |
| Light LLM Calls | Claude API | Tutor, diagnosis, portfolio text, mock interview | Required |
| Agent Isolation | Agent Runner Service | Runs Claude Agent SDK away from web/API service | Required |
| Code Execution | Docker Sandbox | Install/run/test learner projects safely | Required for real review, mockable in v0.1 |
| Observability | Sentry + PostHog + Langfuse | Errors, product analytics, LLM traces | Required |
| Deployment | Vercel + Railway/Render/Fly.io + Supabase | Fast MVP deployment | Required |
| CI/CD | GitHub Actions | Tests, build, smoke checks | Required |
| Payments | Stripe | Cohort payment | Optional in v0.1 |
| Email | Resend or Postmark | Notifications and invitations | Optional in v0.1 |

## 3. Architecture Shape

```text
Browser
  ↓
Next.js Web App / BFF
  ↓                 ↘
Supabase Auth        FastAPI Review Service
Supabase Postgres      ↓
Supabase Storage       Redis / RQ
Supabase pgvector      ↓
                    Worker
                      ↓
                 Agent Runner Service
                      ↓
              Claude Agent SDK + Sandbox
                      ↓
             Structured Review JSON
                      ↓
        Review / Evidence / Skill / Passport
```

## 4. What Goes Through Next.js + Supabase

Use Next.js server-side code and Supabase for product-level reads and simple writes:

```text
auth session handling
profile display
target job selection
project list reads
project detail reads
public Hiring Passport reads
static course / project content reads
light portfolio display
```

Why:

```text
faster product development
less API boilerplate
excellent fit for dashboard and public pages
Supabase Auth integrates cleanly with Next.js
```

Boundary:

```text
Next.js can write simple learner preference and profile data.
Next.js must not write reviews, evidence, skill scores, or passport snapshots directly.
```

## 5. What Must Go Through FastAPI Review Service

Use FastAPI for all trusted domain writes:

```text
review_jobs
reviews
review_scores
review_risk_flags
evidence_items
learner_skill_scores
skill_score_history
passport_snapshots
agent_runs
agent_tool_calls
sandbox_runs
technical_defense scoring
```

Why:

```text
Pydantic is ideal for strict Review JSON validation.
Python is the better ecosystem for AI review, file parsing, agent orchestration, and workers.
Review/Evidence/Skill logic must be centralized.
The same domain services can be used by API endpoints and workers.
```

FastAPI is not selected because every SaaS app needs a separate backend. It is selected because AgentLab's core product is an evidence pipeline.

## 6. Why Not All FastAPI

Rejected as the only route:

```text
Browser → FastAPI → Supabase for everything
```

Pros:

```text
clear backend boundary
all business logic centralized
clean RBAC and auditing
```

Cons:

```text
slower MVP UI development
more endpoint boilerplate for simple reads
duplicate auth/session plumbing
more type synchronization overhead between frontend and backend
```

Decision:

```text
Use FastAPI where trust and domain correctness matter.
Use Next.js + Supabase where speed and product experience matter.
```

## 7. Why Not All Next.js

Rejected:

```text
Next.js Server Actions / Route Handlers own all business logic
```

Pros:

```text
single TypeScript stack
fastest UI iteration
easy colocation with pages
```

Cons:

```text
not ideal for long-running review jobs
not ideal for Claude Agent SDK execution
not ideal for sandbox orchestration
risks scattering Evidence/Skill logic across UI-adjacent code
Vercel/serverless limits are a poor fit for heavy repo review
```

Decision:

```text
Next.js is the product layer and BFF, not the review/evidence engine.
```

## 8. Why Not Supabase Edge Functions as the Core Backend

Rejected as primary backend:

```text
Supabase Edge Functions own core review logic
```

Pros:

```text
close to Supabase Auth and Postgres
simple deployment
good for webhooks and light server-side actions
```

Cons:

```text
Deno/runtime constraints are not a good fit for Claude Agent SDK + sandbox
not ideal for long-running repo analysis
Python review ecosystem is stronger
harder to share logic with worker and agent runner
```

Decision:

```text
Use Edge Functions later for webhooks or lightweight integrations, not the core review pipeline.
```

## 9. Why FastAPI for the Review Service

Selected because:

```text
Pydantic gives strict schema validation.
Python is strong for AI, document parsing, test execution, and worker code.
FastAPI is simple enough for MVP but mature enough for production.
It works well with SQLModel/SQLAlchemy, Alembic, pytest, and RQ.
It can share models and service code with worker processes.
```

Tradeoffs:

```text
Adds a second language next to the TypeScript frontend.
Requires JWT validation against Supabase.
Requires API client types or generated schemas for frontend.
```

Mitigation:

```text
Keep FastAPI focused on Review/Evidence/Skill/Passport.
Generate OpenAPI types for frontend later.
Use shared JSON schemas for ReviewResult and EvidenceCandidate.
```

## 10. Why Supabase

Selected for:

```text
Postgres source of truth
Auth and JWT
Storage for submissions and artifacts
pgvector for retrieval
admin UI during MVP
low operational overhead
```

Tradeoffs:

```text
Vendor dependency.
RLS can become complex if mixed with service-role backend writes.
Local Supabase setup can add friction.
```

Mitigation:

```text
Use standard Postgres schemas and migrations.
Keep all core writes service-side.
Use RLS as defense-in-depth, not the only authorization mechanism.
Avoid Supabase-specific business logic where possible.
```

## 11. Why Claude Agent SDK

Claude Agent SDK is selected as the project-level review runtime.

It should handle:

```text
repo reading
code review
README review
RAG implementation review
workflow/tool-use review
debug analysis
interview risk generation
structured review output
```

It should not handle:

```text
normal profile CRUD
simple dashboard reads
all tutoring interactions
passport rendering
payment
email notifications
```

Tradeoffs:

```text
Potential cost.
Longer task runtime.
Requires permissions and tool-use controls.
Can produce inconsistent output without strict schema validation.
```

Mitigation:

```text
Run it inside Agent Runner, not the web/API process.
Use permission profiles.
Validate all output with Pydantic.
Keep AGENT_MODE=mock available for CI and local development.
Log agent runs and tool calls.
```

## 12. Why Docker Sandbox

Selected for v0.1 because:

```text
local and inexpensive
well understood
enough for basic install/start/test checks
portable to CI and worker hosts
```

Tradeoffs:

```text
security hardening is non-trivial
Windows local Docker differences can be annoying
scaling many parallel sandboxes is operationally harder
```

Mitigation:

```text
start with limited commands and timeouts
do not inject production secrets
restrict network, CPU, memory, and runtime
move to E2B/Modal/Firecracker when concurrent real execution grows
```

## 13. Why Redis + RQ

Selected for MVP:

```text
simple Python-native queue
low learning cost
works well with FastAPI and worker processes
enough for review jobs, passport snapshots, and portfolio export
```

Tradeoffs:

```text
not as durable or expressive as Temporal
complex retry/compensation flows will become harder later
```

Mitigation:

```text
keep job state in Postgres as source of truth
use Redis as queue, not durable state
move to Temporal when workflow complexity justifies it
```

## 14. Why Not Temporal Now

Temporal is likely a good future choice, but not v0.1.

Reasons to wait:

```text
operational overhead
new programming model
MVP workflow is short enough for RQ
more important to validate product loop first
```

Trigger to adopt later:

```text
multi-step review workflow becomes complex
manual retries become painful
agent jobs need durable resume
many compensation paths appear
```

## 15. Data Access Policy

### Direct Supabase Access

Allowed from Next.js server-side only for:

```text
read public project templates
read public passport snapshots
read current user's non-core profile data
write lightweight profile/preferences where safe
```

### FastAPI Review Service Required

Required for:

```text
submissions that queue review
review job creation
review persistence
evidence generation
skill score update
passport snapshot generation
mentor verification
technical defense scoring
```

### Browser Direct DB Access

Avoid for v0.1 except Supabase Auth client session.

Reason:

```text
The product is evidence-sensitive.
It is safer to keep product data access behind server code until permissions are proven.
```

## 16. Frontend Data Flow

Recommended frontend pattern:

```text
TanStack Query for server state
Zustand for local UI state
React Hook Form + Zod for forms
API client wrapper for FastAPI Review Service
Supabase client only for auth session and safe reads if needed
```

Long-running review flow:

```text
POST create submission/review job
→ receive review_job_id
→ poll GET review job
→ on succeeded, fetch review/evidence/skill-map
→ generate passport snapshot
```

No WebSocket is required in v0.1.

## 17. Observability Selection

### Sentry

Use for:

```text
frontend exceptions
FastAPI errors
worker failures
agent runner failures
sandbox failures
```

### PostHog

Use for:

```text
activation funnel
project submission funnel
review completion funnel
passport generation funnel
passport view analytics
```

### Langfuse

Use for:

```text
Claude API calls
Claude Agent SDK run metadata
prompt versions
review latency
token usage
cost
quality debugging
```

Tradeoff:

```text
Do not over-instrument before the first vertical slice works.
Add minimal event tracking and expand after MVP.
```

## 18. Deployment Selection

### MVP

```text
Next.js: Vercel
FastAPI Review Service: Railway / Render / Fly.io
Worker: Railway / Render / Fly.io
Agent Runner: dedicated Docker service
Redis: Upstash / Railway Redis
Database/Auth/Storage: Supabase
Sandbox: Docker host or E2B if local Docker ops becomes painful
```

### Not MVP

```text
Kubernetes
ECS
Temporal Cloud
full enterprise VPC deployment
```

Reason:

```text
The main MVP risk is product correctness, not infra scaling.
```

## 19. Security Decisions

Required:

```text
Supabase JWT validation in FastAPI
service role key never exposed to browser
LLM keys never exposed to browser
Agent Runner has least required DB/storage permissions
Sandbox has no production secrets
agent tool calls are logged
passport visibility is enforced server-side
raw agent logs are not public
```

Claude Agent SDK permissions:

```text
ReadOnlyReview
StaticRepoReview
SandboxExecutionReview
PassportMode
```

Disallowed in production:

```text
bypassPermissions
host root access
cross-learner workspace access
direct production DB writes from sandbox
```

## 20. Implementation Phases

### Phase 0: Contract First

```text
schemas
migrations
seed data
mock review output
API contracts
```

### Phase 1: Mock Vertical Slice

```text
Next.js pages
Supabase Auth
FastAPI Review Service
Postgres writes
RQ worker
mock Agent Runner
Evidence pipeline
Skill score update
Passport snapshot
```

### Phase 2: Claude Agent SDK Review

```text
Agent Runner
Claude Agent SDK
permission profiles
tool call logs
repo reading
structured JSON output
Langfuse traces
```

### Phase 3: Sandbox Execution

```text
Docker sandbox
install/start/test checks
stdout/stderr artifacts
demo health checks
```

### Phase 4: Hiring Layer

```text
technical defense
mentor verification
portfolio export
mock interview
external reviewer feedback
```

## 21. What This Stack Optimizes For

```text
Fast MVP iteration
clear evidence pipeline
safe agent execution boundary
strong schema validation
low infrastructure overhead
future migration path to more robust workflow infra
```

## 22. What This Stack Does Not Optimize For Yet

```text
massive enterprise multi-tenant deployment
high-concurrency sandbox execution
fully automated recruiting marketplace
offline/on-prem AI model hosting
complex durable multi-day workflows
```

Those can be addressed after the product loop is validated.

## 23. Final Decision

The best v0.1 technology selection is:

```text
Next.js + Supabase for product speed
FastAPI Review Service for trusted evidence writes
Redis/RQ for async execution
Claude Agent SDK in Agent Runner for project review
Docker Sandbox for safe project checks
Postgres Evidence Store for proof-of-work data
Hiring Passport snapshots for recruiter-facing output
```

This is not the only possible architecture. It is the best balance for AgentLab v0.1 because it keeps the product fast to build while protecting the only thing that matters: trusted evidence that a learner can build and explain an AI Agent project.

