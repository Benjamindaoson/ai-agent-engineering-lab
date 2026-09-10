# AI Agent Engineering Lab

一个面向 AI Agent 工程实践的 Python 教学项目库：用 19 个可运行的子项目和若干已并入的 case study，讲清楚 Agent 的工具调用、任务执行、RAG、MCP、A2A、多模态、工作流、评审和学习平台化。

这个仓库不是单个聊天机器人，也不是纯课件。它由三部分组成：

1. **19 个 Python Agent 教学项目**：每个项目对应一个工程主题，包含源码、测试、`self_check` 和离线演示。
2. **课程闯关工具**：`course.py` 按关卡顺序运行测试和演示，通过当前关后解锁下一关。
3. **AgentLab 学习平台**：本地可启动的训练营系统，用 Web + API 跑通“学习规划 -> 项目实战 -> 沙箱运行 -> Agent 评审 -> 能力证据 -> Skill Passport”的闭环。

## 已并入的教学 / Demo 仓

以下内容原本是独立 demo 或课程快照，已经合并到本仓，后续不再单独维护：

| 目录 | 来源 | 定位 |
|---|---|---|
| [`frameworks/crewai/project-task-manager-crew`](frameworks/crewai/project-task-manager-crew/) | `project-task-manager-crew` | CrewAI 三角色顺序协作入门 |
| [`frameworks/crewai/handwrite`](frameworks/crewai/handwrite/) | `crewai-handwrite` | CrewAI 手写练习合集 |
| [`frameworks/crewai/examples-notes`](frameworks/crewai/examples-notes/) | `crewai-examples-private-notes` | CrewAI 示例与本地学习笔记 |
| [`frameworks/langchain/spain-travel-agent`](frameworks/langchain/spain-travel-agent/) | `travelagent` | LangChain 旅行规划教学 demo |
| [`case-studies/email-invitation-agent`](case-studies/email-invitation-agent/) | `email-invitation-agent` | 邮件邀请生成 Agent 小案例 |
| [`case-studies/urban-planning-review-agent`](case-studies/urban-planning-review-agent/) | `agent-for-planning` | 城市控规审查 RAG + 多 Agent 原型 |
| [`case-studies/agentlab-rag`](case-studies/agentlab-rag/) | `agentlab-rag` | AgentLab 浏览器救援训练产品 case study |
| [`protocols/mini-claw-java`](protocols/mini-claw-java/) | `mini-claw` | Java Claw/Skill 小型协议演示 |

合并原则记录在 [`docs/repository-consolidation-2026-09-10.md`](docs/repository-consolidation-2026-09-10.md)。这些目录是教学资产和历史参考，不代表新增公开旗舰项目。

## 适合做什么

- 做 AI Agent 工程课程、训练营或企业内训的案例工程。
- 给学生演示 Agent 不是“一个提示词”，而是模型、工具、状态、记忆、协议、工作流和评审系统的组合。
- 做作品集，重点展示完整的 Agent 学习产品闭环，而不是只展示零散 Demo。
- 做二次开发，把 AgentLab 扩展成训练营平台或企业内部 AI 工程师培养平台。

## 19 个教学项目

| 关卡 | 目录 | 主题 | 主要内容 |
|---:|---|---|---|
| 1 | [`python-react-agent`](python-react-agent/) | ReAct 最小 Agent | 思考/行动/观察循环、工具声明、工具调用解析、离线 Demo、模型 Provider 配置 |
| 2 | [`python-ai-manus`](python-ai-manus/) | Manus 式任务执行器 | 文件工具、搜索工具、浏览器工具、沙箱执行、任务步骤规划 |
| 3 | [`python-ai-engineer`](python-ai-engineer/) | AI 工程师 Agent | 需求拆解、代码/文件修改流程、多角色执行、工程任务自动化雏形 |
| 4 | [`python-ai-deepresearch`](python-ai-deepresearch/) | 深度研究 Agent | 搜索、资料整理、并行研究流程、研究报告生成 |
| 5 | [`python-ai-data`](python-ai-data/) | 数据分析 Agent | Text-to-SQL、SQLite 离线数据集、查询计划、分析报告 |
| 6 | [`python-ai-weekly-report`](python-ai-weekly-report/) | 自动周报 Agent | Git 日志读取、周报生成、邮件发送 dry-run、SMTP 扩展入口 |
| 7 | [`python-ai-order`](python-ai-order/) | 订单业务 Agent | 商品推荐、下单、支付确认、退款、客服知识库 |
| 8 | [`python-ai-consultation`](python-ai-consultation/) | 咨询/分诊 Agent | 科室匹配、RAG 知识检索、澄清追问、预约确认；不提供诊断建议 |
| 9 | [`python-spring-ai-demo`](python-spring-ai-demo/) | AI 框架能力总览 | Chat、Stream、Memory、RAG、Tools、MCP Client 等框架概念的 Python 复现 |
| 10 | [`python-ai-mcp-server-demo`](python-ai-mcp-server-demo/) | MCP Server | Tool、Prompt、Resource 的服务端形态和本地 HTTP 服务 |
| 11 | [`python-a2a-demo`](python-a2a-demo/) | Agent-to-Agent 协作 | Agent 注册、发现、远程调用、顺序组合、内存注册表 |
| 12 | [`python-ai-alibaba-demo`](python-ai-alibaba-demo/) | DashScope/Alibaba 生态 | 模型调用、搜索、文档解析、向量检索、工具链组合 |
| 13 | [`python-ai-alibaba-graph-demo`](python-ai-alibaba-graph-demo/) | Graph 工作流 | 条件路由、checkpoint、中断、恢复、图式任务编排 |
| 14 | [`python-ai-alibaba-agent-framework-demo`](python-ai-alibaba-agent-framework-demo/) | Agent Framework 进阶 | 工具、记忆、Hook、人工审批、流程编排、RAG Agent |
| 15 | [`python-ai-multi-model`](python-ai-multi-model/) | 多模态 Agent | 图片生成、图片理解、视频流、音频转写入口和离线替身 |
| 16 | [`python-claw`](python-claw/) | 综合平台型 Agent | 工作区、技能、记忆、Web 聊天、消息入口、平台化 Agent 结构 |
| 17 | [`python-agentscope-demo`](python-agentscope-demo/) | AgentScope 能力总览 | Agent、Toolkit、Hooks、Memory、Pipeline、Skills、RAG、MCP、Vision、Studio |
| 18 | [`python-agentscope-agui-demo`](python-agentscope-agui-demo/) | AG-UI 事件流 | 浏览器请求、`/agui/run`、SSE 事件流、服务端线程记忆、本地 Web 页面 |
| 19 | [`python-agentscope-a2a-demo`](python-agentscope-a2a-demo/) | AgentScope A2A | Agent Card、服务发现、远程流式事件、Agent 间通信 |

