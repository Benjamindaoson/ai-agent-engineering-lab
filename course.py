from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROJECTS_ROOT = ROOT
PROGRESS_FILE = ROOT / ".course_progress.json"


@dataclass(frozen=True)
class Level:
    number: int
    project: str
    title: str
    package: str


LEVELS = [
    Level(1, "python-react-agent", "基础关：ReAct 最小内核", "python_react_agent"),
    Level(2, "python-ai-manus", "工具关：Manus 工具箱", "python_ai_manus"),
    Level(3, "python-ai-engineer", "工程关：AI 工程师", "python_ai_engineer"),
    Level(4, "python-ai-deepresearch", "研究关：深度研究", "python_ai_deepresearch"),
    Level(5, "python-ai-data", "数据关：数据分析 Agent", "python_ai_data"),
    Level(6, "python-ai-weekly-report", "自动化关：周报生成", "python_ai_weekly_report"),
    Level(7, "python-ai-order", "业务关：订单 Agent", "python_ai_order"),
    Level(8, "python-ai-consultation", "垂直业务关：咨询 Agent", "python_ai_consultation"),
    Level(9, "python-spring-ai-demo", "框架关：Spring AI 对照", "python_spring_ai_demo"),
    Level(10, "python-ai-mcp-server-demo", "协议关：MCP Server", "python_ai_mcp_server_demo"),
    Level(11, "python-a2a-demo", "协作关：A2A", "python_a2a_demo"),
    Level(12, "python-ai-alibaba-demo", "生态关：Alibaba", "python_ai_alibaba_demo"),
    Level(13, "python-ai-alibaba-graph-demo", "图工作流关：Graph", "python_ai_alibaba_graph_demo"),
    Level(14, "python-ai-alibaba-agent-framework-demo", "框架进阶关：Agent Framework", "python_ai_alibaba_agent_framework_demo"),
    Level(15, "python-ai-multi-model", "多模型关：Multi Model", "python_ai_multi_model"),
    Level(16, "python-claw", "Boss 关：Claw 综合项目", "python_claw"),
    Level(17, "python-agentscope-demo", "支线关：AgentScope", "python_agentscope_demo"),
    Level(18, "python-agentscope-agui-demo", "支线关：AgentScope AG-UI", "python_agentscope_agui_demo"),
    Level(19, "python-agentscope-a2a-demo", "支线关：AgentScope A2A", "python_agentscope_a2a_demo"),
]


def load_progress() -> int:
    if not PROGRESS_FILE.exists():
        return 1
    data = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    return max(1, min(int(data.get("current_level", 1)), len(LEVELS)))


def save_progress(current_level: int) -> None:
    PROGRESS_FILE.write_text(
        json.dumps({"current_level": current_level}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def current_level() -> Level:
    return LEVELS[load_progress() - 1]


def print_status() -> None:
    current = load_progress()
    for level in LEVELS:
        if level.number < current:
            mark = "已通关"
        elif level.number == current:
            mark = "当前关"
        else:
            mark = "未解锁"
        print(f"{level.number:02d}. {mark} - {level.project} - {level.title}")


def command_for(level: Level, target: str) -> list[str]:
    if target == "self_check":
        return [sys.executable, "-m", f"{level.package}.self_check"]
    if target == "offline_demo":
        return [sys.executable, "-m", f"{level.package}.offline_demo"]
    if target == "tests":
        return [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
    raise ValueError(f"unknown target: {target}")


def run_target(level: Level, target: str) -> bool:
    project_dir = PROJECTS_ROOT / level.project
    print(f"\n== 第 {level.number:02d} 关：{level.project} / {target} ==")
    result = subprocess.run(command_for(level, target), cwd=project_dir, check=False)
    return result.returncode == 0


def run_current(target: str) -> int:
    level = current_level()
    targets = ["self_check", "offline_demo", "tests"] if target == "all" else [target]
    passed = all(run_target(level, item) for item in targets)
    if not passed:
        print(f"\n第 {level.number:02d} 关未通过，修好后重新运行。")
        return 1
    if target != "all":
        print(f"\n第 {level.number:02d} 关 {target} 已通过，运行 `python course.py run all` 才会解锁下一关。")
        return 0
    if level.number < len(LEVELS):
        save_progress(level.number + 1)
        print(f"\n第 {level.number:02d} 关已通关，已解锁第 {level.number + 1:02d} 关。")
    else:
        print("\n19 关全部通关。")
    return 0


def reset_progress() -> None:
    save_progress(1)
    print("进度已重置到第 01 关。")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Python Agent 课程闯关入口")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("status", help="查看通关进度")
    subparsers.add_parser("reset", help="重置到第 01 关")
    run_parser = subparsers.add_parser("run", help="运行当前关")
    run_parser.add_argument(
        "target",
        nargs="?",
        choices=["self_check", "offline_demo", "tests", "all"],
        default="all",
        help="默认 all，全部通过后解锁下一关",
    )
    args = parser.parse_args(argv)
    if args.command == "status" or args.command is None:
        print_status()
        return 0
    if args.command == "reset":
        reset_progress()
        return 0
    if args.command == "run":
        return run_current(args.target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
