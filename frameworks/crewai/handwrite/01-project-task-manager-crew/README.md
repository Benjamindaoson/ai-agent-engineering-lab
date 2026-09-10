# AI 待办/日程管理器生成 Crew

这是一个 CrewAI 教学项目，用三个 Agent 顺序协作生成 Python 命令行待办/日程管理器代码。

## 工作流

1. Python 开发工程师生成初稿；
2. 代码审查工程师检查并修复问题；
3. 质量验收工程师给出最终验收意见。

## 技术栈

- Python
- uv
- CrewAI
- DeepSeek OpenAI 兼容接口
- YAML Agent/Task 配置
- `Process.sequential`

## 目录结构

```text
src/
  crew.py                 Crew 组装逻辑
  main.py                 CLI 入口
  config/
    agents.yaml           Agent 配置
    tasks.yaml            Task 配置
pyproject.toml
uv.lock
.env.example
```

## 环境配置

复制模板：

```powershell
Copy-Item .env.example .env
```

填写：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
```

`.env` 可以放真实 Key，但不要提交。

## 运行

```powershell
uv sync
uv run project_task_manager_crew
```

冒烟测试入口：

```powershell
uv run project_task_manager_smoke
```

## 当前状态

这是可运行的 CrewAI 学习原型，适合作为多 Agent 顺序协作、代码生成和质量审查流程的示例。
