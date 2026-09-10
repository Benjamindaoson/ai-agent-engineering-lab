import sys
from pathlib import Path

from dotenv import load_dotenv

from crew import ProjectTaskManagerCrew


ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / ".env")


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


FULL_REQUIREMENT = """请生成一个 Python 命令行待办/日程管理器。

功能要求：

1. 支持添加任务。
2. 每个任务包含：
   - id
   - title
   - project
   - priority，取值为 high / medium / low
   - status，取值为 todo / doing / done / cancelled
   - due_date
   - tags
   - notes
   - created_at
   - updated_at

3. 支持查看所有任务。
4. 支持按项目筛选任务。
5. 支持按状态筛选任务。
6. 支持按优先级筛选任务。
7. 支持搜索任务标题、标签和备注。
8. 支持修改任务状态。
9. 支持删除任务。
10. 所有任务保存到 tasks.json。
11. 程序重新启动后可以读取之前保存的任务。
12. 支持导出 Markdown 格式的任务报告。
13. 代码必须只使用 Python 标准库。
14. 代码结构要清晰，适合 Python 初学者阅读。
15. 最终输出必须是一份完整可运行的 Python 代码。"""


SMOKE_REQUIREMENT = """请生成一个只使用 Python 标准库的命令行待办管理器。
第一版只需要：
1. 添加任务；
2. 查看任务；
3. 标记任务完成；
4. 保存到 tasks.json；
5. 程序重启后能读取任务。"""


def run(requirement: str | None = None):
    """运行完整的待办/日程管理器生成流程。"""
    load_dotenv()
    inputs = {"requirement": requirement or FULL_REQUIREMENT}
    result = ProjectTaskManagerCrew().crew().kickoff(inputs=inputs)
    print(result)


def run_smoke():
    """运行简化版待办/日程管理器 smoke 流程。"""
    load_dotenv()
    inputs = {"requirement": SMOKE_REQUIREMENT}
    result = ProjectTaskManagerCrew().crew().kickoff(inputs=inputs)
    print(result)


if __name__ == "__main__":
    run()
