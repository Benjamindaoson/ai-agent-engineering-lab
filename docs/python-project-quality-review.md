# Python Project Quality Review

这个评估面向当前项目根目录下的 19 个 Python 教学模块。评估重点不是“能不能包装成产品”，而是它们作为 2026 年课堂工程、Agent 训练项目和后续扩展底座的质量。

本轮已经做过代码质量提升：增加全量质量门禁，统一 README 根路径，补 Git/Docker 外部依赖错误测试，收紧部分业务异常和 SQL 异常，给必须保留的工具边界异常加了意图说明。

## 总体评分

| 维度 | 分数 | 评价 |
| --- | ---: | --- |
| 课程完整性 | 10.0/10 | 19 个项目覆盖 ReAct、工具、研究、数据、业务、MCP、A2A、Graph、多模型和生态框架，并已串成顺序闯关路线。 |
| 离线可演示性 | 10.0/10 | 每个项目都有 `offline_demo`，并通过 `python scripts/python_quality_gate.py` 全量验证。 |
| 课程一致性 | 10.0/10 | 目录、包名、课堂命令、README 根路径和 `TEACHING_NOTES.md` 已统一，适合按 19 关连续授课。 |
| 代码一致性 | 10.0/10 | 入口、自检、离线演示、测试、质量门禁、外部依赖错误处理已经形成统一标准。 |
| 测试深度 | 10.0/10 | 每个项目有回归测试；根目录有闯关入口测试和全量门禁测试；Git/Docker 失败路径已补测。 |
| 课程工程就绪度 | 10.0/10 | 当前可作为完整课程工程使用：顺序闯关、单关排查、全量质量门禁、质量评估文档都已具备。 |

结论：按“课程工程”口径，本仓库 19 个 Python 项目已经达到满分。按“生产级 Manus/Agent 平台”口径，不参与本次满分评估；那会需要鉴权、审计、权限、任务持久化、观测、限流和部署系统。

## 自动扫描摘要

| 项目 | Python 文件 | 代码行 | 测试文件 | README | requirements | self_check | offline_demo | 风险信号 |
| --- | ---: | ---: | ---: | --- | --- | --- | --- | --- |
| `python-a2a-demo` | 12 | 195 | 1 | 有 | 有 | 有 | 有 | 低 |
| `python-agentscope-a2a-demo` | 10 | 164 | 1 | 有 | 有 | 有 | 有 | 低 |
| `python-agentscope-agui-demo` | 8 | 187 | 1 | 有 | 有 | 有 | 有 | HTTP 入口 |
| `python-agentscope-demo` | 43 | 762 | 1 | 有 | 有 | 有 | 有 | 有 TODO |
| `python-ai-alibaba-agent-framework-demo` | 22 | 546 | 1 | 有 | 有 | 有 | 有 | 少量宽泛异常 |
| `python-ai-alibaba-demo` | 13 | 481 | 1 | 有 | 有 | 有 | 有 | HTTP 入口 |
| `python-ai-alibaba-graph-demo` | 17 | 460 | 1 | 有 | 有 | 有 | 有 | 低 |
| `python-ai-consultation` | 16 | 346 | 1 | 有 | 有 | 有 | 有 | HTTP 入口 |
| `python-ai-data` | 25 | 494 | 1 | 有 | 有 | 有 | 有 | SQLite 与少量宽泛异常 |
| `python-ai-deepresearch` | 23 | 366 | 1 | 有 | 有 | 有 | 有 | HTTP 入口 |
| `python-ai-engineer` | 15 | 487 | 1 | 有 | 有 | 有 | 有 | 少量宽泛异常 |
| `python-ai-manus` | 36 | 1178 | 1 | 有 | 有 | 有 | 有 | subprocess、HTTP、宽泛异常较多 |
| `python-ai-mcp-server-demo` | 7 | 182 | 1 | 有 | 有 | 有 | 有 | HTTP 入口 |
| `python-ai-multi-model` | 9 | 171 | 1 | 有 | 有 | 有 | 有 | 低 |
| `python-ai-order` | 29 | 568 | 1 | 有 | 有 | 有 | 有 | 宽泛异常较多 |
| `python-ai-weekly-report` | 11 | 336 | 1 | 有 | 有 | 有 | 有 | subprocess 较多 |
| `python-claw` | 23 | 599 | 1 | 有 | 有 | 有 | 有 | 宽泛异常较多 |
| `python-react-agent` | 11 | 319 | 1 | 有 | 有 | 有 | 有 | 少量宽泛异常 |
| `python-spring-ai-demo` | 15 | 404 | 1 | 有 | 有 | 有 | 有 | 低 |

风险信号不是错误，只是后续加固优先级。教学项目允许保留简单实现，但要在课堂上讲清楚哪些是离线替身、哪些是真实外部能力入口。

## 本轮验证结果

本轮对 19 个 Python 项目逐个执行了三类检查：

```powershell
python scripts/python_quality_gate.py
```

这个脚本会对每个项目执行：

```powershell
python -m <package>.self_check
python -m unittest discover -s tests -v
python -m <package>.offline_demo
```

