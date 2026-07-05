# Agent Kernel Runtime

## Why

The product currently presents AI roles in the UI, but the backend still records Planner, Tutor, and Review runs through different paths. This makes the system feel like pages plus rules instead of a coherent agent system.

## What Changes

- Add a unified AgentRun record for Planner, Tutor, Review, Course Coach, and generated next actions.
- Keep AgentTrace as the user-visible audit trail, but make every trace link back to an AgentRun.
- Expose one AgentRuntime abstraction with `rule`, `mock`, and `claude_agent_sdk` modes.
- Route Planner and Tutor through the same runtime pattern already used by Review.
- Record sandbox execution and ReviewAgent decisions in the same agent run chain.
- After a submission review, always generate the learner's next task from the review result.
- Surface frontend status as natural AI coach language, not backend terminology.

## Out Of Scope

- Full background worker queue.
- Production-grade container isolation.
- Supabase migration rollout.
- Paid user management.
