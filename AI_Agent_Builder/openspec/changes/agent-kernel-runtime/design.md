# Agent Kernel Runtime Design

## Core Contract

Every agent execution writes:

- `agent_runs`: durable execution record with learner, agent, runtime, provider, model, parent object, tool names, input, output, status, latency, and error.
- `agent_traces`: compact user-facing trace linked to `agent_runs`.

The runtime contract is:

```text
AgentRunRequest
→ choose runtime: rule / mock / claude_agent_sdk
→ run agent
→ validate JSON output
→ persist AgentRun
→ persist AgentTrace
→ return typed decision
```

## Agents

- `LearningPlannerAgent`: clarifies learner intent and produces planning decisions.
- `ProjectTutorAgent`: coaches inside a project without doing the work for the learner.
- `ReviewAgent`: reads sandbox output and submission metadata, then produces review evidence.
- `CoachTaskAgent`: turns review gaps into the next learner action.
- `MicroExerciseCoach`: evaluates short course exercises.

## Runtime Modes

- `rule`: local deterministic fallback.
- `mock`: deterministic review/demo output.
- `claude_agent_sdk`: Claude Agent SDK JSON runner.

## Data Flow

```text
intake message
→ AgentRuntime.run(planner)
→ planning session + agent run + trace

tutor message
→ AgentRuntime.run(tutor)
→ tutor session + agent run + trace

submission
→ sandbox run
→ AgentRuntime.run(review)
→ review + evidence
→ AgentRuntime.run(next-task)
→ coach task
```

## Frontend Contract

The frontend should not render raw terms like AgentRun or quality gate as the primary language. It should show:

- AI 教练正在判断下一步
- 正在检查你的项目能不能运行
- 正在根据检查结果生成下一轮任务
- 这一步完成后会留下什么求职证据

