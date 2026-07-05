# Python ReAct Agent Design

## Scope

Add `python-react-agent/` as a Python counterpart to `java-react-agent/`. Keep the Java module unchanged.

## Structure

- `python_react_agent/agent_tools.py`: `AgentTools.write_file`
- `python_react_agent/model_config.py`: `ModelConfig` and provider selection
- `python_react_agent/react_agent.py`: `ReActAgent` loop and parser
- `python_react_agent/tool.py`: `@tool` metadata decorator
- `python_react_agent/tool_param.py`: `@tool_param` parameter metadata decorator
- `python_react_agent/tool_util.py`: `ToolUtil.get_tool_description`

## Provider Config

`PROVIDER=dashscope` reads `DASHSCOPE_API_KEY` and uses `https://dashscope.aliyuncs.com/compatible-mode/v1`. `PROVIDER=deepseek` reads `DEEPSEEK_API_KEY` and uses `https://api.deepseek.com`. `LLM_NAME` can override the default model.

## Verification

Offline tests cover config selection, tool metadata, parser behavior, and tool execution helpers. Live model calls remain manual because they require provider credentials.
