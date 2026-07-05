# python-ai-deepresearch

A Python teaching project for deep research agents: planning, searching, collecting evidence, and producing reports.

## Run order for class

```powershell
cd python-ai-deepresearch
python -m unittest discover -s tests -v
python -m python_ai_deepresearch.self_check
python -m python_ai_deepresearch.offline_demo
python -m python_ai_deepresearch.parallel_streaming_example
python -m python_ai_deepresearch
```

The first four commands are offline. The last command calls the configured model.

Optional:

- `TAVILY_API_KEY` enables the real Tavily search tool.
- `PROVIDER=deepseek|dashscope`, `DEEPSEEK_API_KEY`, `DASHSCOPE_API_KEY`, and `LLM_NAME` configure the live model.
