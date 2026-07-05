# Python Agent Course Map

这份文档把已经转写完成的 19 个 Python 项目串成一条课堂路线。每章先跑离线命令，再讲 Java/Python 对照，最后才接真实模型或外部服务。

## 通用课堂跑法

每个 Python 项目都优先按这个顺序演示：

```powershell
cd <python-project>
python -m unittest discover -s tests -v
python -m <package>.self_check
python -m <package>.offline_demo
python -m <package>
```

前三步通常是离线演示。最后一步才可能调用真实模型、启动本地服务，或依赖外部运行环境。

## Provider 配置

大多数模块支持 OpenAI-compatible Provider：

```powershell
$env:PROVIDER="deepseek"
$env:DEEPSEEK_API_KEY="your-key"
$env:LLM_NAME="deepseek-chat"
```

或：

```powershell
$env:PROVIDER="dashscope"
$env:DASHSCOPE_API_KEY="your-key"
$env:LLM_NAME="qwen-plus"
```

`LLM_NAME` 通常可省略，具体默认值看各项目的 `model_config.py` 或 README。

## 课程顺序

| 章 | Python 项目 | Java 原项目 | 课堂重点 | 先跑命令 | 外部依赖 |
|---:|---|---|---|---|---|
| 1 | [`python-react-agent`](../python-react-agent/) | `java-react-agent` | 最小 ReAct 循环、工具声明、工具调用、Provider 配置 | `python -m python_react_agent.self_check` -> `python -m python_react_agent.offline_demo` | live 模型需要 DeepSeek 或 DashScope Key |
| 2 | [`python-ai-manus`](../python-ai-manus/) | `ai-manus` | Manus 式任务执行、搜索、浏览器、沙箱工具入口 | `python -m python_ai_manus.self_check` -> `python -m python_ai_manus.offline_demo` | 可选 `TAVILY_API_KEY`、Docker Desktop、Playwright |
| 3 | [`python-ai-engineer`](../python-ai-engineer/) | `ai-engineer` | 工程师 Agent：需求到文件修改的最小工作流 | `python -m python_ai_engineer.self_check` -> `python -m python_ai_engineer.offline_demo` | live 模型 Key |
| 4 | [`python-ai-deepresearch`](../python-ai-deepresearch/) | `ai-deepresearch` | 深度研究：搜索、并行流式、报告生成 | `python -m python_ai_deepresearch.self_check` -> `python -m python_ai_deepresearch.offline_demo` | 可选 `TAVILY_API_KEY`，live 模型 Key |
| 5 | [`python-ai-data`](../python-ai-data/) | `ai-data` | Text-to-SQL、计划执行、SQLite 离线数据查询 | `python -m python_ai_data.self_check` -> `python -m python_ai_data.offline_demo` | live 模型 Key；离线用 SQLite |
| 6 | [`python-ai-weekly-report`](../python-ai-weekly-report/) | `ai-weekly-report` | 周报生成、邮件发送 dry-run、SMTP 实战入口 | `python -m python_ai_weekly_report.self_check` -> `python -m python_ai_weekly_report.offline_demo` | 真实邮件需要 SMTP 环境变量 |
| 7 | [`python-ai-order`](../python-ai-order/) | `ai-order` | 订单推荐、下单、支付确认、退款、客服知识库 | `python -m python_ai_order.self_check` -> `python -m python_ai_order.offline_demo` | live 模型 Key |
| 8 | [`python-ai-consultation`](../python-ai-consultation/) | `ai-consultation` | 医疗咨询路由、科室 RAG、澄清与挂号确认 | `python -m python_ai_consultation.self_check` -> `python -m python_ai_consultation.offline_demo` | live 模型 Key；注意不做诊断建议 |
| 9 | [`python-spring-ai-demo`](../python-spring-ai-demo/) | `spring-ai-demo` | Spring AI 能力总览：chat、stream、memory、RAG、tools、MCP client 形状 | `python -m python_spring_ai_demo.self_check` -> `python -m python_spring_ai_demo.offline_demo` | live 模型 Key |
| 10 | [`python-ai-mcp-server-demo`](../python-ai-mcp-server-demo/) | `spring-ai-mcp-server-demo` | MCP-style server：tool、prompt、resource | `python -m python_ai_mcp_server_demo.self_check` -> `python -m python_ai_mcp_server_demo.offline_demo` | `python -m python_ai_mcp_server_demo` 会启动本地 HTTP 服务 |
| 11 | [`python-a2a-demo`](../python-a2a-demo/) | `a2a-server-demo` + `a2a-client-demo` | A2A 注册、发现、远程 Agent、顺序组合 | `python -m python_a2a_demo.self_check` -> `python -m python_a2a_demo.offline_demo` | 离线用内存注册表 |
| 12 | [`python-ai-alibaba-demo`](../python-ai-alibaba-demo/) | `spring-ai-alibaba-demo` | DashScope/Alibaba 工具链、搜索、文档解析、向量检索 | `python -m python_ai_alibaba_demo.self_check` -> `python -m python_ai_alibaba_demo.offline_demo` | live DashScope/DeepSeek Key；真实搜索可接外部服务 |
| 13 | [`python-ai-alibaba-graph-demo`](../python-ai-alibaba-graph-demo/) | `spring-ai-alibaba-graph-demo` | Graph 工作流、条件路由、checkpoint、中断与恢复 | `python -m python_ai_alibaba_graph_demo.self_check` -> `python -m python_ai_alibaba_graph_demo.offline_demo` | live 模型 Key |
| 14 | [`python-ai-alibaba-agent-framework-demo`](../python-ai-alibaba-agent-framework-demo/) | `spring-ai-alibaba-agent-framework-demo` | Agent Framework：工具、记忆、Hook、人工审批、流程编排、RAG Agent | `python -m python_ai_alibaba_agent_framework_demo.self_check` -> `python -m python_ai_alibaba_agent_framework_demo.offline_demo` | live 模型 Key |
| 15 | [`python-ai-multi-model`](../python-ai-multi-model/) | `ai-multi-model` | 多模态：图片生成、图片理解、视频流、音频转写入口 | `python -m python_ai_multi_model.self_check` -> `python -m python_ai_multi_model.offline_demo` | 真实多模态模型 Key 和本地媒体文件 |
| 16 | [`python-claw`](../python-claw/) | `java-claw` | 平台型 Agent：工作区模板、技能、记忆、Web 聊天、飞书入口 | `python -m python_claw.self_check` -> `python -m python_claw.offline_demo` | 真实飞书/WebSocket/模型调用需要外部配置 |
| 17 | [`python-agentscope-demo`](../python-agentscope-demo/) | `agentscope-demo` | AgentScope 能力总览：Agent、toolkit、hooks、memory、pipeline、skills、RAG、MCP、vision、Studio | `python -m python_agentscope_demo.self_check` -> `python -m python_agentscope_demo.offline_demo` | live AgentScope/DashScope/Mem0/Elasticsearch/MCP/Studio 均为可选扩展 |
| 18 | [`python-agentscope-agui-demo`](../python-agentscope-agui-demo/) | `agentscope-agui-demo` | AG-UI：浏览器请求、`/agui/run`、SSE 事件流、服务端线程记忆 | `python -m python_agentscope_agui_demo.self_check` -> `python -m python_agentscope_agui_demo.offline_demo` | `python -m python_agentscope_agui_demo --port 8000` 启动本地网页 |
| 19 | [`python-agentscope-a2a-demo`](../python-agentscope-a2a-demo/) | `agentscope-a2a-demo` | AgentScope A2A：agent card、Nacos-like 发现、远程流式事件 | `python -m python_agentscope_a2a_demo.self_check` -> `python -m python_agentscope_a2a_demo.offline_demo` | 真实 Nacos/AgentScope A2A/DashScope 为可选扩展 |

