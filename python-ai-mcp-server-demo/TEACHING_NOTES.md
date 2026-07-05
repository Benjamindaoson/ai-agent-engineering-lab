# 教学注释：python-ai-mcp-server-demo

这一关讲 MCP Server。MCP 的核心是把工具、资源、提示词用统一协议暴露出去。

## 这一关学什么

- tools/list
- tools/call
- prompts/list
- prompts/get
- resources/list
- resources/read
- JSON-RPC 风格请求

## 先看哪些文件

1. `python_ai_mcp_server_demo/mcp_server_application.py`：MCP 能力注册。
2. `python_ai_mcp_server_demo/weather_service.py`：工具、资源、提示词的具体实现。
3. `python_ai_mcp_server_demo/offline_demo.py`：课堂离线演示入口。

## 课堂讲法

让学生记住：MCP 不是模型，它是让 Agent 发现和调用外部能力的协议。
