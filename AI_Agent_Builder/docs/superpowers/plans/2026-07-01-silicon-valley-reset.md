# Silicon Valley Reset Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade AgentLab from a working demo into a credible AI Agent engineer training system with agent-native interaction, real project evidence, and recruiter-facing proof.

**Architecture:** Keep FastAPI, Next.js, SQLite/Postgres compatibility, and the existing AgentRun/AgentTrace kernel. Do not rebuild the app. Replace weak product surfaces with a smaller set of stronger flows: coach, planning, project workbench, tutor, review, and hiring report.

**Tech Stack:** Next.js App Router, FastAPI, SQLite/Postgres, Claude Agent SDK runtime path, Playwright, pytest.

## Global Constraints

- No new dependency unless an existing file proves it is already installed.
- Keep the existing routes unless a route is actively harmful.
- All user-facing Chinese must be natural human language.
- Backend terms such as AgentRun, quality gate, Evidence Store, Sandbox, Rubric, Skill Passport must not be primary UI copy.
- Every feature must leave one runnable check: pytest or Playwright.

---

## Current Gaps

1. The system still feels like pages, not a living AI coach.
2. Planner and Tutor have AgentRun records, but the UX does not show active reasoning, memory, or follow-up clearly enough.
3. Course content is too thin to justify premium training.
4. Project Lab is still not enough like a real builder workspace.
5. Review output is not yet recruiter-grade evidence.
6. The hiring report is not persuasive enough for employers.
7. Visual design is improved, but still not Silicon Valley A+ SaaS quality.

---

### Task 1: Make `/coach` The Real Home

**Files:**
- Modify: `apps/web/app/page.tsx`
- Modify: `apps/web/app/coach/page.tsx`
- Modify: `apps/web/app/globals.css`
- Test: `apps/web/tests/vertical-slice.spec.ts`

**Interfaces:**
- Consumes: `GET /api/agents/command-center`
- Produces: one primary action, one visible coach status, one memory summary, one project entry.

- [ ] Replace the current marketing/home surface with the coach-first surface.
- [ ] Show exactly one primary next action.
- [ ] Show "AI 教练正在看：目标、项目、提交记录、检查结果" in human language.
- [ ] Keep secondary links small: project, small lesson, hiring report.
- [ ] Add Playwright checks for the coach-first homepage and no banned backend terms.

### Task 2: Rebuild `/intake` As Planning Agent Conversation

**Files:**
- Modify: `apps/web/app/intake/page.tsx`
- Modify: `apps/api/app/services.py`
- Test: `apps/api/tests/test_agent_kernel.py`
- Test: `apps/web/tests/vertical-slice.spec.ts`

**Interfaces:**
- Consumes: `POST /api/planning/sessions`, `POST /api/planning/sessions/{id}/messages`
- Produces: one clarified goal, weekly time, background, target project domain, plan preview.

- [ ] Remove the questionnaire layout.
- [ ] Use one question per step.
- [ ] Display what the AI has already understood as short memory chips.
- [ ] Add "修改目标 / 修改时间 / 修改项目方向" actions.
- [ ] Test that each planning message creates a `LearningPlannerAgent` run.

### Task 3: Make Course Content Worth Paying For

**Files:**
- Modify: `apps/api/app/seed.py`
- Modify: `apps/api/app/services.py`
- Modify: `apps/web/app/learn/[id]/page.tsx`
- Modify: `apps/web/app/courses/page.tsx`
- Test: `apps/api/tests/test_vertical_slice.py`
- Test: `apps/web/tests/vertical-slice.spec.ts`

**Interfaces:**
- Consumes: `course_modules`, `course_lessons`, `course_exercises`
- Produces: task-bound lessons, micro exercise, expected evidence.

- [ ] Upgrade each core course to include: concept, example, common mistake, mini task, project application.
- [ ] Add evidence language: "学完后写进 README / evaluation report 的内容".
- [ ] Keep course pages short. No video-platform layout.
- [ ] Test course detail returns lessons and an exercise for every recommended course.

### Task 4: Turn Project Lab Into Builder Workspace