## 阶段讲法

### 第一阶段：从一个 Agent 到一个任务执行器

讲 `python-react-agent`、`python-ai-manus`、`python-ai-engineer`。目标是让学生明白 Agent 不是聊天窗口，而是“模型 + 工具 + 循环 + 状态”的程序结构。

### 第二阶段：把 Agent 放进业务场景

讲 `python-ai-deepresearch`、`python-ai-data`、`python-ai-weekly-report`、`python-ai-order`、`python-ai-consultation`。这些模块更像真实业务：研究、数据查询、邮件、交易、咨询。

### 第三阶段：进入框架和协议

讲 `python-spring-ai-demo`、`python-ai-mcp-server-demo`、`python-a2a-demo`、三个 Alibaba 模块。目标是把前面的手写能力映射到框架概念：RAG、Tool、MCP、A2A、Graph、Checkpoint、Human-in-the-loop。

### 第四阶段：平台化和多模态

讲 `python-ai-multi-model` 和 `python-claw`。一个负责多模态入口，一个负责平台化 Agent 工作区、技能、记忆和消息入口。

### 第五阶段：AgentScope 专题

讲 `python-agentscope-demo`、`python-agentscope-agui-demo`、`python-agentscope-a2a-demo`。顺序是框架能力总览 -> UI 事件流 -> Agent 间通信。

