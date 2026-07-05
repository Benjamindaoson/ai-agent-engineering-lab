# TIAI AgentLab

TIAI AgentLab 是一个可本地运行的 AI Agent Builder 训练营系统。第一版目标不是做大平台，而是跑通训练营核心闭环：

```text
规划 Agent 意图识别
-> 澄清追问
-> 个性化学习路线确认
-> 自适应课程推荐
-> 3 个项目实战
-> Sandbox 运行
-> Claude / Mock Agent Review
-> 能力证据
-> 能力知识图谱
-> Skill Passport
```

## 本地启动顺序

安装依赖：

```powershell
npm install
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r apps/api/requirements.txt
```

初始化本地 SQLite 数据：

```powershell
npm run seed
```

启动后端：

```powershell
npm run dev:api
```

另开终端启动前端：

```powershell
npm run dev:web -- --hostname 127.0.0.1 --port 3000
```

打开：

```text
http://127.0.0.1:3000
```

## 验证命令

每次交付前按顺序执行：

```powershell
npm run seed
npm run test:api
npm run smoke
npm run typecheck:web
npm run build:web
npm run test:e2e
npm audit --audit-level=high
```

## 当前运行模式

本地开发默认使用：

```env
AUTH_MODE=dev
NEXT_PUBLIC_AUTH_MODE=dev
NEXT_PUBLIC_AGENT_REVIEW_MODE=mock
AGENT_MODE=mock
```

生产或多人训练营可以切换到：

```env
AUTH_MODE=supabase
DATABASE_URL=postgresql://...
NEXT_PUBLIC_AUTH_MODE=supabase
NEXT_PUBLIC_AGENT_REVIEW_MODE=claude
AGENT_MODE=claude
ANTHROPIC_API_KEY=...
```

Supabase 建库、Auth 和 Postgres 说明见 `infra/supabase/README.md`。

## Agentic 学习规划

入营不再只是表单测评。当前实现包含一个可审计的 Planning Agent 流程：

```text
用户自由输入目标
-> Intent Agent 识别核心目标
-> Clarification Agent 追问缺失信息
-> Learning Planner Agent 生成路线预览
-> 用户确认
-> 写入正式 learning_plans
```

相关数据表：

```text
planning_sessions     规划会话状态、识别意图、上下文、路线预览
planning_messages     用户和 Agent 的对话记录
planning_agent_runs   Agent 每次判断的输入和输出
```

## 技术结构

```text
Next.js Web
FastAPI API / Review Service
Supabase Auth 兼容用户上下文
SQLite / Postgres 数据层
Intent / Clarification / Learning Planner Agent
个性化学习路线引擎
自适应课程推荐
Project Lab
本地 Sandbox Runner
Claude Agent SDK Review Runner
Evidence Store
Skill Score Engine
Skill Passport Snapshot
```

## 课程存储

课程不是省略项，当前以数据库形式保存：

```text
course_modules       课程模块
course_lessons       课程讲义 / 内容引用
task_course_modules  项目任务与课程绑定
course_progress      学员课程进度
```

后续可以把 `course_lessons.content_ref` 从 `db://...` 替换为视频、文档、代码仓库或外部 LMS 链接。
