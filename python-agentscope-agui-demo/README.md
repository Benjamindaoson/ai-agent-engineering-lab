# python-agentscope-agui-demo

A Python teaching project for AG-UI interaction: browser requests, `/agui/run`, SSE events, and thread memory.

## Run order for class

```powershell
cd python-agentscope-agui-demo
python -m unittest discover -s tests -v
python -m python_agentscope_agui_demo.self_check
python -m python_agentscope_agui_demo.offline_demo
python -m python_agentscope_agui_demo --port 8000
```

Then open `http://127.0.0.1:8000`.

## Class storyline

1. This project uses a small local HTTP service for the AG-UI event entry.
2. Python uses stdlib `http.server` to expose the same teaching surface.
3. Browser posts `{threadId, runId, messages}` to `/agui/run`.
4. Server streams AG-UI SSE events back to the browser.
5. Server keeps per-thread memory while the process is running.
