# Java / Python Project Comparison

当前仓库按语言分成两个独立项目：

```text
handwritten-ai-agent-java/      Java 原课程项目
handwritten-ai-agent-python/    Python 对照转写项目
```

Python 版的目标不是替代 Java 版，而是方便课堂并排讲解：先看 Java 原实现讲框架能力，再看 Python 版用更少依赖复现同一个概念。

## 对照表

| Java 原项目 | Python 对照项目 | 对比重点 |
|---|---|---|
| `java-react-agent` | `python-react-agent` | 最小 ReAct Agent、工具调用、Provider 配置 |
| `ai-manus` | `python-ai-manus` | Manus 式任务执行、搜索、浏览器、沙箱工具 |
| `ai-engineer` | `python-ai-engineer` | 工程师 Agent、文件生成和修改流程 |
| `ai-deepresearch` | `python-ai-deepresearch` | 深度研究、搜索、并行流式、报告生成 |
| `ai-data` | `python-ai-data` | Text-to-SQL、计划执行、SQLite 离线查询 |
| `ai-weekly-report` | `python-ai-weekly-report` | 周报生成、邮件 dry-run、SMTP 入口 |
| `ai-order` | `python-ai-order` | 订单推荐、支付确认、退款、客服知识库 |
| `ai-consultation` | `python-ai-consultation` | 科室 RAG、澄清、挂号确认 |
| `spring-ai-demo` | `python-spring-ai-demo` | Spring AI 能力总览的 Python 对照 |
| `spring-ai-mcp-server-demo` | `python-ai-mcp-server-demo` | MCP-style tool、prompt、resource 服务 |
| `a2a-server-demo` + `a2a-client-demo` | `python-a2a-demo` | A2A 注册、发现、远程 Agent、顺序组合 |
| `spring-ai-alibaba-demo` | `python-ai-alibaba-demo` | DashScope/Alibaba 搜索、文档、向量检索 |
| `spring-ai-alibaba-graph-demo` | `python-ai-alibaba-graph-demo` | Graph、路由、checkpoint、中断恢复 |
| `spring-ai-alibaba-agent-framework-demo` | `python-ai-alibaba-agent-framework-demo` | Agent Framework、Hook、人工审批、复杂流程 |
| `ai-multi-model` | `python-ai-multi-model` | 图片、视频、音频等多模态入口 |
| `java-claw` | `python-claw` | 平台型 Agent、工作区、技能、记忆、消息入口 |
| `agentscope-demo` | `python-agentscope-demo` | AgentScope 基础能力总览 |
| `agentscope-agui-demo` | `python-agentscope-agui-demo` | AG-UI 浏览器事件流 |
| `agentscope-a2a-demo` | `python-agentscope-a2a-demo` | AgentScope A2A agent card 和流式事件 |

## 课堂对比方法

1. 先打开 Java 原项目，说明它依赖的框架能力。
2. 再打开 Python 对照项目，看同名模块或 README 的 `Java to Python map`。
3. Python 先跑 `self_check` 和 `offline_demo`，确认学生不被 Key、Docker、Nacos、浏览器依赖卡住。
4. 最后才跑 live 模型或外部服务。

## 结构差异

| 项 | Java 版 | Python 版 |
|---|---|---|
| 目录位置 | `handwritten-ai-agent-java/` | `handwritten-ai-agent-python/` |
| 依赖管理 | Maven 多模块 | 每个项目一个 `requirements.txt` |
| 默认演示 | 真实框架/服务优先 | 离线优先，外部服务可选 |
| 课堂用途 | 展示原课程框架写法 | 展示同一能力的最小 Python 复现 |
| 验证方式 | Maven/框架启动 | `unittest`、`self_check`、`offline_demo` |

更多课程顺序见 [python-course-map.md](python-course-map.md)。
