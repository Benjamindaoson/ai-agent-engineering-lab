# Agent-Native Training System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将当前 TIAI 从页面式训练营网站重构成 Agent-native 的 AI Agent Builder 训练、评审、证据生成系统。

**Architecture:** 保留现有 Next.js + FastAPI + Supabase/Postgres 方向，先重构黄金路径：Planning Agent -> AI Coach -> Project Lab -> Tutor -> Review Gate -> Evidence -> Skill Passport。每一阶段都必须保持可运行，并通过前端 typecheck、生产构建、E2E 和 API smoke。

**Tech Stack:** Next.js App Router, React Server Components, Server Actions, FastAPI, Postgres/Supabase schema, Claude Agent SDK compatible agent runtime, Playwright, Python smoke tests.

---

## File Map

- Modify: `apps/web/app/intake/page.tsx`
  - 保持单问题推进式 Planning Agent，不回退成问卷。
- Modify: `apps/web/app/coach/page.tsx`
  - 重构为 Today / Next Best Action 指挥中心。
- Modify: `apps/web/app/lab/[id]/page.tsx`
  - 重构为项目核心工作台，课程、任务、Tutor、提交、质量门在同屏协作。
- Modify: `apps/web/app/learn/[id]/page.tsx`
  - 课程从静态内容页变成任务上下文里的互动微练习。
- Modify: `apps/web/app/report/[id]/page.tsx`
  - Review 报告从结果展示变成下一轮任务生成器。
- Modify: `apps/web/app/passport/[slug]/page.tsx`
  - Skill Passport 改成招聘方能力报告。
- Modify: `apps/web/app/globals.css`
  - 建立统一 Agent 工作台视觉语言。
- Modify: `apps/web/lib/api.ts`
  - 扩展前端类型，统一 Agent decision / evidence / task contract。
- Modify: `apps/web/tests/vertical-slice.spec.ts`
  - 黄金路径测试改成 Agent-native 行为断言。
- Modify: `apps/api/app/api_schemas.py`
  - 增加 Agent decision、coach task、evidence item、micro exercise 的响应结构。
- Modify: `apps/api/app/services.py`
  - 核心业务编排：next best action、课程嵌入任务、Review 后生成任务、Evidence 更新。
- Modify: `apps/api/app/planning_agent.py`
  - 保持意图澄清和路线生成，但输出可解释的 missing slot / trace。
- Modify: `apps/api/app/tutor_agent.py`
  - Tutor 读取提交物、Review、Coach tasks，主动指出风险。
- Modify: `apps/api/app/schema.sql`
  - 补齐 evidence、agent memory、micro exercise、coach task 的字段。
- Modify: `apps/api/app/seed.py`
  - 增加可演示的课程、任务、提交物、评审、证据数据。
- Modify: `apps/api/app/smoke.py`
  - 验证 API 黄金路径。

---

## Phase 1: Define Agent-Native Contracts

**Objective:** 先统一“后端怎么告诉前端下一步做什么”。没有这个，前端会继续退化成静态页面。

- [ ] Step 1: 在 `apps/api/app/api_schemas.py` 增加统一结构。

Required response concepts:

```python
class AgentDecision(BaseModel):
    agent_name: str
    status: str
    primary_action: dict[str, Any]
    reasoning: list[dict[str, str]]
    missing_inputs: list[str] = []
    evidence_outcome: str | None = None

class WorkspaceState(BaseModel):
    learner_stage: str
    next_best_action: dict[str, Any]
    active_project: dict[str, Any] | None
    recommended_course: dict[str, Any] | None
    open_coach_tasks: list[dict[str, Any]]
    latest_evidence: list[dict[str, Any]]
    agent_decision: AgentDecision
```

- [ ] Step 2: 在 `apps/web/lib/api.ts` 增加对应 TypeScript 类型。

Required frontend concepts:

```ts
export type AgentDecision = {
  agent_name: string;
  status: string;
  primary_action: {
    label: string;
    href: string;
    type: string;
  };
  reasoning: Array<{
    title: string;
    detail: string;
  }>;
  missing_inputs: string[];
  evidence_outcome: string | null;
};
```

