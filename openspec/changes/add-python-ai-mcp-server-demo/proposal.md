## Why

`spring-ai-mcp-server-demo` is the server-side counterpart to the Spring AI MCP client demo. It teaches how tools, prompts, and resources are exposed by an MCP server.

## What Changes

- Add `python-ai-mcp-server-demo/` without modifying `spring-ai-mcp-server-demo/`.
- Mirror Java `WeatherService` and `McpServerApplication`.
- Preserve the Java MCP capabilities: weather tool, greeting prompt, and `config://{key}` resource.
- Use stdlib-only local dispatch and an optional HTTP JSON endpoint for offline classroom use.

## Impact

- New Python module under `python-ai-mcp-server-demo/`.
- New OpenSpec change under `openspec/changes/add-python-ai-mcp-server-demo/`.
