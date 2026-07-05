# python-ai-mcp-server-demo

Python counterpart of the Java `spring-ai-mcp-server-demo` module.

## Run order for class

```powershell
cd python-ai-mcp-server-demo
python -m unittest discover -s tests -v
python -m python_ai_mcp_server_demo.self_check
python -m python_ai_mcp_server_demo.offline_demo
python -m python_ai_mcp_server_demo
```

The first three commands are offline and stdlib-only. The last command starts a small JSON HTTP server on `127.0.0.1:8082`.

## Capabilities

- Tool: `getWeather(cityName)` returns weather for `上海`, `北京`, or `不知道`.
- Prompt: `greeting(name)` returns the assistant greeting prompt result.
- Resource: `config://{key}` returns configured values, defaulting to `123`.

## Classroom story

This module follows `python-spring-ai-demo`: the previous module showed an MCP client shape; this module shows what a tiny MCP-style server exposes.
