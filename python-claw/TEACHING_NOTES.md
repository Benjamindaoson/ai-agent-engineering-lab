# 教学注释：python-claw

这一关是 Boss 关，用来把前面学过的能力组织成一个更完整的项目。

## 这一关学什么

- Workspace 初始化
- Prompt 模板
- Skill 加载
- Memory
- WebSocket 对话
- Feishu 消息入口
- 工具集合

## 先看哪些文件

1. 应用组装入口：负责把工作区、技能、记忆和消息入口串起来。
2. `python_claw/claw_agent.py`：核心 Agent。
3. `python_claw/memory/memory_service.py`：记忆系统。
4. `python_claw/skill/skill_loader.py`：技能加载。
5. `python_claw/web_socket_handler.py`：网页对话入口。
6. `python_claw/offline_demo.py`：课堂离线演示入口。

## 课堂讲法

这是综合项目，不建议第一天就讲。等学生理解工具、记忆、协议、多 Agent 后，再把它作为收束。
