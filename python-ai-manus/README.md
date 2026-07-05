# python-ai-manus

A Python teaching project for Manus-style task execution: planning, file tools, search tools, browser tools, and sandbox boundaries.

## Run order for class

```powershell
cd python-ai-manus
python -m unittest discover -s tests -v
python -m python_ai_manus.self_check
python -m python_ai_manus.offline_demo
python -m python_ai_manus.external_smoke_check
python -m python_ai_manus
```

The first three commands are offline. `external_smoke_check` checks Tavily, Docker, and Playwright when their local environment is available. The last command calls the configured model.

## Provider config

```powershell
$env:PROVIDER="deepseek"
$env:DEEPSEEK_API_KEY="your-key"
$env:LLM_NAME="deepseek-chat"
```

or:

```powershell
$env:PROVIDER="dashscope"
$env:DASHSCOPE_API_KEY="your-key"
$env:LLM_NAME="qwen-plus"
```

Optional tool keys/runtime:

- `TAVILY_API_KEY` for `tavily_search`
- Docker Desktop for `sandbox`
- `playwright` Python package plus browsers for `browser`
