# Rebuild Learner Core Experience Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the learner-facing core with a diagnosis-driven Personal Mission Control that shows track selection, multi-thread training, course window, practice window, project studio, and agent team.

**Architecture:** Reuse current FastAPI contracts. Add a small frontend view-model adapter and rewrite `/coach` as the new core experience. Keep existing pages as handoff targets.

**Tech Stack:** Next.js App Router, React Server Components, existing FastAPI API, existing CSS, Playwright.

## Global Constraints

- No new dependencies.
- No backend schema migration.
- `/coach` must be readable and usable at 127.0.0.1:3000/coach.
- Courses and practice must be visible in the core learner screen.
- The screen must show multi-thread training, not one linear step.
- Keep tests runnable with `npm --workspace apps/web run test:e2e -- tests/vertical-slice.spec.ts`.

---

## Task 1: Create Learner Mission View Model

**Files:**
- Create: `apps/web/lib/learner-mission.ts`
- Modify: `apps/web/lib/api.ts`

**Interfaces:**
- Consumes: `AgentCommandCenter`, `LearningPlan`, skill map data.
- Produces: `LearnerTrack`, `MissionThread`, `AgentRole`, and `buildLearnerMission()`.

Steps:
- [ ] Create `LearnerTrack = "foundation" | "builder" | "workflow"`.
- [ ] Create `buildLearnerMission(center, learningPlan, skillMap)`.
- [ ] Derive track from `learningPlan.current_level` and `learner.target_role`.
- [ ] Return visible threads: main, foundation, course, practice, project, review, career.
- [ ] Run `npm --workspace apps/web run typecheck`.

## Task 2: Rebuild `/coach`

**Files:**
- Modify: `apps/web/app/coach/page.tsx`
- Modify: `apps/web/app/page.tsx`

**Interfaces:**
- Consumes: `/api/agents/command-center`, `/api/learning-plan/me`, `/api/skill-map/me`.
- Produces: Personal Mission Control.

Steps:
- [ ] Fetch command center, learning plan, and skill map.
- [ ] Render diagnosis result, assigned track, and reason.
- [ ] Render multi-thread training lanes.
- [ ] Render course window and practice window.
- [ ] Render project studio preview and agent team.
- [ ] Keep handoffs to `/intake`, `/learn/[id]`, `/lab/[id]`, `/gate`, `/skill-map`, `/passport`.
- [ ] Run `npm --workspace apps/web run typecheck`.

## Task 3: Replace Core Visual Layer

**Files:**
- Modify: `apps/web/app/globals.css`

**Interfaces:**
- Produces: readable professional training system UI.

Steps:
- [ ] Add `.mission-control-v2` layout.
- [ ] Add `.track-brief`, `.training-thread`, `.course-window`, `.practice-window`, `.agent-team`.
- [ ] Avoid low-contrast overlays and diagonal hero backgrounds.
- [ ] Run Playwright e2e.

## Task 4: Update E2E

**Files:**
- Modify: `apps/web/tests/vertical-slice.spec.ts`

**Interfaces:**
- Verifies learner core.

Steps:
- [ ] Assert `/coach` shows diagnosis track.
- [ ] Assert course window is visible.
- [ ] Assert practice window is visible.
- [ ] Assert project studio is visible.
- [ ] Assert at least six training threads are visible.
- [ ] Assert no backend terms appear.

## Task 5: Final Verification

Steps:
- [ ] Run `npm run test:api`.
- [ ] Run `npm --workspace apps/web run typecheck`.
- [ ] Run `npm --workspace apps/web run build`.
- [ ] Run `npm --workspace apps/web run test:e2e -- tests/vertical-slice.spec.ts`.
- [ ] Check `http://127.0.0.1:3000/coach`.

