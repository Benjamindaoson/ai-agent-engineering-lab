from pathlib import Path


def run_agent_skill_demo3() -> str:
    skill_path = Path(__file__).resolve().parents[1] / "resources" / "skills" / "explain-code" / "SKILL.md"
    first_line = skill_path.read_text(encoding="utf-8").splitlines()[0]
    return f"从内置 skills 目录读取技能：解释代码，入口 {first_line}"


def main() -> None:
    print(run_agent_skill_demo3())


if __name__ == "__main__":
    main()
