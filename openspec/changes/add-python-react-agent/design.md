## Context

`java-react-agent` contains a compact Java ReAct Agent implementation with six source files: `AgentTools`, `ModelConfig`, `ReActAgent`, `Tool`, `ToolParam`, and `ToolUtil`. The Python module will sit beside it as `python-react-agent/` so students can compare implementations without changing the original Maven project.

The Java module uses OpenAI-compatible DashScope settings through `openai-java`. The Python module will use the official `openai` package and keep provider differences in one config file.

## Goals / Non-Goals

**Goals:**

- Create a Python module whose files map directly to the Java source files.
- Keep the ReAct control flow close to the Java version.
- Support `dashscope` and `deepseek` providers through environment variables.
- Include a small local verification path that does not require an API key.
- Document setup and run commands.

**Non-Goals:**

- Do not change `java-react-agent/`.
- Do not translate the other Maven modules in this change.
- Do not add a Python packaging system beyond `requirements.txt`.
- Do not implement OpenAI function-calling; this remains a prompt-parsing ReAct example.

## Decisions

- **Create `python-react-agent/` instead of nesting under `java-react-agent/`.** This keeps the Java module untouched and makes each course module independently runnable.
- **Use snake_case filenames with Java class names preserved inside the files.** Python imports stay idiomatic while class/function names remain easy to map back to Java.
- **Use a small decorator-based tool metadata layer.** `@tool` and `@tool_param` replace Java annotations with the least Python code needed for reflection-style tool descriptions.
- **Centralize provider config in `model_config.py`.** `ModelConfig.from_env()` reads `PROVIDER`, `DASHSCOPE_API_KEY`, and `DEEPSEEK_API_KEY`, then returns `api_key`, `base_url`, and `llm_name`.
- **Keep tests as a stdlib self-check.** A `python -m python_react_agent.self_check` command verifies parser and tool metadata without adding pytest.

## Risks / Trade-offs

- **DeepSeek model names can change** -> Use environment override `LLM_NAME` and document defaults.
- **Prompt parsing is brittle** -> Match the Java behavior and test common fenced JSON and final answer cases.
- **File-writing tool is powerful** -> Keep it equivalent to Java but document that it writes to local paths supplied by the model.
