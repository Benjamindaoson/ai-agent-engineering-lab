# AI 待办/日程管理器 CLI 生成 Crew

## 项目介绍

这是一个基于 `game-builder-crew` 的三角色顺序协作结构改造而来的教学项目。

本项目保留了 CrewAI 最核心、最适合入门理解的组织方式：`Agent`、`Task`、`Crew`、YAML 配置、`Process.sequential` 顺序执行，以及 `kickoff(inputs)` 调用入口。

项目目标是让三个 Agent 按顺序协作完成一份 Python 命令行待办/日程管理器代码生成任务：

1. Python 开发工程师先产出初稿；
2. 代码审查工程师再检查并修复；
3. 质量验收工程师最后验收并输出最终结果。

## 技术栈与约定

- Python 3.10 / 3.11 / 3.12
- 推荐使用 `uv`
- CrewAI
- DeepSeek OpenAI 兼容接口
- `Agent`、`Task`、`Crew`
- YAML 配置
- `Process.sequential`
- `kickoff(inputs)`

## 目录结构

- `src/project_task_manager_crew/main.py`
- `src/project_task_manager_crew/crew.py`
- `src/project_task_manager_crew/config/agents.yaml`
- `src/project_task_manager_crew/config/tasks.yaml`

## 环境配置

复制 `.env.example` 为 `.env`，并配置 DeepSeek：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
```

注意：

- `.env` 里可以放真实 Key；
- `.env.example` 只能保留占位符；
- README 中不会显示真实 Key。

## 安装

建议直接使用 `uv`：

```bash
uv sync
```

## 运行

完整需求默认入口：

```bash
uv run project_task_manager_crew
```

如需 smoke 测试入口：

```bash
uv run project_task_manager_smoke
```

## 运行说明

- `Crew Execution Started` 不代表已经执行完成，只表示开始调度；
- 三个 Agent 会产生三次顺序模型调用；
- 完整运行通常需要一定时间；
- 最终结果只打印到终端；
- 不会自动创建 `task_manager.py`；
- 不会自动执行生成代码；
- 不会自动测试生成代码。

## 三个 Agent

1. Python 开发工程师
2. 代码审查工程师
3. 质量验收工程师

## 关键实现方式

本项目仍然采用最基础的 CrewAI 编排方式：

- `@CrewBase`
- `@agent`
- `@task`
- `@crew`
- `Process.sequential`
- `kickoff(inputs={...})`

## 安全说明

- 真实 API Key 只应存在于 `.env`；
- `.env` 已加入 `.gitignore`；
- `.env.example` 不包含真实密钥；
- 本项目不会打印 API Key。

## smoke 与 full

- `run()`：运行完整需求；
- `run_smoke()`：运行简化需求；

如果你只想做快速连通性验证，可以使用 smoke 命令；默认运行命令始终对应完整需求。

## 常见问题

### 为什么启动后会先看到 Crew Execution Started？

这只是开始执行的提示，并不代表三个任务已经全部完成。

### 为什么有时候需要等待一段时间？

因为这里是三次顺序模型调用，且每个 Agent 都要真正请求远端模型接口。

### 会不会自动保存或执行生成代码？

不会。本项目只负责生成文本结果，不自动保存、执行或测试生成代码。

## 与参考项目的关系

本项目从 `game-builder-crew` 的教学结构迁移而来，但业务目标已经改成了“AI 待办/日程管理器 CLI 代码生成”。
