from .chat_client import ChatClient
from .email_tool import EmailTool
from .git_tool import GitTool
from .model_config import ModelConfig
from .weekly_report_controller import WeeklyReportController


def create_controller() -> WeeklyReportController:
    return WeeklyReportController(ChatClient(ModelConfig.from_env()), GitTool(), EmailTool())


def main() -> None:
    project_path = input("请输入 Git 项目路径: ").strip()
    controller = create_controller()
    for chunk in controller.sse("cli", project_path):
        print(chunk["content"], end="", flush=True)
    print()
    confirm = input("确认发送邮件？输入“确认发送邮件”继续: ").strip()
    for chunk in controller.sse("cli", confirm):
        print(chunk["content"], end="", flush=True)
    print()


if __name__ == "__main__":
    main()