- [ ] Step 3: 修改 `apps/api/app/services.py` 的 dashboard/coach 数据返回，确保 `/coach` 不再自己拼页面逻辑，而是消费 `WorkspaceState`。

- [ ] Step 4: 验证。

Run:

```powershell
npm run smoke
npm run typecheck:web
```

Expected:

```text
Smoke test passed.
tsc --noEmit exits 0.
```

---

## Phase 2: Rebuild `/coach` As Today Command Center

**Objective:** 用户进入系统第一屏不再是 dashboard，而是 Agent 给出的“今天唯一最重要动作”。

- [ ] Step 1: 修改 `apps/web/app/coach/page.tsx`。

Required layout:

```text
Top: AI Coach Live / 当前阶段 / 目标岗位
Center: Today Mission
Right: Agent Decision Trace
Below: Evidence Progress + Current Project + Recommended Micro Lesson
```

- [ ] Step 2: 页面必须只突出一个主 CTA。

Allowed CTA examples:

```text
继续项目任务
完成推荐微课
提交到质量门
查看 Review 后任务
生成 Skill Passport
```

- [ ] Step 3: 保留 secondary CTA，但不得超过两个。

- [ ] Step 4: 修改 `apps/web/tests/vertical-slice.spec.ts`。

Required assertions:

```ts
await expect(page.getByText("AI Coach Live")).toBeVisible();
await expect(page.getByText("Next Best Action")).toBeVisible();
await expect(page.getByText("Agent Decision")).toBeVisible();
```

- [ ] Step 5: 验证。

Run:

```powershell
npm run typecheck:web
npm run build:web
```

---

## Phase 3: Rebuild Project Lab As The Core Workspace

**Objective:** `/lab/[id]` 成为产品核心，不再像项目详情页。

- [ ] Step 1: 修改 `apps/api/app/services.py` 的 project detail 返回，确保包含：

```text
current_task
required_deliverables
recommended_micro_courses
tutor_context
latest_submission
latest_review
open_coach_tasks
quality_gate_status
```

- [ ] Step 2: 修改 `apps/web/lib/api.ts` 的 `ProjectDetail` 类型，补齐上述字段。

- [ ] Step 3: 修改 `apps/web/app/lab/[id]/page.tsx` 为三栏工作台。

Required layout:

```text
Left rail: 项目阶段 / 任务列表 / 质量门状态
Center: 当前任务 / 提交要求 / 推荐课程 / 提交表单
Right rail: 常驻 Agent Tutor / 风险提醒 / 下一步建议
```

- [ ] Step 4: Tutor 区域必须显示主动判断，不只是聊天框。

Required copy concepts:

```text
我读取了你的当前任务和最近一次提交。
当前最大风险是 ...
先完成这个最小动作 ...
```

- [ ] Step 5: E2E 必须从 `/coach` 点击进入 `/lab/[id]`，完成 Tutor 检查和 Review Gate。

Run:

```powershell
npm run test:e2e
```

---

## Phase 4: Embed Courses Into Tasks

**Objective:** 课程不再是课程库，而是项目任务的即时补给。

- [ ] Step 1: 在 `apps/api/app/services.py` 中实现 task -> course recommendation。

Rule:

```text
当前任务缺什么技能，只返回最小课程集合。
不要返回完整课程库。
```

- [ ] Step 2: 修改 `apps/web/app/learn/[id]/page.tsx`。

Required layout:

```text
为什么推荐这门课
当前项目任务
本节最小学习内容
互动微练习
提交后如何影响能力图谱
```

- [ ] Step 3: 微练习提交后必须返回：

```text
score
feedback
next_action
affected_skill
evidence_created
```

- [ ] Step 4: 修改 `apps/api/app/smoke.py`，验证课程详情和练习提交。

---

## Phase 5: Make Review Gate Generate Next Work

**Objective:** Review 不是终点，而是下一轮训练任务生成器。

