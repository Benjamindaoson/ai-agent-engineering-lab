from pathlib import Path


def run_agent_skill_demo2() -> str:
    skill_path = Path(__file__).resolve().parents[1] / "resources" / "skills" / "explain-code" / "python.md"
    rules = skill_path.read_text(encoding="utf-8").strip()
    return f"从文件系统技能仓库读取 explain-code。Python 规则：{rules}"


def main() -> None:
    print(run_agent_skill_demo2())


if __name__ == "__main__":
    main()
