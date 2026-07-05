# 教学注释：python-ai-alibaba-agent-framework-demo

这一关讲 Agent 框架常见组件如何组合。

## 这一关学什么

- Agent
- Tool
- Memory
- Hook
- Interceptor
- Human Approval
- Multi-Agent
- Agent-as-Tool

## 先看哪些文件

1. `python_ai_alibaba_agent_framework_demo/agent/zhouyu_agent.py`：Agent 主体。
2. `python_ai_alibaba_agent_framework_demo/hooks/`：Hook 如何插入流程。
3. `python_ai_alibaba_agent_framework_demo/interceptor/`：拦截器如何包装调用。
4. `python_ai_alibaba_agent_framework_demo/tools/`：工具实现。
5. `python_ai_alibaba_agent_framework_demo/offline_demo.py`：课堂离线演示入口。

## 课堂讲法

不要一次讲完所有组件。建议分两节：先讲 Agent + Tool + Memory，再讲 Hook + Interceptor + 多 Agent。
