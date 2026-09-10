# 游戏构建 CrewAI 示例

这是一个 CrewAI 多智能体教学示例，用多个 Agent 模拟一个小型游戏开发团队：有人负责需求理解，有人负责编码，有人负责审查和验收。

## 项目用途

本项目用于学习 CrewAI 的基础结构：

- `Agent`
- `Task`
- `Crew`
- YAML 配置
- 顺序执行流程
- 从自然语言需求生成代码的基本模式

## 目录结构

```text
config/
  agents.yaml      Agent 角色配置
  tasks.yaml       任务配置
  gamedesign.yaml  游戏设计输入示例
src/
  crew.py          Crew 组装逻辑
  main.py          运行入口
pyproject.toml     项目依赖配置
.env.example       环境变量模板
```

## 环境配置

复制 `.env.example` 为 `.env`，填写模型服务所需的 API Key 和 Base URL。

```powershell
Copy-Item .env.example .env
```

真实 `.env` 不应提交到 GitHub。

## 运行

```powershell
uv sync
uv run game_builder_crew
```

## 当前状态

这是实验/教学项目，不是生产级游戏生成器。它的价值在于展示 CrewAI 如何组织多角色协作流程，而不是生成可直接发布的游戏。
