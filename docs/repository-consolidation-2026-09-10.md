# Repository Consolidation — 2026-09-10

`Benjamindaoson/ai-agent-engineering-lab` is the canonical repository for small Agent demos, framework exercises, teaching examples and course case studies.

## Rule

One small demo should not remain one standalone repository. New framework demos, Agent experiments, protocol samples and course exercises should be added here under a clear teaching category.

## Imported sources

| Source repository | Destination | Preserved assets | Exclusions |
|---|---|---|---|
| `project-task-manager-crew @ 3081824` | `frameworks/crewai/project-task-manager-crew/` | CrewAI sequential three-agent teaching demo, YAML agent/task config, README, env example and lockfile | local indexes and caches |
| `crewai-handwrite @ 1805f32` | `frameworks/crewai/handwrite/` | CrewAI handwritten exercises, Markdown validator, marketing strategy eval examples, configs, tests and sample outputs | local skill config, caches |
| `crewai-examples-private-notes @ db4af66` | `frameworks/crewai/examples-notes/` | reusable CrewAI example source, local notes, prompts, configs and small teaching data | GitHub automation metadata, binary/vector DB/model artifacts, caches |
| `travelagent @ 6ea654a` | `frameworks/langchain/spain-travel-agent/` | LangChain Spain travel Agent teaching script, README, requirements and env template | zip teaching bundle |
| `email-invitation-agent @ 19559af` | `case-studies/email-invitation-agent/` | lightweight email invitation Agent source and package metadata | none beyond local caches |
| `agent-for-planning @ 82a2b71` | `case-studies/urban-planning-review-agent/` | urban planning review RAG prototype, knowledge-base scripts, notebook and project document | local caches |
| `agentlab-rag @ 56c7d73` | `case-studies/agentlab-rag/` | AgentLab product case study, controlled world, runtime, tests, evidence, docs and project packs | local Codex skill config and indexes |
| `mini-claw @ 28ff97f` | `protocols/mini-claw-java/` | Java Claw/Skill runtime demo, templates, static page and Spring service code | IDE metadata |

## Development rule

These imported projects are teaching/reference material. Keep production claims out of this repository unless backed by runnable tests, evidence artifacts or measured results.