- [ ] Step 1: 修改 `apps/api/app/services.py` 的 Review persistence。

Required behavior:

```text
保存 review_report
保存 rubric_scores
保存 risk_flags
创建 evidence_items
创建 coach_tasks
更新 learner_skill_scores
```

- [ ] Step 2: 修改 `apps/web/app/report/[id]/page.tsx`。

Required sections:

```text
质量门结论
招聘风险
证据增加了什么
能力图谱变化
Agent 自动生成的下一轮任务
回到 Project Lab 继续修复
```

- [ ] Step 3: E2E 必须断言 Review 后回到 Project Lab 可以看到新任务。

---

## Phase 6: Convert Skill Passport Into Hiring Report

**Objective:** Passport 不再像结业证书，而是招聘方能读的候选人能力报告。

- [ ] Step 1: 修改 `apps/api/app/services.py` 的 passport 数据生成。

Required data:

```text
target_role
hiring_readiness
completed_projects
demo_links
github_links
review_summaries
skill_graph
ai_dependency_score
evidence_items
interview_talking_points
remaining_risks
```

- [ ] Step 2: 修改 `apps/web/app/passport/[slug]/page.tsx`。

Required page framing:

```text
Candidate Readiness Report
是否建议面试
可验证项目证据
工程能力雷达
AI 依赖风险
面试官建议追问
```

- [ ] Step 3: E2E 必须从 skill map 生成 passport 并打开 report。

---

## Phase 7: Visual System Cleanup

**Objective:** 统一硅谷 SaaS / developer tool 风格，避免每页像不同产品。

- [ ] Step 1: 在 `apps/web/app/globals.css` 整理通用 Agent workspace classes。

Required reusable concepts:

```text
agent-shell
agent-stage
agent-memory
agent-trace
mission-card
workbench-grid
quality-gate-card
evidence-card
coach-panel
```

- [ ] Step 2: 删除明显重复或不再使用的旧样式。

- [ ] Step 3: 移动端验证。

Run Playwright viewport checks:

```text
1440 x 920
390 x 844
```

Expected:

```text
No overlapping text.
Primary CTA visible.
Right rail stacks below main content on mobile.
```

---

## Phase 8: Final Verification Gate

**Objective:** 每次阶段性重构后都必须证明系统能跑。

- [ ] Step 1: Kill stale local servers.

```powershell
$ports = 3000,8000
Get-NetTCPConnection -LocalPort $ports -ErrorAction SilentlyContinue |
  Where-Object { $_.State -eq 'Listen' } |
  ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
```

- [ ] Step 2: Run full verification.

```powershell
npm run typecheck:web
npm run build:web
npm run test:e2e
npm run smoke
```

- [ ] Step 3: Start local demo servers.

```powershell
Start-Process -FilePath powershell -ArgumentList '-NoProfile','-Command','cd D:\AI_Agent_Builder; npm run serve:api' -WindowStyle Hidden
Start-Process -FilePath powershell -ArgumentList '-NoProfile','-Command','cd D:\AI_Agent_Builder; npm run dev:web -- --hostname 127.0.0.1 --port 3000' -WindowStyle Hidden
```

- [ ] Step 4: Browser inspect these routes:

```text
http://127.0.0.1:3000/intake
http://127.0.0.1:3000/coach
http://127.0.0.1:3000/lab/{id}
http://127.0.0.1:3000/learn/{id}
http://127.0.0.1:3000/report/{id}
http://127.0.0.1:3000/passport/{slug}
```

Expected:

```text
The system feels like an active AI training OS.
The user always sees the next best action.
Courses are embedded in project tasks.
Review produces evidence and next work.
Passport reads like a hiring report.
```

---

## Execution Rule

Do not start Phase 2 before Phase 1 contracts are stable. Do not start visual cleanup before Project Lab and Coach are functionally Agent-native. Every phase must leave the product runnable.

Current environment note: `D:\AI_Agent_Builder` is not a Git repository, so this plan omits commit steps. Use verification commands as the integration gate.