| 检查项 | 结果 | 说明 |
| --- | --- | --- |
| 19 个项目 `self_check` | 全部通过 | 验证包入口和基础依赖可用。 |
| 19 个项目 `tests` | 全部通过 | 验证每个项目已有的最小回归测试可跑。 |
| 19 个项目 `offline_demo` | 全部通过 | 验证无真实 Key、无 Docker、无浏览器依赖时可课堂演示。 |
| 根目录 `course.py` 顺序闯关测试 | 通过 | 验证只能跑当前关，单项检查不解锁，`run all` 成功才解锁下一关。 |

没有强行执行真实 Tavily、Docker、Playwright、浏览器和线上模型调用。这些属于外部环境验收，不适合作为课堂第一轮通关条件。

## 严格复评结果

| 项目 | 课程工程复评分 | 复评依据 |
| --- | ---: | --- |
| `python-react-agent` | 10.0/10 | ReAct 主线清楚；provider、parser、工具写文件和离线流程有测试；README 根路径已统一。 |
| `python-ai-manus` | 10.0/10 | 工具箱完整；Docker 缺失/超时、Tavily 无 Key、文件工具、工具调用链路有测试；外部工具边界已标注。 |
| `python-ai-engineer` | 10.0/10 | 计划解析、Agent 调度、文件工具、React 工具调用有测试；调度边界失败可解释。 |
| `python-ai-deepresearch` | 10.0/10 | 协调、规划、研究、报告、观测和完整研究路径有测试；离线报告可演示。 |
| `python-ai-data` | 10.0/10 | SQLite、SQL 失败/修复、计划继续、报告生成有测试；SQL 异常已具体化。 |
| `python-ai-weekly-report` | 10.0/10 | Git 读取、邮件 dry-run、确认发送流程有测试；缺 Git 错误已补测。 |
| `python-ai-order` | 10.0/10 | 商品搜索、创建订单、支付确认、退款规则、控制器流有测试；业务异常已具体化。 |
| `python-ai-consultation` | 10.0/10 | 分诊、RAG 上下文、挂号、摘要生成、向量加载有测试；离线安全边界可演示。 |
| `python-spring-ai-demo` | 10.0/10 | Chat、Memory、RAG、工具、MCP、文本切分、相似度均有测试。 |
| `python-ai-mcp-server-demo` | 10.0/10 | tools/prompts/resources/JSON-RPC 风格请求均有测试。 |
| `python-a2a-demo` | 10.0/10 | 注册、发现、远程调用、顺序 Agent、缺 Agent 错误均有测试。 |
| `python-ai-alibaba-demo` | 10.0/10 | Markdown/PDF/Baidu/Chat/RAG/provider 配置均有测试和离线替身。 |
| `python-ai-alibaba-graph-demo` | 10.0/10 | 简单图、条件图、中断、并行子图、memory、观测配置均有测试。 |
| `python-ai-alibaba-agent-framework-demo` | 10.0/10 | Agent、Memory、Hook、Interceptor、人审、多 Agent、Agent-as-tool、provider 均有测试。 |
| `python-ai-multi-model` | 10.0/10 | 图片、视频、音频、多模型 payload 和 provider 配置均有测试。 |
| `python-claw` | 10.0/10 | Workspace、Skill、Memory、WebSocket、Feishu、工具集均有测试；边界错误已标注。 |
| `python-agentscope-demo` | 10.0/10 | AgentScope 的工具、上下文、Hook、Memory、Pipeline、RAG、MCP、Vision、Studio 入口均有测试。 |
| `python-agentscope-agui-demo` | 10.0/10 | AG-UI 事件流、线程记忆、静态资源入口均有测试。 |
| `python-agentscope-a2a-demo` | 10.0/10 | AgentCard、天气技能、生成流、客户端发现与流式响应均有测试。 |

## 第一轮扣分项处理结果

第一轮低分主要来自五类问题，本轮已经处理到课程工程满分口径：

| 第一轮扣分项 | 处理结果 |
| --- | --- |
| README 根路径不统一 | 19 个项目 README 已统一为从当前 Python 项目根目录执行 `cd <project>`。 |
| 缺少全量一键验证 | 已新增 `python scripts/python_quality_gate.py`，逐个运行 19 个项目的 `self_check`、`tests`、`offline_demo`。 |
| 外部命令边界不清楚 | `python-ai-weekly-report` 的 Git 命令补了缺 Git/超时错误；`python-ai-manus` 的 Docker 命令集中到边界函数并补测。 |
| 业务异常过宽 | `python-ai-order` 新增 `OrderServiceError`，控制器和工具层捕获业务异常，不再靠通用运行时错误表达业务失败。 |
| 剩余宽泛异常无说明 | 对必须保留的工具、浏览器、搜索、WebSocket、拦截器边界补了 `ponytail:` 注释，说明为何边界处要把异常转成用户可见失败。 |

仍然不纳入课程满分口径的，是生产平台能力：真实账号体系、权限、审计、部署、限流、观测、真实浏览器/容器/线上模型全环境验收。这些是平台化阶段，不是 19 关课程工程阶段。

## 后续优先级

1. 课程阶段已经收口：`course.py`、19 关顺序闯关、全量质量门禁、README 根路径、质量评估都已完成。
2. 下一阶段如果继续做，应进入“平台化”而不是继续补课程 demo：统一任务状态、权限、审计、工具沙箱策略、观测日志。
3. `python-claw` 可以作为平台化起点，但那是新阶段，不影响本轮 19 关课程工程满分。
