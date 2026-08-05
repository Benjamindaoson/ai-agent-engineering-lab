# AgentLab Local Development and Test Plan

## 1. Goal

The system must run locally before any production deployment.

MVP must support two modes:

```text
AGENT_MODE=mock
AGENT_MODE=claude
```

Mock mode is mandatory for all developers and CI. Claude mode is optional and only runs when credentials and Agent Runner are configured.

## 2. Required Local Services

```text
Next.js web app
FastAPI API
Worker
Redis
Postgres or Supabase local stack
Agent Runner
Docker Sandbox, optional in mock mode
```

## 3. Recommended Commands

Final commands may change after code scaffolding, but the target developer experience should be:

```powershell
pnpm install
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r apps/api/requirements.txt
docker compose up -d
pnpm dev
```

Backend:

```powershell
cd apps/api
uvicorn app.main:app --reload
```

Worker:

```powershell
cd apps/worker
python -m worker.main
```

Agent Runner:

```powershell
cd apps/agent-runner
python -m agent_runner.main
```

## 4. Environment Variables

Create `.env.example` with:

```text
APP_ENV=development
AGENT_MODE=mock

NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/agentlab
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

REDIS_URL=redis://localhost:6379/0

ANTHROPIC_API_KEY=
CLAUDE_AGENT_SDK_ENABLED=false

STORAGE_BUCKET=submissions

SENTRY_DSN=
POSTHOG_KEY=
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=
```

Rules:

```text
System must boot with AGENT_MODE=mock and no ANTHROPIC_API_KEY.
Claude mode must fail clearly when credentials are missing.
No service role key may be exposed to frontend.
```

## 5. Seed Data

Seed script must create:

```text
3 target jobs
10 skill nodes
1 RAG project template
1 final submission task
1 learner user
1 mentor user
basic job_skill_requirements
```

## 6. Smoke Test Flow

Manual smoke test:

```text
Open web app
Sign in as learner
Select AI Application Engineer
Open RAG Knowledge Agent project
Submit GitHub repo URL and reflection
Run review in mock mode
Wait for review completed
Open review report
Open skill graph
Generate Hiring Passport
Open passport page
Export resume bullets
```

## 7. Backend Tests

Required pytest coverage:

```text
Review JSON validation
Mock review job execution
Evidence generation
Skill score update
Passport snapshot generation
Submission state transition
Role authorization for mentor-only endpoints
```

Example test names:

```text
test_mock_review_result_validates
test_review_generates_evidence_items
test_evidence_updates_skill_score_history
test_passport_snapshot_uses_verified_evidence
test_frontend_cannot_write_evidence_directly
```

## 8. Frontend Tests

Recommended:

```text
TypeScript type check
component smoke tests
Playwright end-to-end happy path
```

Playwright happy path:

```text
login
select job
submit project
view review
generate passport
open passport
```

## 9. CI Requirements

GitHub Actions should run:

```text
frontend lint
frontend typecheck
frontend build
backend lint
backend tests
schema validation tests
mock end-to-end smoke test
```

CI must not require:

```text
ANTHROPIC_API_KEY
real Supabase cloud project
paid services
external GitHub repo access
```

## 10. Definition of Done for Any Feature

A feature is done only when:

```text
API works
UI works
data persists
state transitions are valid
loading and error states exist
tests pass
mock mode works
refreshing page preserves state
README or docs updated
no core write bypasses FastAPI
```

## 11. Production Readiness Checklist

Before production:

```text
staging environment exists
migrations run cleanly
seed data separated from production data
Sentry enabled
PostHog enabled
Langfuse enabled for AI calls
review job retry strategy exists
agent logs are stored
sandbox has no production secrets
passport visibility controls work
```

## 12. How to Guarantee It Runs

No software can be guaranteed by assertion. It must be guaranteed by process.

AgentLab should follow these rules:

```text
Build vertical slices, not isolated pages.
Keep mock mode working at all times.
Use migrations for every database change.
Validate every AI output with schema.
Run tests in CI on every commit.
Deploy to staging before production.
Keep the first user flow small enough to smoke test manually.
```

