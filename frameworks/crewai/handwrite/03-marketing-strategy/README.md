# 中文营销策略多 Agent 系统

这是一个基于 CrewAI、DeepSeek 和 Serper 的中文营销研究与内容策划系统。用户输入品牌、产品、目标客户、市场、预算和渠道后，系统按流程生成市场研究、产品理解、营销策略、活动方案、平台文案和最终审核稿。

## 能做什么

- 调研目标市场、行业趋势、竞品和客户需求；
- 分析产品定位、价值主张和购买阻力；
- 生成可执行的营销策略；
- 生成 5 个营销活动；
- 为活动生成平台文案；
- 输出 Markdown 格式的营销方案。

## 不能做什么

- 不能自动投放广告；
- 不能替代人工审核；
- 不能作为 CRM 使用；
- 不能自动成交或回传真实转化数据；
- 不能在没有 API Key 的情况下联网搜索或调用模型。

## Agent 角色

1. 市场研究分析师；
2. 首席营销策略师；
3. 营销创意与内容策划师；
4. 首席营销审核官。

## Task 流程

1. `research_task`
2. `project_understanding_task`
3. `marketing_strategy_task`
4. `campaign_idea_task`
5. `copy_creation_task`
6. `quality_review_task`

## 目录结构

```text
src/marketing_posts/
  crew.py                 Crew 组装逻辑
  main.py                 运行入口
  runtime.py              运行辅助逻辑
  config/
    agents.yaml           Agent 配置
    tasks.yaml            Task 配置
evals/                    轻量评测脚本和案例
output/                   样例输出
pyproject.toml
uv.lock
.env.example
```

## 环境配置

```powershell
Copy-Item .env.example .env
```

需要配置：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
SERPER_API_KEY=your_serper_api_key_here
```

真实 `.env` 不应提交。

## 运行

```powershell
uv sync
uv run marketing_posts
```

## 评测

```powershell
uv run python evals/generate_cases.py
uv run python evals/run_eval.py
```

## 当前状态

这是未完成开发中的多 Agent 营销策略原型。它的主要价值在于 Agent 分工、Prompt 结构、输出格式和轻量评测逻辑。
