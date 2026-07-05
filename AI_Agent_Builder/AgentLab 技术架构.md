下面是我建议的 **AgentLab by TIAI 技术架构**。

# AgentLab 技术架构

## 1. 架构目标

AgentLab 的技术架构不是普通课程平台架构，而是围绕这条就业训练闭环设计：

```text
目标岗位
→ 能力诊断
→ 项目训练
→ 项目提交
→ 自动工程检查
→ Claude Agent SDK Review
→ Technical Defense
→ Evidence Store
→ Skill Graph
→ Hiring Passport
→ Portfolio Export
```

核心目标：

> **验证学员是否真的具备 AI Agent 工程岗位的可交付能力。**

---

## 2. 总体架构

```text
Next.js Web App
        ↓
FastAPI Business API
        ↓
Supabase Auth / Postgres / Storage / pgvector
        ↓
Redis Queue
        ↓
Worker Service
        ↓
Agent Runner Service
        ↓
Claude Agent SDK
        ↓
Sandbox Workspace
        ↓
Review Engine
        ↓
Evidence Store
        ↓
Skill Graph
        ↓
Hiring Passport / Portfolio Export
```

关键原则：

```text
Next.js 负责产品体验
FastAPI 负责业务规则
Claude Agent SDK 只在 Agent Runner 中运行
代码执行必须进入 Sandbox
所有能力判断必须进入 Evidence Store
Hiring Passport 只读取已验证证据
```

---

## 3. 技术栈

### 前端

```text
Next.js
React
Tailwind CSS
shadcn/ui
TanStack Query
Zustand
```

负责：

```text
学员 Dashboard
目标岗位选择
能力诊断
项目任务页面
Submission Center
Review Report
Technical Defense 页面
Skill Graph
Hiring Passport
Portfolio Export
导师后台
```

---

### 后端

```text
FastAPI
Pydantic
SQLModel / SQLAlchemy
Alembic
pytest
```

负责：

```text
用户权限
岗位能力图谱
项目任务状态
提交物管理
Review Job 派发
Evidence 写入
Skill Score 更新
Hiring Passport 生成
导师评审
```

核心规则：

```text
凡是影响能力分数、Review、Passport 的写操作，都必须经过 FastAPI。
```

---

### 数据底座

```text
Supabase Postgres
Supabase Auth
Supabase Storage
Supabase pgvector
```

用途：

```text
用户身份
项目数据
提交物
评审结果
Evidence
能力图谱
Hiring Passport Snapshot
课程 / Rubric / JD 向量检索
```

---

### Agent Runtime

```text
Claude API
Claude Agent SDK
Agent Runtime Adapter
```

分工：

```text
Claude API：
能力诊断、训练路径生成、AI Tutor、Portfolio 文案、Mock Interview

Claude Agent SDK：
Repo Review、Code Review、RAG Review、Workflow Review、Debug Review、Hiring-Grade Review
```

不能把 Claude Agent SDK 直接放在 FastAPI 主进程里跑，必须放在独立 Agent Runner。

---

## 4. 核心服务

### 4.1 Web App

页面模块：

```text
目标岗位选择
能力诊断
项目任务系统
AI Tutor
提交中心
评审报告
技术答辩
能力图谱
Hiring Passport
作品集导出
```

---

### 4.2 Business API

FastAPI 提供领域 API：

```text
/api/auth
/api/jobs
/api/diagnostics
/api/skill-map
/api/projects
/api/submissions
/api/reviews
/api/defense
/api/evidence
/api/passports
/api/portfolio
/api/admin
```

---

### 4.3 Worker Service

处理异步任务：

```text
review_job
repo_clone_job
sandbox_check_job
evidence_generation_job
skill_score_update_job
passport_snapshot_job
portfolio_export_job
mock_interview_job
```

---

### 4.4 Agent Runner Service

专门运行 Claude Agent SDK。

职责：

