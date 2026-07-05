from .email_tool import EmailTool, markdown_to_html
from .weekly_report_controller import WeeklyReportController


class FakeChatClient:
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        return "## 本周项目总结\n* 自检通过\n\n## 下周计划\n* 继续演示"


class FakeGitTool:
    def get_commit_log(self, project_path: str) -> str:
        return "2026-07-04 | Teacher | add weekly report demo"


def main() -> None:
    assert "<h2>周报</h2>" in markdown_to_html("## 周报\n* 完成")
    email_tool = EmailTool(to_email="student@example.com", from_email="teacher@example.com")
    controller = WeeklyReportController(FakeChatClient(), FakeGitTool(), email_tool)
    report = "".join(chunk["content"] for chunk in controller.sse("check", "."))
    assert "本周项目总结" in report
    confirmation = "".join(chunk["content"] for chunk in controller.sse("check", "确认发送邮件"))
    assert "邮件已准备" in confirmation
    print("python-ai-weekly-report self check passed")


if __name__ == "__main__":
    main()
