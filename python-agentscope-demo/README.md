# python-agentscope-demo

Python counterpart of the Java `agentscope-demo` module.

## Run order for class

```powershell
cd python-agentscope-demo
python -m unittest discover -s tests -v
python -m python_agentscope_demo.self_check
python -m python_agentscope_demo.offline_demo
python -m python_agentscope_demo
```

The first three commands are offline. Java AgentScope, DashScope live calls, Mem0, Elasticsearch, MCP server, Studio server, and image model calls are represented by deterministic Python equivalents.

## Java to Python map

- `HelloWorldDemo.java` -> `hello_world_demo.py`
- `ToolDemo.java` -> `tool_demo.py`
- `ToolPresetDemo.java` -> `tool_preset_demo.py`
- `ToolContextDemo.java` -> `tool_context_demo.py`
- `ToolGroupDemo.java` -> `tool_group_demo.py`
- `ToolEmitterDemo.java` -> `tool_emitter_demo.py`
- `HookDemo.java` -> `hook_demo.py`
- `HumanInTheLoopDemo.java` -> `human_in_the_loop_demo.py`
- `ShortMemoryDemo.java` -> `short_memory_demo.py`
- `LongMemoryDemo.java` -> `long_memory_demo.py`
- `MsgHubDemo.java` -> `msg_hub_demo.py`
- `MultiAgentDebateDemo.java` -> `multi_agent_debate_demo.py`
- `SequentialPipelineDemo.java` -> `sequential_pipeline_demo.py`
- `FanoutPipelineDemo.java` -> `fanout_pipeline_demo.py`
- `StructuredOutputDemo.java` -> `structured_output_demo.py`
- `PlanDemo.java` -> `plan_demo.py`
- `AgentSkillDemo1.java` -> `agent_skill_demo1.py`
- `AgentSkillDemo2.java` -> `agent_skill_demo2.py`
- `AgentSkillDemo3.java` -> `agent_skill_demo3.py`
- `RAGDemo.java` -> `rag_demo.py`
- `MCPDemo.java` -> `mcp_demo.py`
- `VisionDemo.java` -> `vision_demo.py`
- `ImageGenerateDemo.java` -> `image_generate_demo.py`
- `StudioDemo.java` -> `studio_demo.py`
- `context/UserContext.java` -> `context/user_context.py`
- `hooks/ConfirmationHook.java` -> `hooks/confirmation_hook.py`
- `hooks/LoggingHook.java` -> `hooks/logging_hook.py`
- `product/ProductInfo.java` -> `product/product_info.py`
- `tools/EmailService.java` -> `tools/email_service.py`
- `tools/WeatherService.java` -> `tools/weather_service.py`

## Class storyline

1. Start with a basic ReAct-style agent and deterministic model response.
2. Add tools, preset parameters, injected user context, and tool groups.
3. Show tool streaming and hooks, then pause sensitive tools for human confirmation.
4. Add short memory, JSONL session persistence, message hub, and pipelines.
5. Demonstrate structured output, skills, RAG, MCP, vision, image generation, Studio, and planning as offline classroom entries.
6. Use `model_config.py` only when moving from offline demos to live OpenAI-compatible providers.
