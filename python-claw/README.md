# python-claw

A Python teaching project for a platform-style agent: workspace, skills, memory, web chat, message entry, and tool orchestration.

## Run order for class

```powershell
cd python-claw
python -m unittest discover -s tests -v
python -m python_claw.self_check
python -m python_claw.offline_demo
python -m python_claw
```

The first three commands are offline. Spring Boot, AgentScope, Feishu SDK, live WebSocket server, shell execution, and DashScope calls are represented by stdlib equivalents.

## Class storyline

1. Initialize workspace from templates and built-in skills.
2. Build system prompt from `BOOTSTRAP`, `AGENTS`, `SOUL`, `USER`, `IDENTITY`, and `TOOLS`.
3. Create `main_session` and `feishu_session`.
4. Log daily notes and long-term memory.
5. Handle web chat JSON messages and `/new`.
6. Handle Feishu events with idempotency and private/group reply routing.
7. Demonstrate local tools and memory-update tool.
