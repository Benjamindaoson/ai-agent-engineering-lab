# Agent Kernel Runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the real backend agent kernel that unifies Planner, Tutor, Review, sandbox results, next task generation, and frontend coach status.

**Architecture:** Add a focused `agent_kernel.py` module with data classes and persistence helpers. Reuse existing service functions but route all agent decisions through the new run recorder. Keep old planning/tutor run tables for compatibility while `agent_runs` becomes the canonical execution log.

**Tech Stack:** FastAPI, SQLite/Postgres-compatible SQL, Pydantic, Claude Agent SDK, Next.js.

---

### Task 1: Unified AgentRun Persistence

**Files:**
- Modify: `apps/api/app/schema.sql`
- Modify: `apps/api/app/db.py`
- Create: `apps/api/app/agent_kernel.py`
- Test: `apps/api/tests/test_agent_kernel.py`

- [ ] Add a failing test that creates a planning session and asserts `agent_runs` contains `LearningPlannerAgent` with `parent_type='planning_session'`.
- [ ] Add schema compatibility columns for learner, agent name, runtime, parent, tools, raw input and raw output.
- [ ] Implement `record_agent_run` and make `record_agent_trace` optionally link to an AgentRun.
- [ ] Re-run the focused API test and confirm it passes.

### Task 2: Planner and Tutor Use Same Runtime Contract

**Files:**
- Modify: `apps/api/app/services.py`
- Modify: `apps/api/app/agent_runtime.py`
- Test: `apps/api/tests/test_agent_kernel.py`

- [ ] Add failing tests for Planner and Tutor proving both write canonical `agent_runs`.
- [ ] Wrap Planner and Tutor outputs with runtime metadata and tool names.
- [ ] Preserve existing `planning_agent_runs` and `tutor_agent_runs` responses.
- [ ] Re-run focused API tests.

### Task 3: Review Chain Writes Canonical AgentRun and Next Task

**Files:**
- Modify: `apps/api/app/services.py`
- Test: `apps/api/tests/test_agent_kernel.py`

- [ ] Add failing test for submission review that asserts sandbox run, ReviewAgent run, CoachTaskAgent run, and open next task all exist.
- [ ] Move ReviewAgent persistence to `record_agent_run`.
- [ ] Make CoachTaskAgent persistence canonical.
- [ ] Re-run focused API tests.

### Task 4: Frontend Shows AI Thinking State

**Files:**
- Modify: `apps/web/lib/api.ts`
- Modify: `apps/web/app/coach/page.tsx`
- Test: `apps/web/tests/vertical-slice.spec.ts`

- [ ] Add contract fields for latest agent run status if missing.
- [ ] Render natural language status: `AI 教练正在判断下一步`.
- [ ] Avoid raw backend wording as primary page language.
- [ ] Run typecheck and focused e2e.

### Task 5: Full Verification

**Files:**
- No new files.

- [ ] Run API tests.
- [ ] Run frontend typecheck.
- [ ] Run frontend build.
- [ ] Run focused e2e test.

