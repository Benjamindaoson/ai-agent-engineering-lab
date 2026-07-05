下面是 **TIAI 第一版完整产品方案定稿版**。

**1. 产品定位**

**TIAI v1 是 AI Agent Builder 训练营系统。**

它不是普通课程平台，也不是完整 SaaS 大平台，而是一个能招生、能交付、能评审、能沉淀能力证据、能生成 Skill Passport 的训练营闭环系统。

更高层定位：

> **TIAI 是 AI Agent Builder 的 Proof-of-Work Credential Network。**

也就是说，别人卖课，TIAI 生产可信能力证据。

**2. 核心用户**

```text
学员：想从 AI 使用者成长为 AI Agent Builder
导师：负责人工复核、答辩、能力校准
管理员：管理课程、项目、Rubric、证书
企业：查看 Skill Passport，提供反馈和合作机会
```

第一版重点服务学员和导师，企业端先做轻量反馈，不做复杂招聘平台。

**3. 核心闭环**

```text
入营测评
→ 个性化学习规划
→ 自适应课程推荐
→ 2–3 个项目实战
→ 任务提交
→ Agent Review
→ 人工抽查
→ Evidence 沉淀
→ Skill Graph 更新
→ Project Certificate / Skill Passport
→ 企业反馈
```

核心逻辑：

```text
规划决定学什么
课程支持做项目
项目产生提交物
评审产生能力证据
证据更新能力图谱
能力图谱生成 Skill Passport
```

**4. 产品承诺**

对学员：

> 不是教你使用 AI，而是训练你完成真实 AI Agent 项目。

对企业：

> 不是看证书，而是看项目、代码、Demo、评审和能力证据。

对市场：

> TIAI 证明谁真的具备 AI Agent Builder 基础能力。

**5. 第一版核心模块**

```text
1. 入营测评
2. 个性化学习规划
3. 自适应课程推荐
4. Project Lab
5. Agent Tutor
6. Submission Center
7. Review Engine
8. Evidence Store
9. Skill Graph
10. Project Certificate
11. Skill Passport
12. 轻量企业反馈
```

**6. 能力标准**

第一版能力图谱固定为：

```text
大模型调用与选型
Prompt Engineering
Structured Output
RAG
Vector Search
Tool Use
Function Calling
Workflow Design
Agent Architecture
Evaluation / Trace
Debug
Deployment
Documentation
Project Delivery
```

这些能力同时用于课程推荐、项目任务、Rubric、Review、Evidence 和 Skill Passport。

**7. 项目实战设计**

第一期设计 3 个递进项目。

```text
项目 1：Prompt + Workflow Agent
目标：构建一个能输出结构化结果的业务助手
训练：Prompt、结构化输出、基础 Workflow、Basic Evaluation
```

```text
项目 2：RAG Knowledge Agent
目标：构建一个企业知识库问答 Agent
训练：RAG、Embedding、Vector DB、Retrieval、引用来源、RAG Evaluation
```

```text
项目 3：Tool Use / Business Automation Agent
目标：构建一个可以调用工具完成业务流程的 Agent
训练：Function Calling、Tool Use、Agent Loop、Human-in-the-loop、Deployment
```

项目 2 是展示核心，项目 3 是区分普通学员和真正 Builder 的关键。

**8. 任务与提交**

每个项目拆成多个任务。每个任务包含：

```text
任务目标
所需课程
提交要求
评分 Rubric
Agent Tutor
Agent Review
人工抽查规则
修改建议
通过标准
```

提交物包括：

```text
Prompt
代码
GitHub Repo
Demo URL
Agent 架构图
README
Evaluation 报告
项目复盘
答辩记录
```

**9. Review Engine**

评审分两层：

```text
Agent Review：自动检查 Prompt、代码、文档、架构、RAG、Tool Use、Evaluation
人工 Review：抽查关键任务、答辩、AI 代做风险、最终 Passport 可信度
```

Review 输出必须结构化：

```text
overall_score
rubric_scores
skill_updates
evidence_items
risk_flags
next_action
confidence
```

自然语言评语可以展示给学员，但系统判断必须依赖结构化数据。

**10. Evidence Store**

Evidence Store 是系统核心资产。

每次提交和评审都会产生 Evidence Item：

