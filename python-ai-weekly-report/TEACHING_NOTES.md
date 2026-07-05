# 教学注释：python-ai-weekly-report

这一关讲自动化 Agent：读取 Git 提交记录，生成周报，再走邮件确认流程。

## 这一关学什么

- Git 日志读取
- 周报生成
- 邮件 dry-run
- 用户确认后再发送
- 外部命令失败处理

## 先看哪些文件

1. `python_ai_weekly_report/git_tool.py`：Git 命令边界。
2. `python_ai_weekly_report/weekly_report_controller.py`：生成周报和确认发送流程。
3. `python_ai_weekly_report/email_tool.py`：邮件工具，默认 dry-run。
4. `python_ai_weekly_report/offline_demo.py`：课堂离线演示入口。

## 课堂讲法

这关适合强调：Agent 做自动化时，危险动作要确认，外部命令要有清晰错误。
