import os
import subprocess
import tempfile

from .email_tool import EmailTool
from .git_tool import GitTool
from .weekly_report_controller import WeeklyReportController


class DemoChatClient:
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        return """## 本周项目总结

### 1. 主要功能与进展
* 完成周报 Agent 的 Git 日志读取和邮件确认流程

### 2. Bug 修复
* 暂无

### 3. 代码重构与优化
* 将工具调用和控制器流程拆开，方便课堂讲解

### 4. 其他
* 增加离线演示

## 下周计划
* 接入真实模型后优化周报措辞
"""


def create_demo_repo() -> str:
    tempdir = tempfile.mkdtemp(prefix="weekly-report-demo-")
    subprocess.run(["git", "init"], cwd=tempdir, check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["git", "config", "user.name", "Teacher"], cwd=tempdir, check=True)
    subprocess.run(["git", "config", "user.email", "teacher@example.com"], cwd=tempdir, check=True)
    with open(os.path.join(tempdir, "weekly.txt"), "w", encoding="utf-8") as file:
        file.write("weekly report demo")
    subprocess.run(["git", "add", "weekly.txt"], cwd=tempdir, check=True)
    subprocess.run(["git", "commit", "-m", "add weekly report demo"], cwd=tempdir, check=True, stdout=subprocess.DEVNULL)
    return tempdir


def main() -> None:
    repo = create_demo_repo()
    email_tool = EmailTool(to_email="student@example.com", from_email="teacher@example.com")
    controller = WeeklyReportController(DemoChatClient(), GitTool(), email_tool)
    print("生成周报：")
    for chunk in controller.sse("demo", repo):
        print(chunk["content"], end="", flush=True)
    print("\n\n确认发送：")
    for chunk in controller.sse("demo", "确认发送邮件"):
        print(chunk["content"], end="", flush=True)
    print()


if __name__ == "__main__":
    main()