```text
学员是谁
完成哪个项目 / 任务
提交了什么作品
对应哪些能力节点
评分是多少
评审依据是什么
可信度是多少
是否人工复核
是否进入 Skill Passport
```

Evidence 只能追加，不能覆盖。这样能力成长可追溯。

**11. Skill Graph**

Skill Graph 分两层：

```text
系统能力图谱：定义 AI Agent Builder 需要哪些能力
个人能力图谱：记录学员在每个能力节点上的表现
```

能力分数来源：

```text
入营测评
课程测验
项目提交
Agent Review
人工 Review
答辩表现
修改记录
企业反馈
```

**12. Skill Passport**

Skill Passport 不是结业证书，而是能力证据档案。

内容包括：

```text
学员信息
目标角色
完成项目
Demo 链接
GitHub Repo
能力图谱
Review 摘要
Evidence 摘要
架构图
Evaluation 报告
答辩记录
导师评价
AI Dependency Risk
证书状态
版本号
```

证书分两层：

```text
Project Certificate：完成单个项目获得
AI Agent Builder Skill Passport：完成全部项目并通过评审获得
```

**13. 技术架构**

围绕 Claude Agent SDK 的最终方案：

```text
Next.js Web App
↓
FastAPI Business API
↓
Supabase Postgres / Auth / Storage / pgvector
↓
Worker Queue
↓
Agent Runner Service
↓
Claude Agent SDK + Claude API
↓
Sandbox / Tool Policy / Trace Logs
↓
Review Engine
↓
Evidence Store
↓
Skill Graph
↓
Skill Passport
```

Claude API 负责轻量智能能力：

```text
入营测评
学习计划
课程推荐
Tutor
Passport 文案
```

Claude Agent SDK 负责项目级能力验证：

```text
Repo Review
Code Review
Project Review
Debug Coach
Evidence Builder
```

**14. 安全原则**

```text
Agent SDK 不放在主 API 服务里运行
所有 Repo Review 进入 Agent Runner
执行代码必须进 Sandbox
不注入生产密钥
限制网络、CPU、内存、时间
记录所有 Tool Call
高风险 Review 进入人工复核
```

**15. 第一版页面**

学员端：

```text
Dashboard
入营测评
个性化学习计划
自适应课程
Project Lab
Agent Tutor
Submission Center
Review Report
能力知识图谱
Certificate / Skill Passport
```

后台端：

```text
学员管理
项目任务管理
课程模块管理
Rubric 管理
Review 管理
Evidence 管理
能力图谱管理
证书管理
```

企业轻量端：

```text
Skill Passport 公共页
Demo 查看
反馈表
合作意向表
```

**16. 商业模式**

第一阶段：

```text
Cohort-based AI Agent Builder 训练营收费
```

第二阶段：

```text
企业内训
企业员工能力评估
AI Agent Builder 认证
企业项目 Demo Day
```

第三阶段：

```text
Skill Passport 验证网络
企业人才筛选
项目匹配
认证与数据服务
```

**17. 第一版成功指标**

```text
30–50 名学员入营
70% 完成至少 2 个项目
50% 完成 3 个项目
每人产生 10+ 条 Evidence
生成 20+ 份 Skill Passport
5–10 家企业查看 Passport
3 家企业给出有效反馈
至少 1 家企业表达合作或内训意向
```

**18. 护城河**

TIAI 的护城河不是课程，也不是 Claude Agent SDK。

真正护城河是：

```text
Agent Builder Skill Standard
Project Graph
Rubric Graph
Evidence Store
Agent Review 数据
企业反馈数据
被市场认可的 Skill Passport
```

最终目标：

> **成为 AI Agent Builder 能力标准、训练交付和可信认证的基础设施。**

**19. 第一版边界**

第一版不做：

```text
完整招聘平台
复杂企业端
大型社区
复杂多 Agent 编排平台
完整企业级权限审计
复杂长期记忆系统
通用 AI SaaS 平台
```

第一版只做一件事：

> **让学员完成 2–3 个真实 AI Agent 项目，并用 Review、Evidence、Skill Graph 和 Skill Passport 证明能力。**

**20. 最终定义**

> **TIAI v1 是一个 AI Agent Builder 训练营交付系统 + 能力评审系统 + Skill Passport 生成系统。**

更强版本：

> **TIAI 用项目制训练、Agent Review、能力证据和 Skill Passport，证明谁真的具备构建 AI Agent 系统的能力。**