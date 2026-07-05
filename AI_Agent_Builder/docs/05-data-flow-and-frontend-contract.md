# Data Flow and Frontend Contract v0.1

## 1. Purpose

This document answers four implementation questions:

```text
How does the backend return information to the frontend?
How do different system parts pass information?
Where is data stored?
How is data read?
```

The main rule:

```text
FastAPI is the trusted Review/Evidence/Skill/Passport gateway.
Supabase is the data store and identity provider.
Next.js may read safe product data through server-side Supabase access.
Next.js must not directly write core review/evidence/skill/passport tables.
```

## 2. System Boundaries

```text
Browser / Next.js
→ uses Supabase Auth for session
→ reads safe product data through Next.js server-side Supabase access or FastAPI
→ sends core review/evidence/passport commands to FastAPI Review Service
→ FastAPI validates Supabase JWT
→ FastAPI reads/writes core Supabase Postgres tables
→ Worker processes async jobs
→ Agent Runner returns structured review output
→ FastAPI persists review/evidence/skill/passport data
→ Next.js polls or refetches API state
```

## 3. Data Ownership

### Supabase Auth

Owns:

```text
identity
login
session
JWT
password / OAuth provider state
```

### FastAPI

Owns writes for:

```text
submissions
review jobs
reviews
evidence
skill scores
technical defense
passport snapshots
portfolio exports
```

FastAPI may also serve reads for these core resources.

### Next.js Server-Side Code

May own safe product reads and lightweight writes:

```text
public project templates
public or unlisted passport reads
learner profile display
target job selection, if implemented as safe server-side mutation
non-core preferences
```

Boundary:

```text
If a write changes review, evidence, skill score, or passport snapshot state, it goes through FastAPI Review Service.
```

### Worker

Owns execution for:

```text
queued review jobs
mock review execution
agent review execution orchestration
evidence generation job
skill score update job
passport snapshot job
portfolio export job
```

The Worker does not expose public APIs.

### Agent Runner

Owns execution for:

```text
workspace preparation
Claude Agent SDK run
tool call logging
structured review JSON output
agent artifacts
```

Agent Runner does not directly update learner skill scores or passport snapshots.

### Next.js

Owns:

```text
page rendering
form state
optimistic UI where safe
loading states
error states
client-side navigation
public passport page display
```

Next.js does not own core business state.

## 4. Read / Write Rules

### Frontend May Read Through FastAPI

```text
GET /api/jobs
GET /api/skill-map/me
GET /api/projects
GET /api/projects/{id}
GET /api/submissions/{id}
GET /api/reviews/jobs/{id}
GET /api/reviews/{id}
GET /api/evidence/me
GET /api/passports/{slug}
```

### Frontend May Write Through FastAPI

```text
POST /api/jobs/select
POST /api/submissions
POST /api/reviews/jobs
POST /api/passports/generate
POST /api/portfolio/export
```

### Frontend Must Not Directly Write

```text
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
```

### Public Passport Read

Public or unlisted passport pages may be served by Next.js using:

```text
GET /api/passports/{slug}
```

or by a dedicated public read endpoint with strict visibility checks.

## 5. Response Envelope

Use direct resource envelopes for successful responses:

```json
{
  "submission": {
    "id": "uuid",
    "status": "review_queued"
  }
}
```

For list responses:

```json
{
  "items": [],
  "next_cursor": null
}
```

For operation responses:

```json
{
  "job_id": "uuid",
  "status": "queued"
}
```