每个子项目优先保证本地离线可运行。真实模型、搜索、邮件、浏览器、Docker、Nacos、Studio 等能力通常作为可选扩展。

## 课程闯关怎么跑

查看当前进度：

```powershell
python course.py status
```

运行当前关的完整检查：

```powershell
python course.py run all
```

`course.py` 默认只运行当前关。当前关通过 `self_check`、`offline_demo` 和测试后，才会解锁下一关。

可单独运行：

```powershell
python course.py run self_check
python course.py run offline_demo
python course.py run tests
```

全量质量门禁：

```powershell
python scripts/python_quality_gate.py
```

## AgentLab 学习平台

AgentLab 位于 [`AI_Agent_Builder`](AI_Agent_Builder/)，是这个仓库里最接近产品形态的部分。

它做的事情：

```text
用户输入学习目标
-> Planning Agent 识别意图
-> 澄清问题
-> 生成学习路线
-> 推荐课程模块
-> 进入 3 个项目实战
-> Sandbox 运行项目
-> Claude / Mock Agent Review
-> 生成能力证据
-> 更新能力图谱
-> 生成 Skill Passport
```

一键本地启动：

```powershell
powershell -ExecutionPolicy Bypass -File .\run-local.ps1
```

启动完成后访问：

```text
http://127.0.0.1:3000
```

只安装依赖和初始化本地 SQLite，不启动服务：

```powershell
powershell -ExecutionPolicy Bypass -File .\run-local.ps1 -SetupOnly
```

AgentLab 技术结构：

- Web：Next.js、React、TypeScript
- API：FastAPI、Pydantic、Uvicorn
- 数据：本地 SQLite，保留 PostgreSQL / Supabase 扩展路径
- 评审：Mock Review 或 Claude Agent SDK Review
- 运行：本地 Sandbox Runner
- 产物：Evidence、Skill Score、Skill Passport

## 目录结构

```text
.
├─ course.py                         # 19 关课程闯关入口
├─ run-local.ps1                     # AgentLab 本地一键启动脚本
├─ scripts/                          # 全量质量检查脚本
├─ tests/                            # 仓库级测试
├─ docs/                             # 课程路线、关卡地图、质量评估
├─ frameworks/                       # 已并入的框架教学 demo
├─ case-studies/                     # 已并入的领域/产品 case study
├─ protocols/                        # 已并入的协议/运行时 demo
├─ production-platform/              # 生产化平台能力说明和预留模块
├─ AI_Agent_Builder/                 # AgentLab 学习平台
├─ python-react-agent/               # 01 ReAct 最小 Agent
├─ python-ai-manus/                  # 02 Manus 式任务执行器
├─ python-ai-engineer/               # 03 AI 工程师 Agent
├─ python-ai-deepresearch/           # 04 深度研究 Agent
├─ python-ai-data/                   # 05 数据分析 Agent
├─ python-ai-weekly-report/          # 06 自动周报 Agent
├─ python-ai-order/                  # 07 订单业务 Agent
├─ python-ai-consultation/           # 08 咨询/分诊 Agent
├─ python-spring-ai-demo/            # 09 AI 框架能力总览
├─ python-ai-mcp-server-demo/        # 10 MCP Server
├─ python-a2a-demo/                  # 11 A2A 协作
├─ python-ai-alibaba-demo/           # 12 DashScope/Alibaba 生态
├─ python-ai-alibaba-graph-demo/     # 13 Graph 工作流
├─ python-ai-alibaba-agent-framework-demo/ # 14 Agent Framework 进阶
├─ python-ai-multi-model/            # 15 多模态 Agent
├─ python-claw/                      # 16 综合平台型 Agent
├─ python-agentscope-demo/           # 17 AgentScope 总览
├─ python-agentscope-agui-demo/      # 18 AG-UI 事件流
└─ python-agentscope-a2a-demo/       # 19 AgentScope A2A
```

## 常用文档

- [Python 19 关课堂路线](docs/python-level-map.md)
- [Python 项目质量评估](docs/python-project-quality-review.md)
- [AgentLab 说明](AI_Agent_Builder/README.md)
- [生产化平台说明](production-platform/README.md)

## License

本项目采用 [Eclipse Public License 1.0](LICENSE)。
