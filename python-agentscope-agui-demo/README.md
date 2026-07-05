# python-agentscope-agui-demo

Python counterpart of the Java `agentscope-agui-demo` module.

## Run order for class

```powershell
cd python-agentscope-agui-demo
python -m unittest discover -s tests -v
python -m python_agentscope_agui_demo.self_check
python -m python_agentscope_agui_demo.offline_demo
python -m python_agentscope_agui_demo --port 8000
```

Then open `http://127.0.0.1:8000`.

## Java to Python map

- `AguiApplication.java` -> `python_agentscope_agui_demo/agui_application.py`
- `application.yml` -> `AguiApplication.memory` and `/agui/run` defaults
- `static/index.html` -> `python_agentscope_agui_demo/static/index.html`
- `static/js/agui-client.js` -> `python_agentscope_agui_demo/static/js/agui-client.js`

## Class storyline

1. Java uses Spring Boot plus AgentScope AG-UI starter.
2. Python uses stdlib `http.server` to expose the same teaching surface.
3. Browser posts `{threadId, runId, messages}` to `/agui/run`.
4. Server streams AG-UI SSE events back to the browser.
5. Server keeps per-thread memory while the process is running.