```text
创建隔离 workspace
拉取 GitHub Repo / 解压提交物
加载 Rubric
配置 Agent 权限
启动 Claude Agent SDK
记录 tool calls
输出结构化 Review JSON
返回给 FastAPI
```

Agent Runner 不直接改能力分数，只输出评审结果。

---

## 5. Sandbox 设计

只要运行学员代码，就必须进入 Sandbox。

```text
Docker Sandbox
限制 CPU
限制内存
限制运行时间
限制网络
不注入生产密钥
只挂载当前提交物目录
任务结束后销毁
保存 stdout / stderr / logs
```

后续可升级：

```text
E2B
Modal
gVisor
Firecracker
```

---

## 6. Claude Agent SDK Review 流程

```text
Submission Created
→ Review Job Created
→ Worker Pulls Job
→ Agent Runner Creates Workspace
→ Clone Repo / Load Files
→ Run Sandbox Checks
→ Claude Agent SDK Review
→ Structured JSON Output
→ Pydantic Validation
→ Save Review
→ Generate Evidence
→ Update Skill Graph
→ Update Hiring Passport Snapshot
```

Review 输出必须结构化：

```json
{
  "overall_score": 82,
  "hiring_readiness": "portfolio_ready_with_revision",
  "rubric_scores": [],
  "skill_updates": [],
  "risk_flags": [],
  "evidence_items": [],
  "interview_questions": [],
  "next_actions": []
}
```

---

## 7. 三层评测系统

### 第一层：自动工程检查

```text
项目能否安装
项目能否启动
测试是否通过
Demo 是否可访问
环境变量是否清楚
README 是否完整
部署说明是否有效
```

### 第二层：Claude Agent SDK Review

```text
代码结构
Prompt 稳定性
RAG 质量
Tool Calling 安全性
Workflow 可控性
错误处理
日志 / Trace
部署质量
面试风险
是否适合放进简历
```

### 第三层：Technical Defense

```text
项目讲解
架构追问
代码追问
现场 Debug
Tradeoff 复盘
导师评分
```

这三层共同决定 Hiring Passport 的可信度。

---

## 8. 数据模型

核心表：

```text
users
user_profiles
target_jobs
job_skill_maps
skill_nodes

diagnostics
diagnostic_results

project_templates
projects
tasks
learner_projects
learner_tasks

submissions
submission_files
submission_links
submission_versions

review_jobs
reviews
review_scores
review_comments
review_risk_flags

agent_runs
agent_tool_calls
agent_artifacts

sandbox_runs
sandbox_logs

technical_defenses
defense_questions
defense_scores

evidence_items
skill_score_history
learner_skill_scores

hiring_passports
passport_snapshots
passport_items

portfolio_exports
mock_interviews
```

最重要的是：

```text
reviews
evidence_items
learner_skill_scores
technical_defenses
passport_snapshots
```

---

## 9. Evidence Store

每次评审都生成 Evidence Item。

字段：

```text
learner_id
project_id
task_id
submission_id
review_id
skill_node_id
source_type
source_url
score
confidence
evidence_text
risk_flags
reviewer_type
is_verified
is_passport_eligible
created_at
```

原则：

```text
Evidence 只能追加，不能覆盖。
```

这样才能解释能力分数为什么变化。

---

## 10. Hiring Passport 生成

Hiring Passport 不是实时查询页面，而是版本化快照。

生成流程：

```text
聚合项目
聚合 Review
聚合 Evidence
聚合 Skill Scores
聚合 Technical Defense
生成 Snapshot
发布公共页面
```

内容包括：

```text
目标岗位
岗位匹配度
能力雷达图
项目 Demo
GitHub Repo
工程评测结果
AI Review 摘要
技术答辩记录
Evidence Links
面试风险提示
推荐补强项
```

---

## 11. 权限与安全

角色：

```text
learner
mentor
admin
external_reviewer
enterprise_viewer
```

安全规则：

```text
前端不暴露 LLM Key
Supabase service role key 只在后端
Agent Runner 不持有生产 DB 写权限
Sandbox 不注入生产密钥
所有 tool calls 记录日志
高风险 Review 进入人工复核
Passport 默认由学员控制公开权限
```

