# Agent-Native Training Cockpit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把当前系统从“AI 教育网站”重构成“AI 教练驱动的训练舱”，让学员一进来就感觉是在被智能体带着完成真实项目，而不是浏览多个传统页面。

**Architecture:** 不新增框架，不新增依赖。复用现有 `AgentCommandCenter`、课程工作台、项目工作台、评审工作台，把前端入口统一成“教练对话 + 今日任务画布 + 右侧常驻教练”的产品形态。后端只补必要 contract 字段，不做大迁移。

**Tech Stack:** Next.js App Router, React Server Components, FastAPI, existing SQLite/Supabase-compatible data layer, existing Playwright e2e, existing API tests.

## Global Constraints

- 不再堆页面；优先把 `/coach`、`/intake`、`/lab/[id]`、`/learn/[id]`、`/gate/[id]` 做成一条 AI 训练链路。
- 页面语言必须是人类语言，不出现 `Agent Command Queue`、`Quality Gate`、`Evidence Store`、`Skill Passport`、`Sandbox`、`Trace` 等后台术语。
- 学员端必须看到智能体角色：AI 教练、项目教练、小课教练、作品检查员。
- 每一步必须有清晰产出：学习路线、当前小课、项目提交物、检查报告、求职报告。
- 不新增 UI 组件库；只改现有 CSS 和页面。
- 每个任务完成后跑最小验证：typecheck + 相关 Playwright e2e。

---

## Product Shape Decision

采用“AI 训练舱”，不是纯聊天框，也不是传统后台。

屏幕结构：

- 左侧：学习路径和当前阶段。
- 中间：今天只做的一件事，包括任务、材料、提交入口。
- 右侧：常驻 AI 教练，解释为什么、看哪里、下一步怎么做。

核心体验：

```text
AI 教练判断下一步
→ 学员进入任务画布
→ 小课只在任务需要时出现
→ 项目教练陪做
→ 作品检查员检查
→ 自动生成下一轮修改任务
→ 形成求职报告
```

## Files

- Modify: `apps/web/app/globals.css`
  - Clean source encoding.
  - Add shared cockpit layout classes.
  - Remove unused older page styles only when no current page uses them.
- Modify: `apps/web/app/layout.tsx`
  - Make navigation feel like a training operating system, not a website menu.
- Modify: `apps/web/app/coach/page.tsx`
  - Rebuild as the main AI training cockpit.
- Modify: `apps/web/app/intake/page.tsx`
  - Keep one-question-at-a-time planning, but make it feel like a live coach interview.
- Modify: `apps/web/app/lab/[id]/page.tsx`
  - Rebuild as the project execution canvas.
- Modify: `apps/web/app/learn/[id]/page.tsx`
  - Keep as task-bound micro lesson, but visually embed it into project progress.
- Modify: `apps/web/app/gate/[id]/page.tsx`
  - Rename and reshape as project check report.
- Modify: `apps/web/app/passport/page.tsx`
  - Rename product language to recruiter-facing outcome.
- Modify: `apps/web/app/passport/[slug]/page.tsx`
  - Make it read like a hiring evidence report.
- Modify: `apps/web/lib/humanize.ts`
  - Centralize all backend-term cleanup.
- Modify: `apps/web/tests/vertical-slice.spec.ts`
  - Add AI-native interaction assertions.
- Modify: `apps/api/app/services.py`
  - Only if needed: add small fields to `AgentCommandCenter` for the cockpit copy.
- Modify: `apps/api/app/seed.py`
  - Clean content and add better demo text.
- Test: `apps/api/tests/test_vertical_slice.py`
- Test: `apps/web/tests/vertical-slice.spec.ts`

## Task 1: Stop the Encoding Bleed

**Files:**
- Modify: `apps/web/app/coach/page.tsx`
- Modify: `apps/web/app/lab/[id]/page.tsx`
- Modify: `apps/web/app/gate/[id]/page.tsx`
- Modify: `apps/web/tests/vertical-slice.spec.ts`

**Interfaces:**
- Consumes: existing API types from `apps/web/lib/api.ts`
- Produces: readable UTF-8 Chinese source and tests

- [ ] Replace mojibake source text with clean Chinese in the four files.
- [ ] Keep route names and data fetching unchanged.
- [ ] Run: `npm --workspace apps/web run typecheck`
- [ ] Run: `npm --workspace apps/web run test:e2e -- tests/vertical-slice.spec.ts`
- [ ] Expected: both pass.

## Task 2: Make `/coach` the AI Training Cockpit

**Files:**
- Modify: `apps/web/app/coach/page.tsx`
- Modify: `apps/web/app/globals.css`
- Modify: `apps/web/tests/vertical-slice.spec.ts`

**Interfaces:**
- Consumes: `AgentCommandCenter`
- Produces: a single first screen with coach, mission, task, project, course, and evidence handoffs

- [ ] Replace hero/dashboard layout with three zones:
  - `左侧：训练路径`
  - `中间：今天只做这一件事`
  - `右侧：AI 教练正在看什么`
- [ ] Keep only three primary actions:
  - `开始今天的任务`
  - `打开项目`
  - `查看学习路线`
- [ ] Remove secondary dashboard-like metric clutter from the first viewport.
- [ ] Add e2e assertions for:
  - “今天只做这一件事”
  - “AI 教练正在看”
  - no backend terms.
- [ ] Run: `npm --workspace apps/web run test:e2e -- tests/vertical-slice.spec.ts`

## Task 3: Make `/intake` Feel Like a Planning Agent

**Files:**
- Modify: `apps/web/app/intake/page.tsx`
- Modify: `apps/web/app/globals.css`
- Modify: `apps/web/tests/vertical-slice.spec.ts`

