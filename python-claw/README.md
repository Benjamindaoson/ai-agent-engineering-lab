# python-claw

Python counterpart of the Java `java-claw` module.

## Run order for class

```powershell
cd python-claw
python -m unittest discover -s tests -v
python -m python_claw.self_check
python -m python_claw.offline_demo
python -m python_claw
```

The first three commands are offline. Spring Boot, AgentScope, Feishu SDK, live WebSocket server, shell execution, and DashScope calls are represented by stdlib equivalents.

## Java to Python map

- `JavaClawApplication.java` -> `java_claw_application.py`
- `JavaClawProperties.java` -> `java_claw_properties.py`
- `ClawAgent.java` -> `claw_agent.py`
- `FeishuMessageReceiver.java` -> `feishu_message_receiver.py`
- `FeishuTools.java` -> `feishu_tools.py`
- `WebSocketHandler.java` -> `web_socket_handler.py`
- `WebSocketConfig.java` -> `web_socket_config.py`
- `memory/MemoryService.java` -> `memory/memory_service.py`
- `memory/SessionStartup.java` -> `memory/session_startup.py`
- `skill/SkillLoader.java` -> `skill/skill_loader.py`
- `tool/memory/UpdateMemoryTool.java` -> `tool/memory/update_memory_tool.py`

## Class storyline

1. Initialize workspace from templates and built-in skills.
2. Build system prompt from `BOOTSTRAP`, `AGENTS`, `SOUL`, `USER`, `IDENTITY`, and `TOOLS`.
3. Create `main_session` and `feishu_session`.
4. Log daily notes and long-term memory.
5. Handle web chat JSON messages and `/new`.
6. Handle Feishu events with idempotency and private/group reply routing.
7. Demonstrate local tools and memory-update tool.
