# 营销策略 CrewAI 示例

这是一个早期 CrewAI 营销策略生成示例，用多个 Agent 协作完成市场分析、策略制定和营销内容生成。

## 项目用途

用户输入产品和市场信息后，CrewAI 会组织 Agent 生成营销策略和内容建议。

## 目录结构

```text
src/
  crew.py              Crew 组装逻辑
  main.py              运行入口
  config/
    agents.yaml        Agent 配置
    tasks.yaml         Task 配置
pyproject.toml
uv.lock
.env.example
```

## 环境配置

复制 `.env.example` 为 `.env`，填写模型和搜索服务配置。

真实 `.env` 不应提交。

## 运行

```powershell
poetry lock
poetry install
poetry run marketing_posts
```

## 当前状态

这是早期示例版本。更完整的中文版本在 `03-marketing-strategy/`，本目录主要作为对照和历史参考。