**Interfaces:**
- Consumes: `/api/planning/sessions/current`, `/api/planning/sessions`
- Produces: one-question live planning flow

- [ ] First screen should ask one open question: “你想通过 AI 能力换来什么结果？”
- [ ] Show memory cards only as a side summary, not the main interaction.
- [ ] Hide route preview until enough context exists.
- [ ] Confirmation should route to `/learning-plan`, not repeat the same assistant message.
- [ ] Run: `npm --workspace apps/web run test:e2e -- tests/vertical-slice.spec.ts`

## Task 4: Rebuild `/lab/[id]` as the Project Canvas

**Files:**
- Modify: `apps/web/app/lab/[id]/page.tsx`
- Modify: `apps/web/app/globals.css`
- Modify: `apps/web/tests/vertical-slice.spec.ts`

**Interfaces:**
- Consumes: `AgentCommandCenter`, `TutorState`
- Produces: a project execution workspace

- [ ] Left rail: current project steps.
- [ ] Center canvas:
  - current task
  - required outputs
  - linked micro lesson
  - submit work form
- [ ] Right rail: persistent AI project coach.
- [ ] Remove generic panel stacking where it makes the page feel like a website.
- [ ] Add e2e assertions for:
  - “项目画布”
  - “AI 项目教练”
  - “提交作品”
- [ ] Run: `npm --workspace apps/web run test:e2e -- tests/vertical-slice.spec.ts`

## Task 5: Make Courses Feel Adaptive, Not Like a Library

**Files:**
- Modify: `apps/web/app/courses/page.tsx`
- Modify: `apps/web/app/learn/[id]/page.tsx`
- Modify: `apps/api/app/seed.py`
- Modify: `apps/web/tests/vertical-slice.spec.ts`

**Interfaces:**
- Consumes: `CourseWorkbench`, `AgentCommandCenter.course_queue`
- Produces: task-bound micro lessons

- [ ] Course list copy must answer:
  - why this now
  - which task it unlocks
  - what evidence it creates
- [ ] Micro lesson page must have:
  - short explanation
  - one small exercise
  - immediate return to project
- [ ] Seed at least 6 credible micro lessons with clean Chinese text.
- [ ] Run: `npm run test:api`
- [ ] Run: `npm --workspace apps/web run test:e2e -- tests/vertical-slice.spec.ts`

## Task 6: Rename Review Into a Human Project Check

**Files:**
- Modify: `apps/web/app/gate/[id]/page.tsx`
- Modify: `apps/web/app/report/[id]/page.tsx`
- Modify: `apps/web/lib/humanize.ts`
- Modify: `apps/web/tests/vertical-slice.spec.ts`

**Interfaces:**
- Consumes: `ReviewGateWorkbench`
- Produces: project check report and repair tasks

- [ ] Rename UI to:
  - “项目检查报告”
  - “能不能运行”
  - “哪里做得好”
  - “下一轮只改这几件事”
- [ ] Keep technical detail visible, but under human labels.
- [ ] Show generated next tasks as the main outcome.
- [ ] Run: `npm --workspace apps/web run test:e2e -- tests/vertical-slice.spec.ts`

## Task 7: Make Passport a Recruiter Report

**Files:**
- Modify: `apps/web/app/passport/page.tsx`
- Modify: `apps/web/app/passport/[slug]/page.tsx`
- Modify: `apps/web/app/skill-map/page.tsx`
- Modify: `apps/web/tests/vertical-slice.spec.ts`

**Interfaces:**
- Consumes: existing passport/evidence APIs
- Produces: recruiter-facing proof page

- [ ] Replace certificate language with:
  - “求职能力报告”
  - “项目证据”
  - “代码和演示”
  - “AI 代做风险”
  - “面试可追问点”
- [ ] Skill map should read as “能力画像”, not analytics dashboard.
- [ ] Run: `npm --workspace apps/web run test:e2e -- tests/vertical-slice.spec.ts`

## Task 8: Final Visual Pass

**Files:**
- Modify: `apps/web/app/globals.css`
- Modify: route files only if layout breaks.

**Interfaces:**
- Produces: coherent AI-native visual system

- [ ] Use one visual metaphor: training cockpit.
- [ ] Remove page sections that look like marketing cards.
- [ ] Keep cards only for task units, coach messages, reports.
- [ ] Verify mobile layout has no horizontal overflow.
- [ ] Run: `npm --workspace apps/web run test:e2e -- tests/vertical-slice.spec.ts`
- [ ] Run: `npm --workspace apps/web run build`

## Task 9: Ship Check

**Files:**
- No source edits unless a check fails.

- [ ] Run: `npm run test:api`
- [ ] Run: `npm --workspace apps/web run typecheck`
- [ ] Run: `npm --workspace apps/web run build`
- [ ] Run: `npm --workspace apps/web run test:e2e -- tests/vertical-slice.spec.ts`
- [ ] Start local services:
  - `npm run dev:api`
  - `npm run dev:web -- --hostname 127.0.0.1 --port 3000`
- [ ] Check:
  - `http://127.0.0.1:8000/health`
  - `http://127.0.0.1:3000/coach`

## Self-Review

**Spec coverage:** This plan addresses the user's concern that the product feels like a traditional website by changing the interaction model, visible AI roles, information architecture, copy, and first-viewport experience.

**Placeholder scan:** No task depends on “later” work. Each task has exact files and verification commands.

**Type consistency:** All frontend tasks consume existing `AgentCommandCenter`, `CourseWorkbench`, `TutorState`, and `ReviewGateWorkbench` contracts already defined in `apps/web/lib/api.ts`.
