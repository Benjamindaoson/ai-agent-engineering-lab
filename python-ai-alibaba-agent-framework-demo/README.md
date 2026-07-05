# python-ai-alibaba-agent-framework-demo

Python counterpart of the Java `spring-ai-alibaba-agent-framework-demo` module.

## Run order for class

```powershell
cd python-ai-alibaba-agent-framework-demo
python -m unittest discover -s tests -v
python -m python_ai_alibaba_agent_framework_demo.self_check
python -m python_ai_alibaba_agent_framework_demo.offline_demo
python -m python_ai_alibaba_agent_framework_demo
```

The first three commands are offline. DashScope, Tavily, Elasticsearch, Spring Boot, and the Alibaba graph runtime are represented by small in-memory equivalents.

## Provider config

```powershell
$env:PROVIDER="deepseek"
$env:DEEPSEEK_API_KEY="your-key"
$env:LLM_NAME="deepseek-chat"
```

## Java to Python map

- `AgentApplication.java` -> `agent_application.py`
- `AgentController.java` -> `agent_controller.py`
- `agent/ZhouyuAgent.java` -> `agent/zhouyu_agent.py`
- `hooks/*.java` -> `hooks/*.py`
- `interceptor/*.java` -> `interceptor/*.py`
- `tools/*.java` -> `tools/*.py`

## Class storyline

1. ReactAgent with tools.
2. MemorySaver and checkpoints.
3. Hooks and interceptors around model/tool calls.
4. Human approval interruption and resume.
5. Store access from tool context.
6. Sequential, parallel, routing, custom flow, complex workflow, agent-as-tool, and RAG-agent patterns.
