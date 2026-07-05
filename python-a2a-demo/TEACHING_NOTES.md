# 教学注释：python-a2a-demo

这一关讲 A2A，也就是 Agent 和 Agent 之间如何发现、调用、协作。

## 这一关学什么

- Agent 注册
- AgentCard
- 远程 Agent 调用
- 顺序组合 Agent
- 缺失 Agent 的错误处理

## 先看哪些文件

1. `python_a2a_demo/server.py`：服务端如何注册 Agent。
2. `python_a2a_demo/client.py`：客户端如何发现和调用远程 Agent。
3. `python_a2a_demo/sequential_agent.py`：多个 Agent 如何串起来。
4. `python_a2a_demo/offline_demo.py`：课堂离线演示入口。

## 课堂讲法

这一关重点讲系统协作：一个 Agent 不必会所有事，它可以把任务交给另一个 Agent。
