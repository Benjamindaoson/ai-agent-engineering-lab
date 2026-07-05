# 教学注释：python-react-agent

这一关是整个课程的第一关，目标是让学员看懂一个最小 ReAct Agent 是怎么跑起来的。

## 这一关学什么

- 大模型先输出 `Reason`
- 再决定是否调用 `Action`
- 工具执行后返回观察结果
- 最后输出 `FinalAnswer`

## 先看哪些文件

1. `python_react_agent/react_agent.py`：主循环，最值得逐行讲。
2. `python_react_agent/agent_tools.py`：工具是怎么暴露给 Agent 的。
3. `python_react_agent/model_config.py`：DashScope / DeepSeek 这类 OpenAI-compatible 配置从哪里来。
4. `python_react_agent/offline_demo.py`：课堂离线演示入口。

## 课堂讲法

先不要讲复杂框架。让学员记住一句话：Agent 不是一次回答，而是“思考、行动、观察、再思考”的循环。