Errors always use:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Invalid submission payload.",
    "details": {}
  }
}
```

## 6. Frontend Data Fetching Pattern

Use TanStack Query for all server state.

Recommended query keys:

```text
['jobs']
['skill-map', 'me']
['projects']
['project', learnerProjectId]
['submission', submissionId]
['review-job', reviewJobId]
['review', reviewId]
['evidence', 'me']
['passport', slug]
```

Recommended mutation keys:

```text
selectTargetJob
createSubmission
createReviewJob
generatePassport
exportPortfolio
```

After mutation success, invalidate related queries.

Example:

```text
createSubmission success
→ invalidate ['projects']
→ invalidate ['project', learnerProjectId]
→ start polling ['review-job', reviewJobId]
```

## 7. Page-Level Data Contracts

### Page: Target Job Selection

Reads:

```text
GET /api/jobs
GET /api/skill-map/me, optional
```

Writes:

```text
POST /api/jobs/select
```

After write:

```text
invalidate skill-map
navigate to /projects
```

### Page: Project Dashboard

Reads:

```text
GET /api/projects
GET /api/skill-map/me
```

Displays:

```text
project status
required project
latest review status
skill gap summary
```

### Page: RAG Project Detail

Reads:

```text
GET /api/projects/{learner_project_id}
GET /api/submissions/{latest_submission_id}, if any
```

Writes:

```text
POST /api/submissions
```

### Page: Review Running

Reads:

```text
GET /api/reviews/jobs/{review_job_id}
```

Polling:

```text
every 2 seconds while queued/running
stop when succeeded/failed/cancelled
```

On succeeded:

```text
read review_id
navigate to /reviews/{review_id}
```

### Page: Review Report

Reads:

```text
GET /api/reviews/{review_id}
GET /api/evidence/me
GET /api/skill-map/me
```

Displays:

```text
overall score
hiring readiness
rubric scores
risk flags
next actions
new evidence
skill changes
```

### Page: Skill Graph

Reads:

```text
GET /api/skill-map/me
GET /api/evidence/me
```

Displays:

```text
current score
required level
confidence
evidence count
evidence links
```

### Page: Hiring Passport

Writes:

```text
POST /api/passports/generate
```

Reads:

```text
GET /api/passports/{slug}
```

Displays:

```text
snapshot version
target job
skill summary
project evidence
review summary
technical defense records
portfolio exports
```

### Page: Portfolio Export

Writes:

```text
POST /api/portfolio/export
```

Displays:

```text
README draft
resume bullets
interview script
LinkedIn project summary
```

## 8. Full Submission-to-Passport Flow

### Step 1: Learner submits project

Frontend:

```http
POST /api/submissions
```

Backend writes:

```text
submissions
review_jobs, if queue_review=true
```

Backend returns:

```json
{
  "submission_id": "uuid",
  "status": "review_queued",
  "review_job_id": "uuid"
}
```

Frontend:

```text
navigate to review running page
poll review job
```

### Step 2: Worker runs review job

Worker reads:

```text
review_jobs
submissions
project_templates
tasks
skill_nodes
job_skill_requirements
rubric config
```

Worker calls:

```text
Mock Review Adapter
or Agent Runner Service
```

Worker receives:

```text
structured ReviewResult JSON
```

Worker writes through internal service layer:

```text
agent_runs
reviews
review_scores
review_risk_flags
evidence_items
skill_score_history
learner_skill_scores
```

Worker updates:

```text
review_jobs.status = succeeded
submissions.status = review_completed or needs_revision or passed
```

### Step 3: Frontend reads review

Frontend polls:

```http
GET /api/reviews/jobs/{review_job_id}
```

When succeeded:

```http
GET /api/reviews/{review_id}
GET /api/skill-map/me
GET /api/evidence/me
```

### Step 4: Learner generates passport

Frontend:

```http
POST /api/passports/generate
```

Backend reads:

```text
target job
learner skill scores
passport-eligible evidence
reviews
technical defenses
portfolio exports
project submissions
```

Backend writes:

```text
hiring_passports, if missing
passport_snapshots
```

Frontend reads:

```http
GET /api/passports/{slug}
```

## 9. Internal Service Layer

FastAPI and Worker should share domain services.

Recommended modules:

```text
SubmissionService
ReviewJobService
ReviewPersistenceService
EvidenceService
SkillScoreService
PassportService
PortfolioService
AuthorizationService
```

The Worker should not duplicate business logic. It should call the same service functions used by FastAPI, or shared domain modules.

## 10. Storage Locations

### Supabase Postgres

Stores structured relational data:

```text
users
jobs
skills
projects
tasks
submissions
reviews
evidence
skill scores
passport snapshots
portfolio exports
```

### Supabase Storage

Stores files:

```text
submission uploads
architecture diagrams
evaluation reports
technical defense videos
agent artifacts
sandbox stdout/stderr logs when large
generated PDFs, optional
```

Store file references in Postgres:

```text
source_url
stdout_ref
stderr_ref
output_ref
```

### Redis

Stores ephemeral queue state:

```text
review job queue
retry metadata
worker locks
short-lived task state
```

Redis is not the source of truth.

### Agent Runner Workspace

Stores temporary files:

```text
cloned repo
extracted submission
temporary sandbox output
Claude Agent SDK session workspace
```

This workspace must be destroyed after the job, except persisted artifacts uploaded to Storage.

## 11. Data Reading Strategy

### Authenticated Learner Reads

FastAPI filters by:

```text
current_user.id
```

Learners can read:

```text
their own submissions
their own reviews
their own evidence
their own skill scores
their own passport
```

### Mentor Reads

Mentors can read assigned cohort learners.

MVP can simplify:

```text
mentor role can read all learner review queues
```

but this must be narrowed before production cohorts.

### Public Reads

Public reads only return:

```text
passport_snapshots where visibility is public or unlisted
```

Never return:

```text
private notes
raw agent prompts
private logs
unverified sensitive feedback
service metadata
```

## 12. Async Status Contract

Long-running operations always return a job id.

Job status values:

```text
queued
running
succeeded
failed
cancelled
```

Frontend behavior:

```text
show queued state
poll while queued/running
show failure with retry action
refetch review/passport when succeeded
```

No websocket is required for v0.1.

Websocket or server-sent events can be added later.

## 13. Caching Rules

Do not cache authenticated learner state globally.

Can cache:

```text
GET /api/jobs
GET /api/projects templates, if separated from learner state
public passport page, short TTL
```

Must refetch after:

```text
submission created
review job completed
evidence generated
passport snapshot generated
mentor verification
```

## 14. Contract Between Worker and Agent Runner

Worker sends:

```json
{
  "review_job_id": "uuid",
  "submission": {
    "github_repo_url": "https://github.com/example/rag-agent",
    "demo_url": "https://example.com",
    "reflection_text": "..."
  },
  "project": {
    "slug": "rag_knowledge_agent",
    "title": "RAG Knowledge Agent"
  },
  "rubric": {
    "version": "rag-v0.1",
    "items": []
  },
  "mode": "mock"
}
```

Agent Runner returns:

```json
{
  "agent_run": {
    "provider": "mock",
    "model": null,
    "latency_ms": 120,
    "token_usage": null
  },
  "review_result": {
    "overall_score": 78,
    "hiring_readiness": "needs_revision",
    "confidence": 0.82,
    "rubric_scores": [],
    "evidence_items": []
  },
  "artifacts": []
}
```

## 15. Source of Truth Summary

```text
Identity:
Supabase Auth

Business state:
Supabase Postgres through FastAPI

File assets:
Supabase Storage

Queue state:
Redis

Agent temporary workspace:
Agent Runner local workspace / Sandbox

Hiring evidence:
evidence_items table

Current skill state:
learner_skill_scores table

Public hiring profile:
passport_snapshots table
```

## 16. Implementation Order

Build in this order:

```text
1. Database schema and seed data
2. FastAPI read endpoints for jobs/projects/skill map
3. Submission endpoint
4. Review job creation
5. Mock Worker
6. Review persistence
7. Evidence generation
8. Skill score update
9. Passport snapshot generation
10. Next.js pages wired to APIs
```

Do not build Claude Agent SDK integration before mock review flow works.
