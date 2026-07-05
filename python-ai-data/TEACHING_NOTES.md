# 教学注释：python-ai-data

这一关讲数据分析 Agent。它把自然语言问题转成 SQL，执行后再生成报告。

## 这一关学什么

- 关键词提取
- 表结构召回
- SQL 计划生成
- SQL 执行与失败修复
- 数据报告生成

## 先看哪些文件

1. `python_ai_data/data_application.py`：完整数据分析工作流。
2. `python_ai_data/node/planner_node.py`：问题如何变成 SQL 计划。
3. `python_ai_data/node/sql_execute_node.py`：SQL 执行边界，只允许查询。
4. `python_ai_data/node/plan_execute_node.py`：SQL 出错后如何修复。
5. `python_ai_data/offline_demo.py`：课堂离线演示入口。

## 课堂讲法

重点讲“AI 不能直接碰数据库乱改数据”。这一关只允许 `SELECT`，这是数据 Agent 的安全底线。