**Files:**
- Modify: `apps/web/app/lab/[id]/page.tsx`
- Modify: `apps/api/app/services.py`
- Test: `apps/web/tests/vertical-slice.spec.ts`

**Interfaces:**
- Consumes: `GET /api/projects/{learner_project_id}`
- Produces: task steps, required deliverables, tutor panel, submit action, latest review action.

- [ ] Show one active task at a time.
- [ ] Put the AI project coach in a right-side sticky panel.
- [ ] Put required deliverables next to the submit form, not buried below.
- [ ] Show latest review fixes above new work if they exist.
- [ ] Test that project page has course, tutor, submit, and review entry points.

### Task 5: Make Tutor Read The Learner Context

**Files:**
- Modify: `apps/api/app/services.py`
- Modify: `apps/api/app/tutor_agent.py`
- Test: `apps/api/tests/test_agent_kernel.py`

**Interfaces:**
- Consumes: project task, latest submission, latest review, open coach tasks, course progress.
- Produces: tutor answer, risk warning, next checkpoint, AI dependency score.

- [ ] Include latest review risks and open coach tasks in tutor context.
- [ ] Tutor must answer with: next step, why, what to submit, one risk.
- [ ] Tutor must not provide full copy-paste solution.
- [ ] Test direct-answer request raises AI dependency score.
- [ ] Test latest review risk appears in tutor context output.

### Task 6: Make Review Report Recruiter-Grade

**Files:**
- Modify: `apps/api/app/review_schema.py`
- Modify: `apps/api/app/mock_review.py`
- Modify: `apps/api/app/services.py`
- Modify: `apps/web/app/report/[id]/page.tsx`
- Modify: `apps/web/app/gate/[id]/page.tsx`
- Test: `apps/api/tests/test_vertical_slice.py`
- Test: `apps/web/tests/vertical-slice.spec.ts`

**Interfaces:**
- Consumes: sandbox run, submission links, review result.
- Produces: hiring summary, strengths, risks, required fixes, evidence items.

- [ ] Rename UI language to "项目检查报告".
- [ ] Add recruiter questions: can it run, can I inspect code, what did the learner prove, what is weak.
- [ ] Show concrete evidence source for each claim.
- [ ] Generate next repair task from the weakest evidence.
- [ ] Test review creates evidence and open coach task.

### Task 7: Make Hiring Report Credible

**Files:**
- Modify: `apps/web/app/passport/page.tsx`
- Modify: `apps/web/app/passport/[slug]/page.tsx`
- Modify: `apps/api/app/services.py`
- Test: `apps/web/tests/vertical-slice.spec.ts`

**Interfaces:**
- Consumes: projects, evidence, reviews, tutor AI dependency summary.
- Produces: public hiring report.

- [ ] Rename visible product language to "求职能力报告".
- [ ] Put projects first, not score charts first.
- [ ] For each project show GitHub, Demo, check result, what skill it proves.
- [ ] Add "可信度限制": what is verified, what is self-reported.
- [ ] Test public report has project, evidence, and AI dependency risk language.

### Task 8: Clean The Design System

**Files:**
- Modify: `apps/web/app/globals.css`
- Modify: `apps/web/app/layout.tsx`
- Test: `apps/web/tests/vertical-slice.spec.ts`

**Interfaces:**
- Produces: consistent SaaS visual language.

- [ ] Reduce visual noise and repeated cards.
- [ ] Use a workbench layout: left navigation, center work area, right coach panel where useful.
- [ ] Keep typography smaller and denser for app pages.
- [ ] Remove remaining mojibake from visible UI.
- [ ] Test the full vertical slice has no banned backend terms.

### Task 9: Verification

**Files:**
- No production files.

- [ ] Run `npm run test:api`.
- [ ] Run `npm --workspace apps/web run typecheck`.
- [ ] Run `npm --workspace apps/web run build`.
- [ ] Run `npm --workspace apps/web run test:e2e -- tests/vertical-slice.spec.ts`.

---

## Deliberate Skips

- No new database provider work. SQLite/Postgres compatibility is enough for now.
- No background worker rewrite. Synchronous review is enough for demo and early users.
- No new UI library. Existing CSS is enough if cleaned.
- No custom Claude tool runtime expansion until the rule/mock path proves the product flow.

