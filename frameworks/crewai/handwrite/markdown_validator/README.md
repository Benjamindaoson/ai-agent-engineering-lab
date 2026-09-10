# Markdown 语法审查 Crew

这是一个简化版 CrewAI 示例，用于演示如何让 Agent 调用自定义工具检查 Markdown 文档。

## 项目用途

系统读取一个 Markdown 文件，工具先返回语法和格式问题，Agent 再把这些问题整理成可读的修改建议。

## 运行

```powershell
Copy-Item .env.example .env
poetry lock
poetry install
poetry run markdown_validator README.md
```

也可以直接运行脚本入口，具体取决于本地环境配置。

## 目录结构

```text
src/markdown_validator/
  crew.py
  main.py
  tools/markdownTools.py
  config/
    agents.yaml
    tasks.yaml
```

## 环境变量

`.env.example` 是模板。真实 `.env` 不应提交到 GitHub。

## 当前状态

这是早期教学示例，保留价值在于 CrewAI Tool 调用模式和 Markdown 检查任务设计。
