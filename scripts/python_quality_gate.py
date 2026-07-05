from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECTS_ROOT = ROOT


@dataclass(frozen=True)
class ProjectCheck:
    project: str
    package: str


def discover_projects() -> list[ProjectCheck]:
    projects: list[ProjectCheck] = []
    for project_dir in sorted(PROJECTS_ROOT.iterdir()):
        if not project_dir.is_dir() or not project_dir.name.startswith("python-"):
            continue
        package_dirs = [item for item in project_dir.iterdir() if item.is_dir() and (item / "__init__.py").exists()]
        if not package_dirs:
            raise RuntimeError(f"No package directory found in {project_dir}")
        projects.append(ProjectCheck(project_dir.name, package_dirs[0].name))
    return projects


def run(project: ProjectCheck, label: str, command: list[str]) -> bool:
    print(f"{project.project}: {label} ... ", end="", flush=True)
    try:
        result = subprocess.run(command, cwd=PROJECTS_ROOT / project.project, check=False, timeout=60)
    except subprocess.TimeoutExpired:
        print("TIMEOUT")
        return False
    if result.returncode == 0:
        print("PASS")
        return True
    print(f"FAIL({result.returncode})")
    return False


def main() -> int:
    checks = discover_projects()
    failed = False
    for project in checks:
        failed |= not run(project, "self_check", [sys.executable, "-m", f"{project.package}.self_check"])
        failed |= not run(project, "tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
        failed |= not run(project, "offline_demo", [sys.executable, "-m", f"{project.package}.offline_demo"])
    print(f"\nChecked {len(checks)} Python projects.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
