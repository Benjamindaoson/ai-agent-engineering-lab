# Markdown 校验 Crew

这是 CrewAI 官方 `markdown_validator` 示例的升级复现版本，用于教学“Agent + 自定义 Tool”的分工方式。

## 项目用途

CLI 接收一个 Markdown 文件路径，先由确定性的自定义 Tool 检查文档问题，再由 CrewAI Agent 汇总问题并给出修改建议。

工具会检查：

- 空文件；
- 标题层级跳跃；
- 空标题；
- 重复标题；
- 未闭合代码块；
- 行尾多余空格；
- 裸 URL；
- 图片缺少 alt 文本。

本项目只报告问题，不会自动修改输入文件。

## 安装

```powershell
uv sync
Copy-Item .env.example .env
```

在 `.env` 中填写 DeepSeek 或其他 OpenAI 兼容模型配置。

## 运行

```powershell
uv run markdown_validator examples/bad_markdown.md
```

输出包含问题摘要、行号、问题类型、解释和修改建议。

## 教学重点

- 为什么确定性检查应该放在 Tool 中；
- 为什么 LLM 更适合总结和解释；
- 如何把工具结果交给 Agent；
- 为什么第一版只给建议，不自动改用户文件。

## 当前状态

这是教学原型，不包含批量仓库扫描、前端、数据库、RAG、CI/CD 或复杂多 Agent 协作。
