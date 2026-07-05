## Why

`java-react-agent` is the smallest hand-written ReAct Agent module in the repository, so it is the right first target for a Python translation. A Python version gives learners a side-by-side implementation while keeping the original Java module intact.

## What Changes

- Add a new `python-react-agent/` module.
- Preserve the Java module and keep the Python structure close enough for file-by-file comparison.
- Implement the same ReAct loop: prompt building, model call, output parsing, tool execution, observation history, and max-iteration stop.
- Use the official `openai` Python package against OpenAI-compatible providers.
- Add provider config for `dashscope` and `deepseek`, using `DASHSCOPE_API_KEY` and `DEEPSEEK_API_KEY`.
- Add a small runnable self-check for parser/tool-description behavior.

## Capabilities

### New Capabilities

- `python-react-agent`: Python implementation of the hand-written ReAct Agent module with OpenAI-compatible provider configuration.

### Modified Capabilities

- None.

## Impact

- New files under `python-react-agent/`.
- New OpenSpec artifacts under `openspec/changes/add-python-react-agent/`.
- New Superpowers design and implementation plan documents under `docs/superpowers/`.
- No changes to existing Java source files.