## 每堂课推荐节奏

1. 打开 Java 原目录和 Python 对照目录。
2. 先读 Python README 的 `Java to Python map`。
3. 跑 `self_check`，确认环境没问题。
4. 跑 `offline_demo`，先看到完整行为。
5. 打开测试文件，讲“这个模块必须保证什么行为”。
6. 最后才设置 Provider Key 跑 live demo。

## 外部依赖速查

| 依赖 | 出现场景 | 不装时怎么讲 |
|---|---|---|
| DeepSeek / DashScope Key | 大多数 live 模型 demo | 先跑 `self_check` 和 `offline_demo` |
| Tavily | Manus、DeepResearch 搜索 | 用离线搜索结果讲流程 |
| Docker Desktop | Manus 沙箱 | 讲工具入口和错误提示 |
| Playwright | Manus 浏览器工具 | 讲浏览器工具抽象，不强行 smoke test |
| SMTP | Weekly Report 真发邮件 | dry-run 足够课堂演示 |
| Nacos | A2A 发现 | Python 版用内存注册表 |
| MCP server | MCP client / AgentScope MCP | 先用离线返回值讲协议形状 |
| Studio / AG-UI | AgentScope UI | AG-UI Python 版可本地启动网页 |

## 收口检查

全仓库 Python 课程检查可以逐个项目跑：

```powershell
python -m unittest discover -s python-react-agent\tests -v
python -m unittest discover -s python-ai-manus\tests -v
python -m unittest discover -s python-ai-engineer\tests -v
python -m unittest discover -s python-ai-deepresearch\tests -v
python -m unittest discover -s python-ai-data\tests -v
python -m unittest discover -s python-ai-weekly-report\tests -v
python -m unittest discover -s python-ai-order\tests -v
python -m unittest discover -s python-ai-consultation\tests -v
python -m unittest discover -s python-spring-ai-demo\tests -v
python -m unittest discover -s python-ai-mcp-server-demo\tests -v
python -m unittest discover -s python-a2a-demo\tests -v
python -m unittest discover -s python-ai-alibaba-demo\tests -v
python -m unittest discover -s python-ai-alibaba-graph-demo\tests -v
python -m unittest discover -s python-ai-alibaba-agent-framework-demo\tests -v
python -m unittest discover -s python-ai-multi-model\tests -v
python -m unittest discover -s python-claw\tests -v
python -m unittest discover -s python-agentscope-demo\tests -v
python -m unittest discover -s python-agentscope-agui-demo\tests -v
python -m unittest discover -s python-agentscope-a2a-demo\tests -v
```
