# Python ReAct Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `python-react-agent/` as a runnable Python counterpart to `java-react-agent/`.

**Architecture:** Keep one Python file per Java concept and centralize provider differences in `ModelConfig`. The ReAct loop remains prompt-parsing based, not function-calling based.

**Tech Stack:** Python standard library plus `openai`.

## Global Constraints

- Do not modify `java-react-agent/`.
- Only add one runtime dependency: `openai`.
- Provider selection MUST support `dashscope` and `deepseek`.
- Offline verification MUST run without API keys.

---

### Task 1: Offline Tests

**Files:**
- Create: `python-react-agent/tests/test_python_react_agent.py`

**Interfaces:**
- Consumes: planned package `python_react_agent`
- Produces: executable offline test command

- [ ] **Step 1: Write failing tests**

Run: `python -m unittest discover -s python-react-agent/tests -v`

Expected before implementation: FAIL because `python_react_agent` does not exist.

### Task 2: Core Package

**Files:**
- Create: `python-react-agent/python_react_agent/*.py`
- Create: `python-react-agent/requirements.txt`
- Create: `python-react-agent/README.md`

**Interfaces:**
- Produces: `ModelConfig.from_env()`, `AgentTools.write_file()`, `ToolUtil.get_tool_description()`, `ReActAgent.parse_llm_output()`, `ReActAgent.run()`

- [ ] **Step 1: Implement minimum code to pass offline tests**
- [ ] **Step 2: Run offline tests**

Run: `python -m unittest discover -s python-react-agent/tests -v`

Expected after implementation: PASS.

### Task 3: Validation

**Files:**
- Check: `openspec/changes/add-python-react-agent/*`
- Check: `python-react-agent/*`

- [ ] **Step 1: Validate OpenSpec**

Run: `npx openspec validate add-python-react-agent`

- [ ] **Step 2: Check unchanged Java module**

Run: `git status --short`

Expected: no modified files under `java-react-agent/`.
