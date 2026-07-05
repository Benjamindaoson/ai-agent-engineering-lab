# 教学注释：python-agentscope-agui-demo

这一关讲 Agent 和前端 UI 如何通过 AG-UI 风格事件连接。

## 这一关学什么

- 线程消息
- Run 事件
- 文本消息开始/增量/结束
- SSE 风格输出
- 静态页面入口

## 先看哪些文件

1. `python_agentscope_agui_demo/agui_application.py`：AG-UI 事件入口。
2. `python_agentscope_agui_demo/offline_demo.py`：课堂离线演示入口。
3. `resources/static/index.html`：前端页面入口。

## 课堂讲法

重点讲事件流，不要把它扩展成完整前端平台。完整平台放到 `production-platform/` 阶段。
