# 教学注释：python-ai-engineer

这一关讲 AI 工程师 Agent：把一个需求拆成步骤，再交给不同 Agent 或工具执行。

## 这一关学什么

- 需求拆解
- 计划 JSON 解析
- 多步骤执行
- 文件工具读写
- Agent Hook 记录执行过程

## 先看哪些文件

1. `python_ai_engineer/planner_agent_service.py`：计划如何被执行。
2. `python_ai_engineer/plan.py`：计划结构。
3. `python_ai_engineer/file_tool.py`：工程文件读写工具。
4. `python_ai_engineer/react_agent.py`：带工具调用的工程 Agent。
5. `python_ai_engineer/offline_demo.py`：课堂离线演示入口。

## 课堂讲法

这一关重点不是“AI 写代码很神奇”，而是让学生理解工程 Agent 必须先计划，再执行，再检查。
