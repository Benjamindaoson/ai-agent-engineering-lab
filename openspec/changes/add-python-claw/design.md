## Design

`python-claw` keeps the platform behaviors and skips live framework plumbing:

- `java_claw_properties.py`: configuration defaults.
- `memory/memory_service.py`: daily notes and `MEMORY.md`.
- `memory/session_startup.py`: loads `BOOTSTRAP`, `AGENTS`, `SOUL`, `USER`, `IDENTITY`, and `TOOLS` into the system prompt.
- `skill/skill_loader.py`: scans `workspace/skills/*/SKILL.md`.
- `claw_agent.py`: initializes workspace, copies templates, creates `main_session` and `feishu_session`, logs conversations, and supports `/new` resets.
- `web_socket_handler.py`: preserves JSON message protocol.
- `feishu_message_receiver.py`: preserves text parsing, event-id idempotency, `/new`, and private/group reply routing.
- `feishu_tools.py` and `tool/memory/update_memory_tool.py`: local tools.

Live Spring Boot, WebSocket server runtime, Feishu SDK connection, AgentScope model calls, and shell execution are deliberately not included in the offline Python teaching port.

## Verification

Unit tests cover workspace initialization, prompt assembly, memory writes, update-memory categories, web chat protocol, Feishu event idempotency, reply routing, skill loading, and local tools.
