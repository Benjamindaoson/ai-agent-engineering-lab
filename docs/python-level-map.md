# Python Agent Level Map

这个文档把当前 Python 项目根目录下的 19 个教学模块组织成一套“轻度闯关式”的课堂路线。默认用根目录的 `course.py` 顺序推进，当前关通过后才解锁下一关。

这里的“闯关”不是做积分、排行榜、剧情人物，而是把学习路径讲清楚：每一关解决一个 Agent 能力问题，上一关的能力会成为下一关的基础，最后汇总成一个完整 Agent 工程视角。

## 课堂运行规则

每个 Python 项目目录下都有 `TEACHING_NOTES.md`，用于课堂手写讲解。建议老师进入每一关后先读这个文件，再打开代码。

从仓库根目录运行测试：

```powershell
python course.py status
python course.py run all
```

需要单独排查当前关时，可以只跑其中一项：

```powershell
python course.py run self_check
python course.py run offline_demo
python course.py run tests
```

单项目手动调试时，也可以从仓库根目录运行测试：

```powershell
python -m unittest discover -s <project>\tests -v
```

进入某个项目后运行自检和离线演示：

```powershell
cd <project>
python -m <package>.self_check
python -m <package>.offline_demo
```

真实模型、Tavily、Docker、Playwright、浏览器等外部能力只作为进阶演示，不作为课堂第一遍验收条件。

## 19 关路线

| 关卡 | 项目 | 类型 | 本关能力 | 首跑命令 |
| --- | --- | --- | --- | --- |
| 01 | `python-react-agent` | 基础关 | ReAct 循环、工具调用、OpenAI-compatible provider 配置 | `python -m python_react_agent.offline_demo` |
| 02 | `python-ai-manus` | 工具关 | 文件、搜索、浏览器、沙箱、工具注册与执行 | `python -m python_ai_manus.offline_demo` |
| 03 | `python-ai-engineer` | 工程关 | 需求拆解、文件规划、代码生成、工程任务流 | `python -m python_ai_engineer.offline_demo` |
| 04 | `python-ai-deepresearch` | 研究关 | 研究计划、搜索、资料归纳、报告生成 | `python -m python_ai_deepresearch.offline_demo` |
| 05 | `python-ai-data` | 数据关 | SQLite 数据分析、查询生成、结果解释 | `python -m python_ai_data.offline_demo` |
| 06 | `python-ai-weekly-report` | 自动化关 | 周报素材收集、Git 信息读取、报告生成 | `python -m python_ai_weekly_report.offline_demo` |
| 07 | `python-ai-order` | 业务关 | 订单状态流转、业务规则、客服 Agent | `python -m python_ai_order.offline_demo` |
| 08 | `python-ai-consultation` | 垂直业务关 | 咨询分诊、问答边界、安全提醒 | `python -m python_ai_consultation.offline_demo` |
| 09 | `python-spring-ai-demo` | 框架关 | Spring AI 概念的 Python 对照表达 | `python -m python_spring_ai_demo.offline_demo` |
| 10 | `python-ai-mcp-server-demo` | 协议关 | MCP 工具协议、资源暴露、客户端调用思路 | `python -m python_ai_mcp_server_demo.offline_demo` |
| 11 | `python-a2a-demo` | 协作关 | Agent registry、远程 Agent 调用、A2A 基础 | `python -m python_a2a_demo.offline_demo` |
| 12 | `python-ai-alibaba-demo` | 生态关 | Alibaba/Spring AI Alibaba 能力的 Python 化演示 | `python -m python_ai_alibaba_demo.offline_demo` |
| 13 | `python-ai-alibaba-graph-demo` | 图工作流关 | 节点、边、状态、条件分支、图执行 | `python -m python_ai_alibaba_graph_demo.offline_demo` |
| 14 | `python-ai-alibaba-agent-framework-demo` | 框架进阶关 | Agent 框架组件、记忆、工具、规划器组合 | `python -m python_ai_alibaba_agent_framework_demo.offline_demo` |
| 15 | `python-ai-multi-model` | 多模型关 | 文本、图片、音频等多模型调用形态 | `python -m python_ai_multi_model.offline_demo` |
| 16 | `python-claw` | Boss 关 | 任务编排、角色协作、项目级 Agent 系统 | `python -m python_claw.offline_demo` |
| 17 | `python-agentscope-demo` | 支线关 | AgentScope 核心 API 与多 Agent 组织方式 | `python -m python_agentscope_demo.offline_demo` |
| 18 | `python-agentscope-agui-demo` | 支线关 | AgentScope 与 AG-UI 事件/交互模型 | `python -m python_agentscope_agui_demo.offline_demo` |
| 19 | `python-agentscope-a2a-demo` | 支线关 | AgentScope 与 A2A 协议的组合演示 | `python -m python_agentscope_a2a_demo.offline_demo` |

## 课程叙事

这 19 个项目更适合定位为“训练营关卡”，不是强行合并成一个巨型应用。

推荐课堂讲法：

1. 第 1 关讲最小 Agent 内核：模型、提示词、工具、循环。
2. 第 2-8 关讲 Agent 能力扩展：工具、工程、研究、数据、自动化、业务、安全边界。
3. 第 9-15 关讲框架与协议：Spring AI 对照、MCP、A2A、Alibaba、Graph、多模型。
4. 第 16 关讲完整项目：把前面的能力组织成一个可解释、可扩展的系统。
5. 第 17-19 关作为生态支线：让学生看到同一套 Agent 思想在 AgentScope 生态中的表达。

## 过关标准

每一关至少满足四件事：

1. `self_check` 能通过，说明基本依赖和入口没有坏。
2. `offline_demo` 能跑，说明无 Key 课堂环境也能演示。
3. `tests` 能通过，说明核心行为有最低限度的回归保护。
4. 老师能用 README 讲清楚：本关新增了什么能力，和上一关有什么关系。

## 不建议做的游戏化

不建议在这个阶段加入排行榜、积分商城、剧情角色、复杂 UI 或强制注册系统。这些会把注意力从 Agent 工程能力转移到产品包装。

更合理的轻量游戏化是：

- 关卡编号：让学生知道自己学到哪里。
- Boss 关：把 `python-claw` 定位成综合项目。
- 支线关：把 AgentScope 三个项目定位成生态扩展。
- 过关清单：用测试、自检、离线演示作为验收。
