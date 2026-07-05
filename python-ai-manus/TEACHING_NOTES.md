# 教学注释：python-ai-manus

这一关是工具关，用来说明 Manus 类 Agent 为什么比普通聊天机器人更强：它可以调工具完成任务。

## 这一关学什么

- 工具注册
- 文件读写
- 搜索工具
- 浏览器工具
- Docker 沙箱工具
- 工具失败时如何返回清晰错误

## 先看哪些文件

1. `python_ai_manus/agent/tool_call_agent.py`：模型返回 tool call 后如何执行工具。
2. `python_ai_manus/tools/tool_collection.py`：工具注册表。
3. `python_ai_manus/tools/impl/file_writer_tool.py`：最简单的工具实现。
4. `python_ai_manus/tools/impl/docker_sandbox.py`：外部 Docker 边界。
5. `python_ai_manus/offline_demo.py`：课堂离线演示入口。

## 课堂讲法

这一关不要追求真实跑 Docker 或浏览器。先讲清楚工具边界：Agent 负责决定调用什么，工具负责执行，失败要变成可读错误。