---

## 12. Observability

```text
Sentry：前后端和 Worker 错误
PostHog：用户行为和转化
Langfuse / LangSmith：Agent Run、Prompt、Token、成本、延迟
```

需要追踪：

```text
项目完成率
Review 通过率
答辩通过率
Passport 查看次数
Mock Interview 分数
学员获得面试次数
```

---

## 13. 部署架构

```text
Next.js        → Vercel
FastAPI        → Railway / Render / Fly.io
Worker         → Railway / Render / Fly.io
Agent Runner   → 独立容器服务
Redis          → Upstash / Railway Redis
Database       → Supabase
Storage        → Supabase Storage
Sandbox        → Docker Host / E2B / Modal
```

环境：

```text
development
staging
production
```

---

## 14. MVP 技术范围

第一版必须做：

```text
目标岗位选择
岗位能力图谱
3 个项目任务
提交中心
自动工程检查
Claude Agent SDK Review
Technical Defense 记录
Evidence Store
Skill Graph
Hiring Passport
Portfolio Export
Mock Interview
```

第一版不做：

```text
完整企业端
投递管理
简历版本管理
复杂岗位匹配
大型社区
通用 Agent 平台
```

---

## 最终技术定义

> **AgentLab 的技术架构是一个围绕 Claude Agent SDK 的 AI Agent 工程能力评测系统。**

它的核心不是课程播放，而是：

```text
项目提交
→ 工程检查
→ Agent Review
→ 技术答辩
→ Evidence
→ Skill Graph
→ Hiring Passport
```

这套架构的关键资产是：

```text
Job-backed Skill Map
Hiring-grade Rubric
Agent Review Logs
Evidence Store
Technical Defense Record
Hiring Passport
```

下面是更完整的 **AgentLab by TIAI 技术选型定稿版**。

核心原则：

> **第一版不是做大平台，而是做“AI Agent 工程就业训练 + 项目评测 + Hiring Passport”的闭环系统。**

所以技术选型要服务这条链：

```text
岗位目标
→ 项目训练
→ 项目提交
→ 自动工程检查
→ Claude Agent SDK Review
→ 技术答辩
→ Evidence Store
→ Skill Graph
→ Hiring Passport
```

---

# 1. 总体推荐技术栈

| 层级            | 推荐技术                                        | 作用                                    | 阶段          |
| --------------- | ----------------------------------------------- | --------------------------------------- | ------------- |
| 前端            | Next.js + React + Tailwind + shadcn/ui          | 学员端、导师端、Passport 页面           | MVP           |
| 状态 / 数据请求 | TanStack Query + Zustand                        | API 数据、局部状态                      | MVP           |
| 后端            | FastAPI + Pydantic + SQLModel / SQLAlchemy      | 核心业务 API                            | MVP           |
| 数据库          | Supabase Postgres                               | 主业务数据                              | MVP           |
| 认证            | Supabase Auth                                   | 登录、角色、权限基础                    | MVP           |
| 文件存储        | Supabase Storage                                | 提交物、图片、视频、报告                | MVP           |
| 向量检索        | Supabase pgvector                               | 课程知识、JD、Rubric、项目资料检索      | MVP           |
| 异步任务        | Redis + RQ                                      | Review、Passport、Portfolio 生成        | MVP           |
| Agent Runtime   | Claude Agent SDK                                | Repo Review、Code Review、Hiring Review | MVP 核心      |
| 普通 LLM        | Claude API                                      | Tutor、诊断、学习路径、文案生成         | MVP           |
| Embedding       | OpenAI Embeddings / Voyage / Jina，封装 Adapter | 知识库向量化                            | MVP           |
| 代码隔离        | Docker Sandbox                                  | 安装、启动、测试学生项目                | MVP / Phase 2 |
| 观测            | Sentry + PostHog + Langfuse                     | 错误、行为、Agent 调用追踪              | MVP           |
| 支付            | Stripe                                          | 训练营收费                              | MVP 可选      |
| 邮件            | Resend / Postmark                               | 通知、邀请、报告发送                    | MVP           |
| 部署            | Vercel + Railway / Render / Fly.io + Supabase   | 快速上线                                | MVP           |
| CI/CD           | GitHub Actions                                  | 测试、构建、部署                        | MVP           |

