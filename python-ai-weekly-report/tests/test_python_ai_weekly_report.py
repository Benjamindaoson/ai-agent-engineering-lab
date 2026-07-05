import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from python_ai_weekly_report.email_tool import EmailTool
from python_ai_weekly_report.git_tool import GitTool
from python_ai_weekly_report.weekly_report_controller import WeeklyReportController


class FakeChatClient:
    def __init__(self):
        self.calls = []

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        self.calls.append((system_prompt, user_prompt))
        return "## 本周项目总结\n\n### 1. 主要功能与进展\n* 完成登录接口\n\n## 下周计划\n* 补充测试"


class WeeklyReportTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.repo = self.tmpdir.name
        subprocess.run(["git", "init"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["git", "config", "user.name", "Teacher"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.email", "teacher@example.com"], cwd=self.repo, check=True)
        with open(os.path.join(self.repo, "app.txt"), "w", encoding="utf-8") as file:
            file.write("hello")
        subprocess.run(["git", "add", "app.txt"], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-m", "add login api"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_git_tool_reads_weekly_commits_for_local_user(self):
        log = GitTool().get_commit_log(self.repo)

        self.assertIn("Teacher", log)
        self.assertIn("add login api", log)

    def test_git_tool_reports_missing_git(self):
        with patch("subprocess.run", side_effect=FileNotFoundError):
            with self.assertRaisesRegex(RuntimeError, "Git is not installed"):
                GitTool().get_commit_log(self.repo)

    def test_email_tool_dry_run_returns_message_with_html_report(self):
        result = EmailTool(to_email="student@example.com", from_email="teacher@example.com").send_email("## 周报\n* 完成任务")

        self.assertTrue(result.dry_run)
        self.assertEqual("student@example.com", result.to_email)
        self.assertIn("<h2>周报</h2>", result.html_content)
        self.assertIn("<li>完成任务</li>", result.html_content)

    def test_controller_generates_report_then_sends_after_confirmation(self):
        email_tool = EmailTool(to_email="student@example.com", from_email="teacher@example.com")
        controller = WeeklyReportController(FakeChatClient(), GitTool(), email_tool)

        chunks = list(controller.sse("class-1", self.repo))
        report = "".join(chunk["content"] for chunk in chunks)
        sent = list(controller.sse("class-1", "确认发送邮件"))

        self.assertIn("本周项目总结", report)
        self.assertEqual(1, len(email_tool.sent_messages))
        self.assertIn("邮件已准备", "".join(chunk["content"] for chunk in sent))


if __name__ == "__main__":
    unittest.main()
