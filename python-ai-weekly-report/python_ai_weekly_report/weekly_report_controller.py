import os

from .email_tool import EmailTool
from .git_tool import GitTool


SYSTEM_PROMPT = """
## 角色定义
你是一名在软件开发公司工作的Java开发工程师。

## 任务
根据项目 Git 提交历史记录生成简洁、清晰、结构化的工作周报，并在用户确认后发送邮件。

## 周报格式
## 本周项目总结 (YYYY-MM-DD 到 YYYY-MM-DD)

### 1. 主要功能与进展
* [这里总结新功能和主要进展]

### 2. Bug 修复
* [这里总结已修复的 Bug]

### 3. 代码重构与优化
* [这里总结代码结构调整、性能优化等]

### 4. 其他
* [总结文档更新、测试用例添加等其他提交]

## 下周计划
* [你根据本周总结，生成大致的下周计划给用户进行参考]

注意：不要包含 Merge pull request、Merge branch、.gitignore 等提交；邮件发送前必须等待人类确认。
"""


class WeeklyReportController:
    def __init__(self, chat_client, git_tool: GitTool, email_tool: EmailTool):
        self.chat_client = chat_client
        self.git_tool = git_tool
        self.email_tool = email_tool
        self.pending_reports: dict[str, str] = {}

    def sse(self, chat_id: str, message: str):
        if self._is_confirmation(message):
            yield from self._send_pending_report(chat_id)
            return
        if os.path.isdir(message):
            yield from self._generate_report(chat_id, message)
            return
        yield {"content": "请输入一个 Git 项目路径，或在生成周报后输入“确认发送邮件”。"}

    def _generate_report(self, chat_id: str, project_path: str):
        commit_log = self.git_tool.get_commit_log(project_path)
        user_prompt = f"项目路径：{project_path}\n\nGit提交记录：\n{commit_log or '本周没有提交记录'}"
        report = self.chat_client.complete(SYSTEM_PROMPT, user_prompt)
        self.pending_reports[chat_id] = report
        yield from self._stream(report)

    def _send_pending_report(self, chat_id: str):
        report = self.pending_reports.get(chat_id)
        if not report:
            yield {"content": "没有待发送的周报，请先输入项目路径生成周报。"}
            return
        result = self.email_tool.send_email(report)
        yield {"content": f"邮件已准备：{result.to_email}，dry_run={str(result.dry_run).lower()}"}

    def _stream(self, text: str, chunk_size: int = 24):
        for index in range(0, len(text), chunk_size):
            yield {"content": text[index : index + chunk_size]}

    def _is_confirmation(self, message: str) -> bool:
        return any(word in message for word in ("确认", "发送", "send", "yes", "ok"))