---

# 2. 前端选型

## 推荐

```text
Next.js
React
TypeScript
Tailwind CSS
shadcn/ui
TanStack Query
Zustand
React Hook Form
Zod
Recharts / Tremor
```

## 用途

```text
学员 Dashboard
目标岗位选择
能力诊断
项目任务页面
AI Tutor
提交中心
Review Report
Technical Defense
Skill Graph
Hiring Passport
Portfolio Export
导师后台
管理后台
```

## 为什么选 Next.js

Next.js 适合做：

```text
SaaS Dashboard
公开 Passport 页面
SEO 页面
登录态 Web App
服务端渲染
表单和数据提交
```

Next.js 官方支持 App Router 和服务端数据 mutation，适合做训练营系统里大量表单、提交、状态流转页面。参考：[Next.js Mutating Data](https://nextjs.org/docs/app/getting-started/mutating-data)。

## 边界

Next.js 可以处理 UI 交互，但不要直接写核心业务表。

核心原则：

```text
前端展示和交互由 Next.js 做
影响能力分数、Review、Evidence、Passport 的写操作走 FastAPI
```

---

# 3. 后端选型

## 推荐

```text
FastAPI
Python 3.11+
Pydantic
SQLModel / SQLAlchemy
Alembic
httpx
pytest
```

## 用途

```text
岗位能力图谱 API
能力诊断 API
项目任务 API
提交物 API
Review Job API
Evidence API
Skill Graph API
Hiring Passport API
导师评审 API
权限校验
```

## 为什么选 FastAPI

AgentLab 的核心 AI / Review / 数据处理都在 Python 生态更自然：

```text
Claude Agent SDK Python
代码评测
文件处理
RAG
Embedding
评审 Worker
数据分析
PDF / 文档处理
```

FastAPI 用 Pydantic 做结构化输入输出，很适合 Review JSON、Evidence Schema、Rubric Schema 这类强结构化数据。

---

# 4. 数据库 / Auth / Storage

## 推荐

```text
Supabase Postgres
Supabase Auth
Supabase Storage
Supabase pgvector
```

## 为什么选 Supabase

Supabase 每个项目都是完整 Postgres 数据库，并且提供 Auth、Storage、RLS、pgvector 等能力。参考：[Supabase Database](https://supabase.com/docs/guides/database/overview)、[Supabase Auth](https://supabase.com/docs/guides/auth)、[Supabase Storage](https://supabase.com/docs/guides/storage)。

第一版用 Supabase 可以减少大量基础设施建设。

## 核心用途

```text
Postgres：
用户、项目、任务、提交、Review、Evidence、Skill Graph、Passport

Auth：
学员、导师、管理员、外部评审人登录

Storage：
项目文件、架构图、答辩视频、报告、截图

pgvector：
岗位 JD、课程知识、项目资料、Rubric、导师反馈检索
```

Supabase pgvector 是 Postgres 的向量相似度扩展，适合存储 embedding 和做 RAG 检索。参考：[Supabase pgvector](https://supabase.com/docs/guides/database/extensions/pgvector)。

---

# 5. Agent / AI 选型

## 推荐架构

```text
Agent Runtime Adapter
├── Claude API
├── Claude Agent SDK
├── Embedding Provider
└── Future Providers
```

## Claude API 用于轻任务

```text
能力诊断
学习路径生成
AI Tutor
课程推荐
Mock Interview 问题生成
Portfolio 文案生成
Hiring Passport 摘要
```

## Claude Agent SDK 用于重任务

```text
Repo Review
Code Review
RAG Review
Tool Calling Review
Workflow Review
Debug Review
Hiring-Grade Review
Evidence Builder
```

Claude Agent SDK 官方说明它能读取文件、运行命令、搜索代码库、编辑代码，并提供 built-in tools、hooks、subagents、MCP、permissions、sessions 等能力，适合做项目级评审。参考：[Claude Agent SDK Overview](https://code.claude.com/docs/en/agent-sdk/overview)。

## 关键原则

```text
Claude API = 轻量智能生成
Claude Agent SDK = 项目级工程评审
```

不要把所有 AI 功能都交给 Agent SDK，否则成本和复杂度都会上升。

---

# 6. Agent Runner Service

Claude Agent SDK 不直接跑在 FastAPI 主服务里。

## 单独服务

```text
apps/agent-runner
```

## 职责

```text
拉取 Review Job
创建临时 Workspace
Clone GitHub Repo
解压提交物
加载 Rubric
配置 Agent 权限
启动 Claude Agent SDK
记录 tool calls
输出结构化 Review JSON
上传 Agent artifacts
返回 Review Result
```

## 原因

Agent SDK 会涉及：

```text
文件读取
命令执行
多轮 agent loop
长任务
权限控制
session
工具调用日志
```

所以必须和业务 API 隔离。

---

# 7. Sandbox 选型

## MVP 推荐

```text
Docker Sandbox
```

## 后续可选

```text
E2B
Modal
gVisor
Firecracker
```

## 用途

```text
安装依赖
运行测试
启动项目
检查 API
检查 Demo
收集 stdout / stderr
验证 Dockerfile / README
```

## 安全要求

```text
不注入生产密钥
限制网络
限制 CPU
限制内存
限制运行时间
只挂载当前提交目录
任务完成后销毁
记录完整日志
```

---

# 8. 异步任务选型

## MVP 推荐

```text
Redis + RQ
```

## 后续可升级

```text
Celery
Temporal
BullMQ
```

## 为什么 MVP 用 RQ

RQ 简单，适合第一版：

```text
Review Job
Sandbox Check
Evidence Generation
Skill Score Update
Passport Snapshot
Portfolio Export
Mock Interview Generation
```

如果后面工作流复杂、重试逻辑复杂，再升级 Temporal。

---

# 9. Review / Eval 技术选型

## 三层评测

```text
1. 自动工程检查
2. Claude Agent SDK Review
3. Technical Defense
```

## 自动工程检查

技术：

```text
Docker Sandbox
pytest / npm test
HTTP health check
Playwright 可选
GitHub API 可选
```

检查：

```text
能否安装
能否启动
测试是否通过
Demo 是否可访问
README 是否完整
环境变量是否清晰
```

## Claude Agent SDK Review

技术：

```text
Claude Agent SDK
Review Rubric JSON
Pydantic schema validation
Agent tool call logs
```

检查：

```text
代码结构
Prompt 稳定性
RAG 质量
Tool Calling 安全
Workflow 可控
错误处理
日志 / Trace
部署质量
简历可展示度
面试风险
```

## Technical Defense

技术：

```text
Next.js 答辩页面
视频上传 / 录屏
AI 问题生成
导师评分表
结构化 Rubric
```

可选视频方案：

```text
Mux
Cloudflare Stream
Supabase Storage 简单上传
```

MVP 可以先用上传视频或答辩记录表，不必一开始做实时视频会议。

---

# 10. Evidence Store 选型

## 存储

```text
Supabase Postgres
```

## 原则

Evidence 是系统核心资产，必须结构化、可追溯、只能追加。

核心表：

```text
evidence_items
evidence_sources
skill_score_history
review_scores
technical_defense_scores
```

## 每条 Evidence 记录

```text
learner_id
project_id
task_id
submission_id
review_id
skill_node_id
source_type
source_url
score
confidence
evidence_text
risk_flags
reviewer_type
is_verified
is_passport_eligible
created_at
```

---

# 11. Skill Graph 选型

## MVP 推荐

```text
Postgres 表结构
```

暂时不用 Neo4j。

## 原因

第一版能力图谱不复杂，用 Postgres 足够：

```text
skill_nodes
skill_edges
learner_skill_scores
skill_score_history
skill_evidence_map
```

后续如果要做复杂能力路径推理，再考虑图数据库。

---

# 12. Hiring Passport / Portfolio 生成

## 推荐

```text
Next.js 公共页面
FastAPI 聚合 Snapshot
Postgres 保存版本化快照
React PDF / Playwright PDF 可选
```

## 内容

```text
目标岗位
岗位匹配度
能力雷达图
项目 Demo
GitHub Repo
工程评测结果
AI Review 摘要
技术答辩记录
Evidence Links
面试风险
推荐补强项
```

## Portfolio Export

技术：

```text
Claude API 生成文案
Markdown 模板
README 模板
Resume bullets 模板
Next.js 展示页
PDF 导出可选
```

---

# 13. Observability 选型

## 推荐

```text
Sentry
PostHog
Langfuse
```

## Sentry

记录：

```text
前端异常
API 异常
Worker 异常
Agent Runner 异常
Sandbox 异常
```

## PostHog

记录：

```text
注册
完成诊断
进入项目
提交项目
查看 Review
完成答辩
生成 Passport
Passport 被查看
```

## Langfuse / LangSmith

记录：

```text
prompt version
model
input / output
token usage
latency
cost
tool calls
review quality
failure reason
```

---

# 14. 支付 / 通知 / CRM

## 支付

```text
Stripe
```

用途：

```text
训练营收费
分期付款
优惠码
发票
订阅制后续版本
```

## 邮件

```text
Resend / Postmark
```

用途：

```text
注册邮件
提交提醒
Review 完成通知
Passport 发布通知
导师邀请
```

## CRM / 运营

MVP 可先用：

```text
Airtable / Notion / HubSpot Free
```

后续再内置 cohort 管理。

---

# 15. GitHub 集成

## MVP

```text
GitHub Repo URL 提交
后端 clone public repo
private repo 先不支持或手动授权
```

## Phase 2

```text
GitHub OAuth
GitHub App
Repo 权限授权
自动读取 PR / commits
生成项目活跃度证据
```

## 用途

```text
验证提交者
读取代码
分析 commit history
检查 README
检查 tests
生成 Evidence Links
```

---

# 16. 安全选型

## 必须做

```text
Supabase JWT 校验
FastAPI RBAC
RLS 辅助保护
Service role key 只在后端
LLM key 不进前端
Sandbox 无生产密钥
Agent tool call 全记录
Prompt injection 防护
日志脱敏
```

## Agent SDK 权限

Claude Agent SDK 支持 permissions 和 allowed tools。参考：[Claude Agent SDK Permissions](https://code.claude.com/docs/en/agent-sdk/permissions)。

推荐权限 Profile：

```text
ReadOnlyReview：
Read, Glob, Grep

StaticRepoReview：
Read, Glob, Grep, limited Bash

SandboxExecutionReview：
Read, Glob, Grep, Bash in Sandbox only

PassportMode：
No tools, only verified Evidence
```

生产环境禁止：

```text
bypassPermissions
访问宿主机根目录
访问生产密钥
写生产数据库
跨学员读取目录
```

---

# 17. 部署选型

## MVP 推荐

```text
Next.js → Vercel
FastAPI → Railway / Render / Fly.io
Worker → Railway / Render / Fly.io
Agent Runner → 独立 Docker 服务
Redis → Upstash / Railway Redis
Postgres/Auth/Storage → Supabase
Sandbox → 独立 Docker Host / E2B
```

Claude Agent SDK 官方也提供 hosting 相关说明，Agent SDK 是运行在你自己的基础设施里，需要处理 runtime、session、tool、权限等部署问题。参考：[Hosting the Agent SDK](https://code.claude.com/docs/en/agent-sdk/hosting)。

## 为什么不一开始上 Kubernetes

第一版不需要。

先用 managed PaaS：

```text
上线快
运维少
成本可控
方便迭代
```

等到 Review 任务量大、Sandbox 并发高，再上：

```text
Kubernetes
ECS
Nomad
Modal
E2B
```

---

# 18. Monorepo 结构

```text
agentlab/
  apps/
    web/                 # Next.js
    api/                 # FastAPI
    worker/              # RQ Worker
    agent-runner/        # Claude Agent SDK Runner

  packages/
    shared-types/
    schemas/
    prompts/
    rubrics/
    ui/
    portfolio-templates/

  infra/
    docker/
    sandbox/
    migrations/
    deployment/

  docs/
    architecture.md
    data-model.md
    api.md
    agent-runner.md
    review-engine.md
    evidence-store.md
    hiring-passport.md
```

---

# 19. MVP 必选 vs 后置

## MVP 必选

```text
Next.js
FastAPI
Supabase Postgres/Auth/Storage
pgvector
Redis + RQ
Claude API
Claude Agent SDK
Agent Runner
基础 Docker Sandbox
Sentry
PostHog
Langfuse
```

## Phase 2

```text
GitHub App
更强 Sandbox
视频答辩
导师评分工作台
企业反馈表
Rubric Versioning
Prompt Versioning
```

## Phase 3

```text
Temporal
Kubernetes / Modal / E2B
复杂企业端
岗位 JD 自动采集 Agent
企业人才验证网络
```

---

# 20. 不建议第一版采用

```text
Neo4j
第一版能力图谱不需要图数据库。

Kubernetes
第一版运维复杂度过高。

完整 ATS / 招聘系统
会偏离训练与评测核心。

全部用 Next.js Server Actions 写业务
核心能力状态需要 FastAPI 统一管理。

全部用 Claude Agent SDK
轻量任务用 Claude API 更便宜、更可控。

LangChain / LangGraph 作为平台核心
可以作为学员项目技术内容，但平台内部 Review Runtime 优先围绕 Claude Agent SDK。
```

---

# 最终技术选型结论

AgentLab 第一版推荐技术栈：

```text
Next.js + FastAPI + Supabase + Redis/RQ
+ Claude API + Claude Agent SDK
+ Agent Runner + Docker Sandbox
+ Evidence Store + Skill Graph + Hiring Passport
```

一句话：

> **用 Next.js 做产品体验，FastAPI 做业务中枢，Supabase 做数据底座，Claude Agent SDK 做项目级工程评测，Docker Sandbox 做运行隔离，Evidence Store 和 Hiring Passport 做招聘信号输出。**

整个产品的内核不是 Claude Agent SDK。

**AgentLab 的真正内核是：**

> **基于真实岗位的项目能力验证闭环。**

展开就是：

```text
岗位要求
→ 能力图谱
→ 项目任务
→ 提交物
→ 工程评测
→ 技术答辩
→ 能力证据
→ Hiring Passport
```

如果再压缩成一句：

> **用真实项目证明一个人是否具备 AI Agent 工程岗位的可交付能力。**

Claude Agent SDK 是这个闭环里的 **评测引擎**，很重要，但不是最终内核。

更完整地看，AgentLab 有 4 个核心系统：

```text
1. 岗位能力标准系统
定义企业到底需要什么能力。

2. 项目训练系统
让学员通过真实项目训练能力。

3. 能力评测与答辩系统
判断项目是否真实、可运行、可解释、可交付。

4. 证据与招聘信号系统
把能力证据变成 Hiring Passport。
```

所以真正的产品内核是：

```text
Job-Backed Skill Map
+ Hiring-Grade Projects
+ Review / Defense
+ Evidence Store
+ Hiring Passport
```

其中最关键的是 **Evidence Store**。

因为没有 Evidence，能力图谱只是图表，Passport 只是证书，Review 只是评价。

最终判断：

> **AgentLab 的底层内核是 Evidence-driven Proof-of-Work Credential System。**

中文说法：

> **以能力证据为核心的 AI Agent 工程工作证明系统。**