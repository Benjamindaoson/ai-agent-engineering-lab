## Design

`python-ai-mcp-server-demo` mirrors the Java module:

- `weather_service.py`: exposes `get_weather(city_name)`, `greeting(name)`, and `get_config(key)`.
- `mcp_server_application.py`: registers tool, prompt, and resource metadata and dispatches JSON-style MCP requests.
- `offline_demo.py` and `self_check.py`: demonstrate tool/list, tool/call, prompt/get, and resource/read without a live MCP client.

No external MCP package is required. The goal is to make the protocol shape visible for teaching, while keeping the module runnable on a clean Python install.

## Verification

Tests cover tool behavior, prompt/resource behavior, capability listing, capability dispatch, and JSON request handling.
